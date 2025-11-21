import logging

from app.financial.services.integrations.events.base import SaleItemEventHandler
from app.financial.variable.transaction.config import FeeCategory, ChargeCategory, RefundEvent, QuantityCategory
from app.financial.variable.transaction.type.quantity import QuantityShippedType

logger = logging.getLogger(__name__)


class RefundHandler(SaleItemEventHandler):
    event_type = RefundEvent

    def process(self):
        try:
            refund_event = self.content.get('refund_event', None)

            # shipment_event object | null
            if type(refund_event) not in [list, dict]:
                return

            if isinstance(refund_event, dict):
                refund_event = [refund_event]

            for refund_item in refund_event:

                shipment_item_list = refund_item.get('ShipmentItemAdjustmentList', None)

                if type(shipment_item_list) not in [list, dict]:
                    continue

                self.post_date = refund_item.get('PostedDate', None)

                if isinstance(shipment_item_list, dict):
                    shipment_item_list = [shipment_item_list]

                for obj in shipment_item_list:
                    shipment_items = obj.get('ShipmentItem', None)

                    if type(shipment_items) not in [list, dict]:
                        continue

                    if isinstance(shipment_items, dict):
                        shipment_items = [shipment_items]

                    self.__process_shipment_items(shipment_items)
        except Exception as ex:
            logger.error(f'[{self.client_id}][{self.channel_sale_id}][{self.event_type}]: {ex}')

    def __process_shipment_items(self, shipment_items: list):
        for item in shipment_items:
            sku = item.get('SellerSKU', None)

            if not sku:
                continue

            #
            fee_list = item.get('ItemFeeAdjustmentList', [])
            if isinstance(fee_list, dict):
                fee_list = [fee_list]
            #
            charge_list = item.get('ItemChargeAdjustmentList', [])

            if isinstance(charge_list, dict):
                charge_list = [charge_list]

            # ItemTaxWithheldList
            item_tax_withheld_list = item.get('ItemTaxWithheldList', [])

            if isinstance(item_tax_withheld_list, dict):
                item_tax_withheld_list = [item_tax_withheld_list]

            if fee_list:
                self.__process_fee_list(sku, fee_list)

            if charge_list:
                self.__process_charge_list(sku, charge_list)

            if item_tax_withheld_list:
                self._process_item_tax_withheld_list(sku, item_tax_withheld_list)

            # quantity shipped
            quantity_shipped = item.get('QuantityShipped', None)
            if quantity_shipped:
                self.__process_quantity_shipped(sku, quantity_shipped)

    def __process_quantity_shipped(self, sku, quantity_shipped):
        content_type = self.get_content_type()
        if not content_type:
            return

        try:
            data = {
                'content_type': content_type,
                'channel': self.channel,
                'channel_sale_id': self.channel_sale_id,
                'sku': sku,
                'quantity': quantity_shipped,
                'date': self.post_date,
                'category': QuantityCategory,
                'type': QuantityShippedType,
                'event': self.event_type
            }
            self.data = data
        except Exception as ex:
            return

    def __process_charge_list(self, sku: str, data_list: [dict]):
        # loop data
        for item in data_list:

            charge_component = item.get('ChargeComponent', {})

            if not charge_component:
                continue

            if isinstance(charge_component, dict):
                charge_component = [charge_component]

            for component in charge_component:
                self.__process_charge_component(sku, component)

    def __process_fee_list(self, sku: str, data_list: [dict]):
        # loop data
        for item in data_list:

            fee_component = item.get('FeeComponent', {})

            if not fee_component:
                continue

            if isinstance(fee_component, dict):
                fee_component = [fee_component]

            for component in fee_component:
                self.__process_fee_component(sku, component)

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

    def __process_charge_component(self, sku, component: dict):

        charge_type = component.get('ChargeType', None)

        if not charge_type:
            return

        charge_amount = component.get('ChargeAmount', {})

        if not charge_amount:
            return

        if not self._validate_amount_component(charge_amount):
            return

        amount = charge_amount['CurrencyAmount']
        currency = charge_amount['CurrencyCode']

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
                'category': ChargeCategory,
                'type': charge_type,
                'event': self.event_type
            }
            self.data = data
        except Exception as ex:
            return
