from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.views import APIView
from app.financial.permissions.base import JwtTokenPermission
from app.selling_partner.models import OauthTokenRequest
from app.selling_partner.sub_serializers.token_serializer import OauthTokenRequestPayloadSerializer, \
    OauthTokenRequestResponseSerializer
from rest_framework.response import Response


class OauthTokenRequestView(APIView):
    serializer_class = OauthTokenRequestPayloadSerializer
    permission_classes = [JwtTokenPermission]

    @swagger_auto_schema(operation_description='Oauth Token Request', request_body=OauthTokenRequestPayloadSerializer,
                         responses={status.HTTP_200_OK: OauthTokenRequestResponseSerializer})
    def post(self, request, *args, **kwargs):
        data = request.data
        oauth_request_serializer = OauthTokenRequestPayloadSerializer(data=data)
        oauth_request_serializer.is_valid(raise_exception=True)
        validated_data = oauth_request_serializer.validated_data
        oauth_token = get_object_or_404(OauthTokenRequest, **validated_data)
        return Response(status=oauth_token.status_code, data=oauth_token.payload)
