from app.financial.models import StatePopulation
from app.database.sub_serializers.tenant_db_for_serializer import TenantDBForSerializer


class StatePopulationSerializer(TenantDBForSerializer):
    class Meta:
        model = StatePopulation
        exclude = ['id']
