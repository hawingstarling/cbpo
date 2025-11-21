import logging
from datetime import timedelta
from django.utils import timezone

from app.core.variable.marketplace import CHANNEL_DEFAULT
from app.financial.models import FedExShipment, Sale, SaleItem
from app.financial.variable.shipping_cost_source import AMZ_FBA_FULFILLMENT_FEE_SOURCE_KEY, \
    AMZ_POSTAGE_BILLING_SOURCE_KEY, BRAND_SETTING_SOURCE_KEY

from app.financial.services.fedex_shipment.config import FEDEX_SHIPMENT_ONE, FEDEX_SHIPMENT_PENDING, \
    FEDEX_SHIPMENT_MULTI, REOPEN_BY_EXTENSION, FEDEX_SHIPMENT_NONE, SCHEDULER_HOURS_REOPEN_BY_EXTENSION
from .config import REOPEN_BY_SALE_STATUS, REOPEN_BY_AMZ_EVENT
from app.financial.variable.sale_status_static_variable import SALE_CANCELLED_STATUS, SALE_SHIPPED_STATUS, \
    SALE_PENDING_STATUS
from django.db.models import Min, Q

from ...variable.brand_setting import EVALUATED_SHIPPING_COST_ACCURACY_ACCEPT_CALCULATE
from ...variable.fulfillment_type import FULFILLMENT_MFN_GROUP

logger = logging.getLogger(__name__)


class FedExShipmentManage:

    def __init__(self, client_id: str, marketplace: str = CHANNEL_DEFAULT, *args, **kwargs):
        self.client_id = client_id
        self.marketplace = marketplace
        self.shipment_date_filter = None
        self.arg = args
        self.kwargs = kwargs
        self.time_now = timezone.now()

    @property
    def obj_ids(self):
        return self.kwargs.get('obj_ids', [])

    @property
    def reopen_action(self):
        return self.kwargs.get('reopen_action', REOPEN_BY_EXTENSION)

    def _build_queryset(self):
        queryset = None
        if self.reopen_action == REOPEN_BY_AMZ_EVENT:
            # priority low -> high
            # 1. BrandSetting
            # 2. FedEx
            # 3. AMZ
            # Case handler : when 3 override 2 , change FedEx Shipping to Pending for mapping other item
            queryset = SaleItem.objects.tenant_db_for(self.client_id).filter(pk__in=self.obj_ids,
                                                                             shipping_cost_source__in=[
                                                                                 AMZ_POSTAGE_BILLING_SOURCE_KEY,
                                                                                 AMZ_FBA_FULFILLMENT_FEE_SOURCE_KEY])
        elif self.reopen_action == REOPEN_BY_SALE_STATUS:
            queryset = Sale.objects.tenant_db_for(self.client_id).filter(pk__in=self.obj_ids,
                                                                         sale_status__value__in=[SALE_CANCELLED_STATUS,
                                                                                                 SALE_SHIPPED_STATUS])
        elif self.reopen_action == REOPEN_BY_EXTENSION:
            modified__gte = self.time_now - timedelta(hours=(2 * SCHEDULER_HOURS_REOPEN_BY_EXTENSION))
            cond = Q(
                fulfillment_type__name__in=FULFILLMENT_MFN_GROUP,
                ship_date__isnull=False,
                modified__gte=modified__gte,
                sale__customer_name__isnull=False,
                tracking_fedex_id__isnull=False) \
                   & ~Q(sale_status__value__in=[SALE_PENDING_STATUS, SALE_CANCELLED_STATUS]) \
                   & (Q(shipping_cost_source__isnull=True) | Q(shipping_cost_source=BRAND_SETTING_SOURCE_KEY)) \
                   & (Q(shipping_cost_accuracy__isnull=True) |
                      Q(shipping_cost_accuracy__lte=EVALUATED_SHIPPING_COST_ACCURACY_ACCEPT_CALCULATE))
            queryset = SaleItem.objects.tenant_db_for(self.client_id).filter(cond)
        else:
            pass
        return queryset

    @property
    def get_obj_ids_by_action(self):
        ids = []
        queryset = self._build_queryset()
        #
        if self.reopen_action == REOPEN_BY_AMZ_EVENT:
            # get date of sale order for filter shipment date to reopen
            self.shipment_date_filter = queryset.filter(sale__date__isnull=False) \
                .aggregate(value=Min('sale__date'))['value']
            ids = list(queryset.values_list('sale_id', flat=True).distinct())
        elif self.reopen_action == REOPEN_BY_SALE_STATUS:
            # get date of sale order for filter shipment date to reopen
            self.shipment_date_filter = queryset.filter(date__isnull=False).aggregate(value=Min('date'))['value']
            ids = list(queryset.values_list('pk', flat=True))
        elif self.reopen_action == REOPEN_BY_EXTENSION:
            ids = list(queryset.values_list('tracking_fedex_id', flat=True).distinct())
        else:
            pass
        return ids

    @property
    def filter_status(self):
        if self.reopen_action == REOPEN_BY_SALE_STATUS:
            return [FEDEX_SHIPMENT_MULTI]
        elif self.reopen_action == REOPEN_BY_AMZ_EVENT:
            return [FEDEX_SHIPMENT_ONE, FEDEX_SHIPMENT_MULTI]
        elif self.reopen_action == REOPEN_BY_EXTENSION:
            return [FEDEX_SHIPMENT_NONE, FEDEX_SHIPMENT_MULTI]
        else:
            return []

    def reopen_by_sale_event(self, sale_ids: [int]):
        for sale_id in sale_ids:
            queryset = FedExShipment.objects.tenant_db_for(self.client_id) \
                .filter(client_id=self.client_id, matched_sales__contains=[sale_id], status__in=self.filter_status)
            #
            if self.shipment_date_filter is not None:
                queryset = queryset.filter(shipment_date__gte=(self.shipment_date_filter.date() - timedelta(days=2)))
            #
            count = queryset.count()
            if count > 0:
                logger.info(f"[{self.client_id}][{self.marketplace}][{self.reopen_action}][{sale_id}] "
                            f"Reopen {queryset.count()} items")
                queryset.update(status=FEDEX_SHIPMENT_PENDING, matched_sales=[], matched_channel_sale_ids=[],
                                matched_time=None)

    def process(self):
        logger.info(
            f"[{self.client_id}][{self.marketplace}][{self.reopen_action}][process] BEGIN ...")
        obj_ids = self.get_obj_ids_by_action
        if len(obj_ids) == 0:
            logger.error(
                f"[{self.client_id}][{self.marketplace}][{self.reopen_action}][process] not found items")
            return
        #
        trigger_action = {
            REOPEN_BY_SALE_STATUS: "reopen_by_sale_event",
            REOPEN_BY_AMZ_EVENT: "reopen_by_sale_event",
            REOPEN_BY_EXTENSION: "reopen_by_extension"
        }
        #
        try:
            getattr(locals()['self'], trigger_action[self.reopen_action])(obj_ids)
        except Exception as ex:
            logger.error(f"[{self.__class__.__name__}][process][{self.reopen_action}] {ex}")

    def reopen_by_extension(self, obj_ids: list):
        logger.info(
            f"[{self.client_id}][{self.marketplace}][{self.reopen_action}][reopen_item_tracking_ids] process obj_ids = {obj_ids}")
        FedExShipment.objects.tenant_db_for(self.client_id) \
            .filter(client_id=self.client_id, tracking_id__in=obj_ids, status__in=self.filter_status) \
            .update(status=FEDEX_SHIPMENT_PENDING, matched_sales=[], matched_channel_sale_ids=[], matched_time=None)
