import logging
from rest_framework import serializers
from app.financial.models import ClientUserTrack
from app.database.sub_serializers.tenant_db_for_serializer import TenantDBForSerializer

logger = logging.getLogger(__name__)


class ClientUserTrackSerializer(TenantDBForSerializer):
    class Meta:
        model = ClientUserTrack
        fields = '__all__'


class ClientUserTrackPayloadSerializer(ClientUserTrackSerializer):
    widget = serializers.JSONField(required=True)

    class Meta:
        model = ClientUserTrack
        exclude = ['client', 'user']
