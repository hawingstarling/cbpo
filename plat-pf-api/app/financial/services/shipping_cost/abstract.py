from abc import ABC, abstractmethod
from django.utils import timezone
from typing import List
from bulk_update.helper import bulk_update
from django.db import transaction
from django.db.models import Q
from app.core.logger import logger
from app.financial.jobs.data_flatten import flat_sale_items_bulks_sync_task
from app.financial.models import SaleItem, LogClientEntry
from app.database.helper import get_connection_workspace


class ShippingCostService(ABC):

    def __init__(self, sale_item_ids: [str], client_id_only: str = None, chunk_size: int = 5000, is_recalculate=False,
                 *args, **kwargs):
        self._client_id_only = client_id_only
        self._time_now = timezone.now()
        self.client_db = get_connection_workspace(self._client_id_only)
        self.__sale_item_ids = sale_item_ids

        self._chunk_size = chunk_size
        self._size_bulk_update = 500

        self.__part_bulk_update_index = 0
        self._sub_update_mission = []
        self._being_update_queue = []
        self._being_update_audit_log_queue = []

        self._is_recalculate = is_recalculate

        self.args = args
        self.kwargs = kwargs

    @property
    def action(self):
        return self.kwargs.get('action', None)

    @property
    def order_query(self) -> [str]:
        return []

    @property
    def select_related(self) -> [str]:
        return []

    @property
    def update_fields(self):
        return ['modified', 'dirty', 'financial_dirty', 'shipping_cost', 'actual_shipping_cost',
                'estimated_shipping_cost', 'shipping_cost_accuracy', 'shipping_cost_source']

    @abstractmethod
    def _accuracy_base(self) -> int:
        """
        declare base shipping_cost_accuracy
        avoid overlap shipping_cost calculation strategies
        """
        raise NotImplemented

    @classmethod
    def _base_condition(cls) -> Q:
        """
        declare base condition
        should be base fulfilment type such as FBA or MFN
        """
        cond = Q()
        return cond

    @property
    def _pattern_conditions_for_not_recalculate(self) -> List[Q]:
        logger.info(f'[{self.__class__.__name__}][_pattern_conditions_for_not_recalculate]')
        return [
            Q(
                Q(shipping_cost__isnull=True) | Q(shipping_cost=0)
            )
        ]

    @property
    def _pattern_conditions(self) -> List[Q]:
        return [
            Q(fulfillment_type__isnull=False),
            Q(
                Q(shipping_cost_accuracy__isnull=True) | Q(shipping_cost_accuracy__lte=self._accuracy_base())
            )
        ]

    @property
    def _get_sale_item_query_set(self):
        cond = self._base_condition()
        condition_patterns = self._pattern_conditions
        if not self._is_recalculate:
            condition_patterns.extend(self._pattern_conditions_for_not_recalculate)

        for _pattern in condition_patterns:
            cond.add(_pattern, Q.AND)

        if len(self.__sale_item_ids):
            cond.add(Q(id__in=self.__sale_item_ids), Q.AND)

        select_related = self.select_related
        # limit 10K items to avoid keeping job too long
        return SaleItem.objects.tenant_db_for(self._client_id_only).filter(cond).select_related(
            *select_related).order_by(
            *self.order_query)[:10000].iterator(chunk_size=self._chunk_size)

    def update(self):
        logger.info(f'[{self.__class__.__name__}] automatically calculate ship cost for sale items')
        for idx, sale_item in enumerate(self._get_sale_item_query_set):
            self._sub_update_mission.append(sale_item)

            if (idx + 1) % self._chunk_size == 0:
                self._exec_sub_mission()
                self._sub_update_mission.clear()

        if len(self._sub_update_mission):
            self._exec_sub_mission()

    @abstractmethod
    def _exec_sub_mission(self):
        raise NotImplemented

    @abstractmethod
    def _calculate_shipping_cost(self, *args, **kwargs):
        raise NotImplemented

    def _bulk_update_external_protected(self):
        pass

    def _bulk_update(self):
        self.__part_bulk_update_index += 1
        logger.info(f'[{self.__class__.__name__}][bulk update] part {self.__part_bulk_update_index}')
        try:
            assert len(self._being_update_queue) > 0, "Bulks objs is not empty"
            with transaction.atomic():
                bulk_update(self._being_update_queue, batch_size=self._size_bulk_update,
                            update_fields=self.update_fields, using=self.client_db)
                LogClientEntry.objects.tenant_db_for(self._client_id_only).bulk_create(
                    self._being_update_audit_log_queue, ignore_conflicts=True)
                self._bulk_update_external_protected()
            transaction.on_commit(
                lambda: flat_sale_items_bulks_sync_task(self._client_id_only),
                using=self.client_db
            )
        except Exception as err:
            logger.error(f"[{self.__class__.__name__}][{self._client_id_only}][_bulk_update] {err}")

        self._being_update_queue.clear()
        self._being_update_audit_log_queue.clear()
