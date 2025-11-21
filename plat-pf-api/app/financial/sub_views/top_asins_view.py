import logging

from django.db.models import Q
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics
from app.financial.models import TopClientASINs
from app.financial.permissions.base import JwtTokenPermission
from app.financial.services.postgres_fulltext_search import ISortConfigPostgresFulltextSearch
from app.financial.sub_serializers.top_asins_serializer import TopASINsSerializer

logger = logging.getLogger(__name__)


class ListCreateTopASINsView(generics.ListAPIView):
    serializer_class = TopASINsSerializer
    permission_classes = [JwtTokenPermission]

    search = openapi.Parameter('search', in_=openapi.IN_QUERY,
                               description="""Search""",
                               type=openapi.TYPE_STRING)

    channel = openapi.Parameter('channel', in_=openapi.IN_QUERY,
                                description="""Channel filter""",
                                type=openapi.TYPE_STRING)

    sort_field = openapi.Parameter('sort_field', in_=openapi.IN_QUERY,
                                   description="""sort_field""",
                                   type=openapi.TYPE_STRING)
    sort_direction = openapi.Parameter('sort_direction', in_=openapi.IN_QUERY,
                                       description="""desc or asc""",
                                       type=openapi.TYPE_STRING)

    def get_queryset(self):
        client_id = self.kwargs.get('client_id')
        channel = self.request.query_params.get('channel')
        search = self.request.query_params.get('search')
        cond = Q(client_id=client_id)

        if channel:
            cond &= Q(channel__name=channel)

        if search:
            cond &= (Q(parent_asin__icontains=search)
                     | Q(child_asin__icontains=search)
                     | Q(segment__icontains=search))

        # Sorting
        sort_field = self.request.query_params.get('sort_field')
        sort_direction = self.request.query_params.get('sort_direction', 'asc')
        if sort_field:
            sort = [ISortConfigPostgresFulltextSearch(field_name=sort_field, direction=sort_direction)]
        else:
            sort = [ISortConfigPostgresFulltextSearch(field_name='created', direction=sort_direction)]
        order_by = [item.output_str_sorting for item in sort]
        queryset = TopClientASINs.objects.tenant_db_for(client_id) \
            .filter(cond).order_by(*order_by)

        return queryset

    @swagger_auto_schema(operation_description='Get list widgets of dashboard',
                         manual_parameters=[search, channel, sort_field, sort_direction])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class RetrieveUpdateDeleteTopASINsView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TopASINsSerializer
    permission_classes = [JwtTokenPermission]

    def get_queryset(self):
        query_set = TopClientASINs.objects.tenant_db_for(self.kwargs["client_id"]).all()
        return query_set

    def get_permissions(self):
        if hasattr(self.request, 'method') and self.request.method.upper() in ["DELETE"]:
            # @TODO: Handler permission & write activity for action update/delete/created
            self.permission_classes = [JwtTokenPermission]
        return super().get_permissions()

    def put(self, request, *args, **kwargs):
        request.data['client'] = kwargs['client_id']
        return super().put(request, *args, **kwargs)

# class BulkActionTopASINsView(BaseItemView):
#     serializer_class = TopASINsBulkActionSerializer
#     item_ids = openapi.Parameter('item_ids', in_=openapi.IN_QUERY,
#                                  description="""Item ids for bulk action""",
#                                  type=openapi.TYPE_ARRAY,
#                                  items=openapi.Items(type=openapi.TYPE_STRING),
#                                  required=True)
#
#     def get_permissions(self):
#         if self.request.method == 'PUT':
#             self.permission_classes = [JwtTokenPermission]
#             # @TODO:  handler permission PS for bulk update/delete
#             # self.permission_classes = [BulkEditItemJwtPermission]
#         else:
#             self.permission_classes = [JwtTokenPermission]
#             # self.permission_classes = [BulkDeleteItemJwtPermission]
#         return super().get_permissions()
#
#     @swagger_auto_schema(
#         operation_description='''Bulk update item records using request''',
#         request_body=TopASINsBulkActionSerializer, responses={status.HTTP_200_OK: None}, manual_parameters=[item_ids])
#     def put(self, request, *args, **kwargs):
#         try:
#             context = self.get_serializer_context()
#             item_ids = self.get_item_ids_param_query()
#             serializer = TopASINsBulkActionSerializer(data=request.data, context=context)
#             serializer.is_valid(raise_exception=True)
#             serializer.validate_object_ids(item_ids)
#             serializer.bulk_update(item_ids)
#             # @TODO: handler log activity later
#             # self.activity_log(BULK_UPDATE_ITEM_DATA_KEY, item_ids, self.kwargs.get("client_id"))
#             return Response(status=status.HTTP_200_OK, data=None)
#         except Exception as ex:
#             logger.error('[BulkActionItemView][PUT] {}'.format(ex))
#             raise ex
#
#     @swagger_auto_schema(
#         operation_description='''Bulk delete item records using request''',
#         responses={status.HTTP_204_NO_CONTENT: None}, manual_parameters=[item_ids])
#     def delete(self, request, *args, **kwargs):
#         try:
#             context = self.get_serializer_context()
#             item_ids = self.get_item_ids_param_query()
#             serializer = TopASINsBulkActionSerializer(data=None, context=context)
#             serializer.validate_object_ids(item_ids)
#             serializer.bulk_delete(item_ids)
#             # @TODO: handler log activity later
#             # self.activity_log(BULK_DELETE_ITEM_DATA_KEY, item_ids, self.kwargs.get("client_id"))
#             return Response(status=status.HTTP_204_NO_CONTENT, data=None)
#         except Exception as ex:
#             logger.error('[BulkActionItemView][DELETE] {}'.format(ex))
#             raise ex
#
#     def get_item_ids_param_query(self):
#         item_ids = self.request.query_params.get('item_ids')
#         item_ids = item_ids.split(',')
#         return item_ids
