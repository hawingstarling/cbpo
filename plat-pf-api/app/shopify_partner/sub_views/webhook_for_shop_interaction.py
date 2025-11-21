import logging
from abc import ABC

from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from app.shopify_partner.models import Setting
from app.shopify_partner.services.webhhok.mandatory import verify_webhook

logger = logging.getLogger(__name__)

"""
shopify requires some mandatory webhooks on RUD of shop's user data
in the shopify admin
"""


class __WebhookHmacHeader(ABC):

    @classmethod
    def _check_hmac(cls, request) -> bool:
        logger.info(f'[Shopify HMAC checking]')
        setting = Setting.objects.first()
        api_secret_key = setting.get_decrypt_secret
        return verify_webhook(request.body, request.headers.get('X-Shopify-Hmac-SHA256'), api_secret_key)


class WebHookCustomerDataRequestView(__WebhookHmacHeader, generics.GenericAPIView):
    """
    shopify event: Requests to view stored customer data
    """

    permission_classes = (AllowAny,)
    serializer_class = None

    def post(self, request, *args, **kwargs):
        verified = self._check_hmac(request)
        if not verified:
            return Response(status=status.HTTP_401_UNAUTHORIZED, data={"message": "unauthorized"})

        # TODO: implement data usage
        return Response(status=status.HTTP_200_OK, data={"message": "unauthorized"})


class WebHookCustomerDataRequestDeleteView(__WebhookHmacHeader, generics.GenericAPIView):
    """
    shopify event: Requests to delete customer data
    """
    permission_classes = (AllowAny,)
    serializer_class = None

    def post(self, request, *args, **kwargs):
        verified = self._check_hmac(request)
        if not verified:
            return Response(status=status.HTTP_401_UNAUTHORIZED, data={"message": "unauthorized"})

        # TODO: implement data usage
        return Response(status=status.HTTP_200_OK, data={"message": "OK"})


class WebHookShopRequestDeleteView(__WebhookHmacHeader, generics.GenericAPIView):
    """
    shopify event: Requests to delete shop data
    """
    permission_classes = (AllowAny,)
    serializer_class = None

    def post(self, request, *args, **kwargs):
        verified = self._check_hmac(request)
        if not verified:
            return Response(status=status.HTTP_401_UNAUTHORIZED, data={"message": "unauthorized"})

        # TODO: implement data usage
        return Response(status=status.HTTP_200_OK, data={"message": "OK"})
