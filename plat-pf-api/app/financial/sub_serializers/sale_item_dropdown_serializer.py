from app.financial.models import Variant, SaleStatus, ProfitStatus, FulfillmentChannel
from app.database.sub_serializers.tenant_db_for_serializer import TenantDBForSerializer


class SaleItemVariationSerializer(TenantDBForSerializer):
    class Meta:
        model = Variant
        fields = '__all__'


class SaleItemStatusSerializer(TenantDBForSerializer):
    class Meta:
        model = SaleStatus
        fields = '__all__'


class SaleItemProfitStatusSerializer(TenantDBForSerializer):
    class Meta:
        model = ProfitStatus
        fields = '__all__'


class FulfillmentChannelSerializer(TenantDBForSerializer):
    class Meta:
        model = FulfillmentChannel
        fields = '__all__'
