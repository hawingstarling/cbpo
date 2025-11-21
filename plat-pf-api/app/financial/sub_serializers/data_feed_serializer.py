from rest_framework import serializers
from app.financial.models import DataFeedTrack
from app.core.sub_serializers.base_serializer import BaseSerializer
from app.database.sub_serializers.tenant_db_for_serializer import TenantDBForSerializer


class DataFeedTrackSerializer(TenantDBForSerializer):
    class Meta:
        model = DataFeedTrack
        fields = '__all__'


class DataFeedRetrieveItemSerializer(BaseSerializer):
    date = serializers.DateTimeField(required=True)
    file_uri = serializers.URLField(required=True)


class DataFeedRetrieveSerializer(BaseSerializer):
    items = DataFeedRetrieveItemSerializer(many=True)
