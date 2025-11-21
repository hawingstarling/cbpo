import logging

from rest_framework import generics
from rest_framework.response import Response

from app.financial.permissions.base import JwtTokenPermission
from app.shopify_partner.exceptions import ConfigShopifyPartnerException
from app.shopify_partner.models import Setting
from app.shopify_partner.serializers import (
    RequestOauthSerializer)
from app.shopify_partner.services.oauth.generate import (
    generate_oauth_url)

logger = logging.getLogger(__name__)


class RequestOauthView(generics.GenericAPIView):
    serializer_class = RequestOauthSerializer
    permission_classes = [JwtTokenPermission]

    def post(self, request, *args, **kwargs):
        setting = Setting.objects.first()
        if setting is None:
            raise ConfigShopifyPartnerException()
        serializer = RequestOauthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request_oauth = serializer.save()
        auth_url = generate_oauth_url(
            request_oauth.shop_url,
            request_oauth.state,
            setting
        )
        return Response(status=200, data={'auth_url': auth_url})



