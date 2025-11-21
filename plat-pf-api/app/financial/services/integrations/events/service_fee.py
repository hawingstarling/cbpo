import logging

from app.financial.services.integrations.events.base import SaleItemEventHandler
from app.financial.variable.transaction.config import FeeCategory, ServiceFeeEvent

logger = logging.getLogger(__name__)


class ServiceFeeHandler(SaleItemEventHandler):
    event_type = ServiceFeeEvent

    def process(self):
        try:
            service_fee_event = self.content.get('service_fee_event', None)

            # shipment_event object | list
            if type(service_fee_event) not in [dict, list]:
                return

            if isinstance(service_fee_event, dict):
                service_fee_event = [service_fee_event]

            for obj in service_fee_event:

                self.post_date = obj.get('PostedDate', None)

                sku = obj.get('SellerSKU', None)

                if not sku:
                    continue

                fee_list = obj.get('FeeList', None)

                if type(fee_list) not in [dict, list]:
                    continue

                if isinstance(fee_list, dict):
                    fee_list = [fee_list]

                for fee in fee_list:

                    fee_component = fee.get('FeeComponent', None)

                    if type(fee_component) not in [dict, list]:
                        continue

                    if isinstance(fee_component, dict):
                        fee_component = [fee_component]

                    for component in fee_component:
                        self.__process_fee_component(sku, component)
        except Exception as ex:
            logger.error(f'[{self.client_id}][{self.channel_sale_id}][{self.event_type}]: {ex}')

    def __process_fee_component(self, sku, component: dict):
        fee_type = component.get('FeeType', None)

        if not fee_type:
            return

        fee_amount = component.get('FeeAmount', {})

        if not fee_amount:
            return

        if not self._validate_amount_component(fee_amount):
            return

        amount = fee_amount['CurrencyAmount']
        currency = fee_amount['CurrencyCode']

        content_type = self.get_content_type()
        if not content_type:
            return
        try:
            data = {
                'content_type': content_type,
                'channel_sale_id': self.channel_sale_id,
                'channel': self.channel,
                'sku': sku,
                'amount': amount,
                'currency': currency,
                'date': self.post_date,
                'category': FeeCategory,
                'type': fee_type,
                'event': self.event_type
            }
            self.data = data
        except Exception as ex:
            return
