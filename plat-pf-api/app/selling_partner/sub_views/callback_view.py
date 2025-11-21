import logging
from datetime import datetime

from django.db import transaction, DEFAULT_DB_ALIAS
from django.http import HttpResponseRedirect
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from app.financial.models import ClientSettings
from app.financial.variable.client_setting_variable import SPAPI_RECONNECT_ROTATION_DATELINE_TYPE, \
    SPAPI_RECONNECT_LWA_SECRET_KEY_TYPE
from app.selling_partner.jobs.register import register_spapi_keys_setting, recheck_spapi_connection_settings
from app.selling_partner.models import Setting, AppSetting
from app.selling_partner.permissions.internal_token import PortalServiceInternalPermission
from app.selling_partner.sub_serializers.callback_serializer import LWAClientCallbackSerializer
from app.selling_partner.sub_serializers.token_serializer import OauthTokenRequestSerializer

logger = logging.getLogger(__name__)


class SellerCentralOauthCallbackView(APIView):
    permission_classes = [AllowAny]
    selling_partner_id = openapi.Parameter('selling_partner_id', in_=openapi.IN_QUERY,
                                           description="The identifier of the selling partner who is authorizing your application.",
                                           type=openapi.TYPE_STRING,
                                           required=True)
    spapi_oauth_code = openapi.Parameter('spapi_oauth_code', in_=openapi.IN_QUERY,
                                         description="Selling Partner ID",
                                         type=openapi.TYPE_STRING,
                                         required=True)

    state = openapi.Parameter('state', in_=openapi.IN_QUERY,
                              description="The state value",
                              type=openapi.TYPE_STRING,
                              required=True)

    mws_auth_token = openapi.Parameter('mws_auth_token', in_=openapi.IN_QUERY,
                                       description="The MWSAuthToken value",
                                       type=openapi.TYPE_STRING,
                                       required=False)

    @swagger_auto_schema(manual_parameters=[selling_partner_id, spapi_oauth_code, state, mws_auth_token])
    def get(self, request, *args, **kwargs):
        #
        spapi_setting = Setting.objects.first()
        assert spapi_setting is not None, "Selling Partner setting is not Empty"
        try:
            data = dict(
                selling_partner_id=self.request.query_params.get('selling_partner_id'),
                spapi_oauth_code=self.request.query_params.get('spapi_oauth_code'),
                state=self.request.query_params.get('state')
            )
            oauth_token_serializer = OauthTokenRequestSerializer(data=data)
            oauth_token_serializer.is_valid(raise_exception=True)
            oauth_token_serializer.save()
            #
            request_url = request.get_full_path()
            query_params_path = request_url.split('?')[1]
            url_redirect = f"{spapi_setting.web_aws_oauth_redirect}?{query_params_path}"
        except Exception as ex:
            logger.error(f"[{self.__class__.__name__}] {ex}")
            url_redirect = f"{spapi_setting.web_aws_oauth_redirect}?errors={str(ex)}"
        return HttpResponseRedirect(redirect_to=url_redirect)


class LWAClientCallback(APIView):
    permission_classes = [PortalServiceInternalPermission]

    @swagger_auto_schema(operation_description='Callback update LWA to system',
                         request_body=LWAClientCallbackSerializer, responses={status.HTTP_200_OK: None})
    def post(self, request, *args, **kwargs):
        serializer = LWAClientCallbackSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        spapi_app_setting = get_object_or_404(AppSetting, spapi_app_id=validated_data["app_id"])
        #
        amz_lwa_expired = datetime.strptime(validated_data["date_expired"], "%Y-%m-%d %H:%M:%S") \
            if "date_expired" in validated_data else spapi_app_setting.amz_lwa_expired
        is_changed_expired = spapi_app_setting.amz_lwa_expired != amz_lwa_expired
        is_changed = spapi_app_setting.amz_lwa_client_id != validated_data["lwa_client_id"] \
                     or spapi_app_setting.amz_lwa_client_secret != validated_data["lwa_client_secret"] \
                     or is_changed_expired
        if is_changed:
            spapi_app_setting.amz_lwa_client_id = validated_data["lwa_client_id"]
            spapi_app_setting.amz_lwa_client_secret = validated_data["lwa_client_secret"]
            spapi_app_setting.amz_lwa_expired = amz_lwa_expired
            if is_changed_expired:
                spapi_app_setting.ac_spapi_type_reconnect = SPAPI_RECONNECT_ROTATION_DATELINE_TYPE
            else:
                spapi_app_setting.ac_spapi_type_reconnect = SPAPI_RECONNECT_LWA_SECRET_KEY_TYPE
            spapi_app_setting.save()
            client_ids = ClientSettings.objects.tenant_db_for(DEFAULT_DB_ALIAS).filter(ac_spapi_enabled=True) \
                .values_list("client_id", flat=True)
            transaction.on_commit(lambda: {
                register_spapi_keys_setting(client_ids=list(client_ids)),
                recheck_spapi_connection_settings(client_ids=list(client_ids))
            })
        return Response(status=status.HTTP_200_OK, data=None)

    @classmethod
    def _get_msg_reconnect(cls, client_id: str, is_changed_expired: bool = False):
        # @TODO: Handler msg show in UI setting page
        return f"{client_id} has been reconnected"
