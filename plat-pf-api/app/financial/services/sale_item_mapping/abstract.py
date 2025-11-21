import logging
from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Union
from django.utils import timezone
from app.core.variable.marketplace import CHANNEL_DEFAULT
from app.database.helper import get_connection_workspace
from app.financial.models import ClientPortal
from app.core.services.utils import get_marketplace_type, get_sc_method
from app.job.utils.helper import register
from app.job.utils.variable import SYNC_ANALYSIS_CATEGORY, MODE_RUN_IMMEDIATELY

logger = logging.getLogger(__name__)


class MappingSaleItemAbstract(ABC):
    __chunk_size = 1000

    _list_sku = set()
    _sub_mission_being_calculate = []

    def __init__(self, client_id: str, marketplace: str = CHANNEL_DEFAULT, *args, **kwargs):
        self.client_id = client_id
        self.client = ClientPortal.objects.tenant_db_for(
            self.client_id).get(pk=self.client_id)
        self.client_setting = self.client.clientsettings
        self.setting_cog_priority_source = self.client_setting.cog_priority_source
        self.client_db = get_connection_workspace(self.client_id)
        self.marketplace = marketplace
        self.time_now = timezone.now()
        #
        self.marketplace_type = get_marketplace_type(self.marketplace)
        self.sc_method = get_sc_method(self.marketplace_type)
        #
        self.args = args
        self.kwargs = kwargs
        #
        self._is_override_mode = self.kwargs.get("is_override_mode", False)
        self._chunk_size = self.kwargs.get("limit_query_set_sale_item", 2000)
        self._affected_sale_item_ids = self.kwargs.get(
            "affected_sale_item_ids", None)

    @abstractmethod
    def _base_condition(self):
        raise NotImplemented

    @abstractmethod
    def _query_sale_items(self):
        raise NotImplemented

    @abstractmethod
    def _query_objects_ref_mapping(self, *args, **kwargs):
        raise NotImplemented

    @abstractmethod
    def _exec_mission(self):
        raise NotImplemented

    def exec(self):
        try:
            sale_items = self._query_sale_items()
            # print(f"Query : {sale_items.query}")
            for inx, sale_item in enumerate(sale_items):
                #  process with chunk size iterator
                self._list_sku.add(sale_item['sku'])
                self._sub_mission_being_calculate.append(sale_item)

                if (inx + 1) % self.__chunk_size == 0:
                    self._exec_mission()
                    self.__clear_object_mission_params()

            if len(self._sub_mission_being_calculate) > 0:
                self._exec_mission()
                self.__clear_object_mission_params()
        except BaseException as ex:
            self.__clear_object_mission_params()
            raise ex

    def __clear_object_mission_params(self):
        self._list_sku.clear()
        self._sub_mission_being_calculate.clear()

    def _mapping_warehouse_processing_fee_by_brand_settings(self, from_mapping: str, sale_item_ids: list = []):
        try:
            assert len(sale_item_ids) > 0
            data = dict(
                name=f"calculated_warehouse_processing_fee_trigger_by_{from_mapping}_{self.time_now.timestamp()}",
                job_name="app.financial.jobs.shipping_cost.handler_warehouse_processing_fee_calculation",
                module="app.financial.jobs.shipping_cost",
                method="handler_warehouse_processing_fee_calculation",
                meta=dict(client_id=self.client_id,
                          sale_item_ids=sale_item_ids)
            )
            register(SYNC_ANALYSIS_CATEGORY, self.client_id,
                     **data, mode_run=MODE_RUN_IMMEDIATELY)
        except Exception as ex:
            logger.error(
                f"[{self.__class__.__name__}][{self.client_id}][_mapping_warehouse_processing_fee_by_brand_settings] {ex}")


class MappingCogMethod(ABC):

    @classmethod
    def _mapping_appropriate_cog(cls, sale_date, ref_cogs, quantity: int) -> Union[Decimal, None]:
        for cog in ref_cogs:
            if cog['effect_start_date'] is None:
                if cog['effect_end_date'] is not None and sale_date <= cog['effect_end_date']:
                    return cls._cog_with_quantity(cog['cog'], quantity)

            elif cog['effect_start_date'] is not None and cog['effect_start_date'] <= sale_date:
                if cog['effect_end_date'] is None or sale_date <= cog['effect_end_date']:
                    return cls._cog_with_quantity(cog['cog'], quantity)
        if len(ref_cogs) > 0:
            return cls._cog_with_quantity(ref_cogs[0]['cog'], quantity)
        return None

    @classmethod
    def _cog_with_quantity(cls, cog: Union[Decimal, None], quantity: int) -> Union[Decimal, None]:
        # FIXME: cog * quantity could be larger than COG model validation -> got error
        return None if cog is None else cog * quantity
