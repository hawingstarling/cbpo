from datetime import datetime, timezone, timedelta
from django.conf import settings
from app.core.logger import logger
from app.core.services.ac_service import ACManager
from app.core.services.audit_logs.config import SYSTEM_AC
from app.financial.services.sale_item_mapping.mapping_sale_item_common_from_live_feed_dc import (
    MappingSaleItemCommonFromLiveFeedDC)

VALID_SALE_ITEM_COMMON_FIELDS_LIVE_FEED_AC = ['brand', 'upc']


class MappingSaleItemCommonFromLiveFeedAC(MappingSaleItemCommonFromLiveFeedDC):
    COMMON_FIELDS_ACCEPT = VALID_SALE_ITEM_COMMON_FIELDS_LIVE_FEED_AC
    """
    inherits form MappingSaleItemCommonFromLiveFeedDC
    """

    def __init__(self, client_id: str, *args, **kwargs):
        super().__init__(client_id, *args, **kwargs)
        self._is_use_cached = self.kwargs["use_cached"]  # use cached from AC

    def _load_config_service(self):
        self.__ac_manager = ACManager(client_id=self.client_id)
        self._limit_items = settings.AC_SERVICE_LIMIT_ITEM
        self._actor_name = SYSTEM_AC

    def _query_objects_ref_mapping(self, domain: str, item_type: str, list_value: [str]):
        assert item_type in ['ASIN', 'SKU'], 'item_type query AC is invalid'
        data = {"id_type": item_type, "ids": list_value, "marketplace": domain.lower(),
                "use_cache": self._is_use_cached}
        logger.info(f"[{self.__class__.__name__}][{self.client_id}] getting data from AC")
        if self._is_use_cached:
            response = self.__ac_manager.get_product_details(sc_method=self.sc_method, **data)
        else:
            if len(list_value) <= 5:
                response = self.__ac_manager.get_product_details(sc_method=self.sc_method, **data)
            else:
                return []
        return self._handler_result(response)


class MappingSaleItemCommonFromLiveFeedAC12HRecentOnly(MappingSaleItemCommonFromLiveFeedAC):
    """
    inherits form MappingSaleItemCommonFromLiveFeedAC
    """

    def _base_condition(self):
        time_delta_12h = datetime.now(tz=timezone.utc) - timedelta(hours=12)
        base_cond = {'modified__gte': time_delta_12h}

        if self.client_id is not None:
            base_cond.update({'client__id': self.client_id})
        if self._affected_sale_item_ids is not None:
            base_cond.update({'id__in': self._affected_sale_item_ids})
        return base_cond
