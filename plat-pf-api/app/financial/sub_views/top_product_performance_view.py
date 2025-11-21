from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView

from app.core.variable.marketplace import CHANNEL_DEFAULT
from app.financial.models import TopProductChannelPerformance
from app.financial.sub_serializers.top_product_performance_serializer import TopProductChannelPerformanceSerializer


class TopProductChannelPerformanceView(APIView):
    serializer_class = TopProductChannelPerformanceSerializer
    channel_name = openapi.Parameter('channel_name', in_=openapi.IN_QUERY,
                                     description="""Channel name filter""",
                                     type=openapi.TYPE_STRING)

    def get_queryset(self):
        client_id = self.kwargs["client_id"]
        channel_name = self.request.query_params.get("channel_name", CHANNEL_DEFAULT)
        #
        query_set = TopProductChannelPerformance.objects.tenant_db_for(client_id) \
            .filter(client_id=client_id, channel__name=channel_name).order_by('-units_sold')
        return query_set

    @swagger_auto_schema(operation_description='Search channel name of Top product performance',
                         manual_parameters=[channel_name],
                         responses={status.HTTP_200_OK: TopProductChannelPerformanceSerializer})
    @method_decorator(cache_page(6 * 3600))  # 6 hours
    @method_decorator(vary_on_headers("x-ps-client-id", ))
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        data = queryset.values('sku')
        return Response(status=HTTP_200_OK, data=data)
