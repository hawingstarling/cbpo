from app.database.sub_serializers.tenant_db_for_serializer import TenantDBForSerializer
from app.job.models import RouteWorkerTrack


class RouteWorkerTrackSerializer(TenantDBForSerializer):
    class Meta:
        model = RouteWorkerTrack
        fields = '__all__'
