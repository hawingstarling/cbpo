import logging
from datetime import timedelta

import pytz
from django.conf import settings
from django.db.models import Sum, Q
from django.utils import timezone

from app.financial.models import Channel, SaleItem, SaleStatus, TopProductChannelPerformance
from app.financial.services.utils.helper import bulk_sync
from app.financial.variable.sale_status_static_variable import SALE_UNSHIPPED_STATUS, SALE_PENDING_STATUS, \
    SALE_PARTIALLY_REFUNDED_STATUS, SALE_SHIPPED_STATUS

logger = logging.getLogger(__name__)


class TopProductPerformanceService:
    ds_tz_calculate = settings.DS_TZ_CALCULATE

    def __init__(self, client_id, marketplace, **kwargs):
        self.client_id = client_id
        self.marketplace = marketplace
        self.channel = Channel.objects.tenant_db_for(self.client_id).get(name=marketplace)
        self.date_now = timezone.now()
        self.sale_status_accept_generate = [SALE_PENDING_STATUS, SALE_UNSHIPPED_STATUS, SALE_SHIPPED_STATUS,
                                            SALE_PARTIALLY_REFUNDED_STATUS]
        self.number_top_records = 5
        self.number_filter_days = 30
        self.kwargs = kwargs

    @property
    def hour_dt_tz_vs_utc(self):
        if self.ds_tz_calculate is None:
            return 0
        try:
            tz = pytz.timezone(self.ds_tz_calculate)
            dt_tz = self.date_now.astimezone(tz)
            # get hour by timezone set for query
            tz_info = dt_tz.strftime('%z')
            hour = int(tz_info.replace('0', ''))
            # database default UTC
            # need calculate hour (ds_tz_calculate) compare vs UTC
            # UTC vs UTC+7 => hour = -7
            # UTC vs UTC-7 => hour = 7
            # apply : dt = dt + timedelta(hours=hour)
            # E.g dt = 2021-01-01 00:00:00, ds_tz_calculate = America/Dawson -> dt = 2021-01-01 07:00:00
            hour *= -1
        except Exception as ex:
            logger.error(f"[{self.__class__.__name__}]: {ex}")
            hour = 0
        return hour

    def convert_dt_to_tz(self, dt: any, strftime: bool = True, fm_as_time: str = '%Y-%m-%d %H:%M:%S'):
        dt = dt + timedelta(hours=self.hour_dt_tz_vs_utc)
        if strftime:
            dt = dt.strftime(fm_as_time)
        return dt

    def get_date_calculate_filter(self):
        fd = self.date_now - timedelta(days=self.number_filter_days)
        fd = self.convert_dt_to_tz(fd.replace(hour=0, minute=0, second=0, microsecond=0), strftime=False)
        #
        td = self.date_now.replace(hour=23, minute=59, second=59, microsecond=999)
        td = self.convert_dt_to_tz(td, strftime=False)

        return fd, td

    @property
    def sale_status_accept_ids(self):
        ids = SaleStatus.objects.tenant_db_for(self.client_id).filter(
            value__in=self.sale_status_accept_generate).values_list('pk', flat=True)
        return list(ids)

    def process(self):
        logger.info(
            f"[{self.__class__.__name__}][{self.marketplace}][process] Begin calculation Top Product Performance")
        fd, td = self.get_date_calculate_filter()
        #
        queryset = SaleItem.objects.tenant_db_for(self.client_id) \
            .filter(sale__channel_id=self.channel.pk,
                    sale_date__gte=fd, sale_date__lte=td,
                    sale_status__in=self.sale_status_accept_ids) \
            .values('sku') \
            .annotate(units_sold=Sum('quantity')) \
            .order_by('-units_sold')
        list_sku = list(queryset.values_list('sku', flat=True)[:self.number_top_records])
        top_product_queryset = TopProductChannelPerformance.objects.tenant_db_for(self.client_id) \
            .filter(client_id=self.client_id, sku__in=list_sku)
        logger.info(f"[{self.__class__.__name__}][{self.marketplace}][process] SKU {list_sku}")
        if top_product_queryset.count() == self.number_top_records:
            logger.info(f"[{self.__class__.__name__}][{self.marketplace}][process] list SKU same with table tracking")
            return
        objs = []
        for item in queryset[:self.number_top_records]:
            obj = TopProductChannelPerformance(client_id=self.client_id, channel_id=self.channel.pk, sku=item["sku"],
                                               units_sold=item["units_sold"])
            objs.append(obj)
        if not objs:
            logger.info(f"[{self.__class__.__name__}][{self.marketplace}][process] not found top products")
            return
        logger.info(f"[{self.__class__.__name__}][{self.marketplace}][process] Begin bulk sync top products objs")
        bulk_sync(
            client_id=self.client_id,
            new_models=objs,
            filters=Q(client_id=self.client_id, channel_id=self.channel.pk),
            key_fields=['client', 'channel', 'sku'],
            fields=['client', 'channel', 'sku', 'units_sold']
        )

    def complete(self):
        logger.info(f"[{self.__class__.__name__}][{self.marketplace}][process] "
                    f"completed calculation Top Product Performance")
