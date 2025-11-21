from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework.views import APIView
from app.core.permissions.whilelist import SafeListPermission
from app.job.models import RouteWorkerTrack
from app.job.sub_serializers.route_serializer import RouteWorkerTrackSerializer


class GCPSummaryView(APIView):
    permission_classes = [SafeListPermission]
    serializer_class = RouteWorkerTrackSerializer

    @swagger_auto_schema(tags=["Stats Reports"])
    def get(self, request, *args, **kwargs):
        data = RouteWorkerTrack.summary()
        return Response(data)
