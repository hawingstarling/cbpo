import math
from ..models import RawDataTemporary
from ..services.utils.response import ResponseDataService
from ..sub_serializers.lib_import_serializer import ItemsDataImportSerializer
from ..sub_serializers.common_serializer import ItemsListSerializer
from ..sub_views.base import GenericImportView
from drf_yasg import openapi
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import ListAPIView


class ItemImportView(ListAPIView, GenericImportView):
    serializer_class = ItemsDataImportSerializer
    queryset = RawDataTemporary.objects.all()

    type = openapi.Parameter('type', in_=openapi.IN_QUERY,
                             description="""Search type valid , invalid ...""",
                             type=openapi.TYPE_STRING)
    key = openapi.Parameter('key', in_=openapi.IN_QUERY,
                            description="""Search key value""",
                            type=openapi.TYPE_STRING)
    search = openapi.Parameter('s', in_=openapi.IN_QUERY,
                               description="""Search value""",
                               type=openapi.TYPE_STRING)

    page = openapi.Parameter('page', in_=openapi.IN_QUERY,
                             description="""Page""",
                             type=openapi.TYPE_INTEGER)

    limit = openapi.Parameter('limit', in_=openapi.IN_QUERY,
                              description="""Limit""",
                              type=openapi.TYPE_INTEGER)

    response = openapi.Response('response', ItemsListSerializer)

    def get_queryset(self):
        #
        filters = dict(
            type=self.request.query_params.get('type', None),
            key=self.request.query_params.get('key', self.request.query_params.get('s', None))
        )
        response = ResponseDataService(lib_import_id=self.kwargs['import_id'])
        return response.queryset_filter_raws_data_temporary(filters, 'index')

    @swagger_auto_schema(operation_description='Get import detail', manual_parameters=[type, key, search, page, limit],
                         responses={status.HTTP_200_OK: response})
    def get(self, request, *args, **kwargs):
        rs = super().get(request, *args, **kwargs)
        #
        page_count = math.ceil(self.get_queryset().count() / int(self.request.query_params.get('limit', 20)))
        #
        rs_data = rs.data
        data = dict(
            total=rs_data['count'],
            page_current=self.request.query_params.get('page', 1),
            page_count=page_count,
            page_size=self.request.query_params.get('limit', 20),
            items=rs_data['results']
        )
        rs.data = data
        return rs
