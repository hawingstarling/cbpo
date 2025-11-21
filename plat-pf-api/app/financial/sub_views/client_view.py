import logging, copy
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema, no_body
from rest_framework import status, generics
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from app.core.context import AppContext
from app.core.exceptions import InvalidFormatException, ObjectNotFoundException
from app.core.services.workspace_management import WorkspaceManagement
from app.financial.exceptions import ClientPortalSyncException, InvalidDatasourceStatusException
from app.financial.jobs.schema_datasource import handler_generate_client_source
from app.financial.models import (
    SaleItem, ClientPortal, DataFlattenTrack, Variant, SaleStatus, ProfitStatus, FulfillmentChannel, Channel,
    ClientSettings)
from app.financial.permissions.base import JwtTokenPermission, ClientUserPermission
from app.financial.permissions.sale_items import (
    SaleItemSingleUpdatePermission, SaleItemSingleDeletePermission, SaleItemBulkUpdatePermission,
    SaleItemBulkDeletePermission)
from app.financial.services.activity import ActivityService
from app.core.services.audit_logs.base import AuditLogCoreManager
from app.financial.services.data_flatten import DataFlatten
from app.financial.sub_serializers.client_serializer import (
    ClientPortalSerializer, CreateSyncClientSerializer, ClientSaleItemSerializer, DataFlattenTrackSerializer,
    DataSourceConnectionSerializer, SaleItemAuditLogSerializer, ChannelSerializer)
from app.financial.sub_serializers.sale_item_dropdown_serializer import (
    SaleItemVariationSerializer, SaleItemStatusSerializer, SaleItemProfitStatusSerializer, FulfillmentChannelSerializer)
from app.financial.variable.activity_variable import (
    DELETE_SALE_ITEM_DATA_KEY, BULK_DELETE_SALE_ITEM_DATA_KEY, BULK_EDIT_SALE_ITEM_DATA_KEY, EDIT_SALE_ITEM_DATA_KEY)
from app.financial.variable.data_flatten_variable import DATA_FLATTEN_DASHBOARD_TYPE, DATA_FLATTEN_TYPE_LIST, \
    DATA_FLATTEN_TYPE_ANALYSIS_LIST
from app.financial.variable.variant_type_static_variable import VARIANT_TYPE
from app.financial.variable.sale_item import JOB_ACTION, SINGLE_EDIT_JOB, BULK_EDIT_JOB
from app.financial.variable.job_status import SUCCESS
from app.financial.services.utils.source_config import data_source_generator_config

logger = logging.getLogger(__name__)


class ClientSyncPortalView(APIView):
    serializer_class = CreateSyncClientSerializer
    permission_classes = (ClientUserPermission,)

    @swagger_auto_schema(operation_description='Sync client from PS to PF', request_body=no_body,
                         responses={status.HTTP_200_OK: ClientPortalSerializer})
    def post(self, request, *args, **kwargs):
        try:
            client_id = AppContext.instance().client_id
            user_id = AppContext.instance().user_id
            jwt_token = AppContext.instance().jwt_token
            # sync list client to portal
            client_portal = WorkspaceManagement(client_id=client_id, jwt_token=jwt_token) \
                .sync_client_ps_to_pf(user_id=user_id)
            serializer = ClientPortalSerializer(client_portal)
            return Response(status=status.HTTP_200_OK, data=serializer.data)
        except Exception as ex:
            logger.error('[CreateClientSyncPortalView] {}'.format(ex))
            raise ClientPortalSyncException(message=ex, verbose=True)

    def get_object(self):
        client_id = AppContext.instance().client_id
        return ClientPortal.objects.tenant_db_for(client_id).get(pk=client_id)

    @swagger_auto_schema(operation_description='Sync client from PS to PF', request_body=no_body,
                         responses={status.HTTP_200_OK: ClientPortalSerializer})
    def get(self, request, *args, **kwargs):
        try:
            client_portal = self.get_object()
            serializer = ClientPortalSerializer(client_portal)
            return Response(status=status.HTTP_200_OK, data=serializer.data)
        except Exception as ex:
            logger.error('[GetClientSyncPortalView] {}'.format(ex))
            raise ClientPortalSyncException(message=ex, verbose=True)


class SaleItemsBaseView(GenericAPIView):
    serializer_class = ClientSaleItemSerializer
    permission_classes = (ClientUserPermission,)
    queryset = SaleItem.objects.all()
    # info user
    client_id = None
    sale_item_ids = []

    def fetch_info_request(self):
        # client id
        self.client_id = AppContext().instance().client_id
        # sale item ids
        sale_item_id = self.kwargs.get('pk', None)
        if sale_item_id:
            sale_item_ids = [str(sale_item_id)]
            self.get_objects(sale_item_ids)
            self.sale_item_ids = sale_item_ids
        else:
            sale_item_ids = self.request.GET.getlist('sale_item_ids[]', [])
            if not sale_item_ids:
                raise InvalidFormatException(
                    message="Missing request param ?sale_item_ids[]=<sale_item_id_a>&sale_item_ids[]=<sale_item_id_b>")
            self.get_objects(sale_item_ids)
            self.sale_item_ids = sale_item_ids

    def get_objects(self, sale_item_ids):
        assert len(sale_item_ids) > 0, "Sale Item Ids is not empty"
        finds = SaleItem.objects.tenant_db_for(self.client_id).filter(id__in=sale_item_ids, client_id=self.client_id)
        if finds.count() != len(sale_item_ids):
            raise InvalidFormatException(message="Sale Item Id invalid", verbose=True)
        return True

    def valid_data_sale_item(self, data, context):
        serializer = self.serializer_class(data=data, context=context)
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data

    def get_serializer_context(self):
        return {
            'request': self.request,
            'format': self.format_kwarg,
            'sale_item_ids': self.sale_item_ids,
            'view': self,
            'kwargs': self.kwargs,
            'client_id': self.kwargs.get('client_id')
        }

    def activity_log(self):
        user_id = AppContext.instance().user_id
        active_service = ActivityService(client_id=self.client_id, user_id=user_id)
        if self.request.method in ['PUT', 'PATCH']:
            if len(self.sale_item_ids) == 1:
                active_service.create_activity_action_sale_data(EDIT_SALE_ITEM_DATA_KEY, None, self.sale_item_ids)
            else:
                active_service.create_activity_action_sale_data(BULK_EDIT_SALE_ITEM_DATA_KEY, None, self.sale_item_ids)
        if self.request.method == 'DELETE':
            if len(self.sale_item_ids) == 1:
                active_service.create_activity_action_sale_data(DELETE_SALE_ITEM_DATA_KEY, None, self.sale_item_ids)
            else:
                active_service.create_activity_action_sale_data(BULK_DELETE_SALE_ITEM_DATA_KEY, None,
                                                                self.sale_item_ids)


class ClientSaleItemsSingleUpdateDeleteView(SaleItemsBaseView):

    def get_permissions(self):
        if hasattr(self.request, 'method') and self.request.method.upper() in ['PUT']:
            self.permission_classes = [SaleItemSingleUpdatePermission]
        if hasattr(self.request, 'method') and self.request.method.upper() in ['DELETE']:
            self.permission_classes = [SaleItemSingleDeletePermission]
        return super().get_permissions()

    @swagger_auto_schema(operation_description='Single update sale items record',
                         request_body=ClientSaleItemSerializer, responses={status.HTTP_200_OK: None})
    def put(self, request, *args, **kwargs):
        try:
            self.fetch_info_request()
            client_setting, _ = ClientSettings.objects.tenant_db_for(self.client_id) \
                .get_or_create(client_id=self.client_id)
            context = self.get_serializer_context()
            context.update(
                {
                    'is_remove_cogs_refunded': getattr(client_setting, "is_remove_cogs_refunded", False)
                }
            )
            context['kwargs'].update({JOB_ACTION: SINGLE_EDIT_JOB})
            data = self.valid_data_sale_item(data=request.data, context=context)

            serializer_class = self.serializer_class(context=context)
            serializer_class.bulk_update(validated_data=data)
            self.activity_log()
            return Response(status=status.HTTP_200_OK, data=None)
        except Exception as ex:
            title = '[Single Update Client Sale Items][Single][{sale_item_id}]'.format(
                sale_item_id=str(kwargs.get('pk')))
            logger.error(title, exc_info=True)
            raise ex

    @swagger_auto_schema(operation_description='Single delete sale items record',
                         responses={status.HTTP_204_NO_CONTENT: None})
    def delete(self, request, *args, **kwargs):
        try:
            self.fetch_info_request()
            serializer_class = self.serializer_class(context=self.get_serializer_context())
            serializer_class.bulk_delete()
            self.activity_log()
            return Response(status=status.HTTP_204_NO_CONTENT, data=None)
        except Exception as ex:
            title = '[Single Delete Client Sale Items][Single][{sale_item_id}]'.format(
                sale_item_id=str(kwargs.get('pk')))
            logger.error(title, exc_info=True)
            raise ex


class ClientSaleItemsBulkUpdateView(SaleItemsBaseView):

    def get_permissions(self):
        self.permission_classes = [SaleItemBulkUpdatePermission]
        return super().get_permissions()

    @swagger_auto_schema(
        operation_description='Bulk update sale items record using request params ?sale_item_ids[]=<sale_item_id_a>&sale_item_ids[]=<sale_item_id_b>&...',
        request_body=ClientSaleItemSerializer, responses={status.HTTP_200_OK: None})
    def patch(self, request, *args, **kwargs):
        try:
            self.fetch_info_request()
            client_setting, _ = ClientSettings.objects.tenant_db_for(self.client_id) \
                .get_or_create(client_id=self.client_id)
            context = self.get_serializer_context()
            context.update(
                {
                    'is_remove_cogs_refunded': getattr(client_setting, "is_remove_cogs_refunded", False)
                }
            )
            context['kwargs'].update({JOB_ACTION: BULK_EDIT_JOB})
            data = self.valid_data_sale_item(data=request.data, context=context)
            serializer_class = self.serializer_class(context=context)
            serializer_class.bulk_update(validated_data=data)
            self.activity_log()
            return Response(status=status.HTTP_200_OK, data=None)
        except Exception as ex:
            title = '[Bulk Update Client Sale Items][Bulk][{sale_item_ids}]'.format(
                sale_item_ids=','.join(self.sale_item_ids))
            logger.error(title, exc_info=True)
            raise ex


class ClientSaleItemsBulkDeleteView(SaleItemsBaseView):

    def get_permissions(self):
        self.permission_classes = [SaleItemBulkDeletePermission]
        return super().get_permissions()

    @swagger_auto_schema(
        operation_description='Bulk delete sale items record using request params ?sale_item_ids[]=<sale_item_id_a>&sale_item_ids[]=<sale_item_id_b>&...',
        responses={status.HTTP_204_NO_CONTENT: None})
    def delete(self, request, *args, **kwargs):
        try:
            self.fetch_info_request()
            serializer_class = self.serializer_class(context=self.get_serializer_context())
            serializer_class.bulk_delete()
            self.activity_log()
            return Response(status=status.HTTP_204_NO_CONTENT, data=None)
        except Exception as ex:
            title = '[Bulk Delete Client Sale Items][Bulk][{sale_item_ids}]'.format(
                sale_item_ids=','.join(self.sale_item_ids))
            logger.error(title, exc_info=True)
            raise ex


class GenerateDataFlattenView(GenericAPIView):
    permission_classes = (JwtTokenPermission,)
    serializer_class = DataFlattenTrackSerializer

    @swagger_auto_schema(request_body=no_body,
                         operation_description="Generate or re-generating data view")
    def post(self, request, *args, **kwargs):
        try:
            logger.info('{}'.format(self.__class__.__name__))
            jwt_token = AppContext.instance().jwt_token
            client_id = str(self.kwargs.get('client_id'))
            _ = get_object_or_404(ClientPortal, id=client_id)
            #
            handler_generate_client_source(client_id=client_id, access_token=jwt_token, token_type='JWT')
            #
            data = {
                'status': SUCCESS
            }
            return Response(status=status.HTTP_200_OK, data=data)
        except Exception as err:
            logger.error('[{}] {}'.format(self.__class__.__name__, err))
            raise err


class RetrieveDataFlattenView(APIView):
    permission_classes = (JwtTokenPermission,)
    serializer_class = DataFlattenTrackSerializer
    queryset = DataFlattenTrack.objects.all()

    def get_queryset(self):
        query_set = DataFlattenTrack.objects.tenant_db_for(self.kwargs["client_id"]).all()
        return query_set

    def do_flattens_analysis(self):
        client_id = str(self.kwargs.get('client_id'))
        for type_flatten in DATA_FLATTEN_TYPE_ANALYSIS_LIST:
            data_flatten_track = (DataFlattenTrack.objects.tenant_db_for(client_id)
                                  .get(client_id=client_id, type=type_flatten))
            config = data_source_generator_config()[type_flatten]
            data_flatten = DataFlatten(client_id=client_id, type_flatten=type_flatten, **config,
                                       source=data_flatten_track.source)
            if not data_flatten.is_flatten_exists():
                data_flatten.do_flatten()

    def get(self, request, *args, **kwargs):
        #
        __status = SUCCESS
        #
        client_id = str(self.kwargs.get('client_id'))
        queryset = DataFlattenTrack.objects.tenant_db_for(client_id).filter(client_id=client_id,
                                                                            type__in=DATA_FLATTEN_TYPE_LIST,
                                                                            status=SUCCESS)

        if queryset.count() != len(DATA_FLATTEN_TYPE_LIST):
            for item in queryset:
                print(item.type)
            raise InvalidDatasourceStatusException(message="Data source flatten generate less than number ds config")
        #
        self.do_flattens_analysis()
        #
        data = {
            'status': __status
        }
        return Response(status=status.HTTP_200_OK, data=data)


class DataSourceConnectionSaleDataView(APIView):
    permission_classes = (JwtTokenPermission,)
    serializer = DataSourceConnectionSerializer

    ds_type = openapi.Parameter('ds_type', in_=openapi.IN_QUERY,
                                description="""Data source type""",
                                type=openapi.TYPE_STRING)

    dashboard_type = openapi.Parameter('dashboard_type', in_=openapi.IN_QUERY,
                                       description="""Dashboard type""",
                                       type=openapi.TYPE_STRING)

    def get_condition_filter(self):
        client_id = str(self.kwargs.get('client_id'))

        ds_type = self.request.query_params.get('ds_type', None)
        dashboard_type = self.request.query_params.get('dashboard_type', None)

        cond = Q(client_id=client_id)

        if ds_type:
            cond = cond & Q(type__iexact=ds_type)
            return cond

        if dashboard_type:
            ds_list_type = DATA_FLATTEN_DASHBOARD_TYPE.get(dashboard_type, None)

            ds_list_type = copy.deepcopy(ds_list_type)

            cond_type = Q(type__iexact=ds_list_type[0])

            del ds_list_type[0]

            for i in ds_list_type:
                cond_type = cond_type | Q(type__iexact=i)
            return cond & (cond_type)
        return cond

    def get_queryset(self):
        cond = self.get_condition_filter()
        return DataFlattenTrack.objects.tenant_db_for(self.kwargs['client_id']).filter(cond)

    @swagger_auto_schema(operation_description="GET Data source connection for sale items",
                         manual_parameters=[ds_type, dashboard_type],
                         responses={status.HTTP_200_OK: DataSourceConnectionSerializer})
    def get(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()

            # print(queryset.query)

            data = {}

            for item in queryset:
                data[item.type] = self.serializer(item).data

            return Response(status=status.HTTP_200_OK, data=data)
        except Exception as err:
            raise ObjectNotFoundException('DataSourceConnectionSaleData not found')


class SaleItemAuditLogListView(ListAPIView):
    permission_classes = (JwtTokenPermission,)
    serializer_class = SaleItemAuditLogSerializer

    keyword = openapi.Parameter('keyword', in_=openapi.IN_QUERY,
                                description="""Search by actor information (name, email, id, phone, ...), 
                                changes value, changes field name""",
                                type=openapi.TYPE_STRING)

    def get_queryset(self):
        keyword = self.request.query_params.get('keyword', None)
        sale_item_id = str(self.kwargs.get('sale_item_pk'))
        sale_item = SaleItem.objects.tenant_db_for(self.kwargs['client_id']).get(pk=sale_item_id)
        query_set = AuditLogCoreManager(client_id=self.kwargs['client_id']).get_logs_from_ids(
            [sale_item.id, sale_item.sale_id], keyword)
        return query_set

    @swagger_auto_schema(operation_description='Get list audit log of Sale Item', manual_parameters=[keyword])
    def get(self, request, *args, **kwargs):
        return super(SaleItemAuditLogListView, self).get(request, *args, **kwargs)


class ListVariationView(generics.ListAPIView):
    permission_classes = (JwtTokenPermission,)
    serializer_class = SaleItemVariationSerializer

    search = openapi.Parameter('search', in_=openapi.IN_QUERY,
                               description="""Search by value variation of type (Size, Style)""",
                               type=openapi.TYPE_STRING)

    def get_queryset(self):
        query = Variant.objects.tenant_db_for(self.kwargs['client_id']).all()
        variation_type = self.kwargs.get('type', 'size')
        search = self.request.query_params.get('search', None)
        variation_type_list = [item[0] for item in VARIANT_TYPE]
        if variation_type.title() not in variation_type_list:
            raise InvalidFormatException(message="Variation type {} not correct".format(variation_type), verbose=True)
        variation_type = variation_type.title()
        query = query.filter(type=variation_type)
        if search:
            query = query.filter(Q(name__icontains=search) | Q(value__icontains=search))
        return query.order_by('value')

    @swagger_auto_schema(operation_description='Get list variation type Sale Item', manual_parameters=[search])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class ListSaleStatusView(generics.ListAPIView):
    permission_classes = (JwtTokenPermission,)
    serializer_class = SaleItemStatusSerializer

    search = openapi.Parameter('search', in_=openapi.IN_QUERY,
                               description="""Search by value of sale status""",
                               type=openapi.TYPE_STRING)

    def get_queryset(self):
        search = self.request.query_params.get('search', None)
        query = SaleStatus.objects.tenant_db_for(self.kwargs['client_id']).all()
        if search:
            query = query.filter(Q(name__icontains=search) | Q(value__icontains=search))
        return query.order_by('order')

    @swagger_auto_schema(operation_description='Get list sale status', manual_parameters=[search])
    @method_decorator(cache_page(60 * 60))
    @method_decorator(vary_on_headers("x-ps-client-id", ))
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class ListProfitStatusView(generics.ListAPIView):
    permission_classes = (JwtTokenPermission,)
    serializer_class = SaleItemProfitStatusSerializer

    search = openapi.Parameter('search', in_=openapi.IN_QUERY,
                               description="""Search by value of profit status""",
                               type=openapi.TYPE_STRING)

    def get_queryset(self):
        search = self.request.query_params.get('search', None)
        query = ProfitStatus.objects.tenant_db_for(self.kwargs['client_id']).all()
        if search:
            query = query.filter(Q(name__icontains=search) | Q(value__icontains=search))
        return query.order_by('order')

    @swagger_auto_schema(operation_description='Get list profit status', manual_parameters=[search])
    @method_decorator(cache_page(60 * 60))
    @method_decorator(vary_on_headers("x-ps-client-id", ))
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class ListFulfillmentTypeView(generics.ListAPIView):
    permission_classes = (JwtTokenPermission,)
    serializer_class = FulfillmentChannelSerializer

    search = openapi.Parameter('search', in_=openapi.IN_QUERY,
                               description="""Search by name of fulfillment channel""",
                               type=openapi.TYPE_STRING)

    def get_queryset(self):
        search = self.request.query_params.get('search', None)
        query = FulfillmentChannel.objects.tenant_db_for(self.kwargs['client_id']).all()
        if search:
            query = query.filter(Q(name__icontains=search))
        return query.order_by('name')

    @swagger_auto_schema(operation_description='Get list fulfillment types', manual_parameters=[search])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class ListChannelView(generics.ListAPIView):
    serializer_class = ChannelSerializer
    permission_classes = (JwtTokenPermission,)
    queryset = Channel.objects.all().order_by('name')

    def get_queryset(self):
        query_set = Channel.objects.tenant_db_for(self.kwargs["client_id"]).filter(use_in_global_filter=True) \
            .order_by('name')
        return query_set
