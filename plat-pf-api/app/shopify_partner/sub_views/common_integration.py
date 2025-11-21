import logging

from django.http import HttpResponseRedirect, HttpResponse
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from app.financial.permissions.base import JwtTokenPermission
from app.shopify_partner.exceptions import ConfigShopifyPartnerException
from app.shopify_partner.exceptions import NotFoundShopifyPartnerOauthClientRegister
from app.shopify_partner.models import OauthTokenRequest
from app.shopify_partner.models import Setting
from app.shopify_partner.models import ShopifyPartnerOauthClientRegister
from app.shopify_partner.serializers import (
    ShopifyPartnerOauthClientRegisterSerializer, RevokeShopifyPartnerSetting)
from app.shopify_partner.services.integrations.ac_register_or_revoke import ac_register
from app.shopify_partner.services.integrations.ac_register_or_revoke import ac_revoke
from app.shopify_partner.services.oauth.generate import (
    get_access_token_callback, validate_shopify_app_integration, shopify_revoke)

logger = logging.getLogger(__name__)


class GetShopifyPartnerOauthClientRegisterView(generics.RetrieveAPIView):
    permission_classes = (JwtTokenPermission,)
    serializer_class = ShopifyPartnerOauthClientRegisterSerializer

    def get_object(self):
        try:
            client_id = self.kwargs.get("client_id")
            return ShopifyPartnerOauthClientRegister.objects.tenant_db_for(client_id).get(
                client_id=client_id, enabled=True)
        except ShopifyPartnerOauthClientRegister.DoesNotExist:
            raise NotFoundShopifyPartnerOauthClientRegister()


class RevokeAccessShopifyPartner(generics.GenericAPIView):
    permission_classes = (JwtTokenPermission,)
    serializer_class = RevokeShopifyPartnerSetting

    def post(self, request, *args, **kwargs):
        serializer = RevokeShopifyPartnerSetting(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data

        is_success_sp_revoke = shopify_revoke(str(data['client_id']))
        if is_success_sp_revoke:
            ac_revoke(str(data['client_id']))
            return Response(status=status.HTTP_200_OK, data={"message": "Revoke successful"})
        else:
            return Response(
                status=status.HTTP_400_BAD_REQUEST, data={"message": "Oops! Something went wrong"})


class ShopifyPartnerCallBackView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        setting = Setting.objects.get()
        if setting is None:
            raise ConfigShopifyPartnerException()

        is_valid = validate_shopify_app_integration(request.query_params, setting)
        if not is_valid:
            return HttpResponse("Oauth process error!")

        shop_url, state = self.get_shop_and_state(request.query_params)
        oauth_request = OauthTokenRequest.objects.get(shop_url=shop_url, state=state)
        access_token = get_access_token_callback(shop_url, request.query_params, setting)
        oauth_request.access_token = access_token
        oauth_request.save(update_fields=['access_token'])
        ShopifyPartnerOauthClientRegister.objects.tenant_db_for(str(oauth_request.client_id)).update_or_create(
            client_id=oauth_request.client_id,
            defaults={"enabled": True, "oauth_token_request": oauth_request})
        redirect_url_web = Setting.generate_web_redirect_url(
            client_id=str(oauth_request.client_id),
            web_redirect_url=setting.web_redirect_url)
        # TODO: sending to celery
        ac_register(str(oauth_request.client_id))
        return HttpResponseRedirect(redirect_to=redirect_url_web)

    @classmethod
    def get_shop_and_state(cls, query_params: dict):
        return query_params['shop'], query_params['state']
