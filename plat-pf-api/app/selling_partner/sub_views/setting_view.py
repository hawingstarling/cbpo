from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.response import Response

from app.core.exceptions import InvalidParameterException
from app.financial.models import ClientPortal
from app.financial.permissions.base import JwtTokenPermission
from app.financial.sub_views.client_settings_view import ClientSettingsBaseView
from app.selling_partner.models import AppSetting
from app.selling_partner.sub_serializers.setting_serializer import AppSettingSerializer, ConnectionSPAccountSerializer, \
    RevokeSPAccountSerializer


class RetrieveSPAPIAppSettingView(generics.RetrieveAPIView):
    serializer_class = AppSettingSerializer
    queryset = AppSetting.objects.all()
    permission_classes = [JwtTokenPermission]

    def get_object(self):
        client_id = self.kwargs.get("client_id")
        try:
            ClientPortal.objects.tenant_db_for(client_id).get(id=client_id)
            obj = AppSetting.objects.tenant_db_for(client_id).first()
            assert obj is not None, "Setting not found"
            return obj
        except Exception as ex:
            raise InvalidParameterException(f'Object setting not found. Please check again administrator')


class ConnectionSPAccountView(ClientSettingsBaseView):
    serializer_class = ConnectionSPAccountSerializer

    @swagger_auto_schema(
        operation_description="An endpoint sp account connection.",
        request_body=ConnectionSPAccountSerializer
    )
    def post(self, request, *args, **kwargs):
        data = self.request.data
        ins = self.get_object()
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(ins, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_200_OK, data=serializer.data)


class RevokeSPAccountView(ClientSettingsBaseView):
    serializer_class = RevokeSPAccountSerializer

    def delete(self, request, *args, **kwargs):
        data = dict(
            ac_spapi_access_token=None,
            ac_spapi_refresh_token=None,
            ac_spapi_token_expired=None,
            ac_spapi_selling_partner_id=None,
            ac_spapi_auth_code=None,
            ac_spapi_state=None,
            ac_spapi_enabled=False
        )
        ins = self.get_object()
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(ins, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
