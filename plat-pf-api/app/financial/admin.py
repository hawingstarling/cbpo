import hashlib
import itertools
import json

from celery import current_app
from celery.states import STARTED, RECEIVED
from django.conf import settings
from django.core.cache import cache
from django.db import DEFAULT_DB_ALIAS
from django.utils import timezone
import logging
from auditlog.admin import LogEntryAdmin
from auditlog.models import LogEntry
from django.contrib import admin, messages
from django.contrib.admin import DateFieldListFilter, SimpleListFilter
from django.utils.translation import gettext_lazy as _
from django_better_admin_arrayfield.admin.mixins import DynamicArrayMixin
from rangefilter.filter import DateTimeRangeFilter
from app.core.pagination import LargeTablePagination
# from app.core.admin.client_active_simple_filter import ClientActiveFilter
from .jobs.register import register_mws_keys_setting, register_ac_clients_settings, register_cart_rover_keys_setting
from .jobs.settings import handler_init_client_dashboard_widget
from .jobs.top_product_performance import handler_pick_job_calculation_top_product_performance_clients
from .models import (
    Organization, ClientPortal, CustomObject, CustomReport, Sale, SaleStatus, SaleItem, ProfitStatus, Brand, Variant,
    SaleChargeAndCost,
    CustomColumn,
    CustomFilter, CustomView, ShareCustom, Activity, Channel, UserPermission, FulfillmentChannel, DataFlattenTrack,
    Item, ItemCog, SaleItemTransaction, DataStatus, BrandSetting, BrandMissing, ClientSettings, FinancialSettings,
    AutoFeedBrand, DataFeedTrack, FedExShipment, AdSpendInformation, StatePopulation, SKUVaultPrimeTrack,
    AppEagleProfile, InformedMarketplace, User, UserObjectFavorite, Alert, AlertItem, AlertDigest, AlertDelivery,
    ShippingInvoice, TopProductChannelPerformance, DashboardConfig, WidgetConfig, ClientDashboardWidget,
    ClientCartRoverSetting, DivisionManage, DivisionClientUserWidget, TopClientASINs)
from .services.alert.delivery import AlertDeliveryChannel
from .services.fedex_shipment.config import FEDEX_SHIPMENT_PENDING
from .variable.data_flatten_variable import FLATTEN_ES_SOURCE, FLATTEN_PG_SOURCE
from .variable.job_status import POSTED_FILTER_MODE
from app.core.variable.pf_trust_ac import OPEN_STATUS, TIME_CONTROL_LOG_TYPE, SALE_EVENT_TYPE, FINANCIAL_EVENT_TYPE, \
    INFORMED_TYPE, READY_STATUS, PF_TIME_CONTROL_PRIORITY_TYPE, DONE_STATUS
from ..core.admins.tenant_db_admin import TenantDBForModelAdmin
from ..core.helper import get_connections_client_channels
from ..core.services.ds_service import DSManager
from ..core.services.workspace_management import WorkspaceManagement
from ..core.utils import hashlib_content
from ..core.variable.marketplace import SELLER_PARTNER_CONNECTION, INFORMED_MARKETPLACE_CONNECTION
from ..database.helper import get_connection_workspace
from ..job.utils.helper import register_list, ignore_category_job
from ..job.utils.variable import SYNC_ANALYSIS_CATEGORY, SYNC_DATA_SOURCE_CATEGORY, MODE_RUN_IMMEDIATELY, \
    TIME_CONTROL_CATEGORY, STATS_REPORT_CATEGORY, LIST_JOB_CATEGORY
from ..selling_partner.jobs.register import register_spapi_keys_setting
from ..selling_partner.jobs.report_brand_summary import create_jobs_sp_report_brands_summary_clients
from ..third_party_logistic.jobs.sync_account import sync_accounts_3pl_central_keys_setting

logger = logging.getLogger(__name__)


@admin.register(Organization)
class OrganizationAdmin(TenantDBForModelAdmin):
    list_display = ["id", "name", "logo", "created", "modified"]
    search_fields = ["name"]


@admin.register(ClientPortal)
class ClientPortalAdmin(TenantDBForModelAdmin):
    list_display = ["id", "name", "organization",
                    "account_manager", "active", "is_oe", "created", "modified"]
    list_filter = ["active", "is_oe"]
    search_fields = ["name"]
    actions = ["generate_ds_source", "generate_db_table_template", "generate_top_product_performance",
               "generate_stats_report", "clear_view_decorators_cached", "sync_status_of_workspace_from_portal",
               "purge_celery_worker", "generate_brands_summary_pre_monthly_report"]

    def generate_stats_report(self, request, queryset):
        errors = []
        data = []

        for obj in queryset:
            try:
                # healthy check
                data.append(dict(
                    client_id=obj.pk,
                    name="health_check_client_task",
                    job_name="app.stat_report.jobs.healthy.health_check_client_task",
                    module="app.stat_report.jobs.healthy",
                    method="health_check_client_task",
                    meta=dict(client_id=str(obj.pk))
                ))
                # stats events
                data.append(dict(
                    client_id=obj.pk,
                    name="stats_report_client_task",
                    job_name="app.stat_report.jobs.stats.stats_report_client_task",
                    module="app.stat_report.jobs.stats",
                    method="stats_report_client_task",
                    meta=dict(client_id=str(obj.pk))
                ))

            except Exception as ex:
                errors.append(f"[{obj.id}] {ex}")
        if data:
            register_list(STATS_REPORT_CATEGORY, data,
                          mode_run=MODE_RUN_IMMEDIATELY)
        #
        if errors:
            msg = f" , ".join(errors)
            messages.error(request, msg)
        else:
            messages.success(
                request, f"{queryset.count()} pick jobs stats report successfully")

    def clear_view_decorators_cached(self, request, queryset):
        try:
            cache.delete_many(keys=cache.keys('views.decorators.cache.*'))
            messages.success(
                request, f"Clear view decorators cached successfully")
        except Exception as ex:
            messages.error(request, f"Clear Cache Pages Errors : {ex}")

    def purge_celery_worker(self, request, queryset):
        try:
            messages.info(
                request, f"begin purge all tasks waiting celery ....")
            current_app.control.purge()
            for category in LIST_JOB_CATEGORY:
                messages.info(request, f"changed to status `Ignore` of jobs {category} manage "
                                       f"Started, Received....")
                ignore_category_job(category=category, status__in=[
                                    STARTED, RECEIVED])
            messages.success(
                request, f"discard all waiting tasks celery successfully")
        except Exception as ex:
            messages.error(
                request, f"discard all waiting tasks celery errors : {ex}")

    def generate_ds_source(self, request, queryset):
        errors = []
        data = []
        job_name = "app.financial.jobs.schema_datasource.handler_generate_client_source"
        for obj in queryset:
            try:
                data.append(dict(
                    client_id=obj.pk,
                    name=f"sync_data_source_flattens_settings_{obj.pk}",
                    job_name=job_name,
                    module="app.financial.jobs.schema_datasource",
                    method="handler_generate_client_source",
                    meta=dict(client_id=str(
                        obj.pk), access_token=settings.DS_TOKEN, token_type="DS_TOKEN")
                ))
            except Exception as ex:
                errors.append(f"[{obj.id}] {ex}")
        if data:
            register_list(SYNC_DATA_SOURCE_CATEGORY, data,
                          mode_run=MODE_RUN_IMMEDIATELY)
        #
        if errors:
            msg = f" , ".join(errors)
            messages.error(request, msg)
        else:
            messages.success(
                request, f"{queryset.count()} DS generate successfully")

    def generate_db_table_template(self, request, queryset):
        errors = []
        data = []
        job_name = "app.database.jobs.db_table_template.sync_db_table_template_workspace"
        for obj in queryset:
            try:
                data.append(dict(
                    client_id=obj.pk,
                    name=f"sync_db_table_template_workspace_{obj.pk}",
                    job_name=job_name,
                    module="app.database.jobs.db_table_template",
                    method="sync_db_table_template_workspace",
                    meta=dict(client_id=str(obj.pk), sync_column=True)
                ))
            except Exception as ex:
                errors.append(f"[{obj.id}] {ex}")
        if data:
            register_list(SYNC_DATA_SOURCE_CATEGORY, data,
                          mode_run=MODE_RUN_IMMEDIATELY)
        if errors:
            msg = f" , ".join(errors)
            messages.error(request, msg)
        else:
            messages.success(
                request, f"{queryset.count()} generate db table template successfully")

    def generate_top_product_performance(self, request, queryset):
        errors = []
        client_ids = queryset.values_list('pk', flat=True)
        try:
            handler_pick_job_calculation_top_product_performance_clients(
                client_ids=list(client_ids))
        except Exception as ex:
            errors.append(f"clients {len(client_ids)} {ex}")
        #
        if errors:
            msg = f" , ".join(errors)
            messages.error(request, msg)
        else:
            messages.success(
                request, f"{queryset.count()} Top Product Performance generate successfully")

    def sync_status_of_workspace_from_portal(self, request, queryset):
        errors = []
        for obj in queryset:
            try:
                WorkspaceManagement(str(obj.pk)).sync_status_of_client()
            except Exception as ex:
                errors.append(f"client {obj.name} {ex}")
        #
        if errors:
            msg = f" , ".join(errors)
            messages.error(request, msg)
        else:
            messages.success(
                request, f"{queryset.count()} sync status workspace from portal service successfully")

    def generate_brands_summary_pre_monthly_report(self, request, queryset):
        errors = []
        try:
            create_jobs_sp_report_brands_summary_clients(
                client_ids=list(queryset.values_list("pk", flat=True)))
        except Exception as ex:
            errors.append(f"Error {ex}")
        #
        if errors:
            msg = f" , ".join(errors)
            messages.error(request, msg)
        else:
            messages.success(
                request, f"{queryset.count()} register jobs generate successfully")

    generate_ds_source.short_description = 'Generate data source flattens tracking'
    generate_db_table_template.short_description = "Generate DB Table Template Clients"
    generate_top_product_performance.short_description = "Generate Top Product Performance Clients"
    generate_stats_report.short_description = "Generate Stats Reports Clients"
    sync_status_of_workspace_from_portal.short_description = "Sync status of workspace from Portal"
    clear_view_decorators_cached.short_description = "Clear Workspaces Cache Pages"
    purge_celery_worker.short_description = "Purge Workspaces All Waiting Tasks Celery Worker"
    generate_brands_summary_pre_monthly_report.short_description = "Generate Brands Summary Previous Monthly Worker"


@admin.register(Sale)
class SaleAdmin(TenantDBForModelAdmin):
    paginator = LargeTablePagination
    list_display = ['id', 'channel_sale_id', 'date', 'city', 'state', 'country', 'postal_code', 'state_key',
                    'county_key', 'is_prime']
    search_fields = ['id', 'channel_sale_id', 'date',
                     'city', 'state', 'country', 'postal_code']
    list_filter = ['channel', 'client']
    ordering = ['-date']

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if change:
            client_id = str(obj.client_id)
            SaleItem.objects.tenant_db_for(client_id).filter(
                sale=obj, dirty=False).update(dirty=True)
            logger.info(
                'sync sale item of client id {} to ds'.format(client_id))
            data = [
                dict(
                    client_id=client_id,
                    name="sync_data_source_standard",
                    job_name="app.financial.jobs.data_flatten.flat_sale_items_bulks_sync_task",
                    module="app.financial.jobs.data_flatten",
                    method="flat_sale_items_bulks_sync_task",
                    meta=dict(client_id=client_id)
                )
            ]
            register_list(SYNC_ANALYSIS_CATEGORY, data)

    def delete_model(self, request, obj):
        client_id = str(obj.client_id)
        #
        super().delete_model(request, obj)
        # delete all record sale items
        salechargeandcost = obj.salechargeandcost
        salechargeandcost.is_removed = True
        salechargeandcost.save()
        obj.saleitem_set.all().update(is_removed=True)
        # trigger sync to ds
        logger.info('sync sale items of sale to ds'.format(client_id))
        data = [
            dict(
                client_id=client_id,
                name="sync_data_source_standard",
                job_name="app.financial.jobs.data_flatten.flat_sale_items_bulks_sync_task",
                module="app.financial.jobs.data_flatten",
                method="flat_sale_items_bulks_sync_task",
                meta=dict(client_id=client_id)
            )
        ]
        register_list(SYNC_ANALYSIS_CATEGORY, data)

    def delete_queryset(self, request, queryset):
        client_ids = list(queryset.values_list('client_id', flat=True))
        #
        super().delete_queryset(request, queryset)
        # trigger sync to ds
        data = []
        for client_id in client_ids:
            logger.info('sync sale item of sale {} to ds'.format(client_id))
            data.append(
                dict(
                    client_id=client_id,
                    name="sync_data_source_standard",
                    job_name="app.financial.jobs.data_flatten.flat_sale_items_bulks_sync_task",
                    module="app.financial.jobs.data_flatten",
                    method="flat_sale_items_bulks_sync_task",
                    meta=dict(client_id=client_id)
                )
            )
        register_list(SYNC_ANALYSIS_CATEGORY, data)


@admin.register(SaleItem)
class SaleItemAdmin(TenantDBForModelAdmin):
    paginator = LargeTablePagination
    list_display = ['id', 'sale_id', 'client_id', 'brand_id', 'sku', 'brand_sku', 'asin', 'title', 'sale_id',
                    'style_id']
    search_fields = ['id', 'asin', 'title', 'upc', 'sku', 'brand__name']
    list_filter = ['is_removed', 'dirty', 'client']
    autocomplete_fields = ['sale']
    actions = ['find_and_match_fedex_shipment', 'split_financial_record']

    def delete_model(self, request, obj):
        client_id = str(obj.client_id)
        super().delete_model(request, obj)
        # trigger sync to ds
        logger.info('sync sale item of client id {} to ds'.format(client_id))
        data = [
            dict(
                client_id=client_id,
                name="sync_data_source_standard",
                job_name="app.financial.jobs.data_flatten.flat_sale_items_bulks_sync_task",
                module="app.financial.jobs.data_flatten",
                method="flat_sale_items_bulks_sync_task",
                meta=dict(client_id=client_id)
            )
        ]
        register_list(SYNC_ANALYSIS_CATEGORY, data)

    def delete_queryset(self, request, queryset):
        client_ids = list(queryset.values_list('client_id', flat=True))
        super().delete_queryset(request, queryset)
        # trigger sync to ds
        data = []
        for client_id in client_ids:
            logger.info(
                'sync sale item of client id {} to ds'.format(client_id))
            data.append(
                dict(
                    client_id=client_id,
                    name="sync_data_source_standard",
                    job_name="app.financial.jobs.data_flatten.flat_sale_items_bulks_sync_task",
                    module="app.financial.jobs.data_flatten",
                    method="flat_sale_items_bulks_sync_task",
                    meta=dict(client_id=client_id)
                )
            )
        register_list(SYNC_ANALYSIS_CATEGORY, data)

    def save_model(self, request, obj, form, change):
        if change:
            obj.dirty = True
        super().save_model(request, obj, form, change)
        client_id = obj.client_id
        # trigger sync to ds
        # find dirty
        count = SaleItem.objects.tenant_db_for(
            client_id).filter(dirty=True).count()
        if count > 0:
            logger.info(
                'sync sale item of client id {} to ds'.format(client_id))
            data = [
                dict(
                    client_id=client_id,
                    name="sync_data_source_standard",
                    job_name="app.financial.jobs.data_flatten.flat_sale_items_bulks_sync_task",
                    module="app.financial.jobs.data_flatten",
                    method="flat_sale_items_bulks_sync_task",
                    meta=dict(client_id=client_id)
                )
            ]
            register_list(SYNC_ANALYSIS_CATEGORY, data)

    def split_financial_record(self, request, queryset):
        try:
            # change financial dirty
            queryset.update(financial_dirty=True)
            clients_items = queryset.values("client_id", "id")
            #
            group_key_data = {}
            for k, g in itertools.groupby(clients_items, lambda x: x["client_id"]):
                group_key_data.update({k: [str(item["id"]) for item in g]})
            #
            data = []
            for client_id, sale_item_ids in group_key_data.items():
                meta = dict(client_id=client_id, sale_item_ids=sale_item_ids)
                hash_content = hashlib_content(meta)
                data.append(
                    dict(
                        client_id=client_id,
                        name=f"split_sale_item_financial_ws_{hash_content}",
                        job_name="app.financial.jobs.sale_financial.handler_trigger_split_sale_item_financial_ws",
                        module="app.financial.jobs.sale_financial",
                        method="handler_trigger_split_sale_item_financial_ws",
                        meta=meta
                    )
                )
            register_list(SYNC_ANALYSIS_CATEGORY, data)
        except Exception as ex:
            print(ex)

    split_financial_record.short_description = "Split financial record"

    def find_and_match_fedex_shipment(self, request, queryset):
        clients_items = queryset.values("client_id", "id")
        #
        group_key_data = {}
        for k, g in itertools.groupby(clients_items, lambda x: x["client_id"]):
            group_key_data.update({k: [str(item["id"]) for item in g]})
        #
        data = []
        for client_id, sale_item_ids in group_key_data.items():
            data.append(
                dict(
                    client_id=client_id,
                    name="find_and_match_fedex_shipment",
                    job_name="app.financial.jobs.fedex_shipment.sale_item_match_fedex_shipment_job",
                    module="app.financial.jobs.fedex_shipment",
                    method="sale_item_match_fedex_shipment_job",
                    meta=dict(client_id=str(client_id),
                              sale_item_ids=sale_item_ids)
                )
            )
        register_list(SYNC_ANALYSIS_CATEGORY, data)

    find_and_match_fedex_shipment.short_description = "Create a job to matching fedex shipment with these Sale Items"


class ItemCogInline(admin.TabularInline):
    paginator = LargeTablePagination
    model = ItemCog
    exclude = ['is_removed']


@admin.register(Item)
class ItemAdmin(TenantDBForModelAdmin):
    paginator = LargeTablePagination
    list_display = ('client', 'id', 'sku', 'title')
    search_fields = ('sku', 'upc', 'asin')
    ordering = ('-client',)
    list_filter = ['client']

    inlines = [ItemCogInline]


@admin.register(SaleStatus)
class SaleStatusAdmin(TenantDBForModelAdmin):
    pass


@admin.register(ProfitStatus)
class ProfitStatusAdmin(TenantDBForModelAdmin):
    pass


@admin.register(Brand)
class BrandAdmin(TenantDBForModelAdmin):
    paginator = LargeTablePagination
    search_fields = ['name']
    list_display = ('id', 'name', 'client', 'is_obsolete', 'created')
    list_filter = ['is_obsolete', 'client']

    def delete_queryset(self, request, queryset):
        #
        try:
            for obj in queryset:
                client_db = get_connection_workspace(obj.client_id)
                obj.brandsetting_set.tenant_db_for(
                    obj.client_id).all().delete()
                obj.delete(using=client_db)
        except Exception as ex:
            logger.error(
                f"[{self.__class__.__name__}][delete_queryset][{self.model.__name__}] {ex}")


@admin.register(Variant)
class VariantAdmin(TenantDBForModelAdmin):
    pass


@admin.register(SaleChargeAndCost)
class SaleChargeAndCostAdmin(TenantDBForModelAdmin):
    paginator = LargeTablePagination
    list_display = (
        'id', 'sale', 'quantity', 'sale_charged', 'shipping_charged', 'tax_charged', 'total_items_cost',
        'channel_listing_fee', 'other_channel_fees', 'profit', 'margin', 'total_charged',)
    search_fields = ['sale__id']
    list_filter = ['sale__client']

    def margin(self, obj):
        if not obj.margin:
            return None
        return "{} %".format(obj.margin * 100)


class CustomAdminBase(TenantDBForModelAdmin):
    paginator = LargeTablePagination
    list_display = ['id', 'name', 'user__email', 'client__name', 'share_mode']
    list_filter = ['share_mode', 'client']
    search_fields = ['id', 'name', 'user__email',
                     'user__username', 'client__name', 'client__id']

    @classmethod
    def client__name(cls, obj):
        return obj.client.name

    @classmethod
    def user__email(cls, obj):
        return obj.user.email

    @classmethod
    def user__username(cls, obj):
        return obj.user.username


@admin.register(CustomColumn)
class CustomColumnAdmin(CustomAdminBase):
    pass


@admin.register(CustomFilter)
class CustomFilterAdmin(CustomAdminBase):
    pass


@admin.register(CustomView)
class CustomViewAdmin(CustomAdminBase):
    pass


@admin.register(CustomReport)
class CustomReportAdmin(CustomAdminBase):
    list_display = ['id', 'name', 'user__email',
                    'client__name', 'download_url', 'created', 'modified']


@admin.register(CustomObject)
class CustomObjectAdmin(TenantDBForModelAdmin):
    paginator = LargeTablePagination
    list_display = ('id', 'client__name')
    list_filter = ['client']
    search_fields = ('id', 'client__name', 'client__id')

    @classmethod
    def client__name(cls, obj):
        return obj.client.name


@admin.register(ShareCustom)
class ShareCustomAdmin(TenantDBForModelAdmin):
    paginator = LargeTablePagination
    list_filter = ['client']


@admin.register(Activity)
class ActivityAdmin(TenantDBForModelAdmin):
    list_display = ['id', 'client', 'user', 'action', 'created', 'modified']
    paginator = LargeTablePagination
    list_filter = ['client']


@admin.register(Channel)
class ChannelAdmin(TenantDBForModelAdmin):
    list_display = ['id', 'name', 'use_in_global_filter', 'is_pull_data']
    search_fields = ['name']
    list_filter = ['is_pull_data']


@admin.register(UserPermission)
class UserPermissionAdmin(TenantDBForModelAdmin):
    paginator = LargeTablePagination
    search_fields = ['user__user_id']
    list_filter = ['client', 'role', 'module']


@admin.register(FulfillmentChannel)
class FulfillmentChannelAdmin(TenantDBForModelAdmin):
    pass


@admin.register(SaleItemTransaction)
class SaleItemTransactionAdmin(TenantDBForModelAdmin):
    paginator = LargeTablePagination
    list_display = ['id', 'client_id', 'channel_sale_id', 'channel_id', 'sku', 'date', 'amount', 'type', 'category',
                    'event', 'seq']
    search_fields = ['channel_sale_id', 'sku']
    list_filter = ['channel', 'category', 'event', 'client']


@admin.register(DataFlattenTrack)
class DataFlattenTrackAdmin(TenantDBForModelAdmin):
    paginator = LargeTablePagination
    list_display = ['id', 'client_id', 'type', 'source',
                    'status', 'live_feed', 'last_rows_synced', 'last_run']
    list_filter = ['client', 'type', 'status', 'source']
    actions = [
        "reconfig_data_source",
        "clear_cache_data_source",
        "sync_data_to_es_source",
        "sync_data_to_pg_source"
    ]

    def sync_data_to_es_source(self, request, queryset):
        self.sync_data_to_source_type(
            name="sync_data_source_es",
            request=request,
            queryset=queryset,
            source=FLATTEN_ES_SOURCE,
            is_resync_data_source=True
        )

    def reconfig_data_source(self, request, queryset):
        self.sync_data_to_source_type(
            name="reconfig_data_source",
            request=request,
            queryset=queryset,
            is_reconfig_data_source=True
        )

    def sync_data_to_pg_source(self, request, queryset):
        self.sync_data_to_source_type(
            name="sync_data_source_pg",
            request=request,
            queryset=queryset,
            source=FLATTEN_PG_SOURCE,
            is_resync_data_source=True
        )

    def clear_cache_data_source(self, request, queryset):
        errors = []
        for obj in queryset:
            try:
                ds_service = DSManager(client_id=str(obj.client_id))
                if obj.source == FLATTEN_PG_SOURCE:
                    ds_id = obj.data_source_id
                else:
                    ds_id = obj.data_source_es_id
                rs = ds_service.clear_cache_ds(ds_id)
                logger.info(f"[{self.__class__.__name__}] {rs}")
            except Exception as ex:
                errors.append(f"{obj.client_id} {ex}")
        if errors:
            msg = f" , ".join(errors)
            messages.error(request, msg)
        else:
            messages.success(
                request, f"{queryset.count()} clear cache successfully")

    @staticmethod
    def sync_data_to_source_type(name, request, queryset, source: str = None,
                                 is_reconfig_data_source: bool = False, is_resync_data_source: bool = False):
        errors = []
        data = []
        for obj in queryset:
            try:
                kwargs = dict(
                    client_id=obj.client_id,
                    type_flatten=obj.type,
                    bulk_size=10000
                )
                if is_resync_data_source:
                    kwargs.update(dict(
                        source=source,
                        resync_data_source=is_resync_data_source
                    ))

                if is_reconfig_data_source:
                    kwargs.update(dict(
                        reconfig_data_source=True
                    ))

                data.append(
                    dict(
                        client_id=str(obj.client_id),
                        name=f"{name}_{obj.type.lower()}",
                        job_name="app.financial.jobs.schema_datasource.handler_sync_scheme_data_source",
                        module="app.financial.jobs.schema_datasource",
                        method="handler_sync_scheme_data_source",
                        meta=kwargs
                    )
                )
            except Exception as ex:
                errors.append(f"{obj.client_id} {ex}")
        if len(data) > 0:
            register_list(SYNC_DATA_SOURCE_CATEGORY, data,
                          mode_run=MODE_RUN_IMMEDIATELY)
        if errors:
            msg = f" , ".join(errors)
            messages.error(request, msg)
        else:
            messages.success(
                request, f"{queryset.count()} {source} generate successfully")

    sync_data_to_es_source.short_description = 'Sync data to Elasticsearch Source'
    reconfig_data_source.short_description = 'Sync schema config Source'
    sync_data_to_pg_source.short_description = 'Sync data to Postgres Source'
    clear_cache_data_source.short_description = 'Clear caches Datasource'


admin.site.unregister(LogEntry)


@admin.register(LogEntry)
class CustomModelAdminLogEntry(LogEntryAdmin):
    paginator = LargeTablePagination
    list_display = ['created', 'resource_url', 'action', 'msg_short', 'user_url', 'email_actor',
                    'user_id_actor']

    class Meta:
        proxy = True

    def email_actor(self, obj):
        res = obj.additional_data
        if res is not None:
            return res.get('email', None)
        return None

    def user_id_actor(self, obj):
        res = obj.additional_data
        if res is not None:
            return res.get('pk', None)
        return None


@admin.register(DataStatus)
class DataStatusAdmin(TenantDBForModelAdmin):
    paginator = LargeTablePagination
    actions = ['make_reopen_status', 'make_ready_status', 'make_done_status', 'prefetch_all_data_purchase_date',
               'pick_data_status_to_job_time_control', 'make_is_checking_prime']
    list_display = ['id', 'client', 'channel', 'type',
                    'date', 'status', 'priority', 'created', 'modified']
    list_filter = ['client', 'type', 'status', 'channel', ('date', DateFieldListFilter),
                   ('date', DateTimeRangeFilter)]
    ordering = ('-date',)

    def channel__name(self, obj):
        return obj.channel.name if obj.channel else None

    channel__name.short_description = 'Channel'

    def make_reopen_status(self, request, queryset):
        self.make_job_by_status_request(request, queryset, OPEN_STATUS)

    def make_ready_status(self, request, queryset):
        self.make_job_by_status_request(request, queryset, READY_STATUS)

    def make_done_status(self, request, queryset):
        self.make_job_by_status_request(request, queryset, DONE_STATUS)

    def make_is_checking_prime(self, request, queryset):
        errors = []
        total = queryset.count()
        try:
            client_ids = queryset.values_list('client_id', flat=True)
            for client_id in client_ids:
                try:
                    DataStatus.objects.tenant_db_for(
                        client_id).update(is_checking_prime=True)
                except Exception as ex:
                    errors.append(f"[{client_id}] records {ex}")
        except Exception as ex:
            errors.append(f"{total} records {ex}")
        if errors:
            msg = f" , ".join(errors)
            messages.error(request, msg)
        else:
            messages.success(
                request, f"{total} enabled checking prime done")

    def make_job_by_status_request(self, request, queryset, status):
        errors = []
        total = queryset.count()
        try:
            def map_set_object(x):
                x.priority = PF_TIME_CONTROL_PRIORITY_TYPE[x.type]
                x.status = status
                x.modified = timezone.now()
                return x

            client_ids = queryset.values_list('client_id', flat=True)
            for client_id in client_ids:
                try:
                    objs = list(map(map_set_object, queryset.filter(
                        client_id=client_id).exclude(status=status)))
                    if len(objs) > 0:
                        DataStatus.objects.tenant_db_for(client_id).bulk_update(objs,
                                                                                fields=['priority', 'status',
                                                                                        'modified'])
                except Exception as ex:
                    errors.append(f"[{client_id}] {status} records {ex}")
        except Exception as ex:
            errors.append(f"{total} {status} records {ex}")
        if errors:
            msg = f" , ".join(errors)
            messages.error(request, msg)
        else:
            messages.success(
                request, f"{total} make {status} status")

    def pick_data_status_to_job_time_control(self, request, queryset):
        errors = []
        jobs_data = []
        total = queryset.count()
        try:
            def map_set_object(x):
                x.priority = PF_TIME_CONTROL_PRIORITY_TYPE[x.type]
                x.status = READY_STATUS
                x.modified = timezone.now()
                return x

            client_ids = queryset.values_list('client_id', flat=True)
            for client_id in client_ids:
                try:
                    objs = list(map(map_set_object, queryset.filter(
                        client_id=client_id).exclude(status=READY_STATUS)))
                    if len(objs) > 0:
                        DataStatus.objects.tenant_db_for(client_id).bulk_update(objs,
                                                                                fields=['priority', 'status',
                                                                                        'modified'])
                except Exception as ex:
                    errors.append(f"[{client_id}] ready records {ex}")
            #
            job_name = 'app.financial.jobs.time_control.handler_time_control_process_type_is_ready_workspace'
            module = "app.financial.jobs.time_control"
            method = "handler_time_control_process_type_is_ready_workspace"
            #
            marketplaces = Channel.objects.tenant_db_for(client_ids[0]).filter(is_pull_data=True) \
                .values_list('name', flat=True)
            client_connections = get_connections_client_channels(client_ids[0], list(marketplaces),
                                                                 [SELLER_PARTNER_CONNECTION])
            for obj in queryset.filter(status=READY_STATUS).iterator():
                try:
                    assert client_connections[SELLER_PARTNER_CONNECTION].get(obj.channel.name, False) is True, \
                        f"The workspace doesn't connect marketplace"
                    if obj.type == INFORMED_TYPE:
                        assert client_connections[INFORMED_MARKETPLACE_CONNECTION].get(obj.channel.name, False) is True, \
                            f"The workspace doesn't setup informed"
                    data_status_id = str(obj.pk)
                    data = dict(
                        name=f"time_control_process_event_is_ready_{data_status_id}",
                        client_id=obj.client_id,
                        job_name=job_name,
                        module=module,
                        method=method,
                        time_limit=None,
                        is_run_validations=False,
                        meta=dict(
                            client_id=obj.client_id, data_status_id=data_status_id, marketplace=obj.channel.name)
                    )
                    jobs_data.append(data)
                except Exception as ex:
                    logger.error(
                        f"[{client_ids[0]}[{obj.channel.name}][pick_data_status_to_job_time_control] {ex}")
            if len(jobs_data) > 0:
                register_list(TIME_CONTROL_CATEGORY, jobs_data)
                logger.info(f"[pick_data_status_to_job_time_control] {total} "
                            f"register_list app jobs time control completed")
        except Exception as ex:
            errors.append(f"{total} records {ex}")
        if errors:
            msg = f" , ".join(errors)
            messages.error(request, msg)
        else:
            messages.success(
                request, f"{total} make ready status")

    def prefetch_all_data_purchase_date(self, request, queryset):
        errors = []
        data = []
        for obj in queryset:
            try:
                marketplace = obj.channel.name
                from_date = f'{obj.date} 00:00:00'
                to_date = f'{obj.date} 23:59:59'
                meta = dict(
                    client_id=str(obj.client_id),
                    marketplace=marketplace,
                    from_date=from_date, to_date=to_date,
                    track_logs=False, log_type=TIME_CONTROL_LOG_TYPE,
                    time_control_id=str(obj.pk),
                    filter_mode=POSTED_FILTER_MODE
                )

                item_data = dict(
                    client_id=str(obj.client_id),
                    name=f"prefetch_all_data_purchase_date__{obj.type.lower()}__{marketplace}__{obj.date}"
                )

                if obj.type == SALE_EVENT_TYPE:
                    item_data.update(dict(
                        job_name="app.financial.jobs.live_feed.handler_trigger_live_feed_sale_item_ws",
                        module="app.financial.jobs.live_feed",
                        method="handler_trigger_live_feed_sale_item_ws"
                    ))
                elif obj.type == FINANCIAL_EVENT_TYPE:
                    item_data.update(dict(
                        job_name="app.financial.jobs.event.handler_trigger_trans_event_sale_item_ws",
                        module="app.financial.jobs.event",
                        method="handler_trigger_trans_event_sale_item_ws"
                    ))
                elif obj.type == INFORMED_TYPE:
                    item_data.update(dict(
                        job_name="app.financial.jobs.informed.handler_trigger_informed_sale_item_ws",
                        module="app.financial.jobs.informed",
                        method="handler_trigger_informed_sale_item_ws"
                    ))
                    meta.update(dict(override=True))
                else:
                    pass
                item_data.update(dict(meta=meta))
                data.append(item_data)
            except Exception as ex:
                errors.append(f"{obj.client_id} {ex}")
        if len(data) > 0:
            register_list(SYNC_DATA_SOURCE_CATEGORY, data,
                          mode_run=MODE_RUN_IMMEDIATELY)
        if errors:
            msg = f" , ".join(errors)
            messages.error(request, msg)
        else:
            messages.success(
                request, f"{queryset.count()} prefetch pick into jobs sync source manage")

    make_reopen_status.short_description = "Make reopen data status"
    make_ready_status.short_description = "Make ready data status"
    make_done_status.short_description = "Make done data status"
    prefetch_all_data_purchase_date.short_description = "Prefetch All Data Purchase Date"
    pick_data_status_to_job_time_control.short_description = "Pick to job time control"
    make_is_checking_prime.short_description = "Enable Checking Prime"


@admin.register(BrandSetting)
class BrandSettingAdmin(TenantDBForModelAdmin):
    paginator = LargeTablePagination
    list_display = ['id', 'client__name', 'channel', 'brand', 'segment', 'est_first_item_shipcost',
                    'est_add_item_shipcost', 'est_fba_fees', 'po_dropship_cost', 'mfn_formula', 'auto_update_sales']
    search_fields = ('brand__name',)
    ordering = ('brand__name',)
    list_filter = ['client']

    autocomplete_fields = ['brand']

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super(BrandSettingAdmin, self).get_search_results(
            request, queryset, search_term)
        # custom
        queryset_brand_null = BrandSetting.objects.tenant_db_for(self.get_client_id_request(request)).filter(
            brand__isnull=True)
        final_query_set = queryset | queryset_brand_null
        return final_query_set, use_distinct

    @classmethod
    def channel__name(cls, obj):
        return obj.channel.name if obj.channel else None

    @classmethod
    def brand__name(cls, obj):
        return obj.brand.name if obj.brand else None

    @classmethod
    def client__name(cls, obj):
        return obj.client.name

    def delete_model(self, request, obj):
        brand = obj.brand
        obj.delete()
        brand.delete()

    # Handle bulk deletions (from list view)
    def delete_queryset(self, request, queryset):
        for obj in queryset:
            brand = obj.brand
            obj.delete()
            brand.delete()


class CustomBrandMissingSimpleListFilter(SimpleListFilter):
    title = _('Mapped Brand')
    parameter_name = 'custom_mapped_brand'

    def lookups(self, request, model_admin):
        return (
            ("mapped", _("Missing brand is mapped.")),
            ("not_mapped", _("Missing brand is not mapped."))
        )

    def queryset(self, request, queryset):
        if self.value() == 'mapped':
            return queryset.filter(mapped_brand__isnull=False)
        if self.value() == 'not_mapped':
            return queryset.filter(mapped_brand__isnull=True)


@admin.register(BrandMissing)
class BrandMissingAdmin(TenantDBForModelAdmin):
    paginator = LargeTablePagination
    list_filter = [CustomBrandMissingSimpleListFilter, 'client']
    list_display = ('name', 'mapped_brand__name')
    ordering = ('name',)
    search_fields = ('name',)
    autocomplete_fields = ['mapped_brand']

    @classmethod
    def mapped_brand__name(cls, obj):
        return obj.mapped_brand.name if obj.mapped_brand else None


@admin.register(ClientSettings)
class ClientSettingsAdmin(TenantDBForModelAdmin):
    paginator = LargeTablePagination
    list_display = ["client", "allow_sale_data_update_from"]
    list_filter = ['client']
    search_fields = ['client__name']  # Optional
    readonly_fields = ['ac_spapi_token_expired']  # Optional
    fieldsets = (
        ("Client Info", {
            'fields': ('client', 'allow_sale_data_update_from', 'time_bulk_processing_notification'),
        }),

        ("Amazon MWS Settings", {
            'fields': (
                'ac_mws_access_key', 'ac_mws_secret_key', 'ac_mws_merchant_id',
                'ac_mws_merchant_name', 'ac_mws_enabled'
            ),
        }),

        ("Amazon SP-API Settings", {
            'fields': (
                'ac_spapi_app_id', 'ac_spapi_access_token', 'ac_spapi_refresh_token',
                'ac_spapi_token_expired', 'ac_spapi_selling_partner_id',
                'ac_spapi_auth_code', 'ac_spapi_state',
                'ac_spapi_enabled', 'ac_spapi_need_reconnect'
            ),
        }),

        ("CartRover Integration", {
            'fields': (
                'ac_cart_rover', 'ac_cart_rover_api_user', 'ac_cart_rover_api_key', 'ac_cart_rover_enabled'
            ),
        }),

        ("3PL Central", {
            'fields': ('ac_3pl_central_enabled',),
        }),

        ("Health & Widgets", {
            'fields': ('health_hours_check_ac', 'total_sales_tracker_goal'),
        }),

        ("IT Department", {
            'fields': ('is_it_department', 'it_department_orders_limit', 'is_remove_cogs_refunded'),
        }),

        ("COGS Source Configuration", {
            'fields': (
                'cog_use_extensiv', 'cog_extensiv_token',
                'cog_use_dc', 'cog_use_pf', 'cog_priority_source',
            ),
            'description': "Required if both Extensiv and DC & Item are enabled"
        }),
    )
    actions = ["sync_spapi_connections", "sync_mws_keys",
               "sync_cart_rover_accounts", "sync_3pl_central_accounts"]

    def sync_spapi_connections(self, request, queryset):
        errors = []
        client_ids = queryset.values_list("client_id", flat=True)
        #
        try:
            register_spapi_keys_setting(client_ids)
            register_ac_clients_settings(client_ids)
        except Exception as ex:
            errors.append(f"{client_ids}: {ex}")
        if errors:
            msg = f" , ".join(errors)
            messages.error(request, msg)
        else:
            messages.success(
                request, f"{queryset.count()} sync SPAPI connect successfully")

    def sync_mws_keys(self, request, queryset):
        errors = []
        client_ids = queryset.values_list("client_id", flat=True)
        try:
            register_mws_keys_setting(client_ids)
            register_ac_clients_settings(client_ids)
        except Exception as ex:
            errors.append(f"{client_ids}: {ex}")
        if errors:
            msg = f" , ".join(errors)
            messages.error(request, msg)
        else:
            messages.success(
                request, f"{queryset.count()} sync MWS keys successfully")

    def sync_cart_rover_accounts(self, request, queryset):
        errors = []
        client_ids = queryset.values_list("client_id", flat=True)
        try:
            register_cart_rover_keys_setting(client_ids)
        except Exception as ex:
            errors.append(f"{client_ids}: {ex}")
        if errors:
            msg = f" , ".join(errors)
            messages.error(request, msg)
        else:
            messages.success(
                request, f"{queryset.count()} sync CartRover accounts successfully")

    def sync_3pl_central_accounts(self, request, queryset):
        errors = []
        client_ids = queryset.values_list("client_id", flat=True)
        try:
            sync_accounts_3pl_central_keys_setting(client_ids)
        except Exception as ex:
            errors.append(f"{client_ids}: {ex}")
        if errors:
            msg = f" , ".join(errors)
            messages.error(request, msg)
        else:
            messages.success(
                request, f"{queryset.count()} synced 3PL Central Accounts successfully")

    sync_spapi_connections.short_description = "Sync SPAPI Connections"
    sync_mws_keys.short_description = "Sync MWS Keys"
    sync_cart_rover_accounts.short_description = " Sync CartRover Accounts"
    sync_3pl_central_accounts.short_description = "Sync 3PL Central Accounts"


@admin.register(FinancialSettings)
class FinancialSettingAdmin(TenantDBForModelAdmin, DynamicArrayMixin):
    list_display = ("system_contacts",)


@admin.register(AutoFeedBrand)
class AutoFeedBrandAdmin(TenantDBForModelAdmin):
    paginator = LargeTablePagination
    list_display = ('client', 'channel', 'brand')
    list_filter = ['client']
    actions = ['generate_data_feed']

    def generate_data_feed(self, request, queryset):
        errors = []
        data = []
        client_ids = queryset.values_list('client_id', flat=True).distinct()
        try:
            for client_id in client_ids:
                auto_feed_ids = list(queryset.filter(
                    client_id=client_id).values_list('pk', flat=True))
                hash_data = hashlib.md5(json.dumps(
                    auto_feed_ids).encode('utf-8')).hexdigest()[:8]
                job_info = dict(
                    client_id=client_id,
                    name=f"generate_sale_items_data_feed_{hash_data}",
                    job_name="app.financial.jobs.data_feed.handler_auto_generate_sale_items_data_feed",
                    module="app.financial.jobs.data_feed",
                    method="handler_auto_generate_sale_items_data_feed",
                    meta=dict(client_id=client_id, auto_feed_ids=auto_feed_ids)
                )
                data.append(job_info)
                #
                job_info = dict(
                    client_id=client_id,
                    name=f"generate_yoy_30d_sales_data_feed_{hash_data}",
                    job_name="app.financial.jobs.data_feed.handler_auto_generate_yoy_30d_sales_data_feed",
                    module="app.financial.jobs.data_feed",
                    method="handler_auto_generate_yoy_30d_sales_data_feed",
                    meta=dict(client_id=client_id, auto_feed_ids=auto_feed_ids)
                )
                data.append(job_info)
        except Exception as ex:
            errors.append(f"{client_ids}: {ex}")

        if len(data) > 0:
            register_list(SYNC_DATA_SOURCE_CATEGORY, data,
                          mode_run=MODE_RUN_IMMEDIATELY)

        if errors:
            msg = f" , ".join(errors)
            messages.error(request, msg)
        else:
            messages.success(
                request, f"{queryset.count()} records pick jobs successfully")

    generate_data_feed.short_description = "Generate Data Feed"


@admin.register(DataFeedTrack)
class DataFeedTrackAdmin(TenantDBForModelAdmin):
    paginator = LargeTablePagination
    list_display = ['client', 'brand', 'type', 'action',
                    'date', 'file_uri', 'latest', 'created']
    search_fields = ['brand__name']
    list_filter = ['channel', 'client', 'type', 'action', 'latest']


@admin.register(FedExShipment)
class FedExShipmentAdmin(TenantDBForModelAdmin):
    paginator = LargeTablePagination
    list_display = ['id', 'recipient_name', 'service_type', 'shipper_company', 'net_charge_amount',
                    'recipient_address_line_1', 'recipient_address_line_2', 'recipient_country', 'recipient_state',
                    'recipient_city', 'recipient_zip_code', 'shipment_date', 'status', 'matched_sales',
                    'matched_channel_sale_ids', 'matched_time', 'tracking_id', 'invoice_number', 'invoice_date']
    ordering = ('client', 'shipment_date')
    list_filter = ['recipient_country', 'status', 'source', 'client',
                   ('shipment_date', DateTimeRangeFilter),
                   ('invoice_date', DateTimeRangeFilter)]
    search_fields = ['recipient_name', 'recipient_state', 'recipient_city', 'recipient_zip_code', 'net_charge_amount',
                     'tracking_id', 'invoice_number', 'service_type', 'recipient_address_line_1',
                     'recipient_address_line_2', 'matched_sales', 'matched_channel_sale_ids', 'shipper_company']
    actions = ['change_to_pending']

    def change_to_pending(self, request, queryset):
        queryset.update(status=FEDEX_SHIPMENT_PENDING,
                        matched_sales=[], matched_channel_sale_ids=[], matched_time=None)

    change_to_pending.short_description = "Change status to PENDING for re-matching"


@admin.register(AdSpendInformation)
class AdSpendInformationAdmin(TenantDBForModelAdmin):
    paginator = LargeTablePagination
    list_display = ['brand', 'date', 'sales', 'spend', 'impression', 'acos', 'roas', 'ad_revenue_1_day',
                    'ad_revenue_7_day', 'ad_revenue_14_day', 'ad_revenue_30_day']
    search_fields = ['brand__name', 'date']


@admin.register(StatePopulation)
class StatePopulationAdmin(TenantDBForModelAdmin):
    list_display = ('state_postal_code', 'state', 'est')


@admin.register(SKUVaultPrimeTrack)
class SKUVaultPrimeTrackAdmin(TenantDBForModelAdmin):
    paginator = LargeTablePagination
    list_display = ['client', 'channel',
                    'channel_sale_id', 'source', 'status', 'created']
    search_fields = ['channel_sale_id']
    list_filter = ['channel', 'status', 'client', 'source']


@admin.register(AppEagleProfile)
class AppEagleProfileAdmin(TenantDBForModelAdmin):
    paginator = LargeTablePagination
    list_display = ['client', 'profile_id',
                    'profile_name', 'profile_id_link', 'created']
    search_fields = ['profile_id']
    list_filter = ['client']


@admin.register(InformedMarketplace)
class InformedMarketplaceAdmin(TenantDBForModelAdmin):
    paginator = LargeTablePagination
    list_display = ['client', 'channel',
                    'informed_co_marketplace_id', 'created']
    search_fields = ['informed_co_marketplace_id']
    list_filter = ['channel', 'client']
    ordering = ['created']


@admin.register(User)
class UserAdmin(TenantDBForModelAdmin):
    paginator = LargeTablePagination
    list_display = ['user_id', 'email', 'username', 'first_name', 'last_name']
    search_fields = ['user_id', 'email', 'username']


@admin.register(UserObjectFavorite)
class UserObjectFavoriteAdmin(TenantDBForModelAdmin):
    paginator = LargeTablePagination
    list_display = ['client', 'object_id', 'user', 'status', 'modified']
    search_fields = ['object_id']
    list_filter = ['client']


@admin.register(Alert)
class AlertAdmin(TenantDBForModelAdmin):
    paginator = LargeTablePagination
    list_display = ['client', 'name', 'custom_view', 'refresh_rate', 'throttling_alert', 'throttling_period',
                    'last_refresh_rate', 'last_throttling_period', 'creator', 'created', 'modified']
    search_fields = ['name']
    list_filter = ['client']
    actions = ['send_notice']

    def send_notice(self, request, queryset):
        for item in queryset:
            logger.info(
                f"[{self.__class__.__name__}][send_notice][{item.client_id}][{item.pk}] Begin ...")
            AlertDeliveryChannel(
                item.client_id, item.pk).on_validate().on_process().on_complete()

    send_notice.short_description = "Send notice SMS/Email/Push"


@admin.register(AlertDigest)
class AlertDigestAdmin(TenantDBForModelAdmin):
    paginator = LargeTablePagination
    list_display = ['name', 'client', 'alert',
                    'is_digest', 'created', 'modified']
    search_fields = ['name']
    list_filter = ['client']


@admin.register(AlertItem)
class AlertItemAdmin(TenantDBForModelAdmin):
    paginator = LargeTablePagination
    list_display = ['client', 'alert_digest',
                    'sale_item_id', 'created', 'modified']
    search_fields = ['sale_item_id', 'alert_digest__id']
    list_filter = ['client']


@admin.register(AlertDelivery)
class AlertDeliveryAdmin(TenantDBForModelAdmin):
    paginator = LargeTablePagination
    list_display = ['client', 'alert_digest',
                    'via', 'status', 'created', 'modified']
    search_fields = ['sale_item_id']
    list_filter = ['client', 'via', 'status']


@admin.register(ShippingInvoice)
class ShippingInvoiceAdmin(TenantDBForModelAdmin):
    paginator = LargeTablePagination
    list_display = ['id', 'client', 'invoice_number', 'invoice_date',
                    'payer_account_id', 'payee_account_id', 'created', 'modified']
    search_fields = ['invoice_number', 'payer_account_id', 'payee_account_id']
    list_filter = ['client']


@admin.register(TopProductChannelPerformance)
class TopProductChannelPerformanceAdmin(TenantDBForModelAdmin):
    paginator = LargeTablePagination
    list_display = ['id', 'client', 'channel',
                    'sku', 'units_sold', 'created', 'modified']
    search_fields = ['sku']
    list_filter = ['client', 'channel']


@admin.register(DashboardConfig)
class DashboardConfigAdmin(TenantDBForModelAdmin):
    list_display = ['id', 'key', 'value', 'created', 'modified']
    search_fields = ['value']


@admin.register(WidgetConfig)
class WidgetConfigAdmin(TenantDBForModelAdmin):
    list_display = ['id', 'dashboard', 'key', 'value',
                    'position', 'proportion', 'created', 'modified']
    search_fields = ['value']
    list_filter = ['dashboard']
    ordering = ['position', 'dashboard']
    actions = ['reset_all_config_widget_clients',
               'reset_all_config_widget_clients_queue']

    @staticmethod
    def sync_client_dashboard_widgets(using_queue: bool = False, override: bool = False, **kwargs):
        client_ids = ClientPortal.objects.tenant_db_for(
            DEFAULT_DB_ALIAS).values_list('pk', flat=True)
        data = []
        for client_id in client_ids:
            if using_queue:
                data.append(
                    dict(
                        client_id=client_id,
                        name="sync_init_client_dashboard_widget",
                        job_name="app.financial.jobs.settings.handler_init_client_dashboard_widget",
                        module="app.financial.jobs.settings",
                        method="handler_init_client_dashboard_widget",
                        meta=dict(client_ids=[client_id],
                                  override=override, **kwargs)
                    )
                )
                continue
            handler_init_client_dashboard_widget(
                client_ids=client_ids, override=override)
        register_list(SYNC_DATA_SOURCE_CATEGORY, data)

    def delete_model(self, request, obj):
        super().delete_model(request, obj)
        # trigger sync to ds
        self.sync_client_dashboard_widgets()

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        self.sync_client_dashboard_widgets()

    def reset_all_config_widget_clients(self, request, queryset):
        errors = []
        try:
            self.sync_client_dashboard_widgets(
                using_queue=False, override=True)
        except Exception as ex:
            errors.append(str(ex))

        if errors:
            msg = f" , ".join(errors)
            messages.error(request, msg)
        else:
            messages.success(
                request, f"{queryset.count()} sync to all clients successfully")

    def reset_all_config_widget_clients_queue(self, request, queryset):
        errors = []
        try:
            self.sync_client_dashboard_widgets(using_queue=True, override=True)
        except Exception as ex:
            errors.append(str(ex))

        if errors:
            msg = f" , ".join(errors)
            messages.error(request, msg)
        else:
            messages.success(
                request, f"{queryset.count()} sync to all clients successfully")

    reset_all_config_widget_clients.short_description = "Reset All Config Widget Clients"
    reset_all_config_widget_clients_queue.short_description = "Reset All Config Widget Clients Queue"


@admin.register(ClientDashboardWidget)
class ClientDashboardWidgetAdmin(TenantDBForModelAdmin):
    list_display = ['id', 'client', 'widget', 'enabled', 'position', 'position_default', 'proportion', 'created',
                    'modified']
    list_filter = ['client', 'widget', 'proportion']


@admin.register(ClientCartRoverSetting)
class ClientCartRoverSettingAdmin(TenantDBForModelAdmin):
    list_display = ['id', 'client', 'merchant_name', 'api_user',
                    'api_key', 'enabled', 'synced', 'created', 'modified']
    list_filter = ['client', 'merchant_name']
    ordering = ('-modified', '-created')


@admin.register(DivisionManage)
class DivisionManageAdmin(TenantDBForModelAdmin):
    list_display = ['id', 'category', 'key', 'name', 'created', 'modified']
    list_filter = ['category', 'key']
    actions = ["sync_divisions_to_all_clients"]

    def sync_divisions_to_all_clients(self, request, queryset):
        errors = []
        client_ids = DivisionClientUserWidget.objects.tenant_db_for(DEFAULT_DB_ALIAS) \
            .filter(active=True) \
            .values_list('client_id', flat=True).distinct()
        #
        division_client_widgets = []
        for client_id in client_ids:
            for division in queryset.order_by("-created"):
                try:
                    DivisionClientUserWidget.objects.tenant_db_for(DEFAULT_DB_ALIAS).get(
                        client_id=client_id,
                        category=division.category,
                        key=division.key
                    )
                except DivisionClientUserWidget.DoesNotExist:
                    obj = DivisionClientUserWidget(
                        client_id=client_id,
                        category=division.category,
                        key=division.key,
                        name=division.name
                    )
                    division_client_widgets.append(obj)
                except Exception as ex:
                    errors.append(
                        f"{client_id}: {division.category} {division.key} {ex}")
        if division_client_widgets:
            DivisionClientUserWidget.objects.tenant_db_for(DEFAULT_DB_ALIAS).bulk_create(division_client_widgets,
                                                                                         ignore_conflicts=True)

        if errors:
            msg = f" , ".join(errors)
            messages.error(request, msg)
        else:
            messages.success(
                request, f"{queryset.count()} sync to all clients successfully")


@admin.register(DivisionClientUserWidget)
class DivisionClientUserWidgetAdmin(TenantDBForModelAdmin):
    list_display = ['id', 'client', 'category', 'key',
                    'name', 'enabled', 'created', 'modified']
    list_filter = ['client', 'category', 'enabled']


@admin.register(TopClientASINs)
class TopClientASINsAdmin(TenantDBForModelAdmin):
    list_display = ['id', 'client', 'channel', 'parent_asin',
                    'child_asin', 'segment', 'created', 'modified']
    list_filter = ['client', 'channel', 'segment']
    search_fields = ['parent_asin', 'child_asin']
