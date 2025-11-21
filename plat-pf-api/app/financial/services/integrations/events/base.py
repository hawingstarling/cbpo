import logging

from django.contrib.contenttypes.models import ContentType

from app.financial.models import ClientPortal, Channel, SaleItem
from app.database.helper import get_connection_workspace
from app.financial.variable.transaction.config import ChargeCategory

logger = logging.getLogger(__name__)


class EventHandlerBase:

    def __init__(self, *args, **kwargs):
        # data process
        self._data = []
        self._seq_mapping = {}

    @property
    def data(self):
        return self._data

    def get_seg(self, obj: dict):
        key = f"{obj['type']}-{obj['category']}-{obj['event']}-{obj['sku']}"
        try:
            self._seq_mapping[key] += 1
        except Exception as ex:
            # logger.error(f"[{self.__class__.__name__}] {ex}")
            self._seq_mapping.update({key: 1})
        obj.update({'seq': self._seq_mapping[key]})

    @data.setter
    def data(self, obj):
        self.get_seg(obj)
        self._data.append(obj)

    def process(self):
        raise NotImplementedError


class SaleItemEventHandler(EventHandlerBase):
    event_type = None

    def __init__(self, client: ClientPortal, channel_sale_id: str, channel: Channel, content: dict):
        super().__init__()

        self.client = client
        self.client_id = str(self.client.pk)
        self.client_db = get_connection_workspace(self.client_id)
        self.channel_sale_id = channel_sale_id
        self.content = content
        self.channel = channel
        self.post_date = None

        self.__not_define_event_type()

    def _validate_amount_component(self, component):
        if 'CurrencyAmount' not in component or 'CurrencyCode' not in component:
            return False
        amount = self._validate_amount(component['CurrencyAmount'])
        if not amount or amount == 0:
            return False
        return True

    def _validate_amount(self, val):
        try:
            return float(val)
        except Exception as ex:
            return None

    def __not_define_event_type(self):
        if not self.event_type:
            raise NotImplementedError

    def process(self):
        super().process()

    def get_content_type(self, model: any = SaleItem):
        try:
            return ContentType.objects.db_manager(using=self.client_db).get_for_model(model)
        except SaleItem.DoesNotExist:
            return None

    def _process_item_tax_withheld_list(self, sku: str, data_list: [dict]):
        # loop data
        for item in data_list:

            tax_withheld_component = item.get('TaxWithheldComponent', {})

            if not tax_withheld_component:
                continue

            if isinstance(tax_withheld_component, dict):
                tax_withheld_component = [tax_withheld_component]

            for component in tax_withheld_component:
                self._process_tax_withheld_component(sku, component)

    def _process_tax_withheld_component(self, sku, component: dict):

        taxes_withheld = component.get('TaxesWithheld', {})

        if not taxes_withheld:
            return

        if isinstance(taxes_withheld, dict):
            taxes_withheld = [taxes_withheld]

        for withheld in taxes_withheld:

            charge_component = withheld.get('ChargeComponent', {})

            if isinstance(charge_component, dict):
                charge_component = [charge_component]

            for component in charge_component:
                charge_amount = component.get('ChargeAmount', {})
                charge_type = component.get('ChargeType', None)

                if not charge_amount or not charge_type:
                    continue

                if not self._validate_amount_component(charge_amount):
                    continue

                amount = charge_amount['CurrencyAmount']
                currency = charge_amount['CurrencyCode']

                content_type = self.get_content_type()
                if not content_type:
                    continue
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
                    # logger.error(f"[{self.__class__.__name__}] {ex}")
                    continue
