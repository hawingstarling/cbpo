import logging
from typing import Union

from app.financial.services.integrations.events.base import SaleItemEventHandler
from app.financial.variable.transaction.config import AdjustmentEvent, FeeCategory

logger = logging.getLogger(__name__)


class AdjustmentHandler(SaleItemEventHandler):
    event_type = AdjustmentEvent

    def process(self):
        try:

            adjustment_event = self.content.get('adjustment_event', None)

            if type(adjustment_event) not in [list, dict]:
                return

            if isinstance(adjustment_event, dict):
                adjustment_event = [adjustment_event]

            for adjustment_event_item in adjustment_event:

                _adjustment_event = adjustment_event_item.get('AdjustmentEvent', None)

                if type(_adjustment_event) not in [dict, list]:
                    continue

                if isinstance(_adjustment_event, dict):
                    _adjustment_event = [_adjustment_event]

                self.__process_adjustment_event(_adjustment_event)

        except Exception as ex:
            logger.error(f'[{self.client_id}][{self.channel_sale_id}][{self.event_type}]: {ex}')

    def __process_adjustment_event(self, adjustment_event):
        for item in adjustment_event:

            adjustment_type = item.get('AdjustmentType', None)

            if not adjustment_type:
                continue

            self.post_date = item.get('PostedDate', None)

            adjustment_item_list = item.get('AdjustmentItemList', None)

            if adjustment_item_list:
                if isinstance(adjustment_item_list, dict):
                    adjustment_item_list = [adjustment_item_list]

                self.__process_adjustment_item_list(adjustment_type, adjustment_item_list)
                continue

            adjustment_amount_list = item.get('AdjustmentAmount', {})

            if adjustment_amount_list:
                if isinstance(adjustment_amount_list, dict):
                    adjustment_amount_list = [adjustment_amount_list]
                #
                # Need set SKU for make unique trans event record. Because MWS API not returned SellerSKU So if not found default set sku = adjustment_type
                sku = item.get('SellerSKU', adjustment_type)
                for amount in adjustment_amount_list:
                    self.__process_adjustment_component(adjustment_type, sku, amount)
                continue

    def __process_adjustment_item_list(self, adjustment_type, adjustment_item_list):

        for item in adjustment_item_list:
            adjustment_item = item.get('AdjustmentItem', None)

            if not adjustment_item:
                continue

            if isinstance(adjustment_item, dict):
                adjustment_item = [adjustment_item]

            self.__process_adjustment_item(adjustment_type, adjustment_item)

    def __process_adjustment_item(self, adjustment_type, adjustment_item):
        for item in adjustment_item:
            # Need set SKU for make unique trans event record. Because MWS API not returned SellerSKU So if not found default set sku = adjustment_type
            sku = item.get('SellerSKU', adjustment_type)
            if not sku:
                continue

            component = item.get('TotalAmount', {})

            if not component or not isinstance(component, dict):
                continue

            self.__process_adjustment_component(adjustment_type, sku, component)

    def __process_adjustment_component(self, adjustment_type, sku: str, component: dict):
        if not self._validate_amount_component(component):
            return

        amount = component['CurrencyAmount']
        currency = component['CurrencyCode']

        content_type = self.get_content_type()
        if not content_type:
            return
        try:
            data = {
                'content_type': content_type,
                'channel': self.channel,
                'channel_sale_id': self.channel_sale_id,
                'sku': sku,
                'amount': amount,
                'currency': currency,
                'date': self.post_date,
                'type': adjustment_type,
                'category': FeeCategory,
                'event': AdjustmentEvent
            }

            self.data = data
        except Exception as ex:
            return
