import binascii
import os
from urllib.parse import urlparse

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from app.financial.models import ClientPortal
from app.shopify_partner.models import OauthTokenRequest, ShopifyPartnerOauthClientRegister


class RequestOauthSerializer(serializers.Serializer):
    shop_url = serializers.CharField(max_length=256)
    client_id = serializers.UUIDField()

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        client_id = validated_data.pop('client_id')

        validated_data.update(
            {'state': binascii.b2a_hex(os.urandom(15)).decode("utf-8"),
             'access_token': None})

        ins, _ = OauthTokenRequest.objects.update_or_create(
            client_id=client_id,
            defaults=validated_data)
        return ins

    @classmethod
    def validate_shop_url(cls, value):
        if 'https://' in value:
            res = urlparse(value)
            return res.netloc
        # remove last /
        if value[len(value) - 1] == '/':
            return value[:len(value) - 1]
        return value

    def validate(self, attrs):
        try:
            ClientPortal.objects.get(id=attrs['client_id'])
        except ClientPortal.DoesNotExist:
            raise ValidationError(detail={"client_id": 'Invalid client_id'})

        try:
            client_register = ShopifyPartnerOauthClientRegister.objects.get(
                client_id=attrs['client_id'])
            if client_register.enabled:
                raise ValidationError(
                    detail={"client_id": 'This client is already connected to a shop'})
        except ShopifyPartnerOauthClientRegister.DoesNotExist:
            pass
        return attrs


class ShopifyPartnerOauthClientRegisterSerializer(serializers.ModelSerializer):
    shop_url = serializers.SerializerMethodField(source='get_shop_url')

    class Meta:
        model = ShopifyPartnerOauthClientRegister
        fields = ('created', 'enabled', 'shop_url',)

    @classmethod
    def get_shop_url(cls, ins) -> str:
        return ins.oauth_token_request.shop_url


class RevokeShopifyPartnerSetting(serializers.Serializer):
    shop_url = serializers.CharField(max_length=256)
    client_id = serializers.UUIDField()

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    def validate(self, attrs):
        try:
            ClientPortal.objects.get(id=attrs["client_id"])
        except ClientPortal.DoesNotExist:
            raise ValidationError(
                detail={"client_id": "Client does not exist!"}
            )
        try:
            ShopifyPartnerOauthClientRegister.objects.get(
                client_id=attrs["client_id"], enabled=True,
                oauth_token_request__shop_url=attrs["shop_url"])
        except ShopifyPartnerOauthClientRegister.DoesNotExist:
            raise ValidationError(
                detail={"shop_url": f"{attrs['shop_url']} has been not registered yet!"}
            )
        return attrs
