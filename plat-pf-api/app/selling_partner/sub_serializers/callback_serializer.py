from rest_framework import serializers


class LWAClientCallbackSerializer(serializers.Serializer):
    app_id = serializers.CharField(max_length=255)
    lwa_client_id = serializers.CharField(max_length=255)
    lwa_client_secret = serializers.CharField(max_length=255)
    date_expired = serializers.CharField(max_length=255)
