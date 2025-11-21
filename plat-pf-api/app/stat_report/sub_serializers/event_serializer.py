from app.financial.sub_serializers.client_serializer import ChannelSerializer
from app.financial.sub_serializers.organization_serializer import ClientSerializer, OrganizationSerializer
from app.database.sub_serializers.tenant_db_for_serializer import TenantDBForSerializer
from app.stat_report.models import StatReport, StatClientChannelReport


class StatReportSerializer(TenantDBForSerializer):
    class Meta:
        model = StatReport
        fields = '__all__'


class StatOrgClientReportSerializer(TenantDBForSerializer):
    organization = OrganizationSerializer(read_only=True)
    client = ClientSerializer(read_only=True)
    channel = ChannelSerializer(read_only=True)
    class Meta:
        model = StatClientChannelReport
        fields = '__all__'