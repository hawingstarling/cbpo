from rest_framework import serializers

from app.financial.models import Organization, ClientPortal
from app.database.sub_serializers.tenant_db_for_serializer import TenantDBForSerializer


class OrganizationSerializer(TenantDBForSerializer):
    class Meta:
        model = Organization
        fields = '__all__'


class ClientSerializer(TenantDBForSerializer):
    organization = OrganizationSerializer(read_only=True)
    class Meta:
        model = ClientPortal
        fields = '__all__'


class ClientSettingSerializer(ClientSerializer):
    organization = OrganizationSerializer(read_only=True)
    amazon = serializers.BooleanField(default=False)
    shopify = serializers.BooleanField(default=False)
    cart_rover = serializers.BooleanField(default=False)
