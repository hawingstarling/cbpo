from datetime import datetime, timezone, timedelta
from typing import List
from auditlog.models import LogEntry
from django.db.models import Q, Sum
from app.core.logger import logger
from app.financial.models import SaleItem, BrandSetting
from app.core.services.audit_logs.base import AuditLogCoreManager
from app.core.services.audit_logs.config import SYSTEM_BRAND_SETTINGS
from app.financial.services.brand_settings.ship_cost_calculation_adapter import ShipCostCalculationAdapter
from app.financial.services.shipping_cost.abstract import ShippingCostService
from app.financial.utils.shipping_cost_helper import separate_shipping_cost_by_accuracy
from app.financial.variable.fulfillment_type import (FULFILLMENT_FBA, FULFILLMENT_MFN_DS, FULFILLMENT_MFN_RA,
                                                     FULFILLMENT_MFN_PRIME)
from app.financial.variable.brand_setting import EVALUATED_SHIPPING_COST_ACCURACY_SPECIFIC_BRAND, \
    EVALUATED_SHIPPING_COST_ACCURACY_SPECIFIC_BRAND_MFN_DS, EVALUATED_SHIPPING_COST_ACCURACY_DEFAULT_BRAND, \
    EVALUATED_SHIPPING_COST_ACCURACY_ACCEPT_CALCULATE, EVALUATED_SHIPPING_COST_ACCURACY_SPECIFIC_BRAND_MFN_PRIME
from app.financial.variable.job_status import BULK_SYNC_LIVE_FEED_JOB

from app.financial.variable.shipping_cost_source import BRAND_SETTING_SOURCE_KEY


class ShippingCostFromBrandSettings(ShippingCostService):

    @property
    def select_related(self) -> [str]:
        return ['fulfillment_type']

    @property
    def order_query(self) -> [str]:
        return ['client', 'sale__channel', 'modified']

    @property
    def _pattern_conditions(self) -> List[Q]:
        return [
            Q(fulfillment_type__isnull=False, brand__isnull=False),
            Q(
                Q(shipping_cost_accuracy__isnull=True) | Q(shipping_cost_accuracy__lte=self._accuracy_base())
            )
        ]

    def _accuracy_base(self) -> int:
        return EVALUATED_SHIPPING_COST_ACCURACY_ACCEPT_CALCULATE

    def _exec_sub_mission(self):
        channel_ids = set()
        brand_ids = set()
        sale_item_ids = []
        for sale_item in self._sub_update_mission:
            brand_ids.add(sale_item.brand_id)
            channel_ids.add(sale_item.sale.channel.id)
            sale_item_ids.append(sale_item.id)

        cond = Q(client_id=self._client_id_only, brand__id__in=brand_ids, channel__id__in=channel_ids)

        if self.action != BULK_SYNC_LIVE_FEED_JOB:
            cond &= Q(auto_update_sales=True)

        brand_setting_query_set = BrandSetting.objects.tenant_db_for(self._client_id_only).filter(cond)
        #
        cond_null = Q(client_id=self._client_id_only, brand__isnull=True, channel__id__in=channel_ids)

        if self.action != BULK_SYNC_LIVE_FEED_JOB:
            cond_null &= Q(auto_update_sales=True)
        brand_setting_null_query_set = BrandSetting.objects.tenant_db_for(self._client_id_only).filter(cond_null)
        #
        sale_stats = SaleItem.objects.tenant_db_for(self._client_id_only).filter(id__in=sale_item_ids).values(
            "sale_id", "brand_id").annotate(
            sum_sku_quantity=Sum('quantity'))

        self._calculate_shipping_cost(brand_setting_query_set, brand_setting_null_query_set, sale_stats)

    def _calculate_shipping_cost(self, brand_setting_query_set, brand_setting_null_query_set, sale_stats):
        for idx, sale_item in enumerate(self._sub_update_mission):
            ship_cost, evaluated_accuracy = self.__calc_sale_item_ship_cost(sale_item, brand_setting_query_set,
                                                                            brand_setting_null_query_set, sale_stats)
            if ship_cost == sale_item.shipping_cost and evaluated_accuracy == sale_item.shipping_cost_accuracy:
                continue
            if ship_cost is not None:
                sale_item, changes = separate_shipping_cost_by_accuracy(self._client_id_only, sale_item, ship_cost,
                                                                        evaluated_accuracy, BRAND_SETTING_SOURCE_KEY)
                if changes:
                    sale_item.dirty = True
                    sale_item.financial_dirty = True
                    self._being_update_queue.append(sale_item)
                    log_entry = AuditLogCoreManager(client_id=self._client_id_only).set_actor_name(
                        SYSTEM_BRAND_SETTINGS) \
                        .create_log_entry_from_compared_changes(sale_item, changes, action=LogEntry.Action.UPDATE)
                    self._being_update_audit_log_queue.append(log_entry)

            if ((idx + 1) % self._size_bulk_update == 0) and len(self._being_update_queue):
                self._bulk_update()
                self._being_update_queue.clear()
                self._being_update_audit_log_queue.clear()

        if len(self._being_update_queue):
            self._bulk_update()

    def __calc_sale_item_ship_cost(self, sale_item, brand_setting_query_set, brand_setting_null_query_set, sale_stats):
        """
        :rtype: shipping_cost, evaluated_accuracy
        """
        brand_setting, accuracy = self._get_brand_settings(sale_item, brand_setting_query_set,
                                                           brand_setting_null_query_set)
        shipping_cost = None
        if brand_setting is None:
            return shipping_cost, accuracy
        try:
            if sale_item.fulfillment_type.name == FULFILLMENT_FBA:
                # FBA
                shipping_cost = ShipCostCalculationAdapter.calc_for_fba(brand_setting, sale_item)
            elif sale_item.fulfillment_type.name == FULFILLMENT_MFN_RA:
                # MFN Rapid Access
                shipping_cost = ShipCostCalculationAdapter.calc_for_mfn_for_rapid_access(brand_setting, sale_item,
                                                                                         sale_stats)
            elif sale_item.fulfillment_type.name == FULFILLMENT_MFN_DS:
                # MFN Drop Ship
                shipping_cost = ShipCostCalculationAdapter.calc_for_mfn_for_drop_ship(brand_setting, sale_item)
            else:
                # MFN
                shipping_cost = ShipCostCalculationAdapter.calc_for_mfn(brand_setting, sale_item, sale_stats)
            return shipping_cost, accuracy
        except Exception as error:
            logger.error(f'[{self.__class__.__name__}][__update_sale_item_ship_cost] {error}')
            return shipping_cost, accuracy

    @classmethod
    def _get_brand_settings(cls, sale_item, brand_setting_query_set, brand_setting_null_query_set):
        try:
            # brand settings for declared brand
            brand_setting_gen = filter(lambda ele:
                                       ele.client_id == sale_item.client_id
                                       and ele.channel_id == sale_item.sale.channel.id
                                       and ele.brand_id == sale_item.brand_id,
                                       brand_setting_query_set)
            value = next(brand_setting_gen)
            if sale_item.fulfillment_type.name == FULFILLMENT_MFN_DS:
                accuracy = EVALUATED_SHIPPING_COST_ACCURACY_SPECIFIC_BRAND_MFN_DS
            elif sale_item.fulfillment_type.name == FULFILLMENT_MFN_PRIME or sale_item.sale.is_prime:
                accuracy = EVALUATED_SHIPPING_COST_ACCURACY_SPECIFIC_BRAND_MFN_PRIME
            else:
                accuracy = EVALUATED_SHIPPING_COST_ACCURACY_SPECIFIC_BRAND
            return value, accuracy
        except StopIteration:
            pass
        try:
            # brand settings for default brand
            brand_setting_gen = filter(lambda ele:
                                       ele.client_id == sale_item.client_id
                                       and ele.channel_id == sale_item.sale.channel.id,
                                       brand_setting_null_query_set)
            return next(brand_setting_gen), EVALUATED_SHIPPING_COST_ACCURACY_DEFAULT_BRAND
        except StopIteration:
            return None, None


class ShippingCostFromBrandSettings12HRecent(ShippingCostFromBrandSettings):

    @property
    def _pattern_conditions(self) -> List[Q]:
        time_delta_12h = datetime.now(tz=timezone.utc) - timedelta(hours=12)
        return [
            Q(fulfillment_type__isnull=False, brand__isnull=False),
            Q(modified__gte=time_delta_12h),
            Q(
                Q(shipping_cost_accuracy__isnull=True) | Q(
                    shipping_cost_accuracy__lte=self._accuracy_base())
            )
        ]
