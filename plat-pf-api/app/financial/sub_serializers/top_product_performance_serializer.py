from app.financial.models import TopProductChannelPerformance
from app.database.sub_serializers.tenant_db_for_serializer import TenantDBForSerializer


class TopProductChannelPerformanceSerializer(TenantDBForSerializer):
    class Meta:
        model = TopProductChannelPerformance
        fields = '__all__'
