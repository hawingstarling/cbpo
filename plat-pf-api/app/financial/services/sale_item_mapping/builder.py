from app.core.variable.marketplace import CHANNEL_DEFAULT
from app.financial.models import Item
from app.financial.services.sale_item_mapping.mapping_item_cog import MappingItemCog
from app.financial.services.sale_item_mapping.mapping_sale_item_cog import MappingSaleItemCog, \
    MappingSaleItemCog12HRecentOnly
from app.financial.services.sale_item_mapping.mapping_sale_item_common import MappingSaleItemCommon, \
    MappingSaleItemCommon12HRecentOnly
from app.financial.services.sale_item_mapping.mapping_sale_item_common_from_live_feed_ac import (
    MappingSaleItemCommonFromLiveFeedAC, MappingSaleItemCommonFromLiveFeedAC12HRecentOnly)
from app.financial.services.sale_item_mapping.mapping_sale_item_common_from_live_feed_dc import (
    MappingSaleItemCommonFromLiveFeedDC, MappingSaleItemCommonFromLive12HRecentOnlyFeedDC)
from app.financial.services.sale_item_mapping.mapping_sale_item_mfn_classification import \
    MappingSaleItemMFNClassification, MappingSaleItemMFNClassification12HRecent


class MappingSaleItemBuilder:
    def __init__(self):
        """
        usage for all sale item which have type cog == CALCULATED:
        ins = CalculateSaleItemCogBuilder.instance().with_chunk_size_query_set_sale_item(2000).build()
        ins.exec()

        usage for selected sale item ids
        ins = CalculateSaleItemCogBuilder.instance().with_selected_sale_item_ids(['1', '2', '3']).build()
        ins.exec()

        :rtype: object
        """
        self.__chunk_size_query_set_sale_item = 2000
        self.__affected_sale_item_ids = None
        self.__process_null_only = False
        self.__client_id_only = None
        self.__marketplace = CHANNEL_DEFAULT
        self.__is_override_mode = False
        self.__use_cached = True

        self.__common_mapping_fields = []

    @staticmethod
    def instance():
        return MappingSaleItemBuilder()

    def with_chunk_size_query_set_sale_item(self, size: int):
        self.__chunk_size_query_set_sale_item = size
        return self

    def with_selected_sale_item_ids(self, ids: [str]):
        self.__affected_sale_item_ids = ids
        return self

    def with_process_null_cog_only(self, null_cog: bool):
        self.__process_null_only = null_cog
        return self

    def with_marketplace(self, marketplace: str):
        self.__marketplace = marketplace
        return self

    def tenant_db_for_only(self, client_id: str):
        self.__client_id_only = client_id
        return self

    def with_common_mapping_fields(self, mapping_fields: [str]):
        self.__common_mapping_fields = mapping_fields
        return self

    def with_override_mode(self, is_override: bool):
        self.__is_override_mode = is_override
        return self

    def with_cached(self, use_cached: bool):
        self.__use_cached = use_cached
        return self

    def build_mapping_cog_from_item(self):
        return MappingSaleItemCog(client_id=self.__client_id_only,
                                  limit_query_set_sale_item=self.__chunk_size_query_set_sale_item,
                                  affected_sale_item_ids=self.__affected_sale_item_ids,
                                  is_override_mode=self.__is_override_mode,
                                  marketplace=self.__marketplace)

    def build_mapping_cog_from_item_12h_recent_only(self):
        return MappingSaleItemCog12HRecentOnly(client_id=self.__client_id_only,
                                               limit_query_set_sale_item=self.__chunk_size_query_set_sale_item,
                                               affected_sale_item_ids=self.__affected_sale_item_ids,
                                               marketplace=self.__marketplace)

    def build_mapping_common_from_item(self):
        return MappingSaleItemCommon(client_id=self.__client_id_only,
                                     limit_query_set_sale_item=self.__chunk_size_query_set_sale_item,
                                     affected_sale_item_ids=self.__affected_sale_item_ids,
                                     fields_mapping=self.__common_mapping_fields,
                                     is_override_mode=self.__is_override_mode,
                                     marketplace=self.__marketplace)

    def build_mapping_cog_from_item_based(self, item: Item):
        return MappingItemCog(client_id=self.__client_id_only, item=item, marketplace=self.__marketplace)

    def build_mapping_common_from_item_12h_recent(self):
        return MappingSaleItemCommon12HRecentOnly(client_id=self.__client_id_only,
                                                  limit_query_set_sale_item=self.__chunk_size_query_set_sale_item,
                                                  fields_mapping=self.__common_mapping_fields,
                                                  is_override_mode=self.__is_override_mode,
                                                  affected_sale_item_ids=self.__affected_sale_item_ids,
                                                  marketplace=self.__marketplace)

    def build_mapping_mfn_classification(self):
        return MappingSaleItemMFNClassification(client_id=self.__client_id_only,
                                                limit_query_set_sale_item=self.__chunk_size_query_set_sale_item,
                                                affected_sale_item_ids=self.__affected_sale_item_ids,
                                                is_override_mode=self.__is_override_mode,
                                                marketplace=self.__marketplace)

    def build_mapping_mfn_classification_12h_recent(self):
        return MappingSaleItemMFNClassification12HRecent(client_id=self.__client_id_only,
                                                         limit_query_set_sale_item=self.__chunk_size_query_set_sale_item,
                                                         marketplace=self.__marketplace)

    def build_mapping_from_live_feed_ac(self):
        return MappingSaleItemCommonFromLiveFeedAC(client_id=self.__client_id_only,
                                                   limit_query_set_sale_item=self.__chunk_size_query_set_sale_item,
                                                   fields_mapping=self.__common_mapping_fields,
                                                   is_override_mode=self.__is_override_mode,
                                                   use_cached=self.__use_cached,
                                                   affected_sale_item_ids=self.__affected_sale_item_ids,
                                                   marketplace=self.__marketplace)

    def build_mapping_from_live_feed_12h_recent_ac(self):
        return MappingSaleItemCommonFromLiveFeedAC12HRecentOnly(client_id=self.__client_id_only,
                                                                limit_query_set_sale_item=self.__chunk_size_query_set_sale_item,
                                                                fields_mapping=self.__common_mapping_fields,
                                                                is_override_mode=self.__is_override_mode,
                                                                use_cached=self.__use_cached,
                                                                affected_sale_item_ids=self.__affected_sale_item_ids,
                                                                marketplace=self.__marketplace)

    def build_mapping_from_live_feed_dc(self):
        return MappingSaleItemCommonFromLiveFeedDC(client_id=self.__client_id_only,
                                                   limit_query_set_sale_item=self.__chunk_size_query_set_sale_item,
                                                   fields_mapping=self.__common_mapping_fields,
                                                   is_override_mode=self.__is_override_mode,
                                                   affected_sale_item_ids=self.__affected_sale_item_ids,
                                                   marketplace=self.__marketplace)

    def build_mapping_from_live_feed_12h_recent_dc(self):
        return MappingSaleItemCommonFromLive12HRecentOnlyFeedDC(client_id=self.__client_id_only,
                                                                limit_query_set_sale_item=self.__chunk_size_query_set_sale_item,
                                                                fields_mapping=self.__common_mapping_fields,
                                                                is_override_mode=self.__is_override_mode,
                                                                affected_sale_item_ids=self.__affected_sale_item_ids,
                                                                marketplace=self.__marketplace)
