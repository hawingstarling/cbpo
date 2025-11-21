from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from app.selling_partner.models import OauthTokenRequest
from app.selling_partner.services.oauth_token import SPAPIOAuthManage
from django.utils.translation import gettext_lazy as _


class OauthTokenRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = OauthTokenRequest
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=OauthTokenRequest.objects.all(),
                fields=['state', 'spapi_oauth_code', 'selling_partner_id'],
                message=_('Oauth token request must be unique')
            )
        ]

    def create(self, validated_data):
        #
        oauth_token_manage = SPAPIOAuthManage()
        status_code, payload = oauth_token_manage.get_access_token(auth_code=validated_data['spapi_oauth_code'])
        ins, _ = OauthTokenRequest.objects.update_or_create(**validated_data,
                                                            defaults=dict(status_code=status_code, payload=payload))
        return ins


class OauthTokenRequestPayloadSerializer(serializers.Serializer):
    selling_partner_id = serializers.CharField(max_length=250)
    spapi_oauth_code = serializers.CharField(max_length=250)
    state = serializers.CharField(max_length=250)


class OauthTokenRequestResponseSerializer(serializers.Serializer):
    access_token = serializers.CharField()
    refresh_token = serializers.CharField()
    expires_in = serializers.IntegerField()
    token_type = serializers.CharField()
