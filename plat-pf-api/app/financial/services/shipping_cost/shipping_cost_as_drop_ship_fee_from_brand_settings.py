from datetime import timedelta, timezone, datetime
from decimal import Decimal
from typing import List

from auditlog.models import LogEntry
from django.db.models import Q

from app.core.logger import logger
from app.core.services.audit_logs.base import AuditLogCoreManager
from app.core.services.audit_logs.config import SYSTEM_BRAND_SETTINGS
from app.financial.services.brand_settings.ship_cost_calculation_adapter import ShipCostCalculationAdapter
from app.financial.variable.fulfillment_type import (FULFILLMENT_MFN, FULFILLMENT_MFN_DS, FULFILLMENT_MFN_RA)
from app.financial.services.shipping_cost.shipping_cost_from_brand_settings import ShippingCostFromBrandSettings
from app.financial.variable.brand_setting import MFN_DROP_SHIP
from app.financial.variable.brand_setting import EVALUATED_DROP_SHIP_FEE_ACCURACY_ACCEPT_CALCULATE


class DropShipFeeFromBrandSettings(ShippingCostFromBrandSettings):

    @property
    def update_fields(self):
        return ['dirty', 'warehouse_processing_fee', 'warehouse_processing_fee_accuracy']

    @property
    def select_related(self) -> [str]:
        return ['fulfillment_type', 'sale']

    @property
    def _pattern_conditions(self) -> List[Q]:
        return [
            Q(fulfillment_type__name__in=[FULFILLMENT_MFN, FULFILLMENT_MFN_DS, FULFILLMENT_MFN_RA]),
            Q(Q(sale__is_prime=False) | Q(sale__is_prime__isnull=True)),
            Q(
                Q(warehouse_processing_fee_accuracy__isnull=True) | Q(
                    warehouse_processing_fee_accuracy__lte=self._accuracy_base())
            )
        ]

    @property
    def _pattern_conditions_for_not_recalculate(self) -> List[Q]:
        logger.info(f"[{self.__class__.__name__}][{self._client_id_only}][_pattern_conditions_for_not_recalculate]")
        return [
            Q(
                Q(warehouse_processing_fee__isnull=True) | Q(warehouse_processing_fee=0)
            )
        ]

    def _accuracy_base(self) -> int:
        return EVALUATED_DROP_SHIP_FEE_ACCURACY_ACCEPT_CALCULATE

    def _calculate_shipping_cost(self, brand_setting_query_set, brand_setting_null_query_set, sale_stats):
        for idx, sale_item in enumerate(self._sub_update_mission):
            warehouse_processing_fee, evaluated_accuracy = self.__calc_sale_item_ship_cost(sale_item,
                                                                                           brand_setting_query_set,
                                                                                           brand_setting_null_query_set,
                                                                                           sale_stats)
            if warehouse_processing_fee == sale_item.warehouse_processing_fee:
                continue
            if warehouse_processing_fee is not None:
                changes = {"warehouse_processing_fee": [str(sale_item.warehouse_processing_fee),
                                                        Decimal(format(warehouse_processing_fee, '.2f'))],
                           "warehouse_processing_fee_accuracy": [f'{sale_item.warehouse_processing_fee_accuracy}%',
                                                                 f'{evaluated_accuracy}%']}
                sale_item.warehouse_processing_fee = warehouse_processing_fee
                sale_item.warehouse_processing_fee_accuracy = evaluated_accuracy
                sale_item.dirty = True
                sale_item.financial_dirty = True
                self._being_update_queue.append(sale_item)
                log_entry = AuditLogCoreManager(client_id=self._client_id_only).set_actor_name(SYSTEM_BRAND_SETTINGS) \
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
        override, consider drop ship fee only
        :rtype: shipping_cost, evaluated_accuracy

        evaluated_accuracy
            80% for brand setting defined
            50% for null brand setting defined
        """
        brand_setting, accuracy = self._get_brand_settings(sale_item, brand_setting_query_set,
                                                           brand_setting_null_query_set)
        shipping_cost = None
        if brand_setting is None:
            return shipping_cost, accuracy

        # MFN formula == MFN_DROP_SHIP only
        if brand_setting.mfn_formula != MFN_DROP_SHIP:
            return shipping_cost, accuracy

        try:
            warehouse_processing_fee = ShipCostCalculationAdapter.calc_drop_ship_fee_for_mfn(brand_setting, sale_item,
                                                                                             sale_stats)
            return warehouse_processing_fee, accuracy
        except Exception as error:
            logger.error(f'[{self.__class__.__name__}][__update_sale_item_ship_cost] {error}')
            return shipping_cost, accuracy


class DropShipFeeFromBrandSettings12HRecentOnly(DropShipFeeFromBrandSettings):

    @property
    def _pattern_conditions(self) -> List[Q]:
        time_delta_12h = datetime.now(tz=timezone.utc) - timedelta(hours=12)
        return [
            Q(fulfillment_type__name__in=[FULFILLMENT_MFN, FULFILLMENT_MFN_DS, FULFILLMENT_MFN_RA]),
            Q(Q(sale__is_prime=False) | Q(sale__is_prime__isnull=True)),
            Q(modified__gte=time_delta_12h),
            Q(
                Q(warehouse_processing_fee_accuracy__isnull=True) | Q(
                    warehouse_processing_fee_accuracy__lte=self._accuracy_base())
            )
        ]
