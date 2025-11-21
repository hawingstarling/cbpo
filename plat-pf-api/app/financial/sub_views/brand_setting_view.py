import logging
import uuid
from abc import ABC
from django.db import transaction
from django.db.models import Q
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView

from app.core.exceptions import InvalidFormatException, InvalidParameterException
from app.database.helper import get_connection_workspace
from app.financial.exceptions import InvalidBrandSettingException
from app.financial.jobs.brand_setting import BRAND_SETTING_MODULE_UPDATE_SALES, \
    brand_setting_update_sale_create_bulk_progress
from app.financial.models import BrandSetting, ClientPortal
from app.financial.permissions.brand_setting_permissions import (
    ViewBrandSettingJwtPermission, CreateBrandSettingJwtPermission, EditBrandSettingJwtPermission,
    DeleteBrandSettingJwtPermission, UpdateSaleBrandSettingJwtPermission, ExportBrandSettingJwtPermission)
from app.financial.services.brand_settings.ship_cost_calculation_for_sale_item import BrandSettingUpdateSaleItem
from app.financial.services.exports.schema import ExportSchema
from app.financial.services.postgres_fulltext_search import PostgresFulltextSearch, ISortConfigPostgresFulltextSearch, \
    IFieldConfigPostgresFulltextSearch
from app.core.sub_serializers.base_serializer import ExportResponseSerializer
from app.financial.sub_serializers.brand_setting_serializers import (
    BrandSettingSerializer, UpdateSaleSerializer, CountUpdateSaleSerializerRes)
from app.job.utils.helper import register_list
from app.job.utils.variable import BULK_CATEGORY

logger = logging.getLogger(__name__)


class BrandSettingBaseView(ABC):
    def get_client(self):
        client_id = self.kwargs.get('client_id')  # noqa
        try:
            return ClientPortal.objects.tenant_db_for(client_id).get(id=client_id)
        except ClientPortal.DoesNotExist:
            raise InvalidParameterException(f'{client_id} does not exist.')


class ListCreateBrandSettingView(generics.ListCreateAPIView, BrandSettingBaseView):
    serializer_class = BrandSettingSerializer

    channel = openapi.Parameter('channel', in_=openapi.IN_QUERY,
                                description="""Channel filter""",
                                type=openapi.TYPE_STRING)
    keyword = openapi.Parameter('keyword', in_=openapi.IN_QUERY,
                                description="""Search""",
                                type=openapi.TYPE_STRING)

    __config_search = [
        IFieldConfigPostgresFulltextSearch(
            field_name='channel__name', weight='A'),
        IFieldConfigPostgresFulltextSearch(
            field_name='brand__name', weight='B'),
        IFieldConfigPostgresFulltextSearch(
            field_name='mfn_formula', weight='C'),
    ]
    __sort_config = [ISortConfigPostgresFulltextSearch(
        field_name='brand__name', direction='asc')]

    def get_permissions(self):
        if self.request.method == 'POST':
            self.permission_classes = [CreateBrandSettingJwtPermission]
        else:
            self.permission_classes = [ViewBrandSettingJwtPermission]
        return super().get_permissions()

    def get_queryset(self):
        client = self.get_client()
        client_id = str(client.pk)
        channel_filter = self.request.query_params.get('channel')
        base_filter = Q()
        base_filter.add(Q(client_id=client.id), Q.AND)
        if channel_filter is not None:
            base_filter.add(Q(channel__name=channel_filter), Q.AND)
        search_keyword = self.request.query_params.get('keyword')

        if search_keyword:
            res_query_set = PostgresFulltextSearch(
                model_objects_manager=BrandSetting.objects.tenant_db_for(
                    client_id).filter(base_filter),
                fields_config=self.__config_search,
                sort_config=self.__sort_config).search_rank_on_contain(search_keyword)
            queryset_brand_null = BrandSetting.objects.tenant_db_for(client_id).filter(base_filter).filter(
                brand__isnull=True)
            res_query_set = res_query_set | queryset_brand_null
        else:
            res_query_set = BrandSetting.objects.tenant_db_for(
                client_id).filter(base_filter).order_by('brand__name')
        return res_query_set

    @swagger_auto_schema(responses={status.HTTP_201_CREATED: BrandSettingSerializer})
    def post(self, request, *args, **kwargs):
        return super(ListCreateBrandSettingView, self).post(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description='Search brand setting in order by channel name, brand name, formula',
        manual_parameters=[keyword, channel])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class RetrieveUpdateDeleteBrandSettingView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BrandSettingSerializer

    def get_permissions(self):
        method = self.request.method
        if method in ['PUT', 'PATCH']:
            self.permission_classes = [EditBrandSettingJwtPermission]
        elif method == 'DELETE':
            self.permission_classes = [DeleteBrandSettingJwtPermission]
        else:
            self.permission_classes = [ViewBrandSettingJwtPermission]
        return super().get_permissions()

    def get_object(self):
        client_id = self.kwargs["client_id"]
        brand_setting_id = self.kwargs.get("brand_setting_id")
        try:
            return BrandSetting.objects.tenant_db_for(client_id).get(id=brand_setting_id)
        except BrandSetting.DoesNotExist:
            raise InvalidParameterException(
                f'{brand_setting_id} does not exist.')

    def destroy(self, request, *args, **kwargs):
        brand_setting = self.get_object()
        client_id = self.kwargs["client_id"]

        # Optional: store the associated brand before deleting the setting
        brand = brand_setting.brand

        # Delete the BrandSetting
        brand_setting.delete()

        # Optional: delete the brand if no other settings exist
        if not BrandSetting.objects.tenant_db_for(client_id).filter(brand=brand).exists():
            brand.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class UpdateSaleView(generics.GenericAPIView, BrandSettingBaseView):
    permission_classes = (UpdateSaleBrandSettingJwtPermission,)
    serializer_class = UpdateSaleSerializer

    def get_object(self):
        client_id = self.kwargs["client_id"]
        brand_setting_id = self.kwargs.get("brand_setting_id")
        try:
            return BrandSetting.objects.tenant_db_for(client_id).get(id=brand_setting_id)
        except BrandSetting.DoesNotExist:
            raise InvalidParameterException(
                f'{brand_setting_id} does not exist.')

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer_class()(data=request.data)
        serializer.is_valid(raise_exception=True)

        client = self.get_client()
        client_db = get_connection_workspace(self.kwargs["client_id"])
        brand_setting = self.get_object()

        if brand_setting.brand is None:
            raise InvalidBrandSettingException(
                "brand null has been not implemented!")

        from_date = serializer.validated_data.get('sale_date_from')
        to_date = serializer.validated_data.get('sale_date_to')
        recalculate = serializer.validated_data.get('recalculate')

        query_set_count = BrandSettingUpdateSaleItem(str(client.id), brand_setting, recalculate, from_date, to_date,
                                                     None).sale_item_query_set_count()

        if query_set_count == 0:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"message": "no sale items affected"})

        jwt = self.request.auth.decode('utf-8')
        bulk_progress_id = brand_setting_update_sale_create_bulk_progress(str(client.id), brand_setting,
                                                                          recalculate, from_date, to_date,
                                                                          jwt)
        # make sure bulk progress is created before this job is executed in the worker
        data_info = {
            "module": BRAND_SETTING_MODULE_UPDATE_SALES,
            "jwt_token": jwt,
            "import_temp_id": bulk_progress_id,
            "client_id": str(client.id),
            "brand_setting_id": str(brand_setting.id),
            "is_recalculate": recalculate,
            "from_date": from_date,
            "to_date": to_date
        }
        data = [
            dict(
                task_id=bulk_progress_id,
                client_id=str(client.id),
                name=f"bulk_chunk_{bulk_progress_id}",
                job_name="app.financial.jobs.bulk_process.bulk_handler",
                module="app.financial.jobs.bulk_process",
                method="bulk_handler",
                meta=data_info
            )
        ]
        transaction.on_commit(lambda: register_list(
            BULK_CATEGORY, data), using=client_db)
        return Response(status=status.HTTP_200_OK, data={"message": "processing"})


class CountUpdateSaleView(generics.GenericAPIView, BrandSettingBaseView):
    permission_classes = (UpdateSaleBrandSettingJwtPermission,)
    serializer_class = UpdateSaleSerializer

    def get_object(self):
        client_id = self.kwargs["client_id"]
        brand_setting_id = self.kwargs.get("brand_setting_id")
        try:
            return BrandSetting.objects.tenant_db_for(client_id).get(id=brand_setting_id)
        except BrandSetting.DoesNotExist:
            raise InvalidParameterException(
                f'{brand_setting_id} does not exist.')

    @swagger_auto_schema(responses={status.HTTP_200_OK: CountUpdateSaleSerializerRes})
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer_class()(data=request.data)
        serializer.is_valid(raise_exception=True)

        client = self.get_client()
        brand_setting = self.get_object()

        if brand_setting.brand is None:
            raise InvalidBrandSettingException(
                "brand null has been not implemented!")

        from_date = serializer.validated_data.get('sale_date_from')
        to_date = serializer.validated_data.get('sale_date_to')
        recalculate = serializer.validated_data.get('recalculate')

        count_sale_items = BrandSettingUpdateSaleItem(str(client.id),
                                                      brand_setting,
                                                      recalculate,
                                                      from_date,
                                                      to_date,
                                                      None,
                                                      5000).sale_item_query_set_count()
        return Response(status=status.HTTP_200_OK, data={'count-sales': count_sale_items})


class ExportBrandSettingView(APIView, BrandSettingBaseView):
    permission_classes = (ExportBrandSettingJwtPermission,)

    channel = openapi.Parameter('channel', in_=openapi.IN_QUERY,
                                description="""Channel filter""",
                                type=openapi.TYPE_STRING)
    items_ids = openapi.Parameter('items_ids', in_=openapi.IN_QUERY,
                                  description="""Items filter""",
                                  items=openapi.Items(
                                      type=openapi.TYPE_STRING),
                                  type=openapi.TYPE_ARRAY)
    keyword = openapi.Parameter('keyword', in_=openapi.IN_QUERY,
                                description="""Search""",
                                type=openapi.TYPE_STRING)

    __config_search = [
        IFieldConfigPostgresFulltextSearch(
            field_name='channel__name', weight='A'),
        IFieldConfigPostgresFulltextSearch(
            field_name='brand__name', weight='B'),
        IFieldConfigPostgresFulltextSearch(
            field_name='mfn_formula', weight='C'),
    ]
    __sort_config = [ISortConfigPostgresFulltextSearch(
        field_name='brand__name', direction='asc')]

    def get_item_ids_param_query(self):
        rs = set()
        try:
            vals = self.request.query_params.get('items_ids')
            for val in vals.split(','):
                try:
                    rs.add(uuid.UUID(val))
                except Exception as ex:
                    logger.debug(
                        f"[{self.__class__.__name__}][get_item_ids_param_query] {ex}")
        except Exception as ex:
            logger.debug(
                f"[{self.__class__.__name__}][get_item_ids_param_query] {ex}")
        return list(rs)

    def export_query_set(self):
        client = self.get_client()
        client_id = str(client.pk)
        channel_filter = self.request.query_params.get('channel')
        item_ids = self.get_item_ids_param_query()
        base_filter = Q()
        base_filter.add(Q(client_id=client.id), Q.AND)
        try:
            if channel_filter is not None and isinstance(channel_filter, str) and len(channel_filter.strip()) > 0:
                base_filter.add(Q(channel__name=channel_filter), Q.AND)
        except Exception as ex:
            logger.debug(f"[{self.__class__.__name__}][export_query_set] {ex}")
        search_keyword = self.request.query_params.get('keyword')
        if item_ids:
            base_filter.add(Q(pk__in=item_ids), Q.AND)

        if search_keyword:
            res_query_set = PostgresFulltextSearch(
                model_objects_manager=BrandSetting.objects.tenant_db_for(
                    client_id).filter(base_filter),
                fields_config=self.__config_search,
                sort_config=self.__sort_config).search_rank_on_contain(search_keyword)
        else:
            res_query_set = BrandSetting.objects.tenant_db_for(
                client_id).filter(base_filter).order_by('brand__name')
        return res_query_set

    @swagger_auto_schema(
        operation_description='Search brand setting in order by channel name, brand name, formula',
        manual_parameters=[keyword, channel, items_ids], responses={status.HTTP_200_OK: ExportResponseSerializer})
    def get(self, request, *args, **kwargs):
        query_set = self.export_query_set()

        if query_set.count() == 0:
            raise InvalidFormatException(
                "Export records is empty - no data to process")

        columns = {
            'channel__label': 'Channel',
            'brand__name': 'Brand',
            'segment': 'Segment',
            'est_first_item_shipcost': 'Estimation first item ship cost',
            'est_add_item_shipcost': 'Estimation additional item ship cost',
            'po_dropship_method': 'PO Dropship Method',
            'po_dropship_cost': 'PO Dropship',
            'est_unit_inbound_freight_cost': 'Estimation Unit Inbound Freight Cost',
            'est_unit_outbound_freight_cost': 'Estimation Unit Outbound Freight Cost',
            'est_fba_fees': 'Estimation FBA Fees',
            'mfn_formula': 'MFN formula',
            'add_user_provided_method': 'Add. User-Provided Method',
            'add_user_provided_cost': 'Add. User-Provided Cost',
            'auto_update_sales': 'Auto update sales'
        }

        export_schema = ExportSchema(client_id=self.kwargs['client_id'], columns=columns, queryset=query_set,
                                     category='brand_settings')
        file_url = export_schema.processing()
        return Response(status=HTTP_200_OK, data={'file_url': file_url})
