from rest_framework import serializers

from app.app_setting.models import LWACredentialClientSetting


class LWACredentialClientSettingSerializer(serializers.ModelSerializer):
    lwa_client_secret = serializers.CharField(source="plain_text_lwa_secret_key")

    class Meta:
        model = LWACredentialClientSetting
        fields = ("app_id", "lwa_client_id", "lwa_client_secret", "modified")
