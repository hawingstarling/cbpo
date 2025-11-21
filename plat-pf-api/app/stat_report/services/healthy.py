import datetime
import logging
import pytz
from django.conf import settings
from django.db import DEFAULT_DB_ALIAS
from django.db.models import Q
from django.utils import timezone
from django.db.models.expressions import Case, When
from django.db.models.aggregates import Count
from django.db.models.fields import FloatField
from app.es.helper import get_es_health
from app.es.variables.template import INDEX_TEMPLATE_CONFIGS
from app.financial.import_template.custom_report import SaleItemCustomReport
from app.financial.import_template.sale_item_bulk_edit import SaleItemBulkEdit
from app.financial.import_template.sale_item_bulk_sync import SaleItemBulkSync
from app.financial.models import SaleItem, Channel, ClientPortal, ClientSettings, DataFlattenTrack
from plat_import_lib_api.models import Health as LibHealth
from app.financial.services.api_data_source_centre import ApiCentreContainer
from app.financial.variable.data_flatten_variable import FLATTEN_ES_SOURCE, DATA_FLATTEN_TYPE_ANALYSIS_LIST
from app.financial.variable.job_status import ERROR, SUCCESS
from app.shopify_partner.models import ShopifyPartnerOauthClientRegister
from app.stat_report.models import OrgClientHealth

logger = logging.getLogger(__name__)


class Healthy:
    def __init__(self, client_id: str, service: str = None, **kwargs):
        self.service = service
        self.kwargs = kwargs
        self.client_id = client_id
        self.client = ClientPortal.objects.tenant_db_for(client_id).get(pk=client_id)
        self.client_config = self.__get_client_config(client_id)
        # Time calculations
        self.tz = pytz.timezone(settings.DS_TZ_CALCULATE)
        self.now = datetime.datetime.now(tz=self.tz)
        self.now_pytz = self.now.astimezone(tz=pytz.utc)
        # Arrays inserts, updates
        self.inserts = []
        self.updates = []

    def init_obj_client_healthy_ins(self, client: ClientPortal, service_name: str, **kwargs):
        try:
            obj = OrgClientHealth.objects.tenant_db_for(DEFAULT_DB_ALIAS).get(organization=client.organization,
                                                                              client=client, service_name=service_name)
            for k, v in kwargs.items():
                setattr(obj, k, v)
            obj.modified = timezone.now()
            self.updates.append(obj)
        except Exception as ex:
            # logger.error(f"[{client.id}][{service_name}] unexpect {ex}")
            self.inserts.append(
                OrgClientHealth(organization=client.organization, client=client, service_name=service_name, **kwargs))

    def bulk_org_client_healthy_models(self):
        if self.inserts:
            OrgClientHealth.objects.tenant_db_for(DEFAULT_DB_ALIAS).bulk_create(self.inserts, ignore_conflicts=True)

        if self.updates:
            OrgClientHealth.objects.tenant_db_for(DEFAULT_DB_ALIAS) \
                .bulk_update(self.updates, fields=["is_enabled", "is_healthy", "message", "modified"])

    @staticmethod
    def __get_client_config(client_id: str):
        setting, _ = ClientSettings.objects.tenant_db_for(client_id).get_or_create(client_id=client_id)
        is_shopify_connect = ShopifyPartnerOauthClientRegister.objects.tenant_db_for(client_id) \
            .filter(client_id=client_id, enabled=True).exists()
        vals = {
            'health_hours_check_ac': setting.health_hours_check_ac,
            'amazon': setting.ac_spapi_enabled,
            'shopify': is_shopify_connect
        }
        logger.info(f"[__get_client_config][{client_id}] configs = {vals}")
        return vals

    @staticmethod
    def __get_name_server_channel(channel: Channel):
        val = None
        if 'amazon' in channel.name.lower():
            val = 'amazon'
        elif 'shopify' in channel.name.lower():
            val = 'shopify'
        else:
            pass
        return val

    def check_ac(self):
        logger.info(f"[check_ac] hour UTC at now {self.now} timezone {self.now.tzname()} , "
                    f"hour convert to UTC for filter DB now = {self.now_pytz} timezone {self.now_pytz.tzname()}")
        #
        hours_delta = self.client_config['health_hours_check_ac']
        #
        if 0 <= self.now.hour < 6 or 22 <= self.now.hour < 24:
            hours_delta *= 4
        sale_date_gte = self.now_pytz - datetime.timedelta(hours=hours_delta)

        messages = []
        is_healthy = True
        #
        channels = Channel.objects.tenant_db_for(self.client_id).filter(is_pull_data=True).order_by('name')
        if channels.count() == 0:
            messages.append(f"OK")
        else:
            for channel in channels:
                logger.info(f"[{self.client_id}][check_ac] Begin check service channel {channel.name} ...")
                msg = "OK"
                if not self.client_config.get(self.__get_name_server_channel(channel), False):
                    messages.append(f"{channel.name}: {msg}")
                    continue
                try:
                    sale_item = SaleItem.objects.tenant_db_for(self.client_id) \
                        .filter(sale__channel=channel, sale_date__gte=sale_date_gte)
                    if not sale_item.exists():
                        msg = f"ERROR: There are no new sale items in the last {hours_delta} hours"
                        is_healthy = False
                except Exception as err:
                    msg = f"unexpected {err}"
                    is_healthy = False
                messages.append(f"{channel.name}: {msg}")
        kwargs = dict(
            service_name="ac",
            is_enabled=True,
            is_healthy=is_healthy,
            message=messages
        )
        self.init_obj_client_healthy_ins(self.client, **kwargs)
        #
        self.bulk_org_client_healthy_models()

    def check_ds(self):
        is_healthy = True
        message = "OK"
        try:
            api_centre = ApiCentreContainer.data_source_central()
            api_centre.ping_service_proxy()
        except Exception as err:
            is_healthy = False
            message = f"{err}"
        #
        kwargs = dict(
            service_name="ds",
            is_enabled=True,
            is_healthy=is_healthy,
            message=[message]
        )
        self.init_obj_client_healthy_ins(self.client, **kwargs)
        #
        self.bulk_org_client_healthy_models()

    def check_dc(self):
        is_enabled = True
        is_healthy = True
        messages = []

        logger.info(f"[check_ac] hour at now {self.now} timezone {self.now.tzname()}")
        fd = self.now.replace(hour=0, minute=0, second=0, microsecond=000000).astimezone(tz=pytz.utc)
        td = self.now.replace(hour=23, minute=59, second=59, microsecond=999999).astimezone(tz=pytz.utc)
        #
        logger.info(f"[check_ac] hour convert to UTC for filter DB today = {fd} - {td}")
        #
        configs = self.__get_client_config(self.client_id)
        channels = Channel.objects.tenant_db_for(self.client_id).filter(is_pull_data=True).order_by('name')
        if channels.count() == 0:
            messages.append("OK")
        else:
            for channel in channels:
                logger.info(f"[{self.client_id}][check_dc] Begin check service channel {channel.name} ...")
                msg = "OK"
                if not configs.get(self.__get_name_server_channel(channel), False):
                    messages.append(f"{channel.name}: {msg}")
                    continue
                try:
                    result = SaleItem.objects.tenant_db_for(self.client_id) \
                        .filter(sale__channel=channel, sale_date__gte=fd, sale_date__lte=td) \
                        .aggregate(
                        total=Count('pk'),
                        not_null_brand=Count('brand_id'),
                        not_null_brand_percent=Case(
                            When(total=0, then=100),
                            default=Count('brand_id') * 100 / Count('pk'),
                            output_field=FloatField()
                        )
                    )
                    not_null_brand_percent = result['not_null_brand_percent']
                    if not_null_brand_percent < 80:
                        null_brand_percent = 100 - not_null_brand_percent
                        null_brand = result['total'] - result['not_null_brand']
                        if not_null_brand_percent >= 50:
                            msg = f"WARNING: {null_brand_percent}% ({null_brand} items) brand null today"
                        else:
                            msg = f"ERROR: {null_brand_percent}% ({null_brand} items) brand null today"
                        is_healthy = False
                except Exception as err:
                    msg = f"unexpected {err}"
                    is_healthy = False
                messages.append(f"{channel.name}: {msg}")

        kwargs = dict(
            service_name="dc",
            is_enabled=is_enabled,
            is_healthy=is_healthy,
            message=messages
        )
        self.init_obj_client_healthy_ins(self.client, **kwargs)

        self.bulk_org_client_healthy_models()

    def handler_org_client_lib_import_module_healthy(self, service_name, is_enabled, cond):
        messages = []
        cond_ws = cond & Q(client_ids__contains=[self.client_id])
        qs = LibHealth.objects.filter(cond_ws)
        is_healthy = not qs.exists()
        for obj in qs:
            messages.append(f"{obj.module_name}: {obj.message}")

        if not messages:
            messages.append("OK")

        kwargs = dict(
            service_name=service_name,
            is_enabled=is_enabled,
            is_healthy=is_healthy,
            message=messages
        )
        self.init_obj_client_healthy_ins(self.client, **kwargs)
        self.bulk_org_client_healthy_models()

    def check_import(self):
        is_enabled = True
        cond = ~Q(module_name__in=[SaleItemBulkSync.__NAME__, SaleItemBulkEdit.__NAME__, SaleItemCustomReport.__NAME__]) \
               & Q(is_healthy=False)
        self.handler_org_client_lib_import_module_healthy(service_name="import", is_enabled=is_enabled, cond=cond)

    def check_bulk(self):
        is_enabled = True
        cond = Q(module_name__in=[SaleItemBulkSync.__NAME__, SaleItemBulkEdit.__NAME__], is_healthy=False)
        self.handler_org_client_lib_import_module_healthy(service_name="bulk", is_enabled=is_enabled, cond=cond)

    def check_export(self):
        is_enabled = True
        cond = Q(module_name__in=[SaleItemCustomReport.__NAME__], is_healthy=False)
        self.handler_org_client_lib_import_module_healthy(service_name="export", is_enabled=is_enabled, cond=cond)

    def check_es(self):
        is_enabled = True
        is_healthy = True
        messages = []
        #
        flattens_updates = []
        queryset = DataFlattenTrack.objects.tenant_db_for(self.client_id) \
            .filter(source=FLATTEN_ES_SOURCE, type__in=DATA_FLATTEN_TYPE_ANALYSIS_LIST, status=ERROR)
        if queryset.count() > 0:
            #
            for flatten_track in queryset.iterator():
                try:
                    assert flatten_track.data_source_es_id is not None, \
                        f"Index source type {flatten_track.type.lower()} not generated"
                    index = INDEX_TEMPLATE_CONFIGS[flatten_track.type].format(
                        client_id=self.client_id.replace('-', '_'))
                    status = get_es_health(self.client_id, index)
                    assert status is True, f"Index source type {(flatten_track.type.replace('_', ' ')).title()} not ready"
                    flatten_track.status = SUCCESS
                    flatten_track.modified = timezone.now()
                    flatten_track.log = None
                    flattens_updates.append(flatten_track)
                except Exception as ex:
                    messages.append(str(ex))
                    is_healthy = False

        if not messages:
            messages.append("OK")

        kwargs = dict(
            service_name="es",
            is_enabled=is_enabled,
            is_healthy=is_healthy,
            message=messages
        )
        self.init_obj_client_healthy_ins(self.client, **kwargs)
        if flattens_updates:
            DataFlattenTrack.objects.tenant_db_for(self.client_id).bulk_update(flattens_updates,
                                                                               fields=["status", "log", "modified"])
        self.bulk_org_client_healthy_models()

    def process(self):
        services_status = {
            "ac": self.check_ac,
            "dc": self.check_dc,
            "ds": self.check_ds,
            "es": self.check_es,
            "import": self.check_import,
            "bulk": self.check_bulk,
            "export": self.check_export
        }
        if self.service:
            assert self.service in services_status, f"Service must in {services_status.keys()}"
            services_status = {self.service: services_status[self.service]}

        for service_name in services_status.keys():
            logger.info(f"[{self.__class__.__name__}] Begin check service status {service_name} service ...")
            services_status[service_name]()
