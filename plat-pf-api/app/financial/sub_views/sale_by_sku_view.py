from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics
from app.financial.models import SaleBySKU
from app.financial.permissions.base import JwtTokenPermission
from app.financial.sub_serializers.sale_by_sku_serializer import SaleBySKUSerializer


class SaleBySKUListView(generics.ListAPIView):
    serializer_class = SaleBySKUSerializer
    permission_classes = [JwtTokenPermission]

    search = openapi.Parameter('search', in_=openapi.IN_QUERY,
                               description="""Search""",
                               type=openapi.TYPE_STRING)

    @swagger_auto_schema(manual_parameters=[search])
    @method_decorator(cache_page(6 * 3600))  # 6 hours
    @method_decorator(vary_on_headers("x-ps-client-id", ))
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @staticmethod
    def get_db_table_flatten_type(client_id, flatten_type):
        client_db_id = str(client_id).replace('-', '_')
        kwargs = {
            'dollar': 'flatten_sale_by_dollar_{client_db_id}',
            'unit': 'flatten_sale_by_unit_{client_db_id}',
        }
        return kwargs[flatten_type].format(client_db_id=client_db_id)

    def get_queryset(self):
        client_id = self.kwargs.get('client_id')
        flatten_type = self.kwargs.get('flatten_type')
        search = self.request.query_params.get('search')
        db_table = self.get_db_table_flatten_type(client_id, flatten_type)
        #
        SaleBySKU._meta.db_table = db_table
        queryset = SaleBySKU.objects.tenant_db_for(client_id).all()
        if search:
            queryset = queryset.filter(sku__icontains=search)
        queryset = queryset.distinct('sku').order_by('sku')
        return queryset
