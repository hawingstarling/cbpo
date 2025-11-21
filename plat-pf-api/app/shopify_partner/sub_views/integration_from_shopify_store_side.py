import logging
from typing import Tuple, Union

from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings
from rest_framework import status, generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from app.financial.permissions.base import JwtTokenPermission
from app.shopify_partner.exceptions import ConfigShopifyPartnerException
from app.shopify_partner.models import Setting, OauthTokenRequest, ShopifyPartnerOauthClientRegister
from app.shopify_partner.serializers import RequestOauthSerializer
from app.shopify_partner.services.oauth.generate import (
    validate_shopify_app_integration, generate_oauth_url)

logger = logging.getLogger(__name__)


class RegisterShopUrlView(generics.GenericAPIView):
    serializer_class = RequestOauthSerializer
    permission_classes = [JwtTokenPermission]

    def post(self, request, *args, **kwargs):
        setting = Setting.objects.first()
        if setting is None:
            raise ConfigShopifyPartnerException()
        serializer = RequestOauthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=200, data={
            'message': 'Registered successfully! Please install app in the Shopify App Store.'})


class ShopifyPartnerAppIntegrationView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        setting = Setting.objects.get()
        if setting is None:
            raise ConfigShopifyPartnerException()
        is_valid = validate_shopify_app_integration(request.query_params, setting)

        if not is_valid:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"message": "invalid query params"})

        shop_url = request.query_params['shop']
        # check shop_url is registered
        is_register_shop_url, oauth_request = self.is_register_shop_url(shop_url=shop_url)
        is_client_installed_app = self.is_client_installed_merchant(oauth_request)

        if is_register_shop_url and is_client_installed_app:
            # merchant is already installed
            # redirect to PF App
            redirect_url_web = Setting.generate_web_redirect_url(
                client_id=str(oauth_request.client_id),
                web_redirect_url=setting.web_redirect_url)
            return HttpResponseRedirect(redirect_to=redirect_url_web)
        if is_register_shop_url and not is_client_installed_app:
            # merchant is register
            # not installed
            # redirect to Oauth Page
            oauth_url = generate_oauth_url(shop_url, oauth_request.state, setting)
            return HttpResponseRedirect(redirect_to=oauth_url)
        elif settings.CLIENT_ID_SHOPIFY_REVIEW:
            # required CLIENT_ID for review process
            # workaround for shopify review app process
            client_id = settings.CLIENT_ID_SHOPIFY_REVIEW
            is_client_connected = ShopifyPartnerOauthClientRegister.objects.filter(
                client_id=client_id).exists()
            if is_client_connected:
                ShopifyPartnerOauthClientRegister.objects.filter(client_id=client_id).delete()

            serializer = RequestOauthSerializer(
                data={"shop_url": shop_url, "client_id": client_id}
            )
            serializer.is_valid(raise_exception=True)
            oauth_request = serializer.save()

            oauth_url = generate_oauth_url(shop_url, oauth_request.state, setting)
            return HttpResponseRedirect(redirect_to=oauth_url)
        else:
            # Django view to display message
            return redirect(reverse('shopify-integration'))

    @classmethod
    def is_register_shop_url(cls, shop_url: str) -> Tuple[bool, Union[OauthTokenRequest, None]]:
        """
        in case of install App from the Shopify App Store
        need to register shop_url first for match WS and shop_url in callback from Shopify
        """
        try:
            ins = OauthTokenRequest.objects.get(shop_url=shop_url)
            return True, ins
        except OauthTokenRequest.DoesNotExist:
            return False, None

    @classmethod
    def is_client_installed_merchant(cls, oauth_request: Union[OauthTokenRequest, None]):
        """
        check merchant or Client if it has installed Precise Financial Connector App in Shopify App Store
        """
        if not oauth_request:
            return False
        try:
            ShopifyPartnerOauthClientRegister.objects.get(client_id=oauth_request.client_id, enabled=True)
            return True
        except ShopifyPartnerOauthClientRegister.DoesNotExist:
            return False
