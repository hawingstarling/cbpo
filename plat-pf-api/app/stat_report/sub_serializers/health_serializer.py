import logging
from app.financial.sub_serializers.organization_serializer import OrganizationSerializer, ClientSerializer
from app.stat_report.models import OrgClientHealth
from app.database.sub_serializers.tenant_db_for_serializer import TenantDBForSerializer
from app.stat_report.variables.healthy import SERVICE_CONFIG

logger = logging.getLogger(__name__)


class OrgClientHealthySerializer(TenantDBForSerializer):
    organization = OrganizationSerializer(read_only=True)
    client = ClientSerializer(read_only=True)

    class Meta:
        model = OrgClientHealth
        fields = '__all__'

    def to_representation(self, instance: OrgClientHealth):
        data = super().to_representation(instance)
        try:
            data.update(dict(service_name=SERVICE_CONFIG[data["service_name"]]))
        except Exception as ex:
            logger.error(f"[{self.__class__.__name__}][to_representation] {ex}")
        return data
