from app.financial.models import HighChartMapping
from app.database.sub_serializers.tenant_db_for_serializer import TenantDBForSerializer


class HighChartMappingSerializer(TenantDBForSerializer):
    class Meta:
        model = HighChartMapping
        exclude = ['id', 'is_removed']
