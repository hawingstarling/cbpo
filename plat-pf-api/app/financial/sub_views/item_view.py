from django.db.models import Q
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from app.core.context import AppContext
from app.core.logger import logger
from app.financial.models import Item, ItemCog
from app.financial.permissions.base import JwtTokenPermission
from app.financial.permissions.item_permissions import (
    ViewItemJwtPermission, CreateItemJwtPermission, EditItemJwtPermission, DeleteItemJwtPermission,
    BulkEditItemJwtPermission, BulkDeleteItemJwtPermission)
from app.financial.services.activity import ActivityService
from app.financial.services.item.config import config_shipping_items_search
from app.financial.services.postgres_fulltext_search import (PostgresFulltextSearch, ISortConfigPostgresFulltextSearch)
from app.financial.sub_serializers.item_serializer import (
    ItemSerializer, ItemDetailSerializer, ItemImportSerializer, ItemCogSerializer, ItemBulkActionSerializer)
from app.financial.variable.activity_variable import (
    CREATE_ITEM_DATA_KEY, UPDATE_ITEM_DATA_KEY, DELETE_ITEM_DATA_KEY, BULK_UPDATE_ITEM_DATA_KEY,
    BULK_DELETE_ITEM_DATA_KEY)


class BaseItemView(generics.GenericAPIView):
    client_id = None

    def get_queryset(self):
        query_set = Item.objects.tenant_db_for(self.kwargs.get("client_id")).all()
        return query_set

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'kwargs': self.kwargs})
        return context

    def activity_log(self, type_action: str, item_ids: [str], client_id):
        user_id = AppContext.instance().user_id
        ActivityService(client_id=client_id, user_id=user_id).create_activity_action_item_data(type_action, item_ids)


class ListCreateItemView(BaseItemView, generics.ListCreateAPIView):
    serializer_class = ItemSerializer
    permission_classes = (JwtTokenPermission,)

    keyword = openapi.Parameter('keyword', in_=openapi.IN_QUERY,
                                description="""Search""",
                                type=openapi.TYPE_STRING)

    channel = openapi.Parameter('channel', in_=openapi.IN_QUERY,
                                description="""Channel filter""",
                                type=openapi.TYPE_STRING)

    brand = openapi.Parameter('brand', in_=openapi.IN_QUERY,
                              description="""Brand filter""",
                              type=openapi.TYPE_STRING)

    @swagger_auto_schema(
        operation_description='Search items in order by sku, asin, upc, ...',
        manual_parameters=[channel, brand, keyword])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ItemDetailSerializer
        return ItemSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            self.permission_classes = [ViewItemJwtPermission]
        else:
            self.permission_classes = [CreateItemJwtPermission]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save()
        try:
            item_ids = serializer.data['id']
        except AttributeError:
            item_ids = []
        self.activity_log(CREATE_ITEM_DATA_KEY, item_ids, self.kwargs.get('client_id'))

    def get_queryset(self):
        client_id = self.kwargs.get('client_id')
        channel_filter = self.request.query_params.get('channel')
        brand_filter = self.request.query_params.get('brand')
        base_filter = Q()
        base_filter.add(Q(client_id=client_id), Q.AND)

        if channel_filter is not None:
            base_filter.add(Q(channel__name=channel_filter), Q.AND)

        if brand_filter is not None:
            base_filter.add(Q(brand__name=brand_filter), Q.AND)

        search_keyword = self.request.query_params.get('keyword')

        if search_keyword:
            return PostgresFulltextSearch(
                model_objects_manager=Item.objects.tenant_db_for(client_id).filter(base_filter),
                sort_config=[ISortConfigPostgresFulltextSearch(field_name='created', direction='desc')],
                fields_config=config_shipping_items_search).search_rank_on_contain(search_keyword)
        return Item.objects.tenant_db_for(client_id).filter(base_filter).order_by('-created')


class RetrieveUpdateDeleteItemView(BaseItemView, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ItemImportSerializer
    permission_classes = (JwtTokenPermission,)
    queryset = Item.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ItemDetailSerializer
        return ItemSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            self.permission_classes = [ViewItemJwtPermission]
        elif self.request.method in ['PUT', 'PATCH']:
            self.permission_classes = [EditItemJwtPermission]
        else:
            self.permission_classes = [DeleteItemJwtPermission]
        return super().get_permissions()

    def get_object(self):
        client_id = self.kwargs.get('client_id')
        item_id = self.kwargs.get('pk')
        try:
            return Item.objects.tenant_db_for(client_id).get(client_id=client_id, pk=item_id)
        except Item.DoesNotExist:
            raise ValidationError('{} does not exist'.format(item_id))

    def update(self, request, *args, **kwargs):
        res_update = super().update(request, *args, **kwargs)
        self.activity_log(UPDATE_ITEM_DATA_KEY, [str(self.kwargs.get('pk'))], self.kwargs.get('client_id'))
        return res_update

    def destroy(self, request, *args, **kwargs):
        res_destroy = super().destroy(request, *args, **kwargs)
        self.activity_log(DELETE_ITEM_DATA_KEY, [str(self.kwargs.get('pk'))], self.kwargs.get('client_id'))
        return res_destroy


class ListCreateItemCogView(BaseItemView, generics.ListCreateAPIView):
    permission_classes = (JwtTokenPermission,)
    serializer_class = ItemCogSerializer

    def get_serializer_context(self):
        ctx = super(ListCreateItemCogView, self).get_serializer_context()
        ctx.update({'item_id': self.kwargs.get('item_id')})
        return ctx

    def get_permissions(self):
        if self.request.method == 'GET':
            self.permission_classes = [ViewItemJwtPermission]
        else:
            self.permission_classes = [CreateItemJwtPermission]
        return super().get_permissions()

    def get_queryset(self):
        try:
            client_id = self.kwargs.get('client_id')
            item_id = self.kwargs.get('item_id')
            item = Item.objects.tenant_db_for(client_id).get(client_id=client_id, pk=item_id)
            return ItemCog.objects.tenant_db_for(client_id).filter(item=item).order_by('id')
        except Item.DoesNotExist:
            raise ValidationError('item does not exist')


class RetrieveUpdateDeleteItemCogView(BaseItemView, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ItemCogSerializer
    queryset = ItemCog.objects.all()

    def get_object(self):
        try:
            client_id = self.kwargs.get('client_id')
            item_id = self.kwargs.get('item_id')
            pk = self.kwargs.get('pk')
            return ItemCog.objects.tenant_db_for(client_id).get(item_id=item_id, item__client_id=client_id, pk=pk)
        except Item.DoesNotExist:
            raise ValidationError('item cog does not exist')

    def get_permissions(self):
        if self.request.method == 'GET':
            self.permission_classes = [ViewItemJwtPermission]
        else:
            self.permission_classes = [EditItemJwtPermission]
        return super().get_permissions()


class BulkActionItemView(BaseItemView):
    serializer_class = ItemBulkActionSerializer
    item_ids = openapi.Parameter('item_ids', in_=openapi.IN_QUERY,
                                 description="""Item ids for bulk action""",
                                 type=openapi.TYPE_ARRAY,
                                 items=openapi.Items(type=openapi.TYPE_STRING),
                                 required=True)

    def get_permissions(self):
        if self.request.method == 'PUT':
            self.permission_classes = [BulkEditItemJwtPermission]
        else:
            self.permission_classes = [BulkDeleteItemJwtPermission]
        return super().get_permissions()

    @swagger_auto_schema(
        operation_description='''Bulk update item records using request''',
        request_body=ItemBulkActionSerializer, responses={status.HTTP_200_OK: None}, manual_parameters=[item_ids])
    def put(self, request, *args, **kwargs):
        try:
            context = self.get_serializer_context()
            item_ids = self.get_item_ids_param_query()
            serializer = ItemBulkActionSerializer(data=request.data, context=context)
            serializer.is_valid(raise_exception=True)
            serializer.validate_object_ids(item_ids)
            serializer.bulk_update(item_ids)
            self.activity_log(BULK_UPDATE_ITEM_DATA_KEY, item_ids, self.kwargs.get("client_id"))
            return Response(status=status.HTTP_200_OK, data=None)
        except Exception as ex:
            logger.error('[BulkActionItemView][PUT] {}'.format(ex))
            raise ex

    @swagger_auto_schema(
        operation_description='''Bulk delete item records using request''',
        responses={status.HTTP_204_NO_CONTENT: None}, manual_parameters=[item_ids])
    def delete(self, request, *args, **kwargs):
        try:
            context = self.get_serializer_context()
            item_ids = self.get_item_ids_param_query()
            serializer = ItemBulkActionSerializer(data=None, context=context)
            serializer.validate_object_ids(item_ids)
            serializer.bulk_delete(item_ids)
            self.activity_log(BULK_DELETE_ITEM_DATA_KEY, item_ids, self.kwargs.get("client_id"))
            return Response(status=status.HTTP_204_NO_CONTENT, data=None)
        except Exception as ex:
            logger.error('[BulkActionItemView][DELETE] {}'.format(ex))
            raise ex

    def get_item_ids_param_query(self):
        item_ids = self.request.query_params.get('item_ids')
        item_ids = item_ids.split(',')
        return item_ids
