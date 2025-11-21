from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from app.core.exceptions import InvalidParameterException
from app.financial.models import ClientSettings
from app.financial.permissions.base import JwtTokenPermission
from app.financial.permissions.client_settings_permissions import (
    ViewClientSettingsJwtPermission, ChangeClientSettingsJwtPermission)
from app.financial.sub_serializers.client_settings_serializer import ClientSettingsSerializer, CartRoverSerializer


class ClientSettingsBaseView(GenericAPIView):
    def get_object(self):
        client_id = self.kwargs.get("client_id")
        try:
            obj, _ = ClientSettings.objects.tenant_db_for(client_id).get_or_create(client_id=client_id)
            return obj
        except ClientSettings.DoesNotExist:
            raise InvalidParameterException(f'ClientSettings does not exist.')

    def get_permissions(self):
        if self.request.method == 'GET':
            self.permission_classes = [ViewClientSettingsJwtPermission]
        else:
            self.permission_classes = [ChangeClientSettingsJwtPermission]
        return super().get_permissions()


class RetrieveUpdateClientSettingsView(generics.RetrieveUpdateAPIView, ClientSettingsBaseView):
    serializer_class = ClientSettingsSerializer


class CreateClientSettingsView(generics.CreateAPIView):
    serializer_class = ClientSettingsSerializer
    permission_classes = (ChangeClientSettingsJwtPermission,)


class ClientCartRoverValidationView(APIView):
    serializer_class = ClientSettingsSerializer
    permission_classes = [JwtTokenPermission]

    @swagger_auto_schema(operation_description="""Validation cart rover information""",
                         request_body=CartRoverSerializer, responses={status.HTTP_200_OK: None})
    def post(self, request, *args, **kwargs):
        serializer = CartRoverSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)

        client_id = self.kwargs.get("client_id")
        err = ClientSettings.validate_cart_rover(client_id, serializer.validated_data)
        if not err:
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST, data=err)
