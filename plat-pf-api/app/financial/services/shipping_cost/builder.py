from app.financial.services.shipping_cost.shipping_cost_as_drop_ship_fee_from_brand_settings import (
    DropShipFeeFromBrandSettings, DropShipFeeFromBrandSettings12HRecentOnly)
from app.financial.services.shipping_cost.shipping_cost_from_brand_settings import (
    ShippingCostFromBrandSettings, ShippingCostFromBrandSettings12HRecent)
from app.financial.services.shipping_cost.shipping_cost_from_fedex_shipment import (
    ShippingCostFromFedExShipment, ShippingCostFromFedExShipment12HRecent, ShippingCostFromFedExShipmentPassiveAction)


class ShippingCostBuilder:

    def __init__(self):
        self.__sale_item_ids = []
        self.__is_recalculate = False
        self.__action = None
        self.__chunk_size = 1000

        self.__client_id_only = None

    @staticmethod
    def instance():
        return ShippingCostBuilder()

    def with_sale_item_ids(self, sale_item_ids: [str]):
        self.__sale_item_ids = sale_item_ids
        return self

    def with_is_recalculate(self, is_recalculate: bool):
        self.__is_recalculate = is_recalculate
        return self

    def with_action(self, action: bool):
        self.__action = action
        return self

    def with_chunk_size(self, chunk_size: int):
        self.__chunk_size = chunk_size
        return self

    def tenant_db_for_only(self, client_id: str):
        self.__client_id_only = client_id
        return self

    def build_from_brand_settings(self):
        return ShippingCostFromBrandSettings(self.__sale_item_ids, self.__client_id_only, self.__chunk_size,
                                             self.__is_recalculate, action=self.__action)

    def build_from_brand_settings_12h_recent(self):
        return ShippingCostFromBrandSettings12HRecent([], self.__client_id_only, self.__chunk_size,
                                                      self.__is_recalculate, action=self.__action)

    def build_from_fedex_shipment(self):
        return ShippingCostFromFedExShipment(self.__sale_item_ids, self.__client_id_only, self.__chunk_size,
                                             self.__is_recalculate, action=self.__action)

    def build_from_fedex_shipment_for_sale_items_12h_recent(self):
        return ShippingCostFromFedExShipment12HRecent([], self.__client_id_only, self.__chunk_size,
                                                      self.__is_recalculate, action=self.__action)

    def build_from_fedex_shipment_for_sale_items_passive(self):
        return ShippingCostFromFedExShipmentPassiveAction([], self.__client_id_only, self.__chunk_size,
                                                          self.__is_recalculate, action=self.__action)

    def build_from_brand_settings_for_drop_ship_fee(self):
        return DropShipFeeFromBrandSettings(self.__sale_item_ids, self.__client_id_only, self.__chunk_size,
                                            self.__is_recalculate, action=self.__action)

    def build_from_brand_settings_for_drop_ship_fee_12h_recent(self):
        return DropShipFeeFromBrandSettings12HRecentOnly([], self.__client_id_only, self.__chunk_size,
                                                         self.__is_recalculate, action=self.__action)
