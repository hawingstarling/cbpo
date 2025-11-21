import logging
import operator
from decimal import Decimal
from functools import reduce
from typing import Union
from django.db.models import Sum, Q
from app.financial.models import Sale, SaleItem, SaleItemFinancial, BrandSetting, FedExShipment
from app.financial.services.utils.common import round_currency
from app.financial.variable.brand_setting import EVALUATED_SHIPPING_COST_ACCURACY_DEFAULT_BRAND, \
    EVALUATED_SHIPPING_COST_ACCURACY_SPECIFIC_BRAND
from app.financial.variable.shipping_cost_source import SHIP_CARRIER_FEDEX, SHIPPING_COST_ACCURACY_BY_SOURCE, \
    BRAND_SETTING_SOURCE_KEY
from app.financial.variable.transaction.config import TRANS_EVENT_LIST

logger = logging.getLogger(__name__)


class TransBaseCalculate:
    field = None
    field_accuracy = None
    min_accuracy_value = 75
    max_accuracy_value = 100
    field_source = None
    model_instance = None

    def __init__(self, client_id: str, filters: dict, instance: Union[Sale, SaleItem, SaleItemFinancial], *args,
                 **kwargs):
        assert client_id is not None, f"[{self.__class__.__name__}] Client ID is required"
        self.client_id = client_id
        self.filters = filters
        self.instance = instance
        self.args = args
        self.kwargs = kwargs

        self._data = {}

        self._trans_amount_column = None

        self.validate()

        # add fulfillment_type to kwargs
        self.extra_kwargs()

    def validate(self):
        if not self.field:
            logger.error(f"[{self.__class__.__name__}] field not define")
            raise NotImplementedError
        if not isinstance(self.instance, self.model_instance):
            logger.error(f"[{self.__class__.__name__} {self.instance} "
                         f"haven't instance model {self.model_instance.__name__}")
            raise NotImplementedError

    def extra_kwargs(self):
        pass

    @property
    def validated_data(self):
        return self.kwargs.get('validated_data', {})

    def _handler_popular_data(self):
        raise NotImplementedError

    def calculate(self, *args, **kwargs):
        try:
            self._handler_popular_data()
        except Exception as ex:
            logger.debug(
                f"[{self.__class__.__name__}][{self.client_id}][{self.instance.pk}]"
                f"[calculate] {ex}"
            )
            self._data = {}
            self._trans_amount_column = None

    @property
    def data(self):
        return self._data

    @property
    def trans_amount_column(self):
        return self._trans_amount_column


class TransBaseSaleCalculate(TransBaseCalculate):
    model_instance = Sale

    def calculate(self, *args, **kwargs):
        return super().calculate(*args, **kwargs)

    def extra_kwargs(self):
        total_sale_quantity = self.instance.saleitem_set.tenant_db_for(self.instance.client_id).aggregate(
            total=Sum('quantity'))
        self.kwargs.update({
            'quantity': total_sale_quantity['total']
        })


class TransBaseSaleItemCalculate(TransBaseCalculate):
    model_instance = SaleItem

    def calculate(self, *args, **kwargs):
        return super().calculate(*args, **kwargs)

    @property
    def fulfillment_type(self):
        try:
            return self.validated_data['fulfillment_type']
        except Exception as ex:
            logger.debug(f"[{self.__class__.__name__}][{self.client_id}][{self.instance.pk}][fulfillment_type] {ex}")
            return self.instance.fulfillment_type

    @property
    def fulfillment_type_name(self):
        try:
            return self.fulfillment_type.name
        except Exception as ex:
            logger.debug(f"[{self.__class__.__name__}][{self.client_id}][{self.instance.pk}]"
                         f"[fulfillment_type_name] {ex}")
            return None

    @property
    def sale_status(self):
        try:
            return self.validated_data['sale_status']
        except Exception as ex:
            logger.debug(f"[{self.__class__.__name__}][{self.client_id}][{self.instance.pk}][sale_status] {ex}")
            return self.instance.sale_status

    @property
    def sale_instance(self):
        return self.instance.sale

    @property
    def is_prime(self):
        try:
            return self.validated_data['is_prime']
        except Exception as ex:
            logger.debug(f"[{self.__class__.__name__}][{self.client_id}][{self.instance.pk}][is_prime] {ex}")
            return self.instance.sale.is_prime

    @property
    def quantity(self):
        try:
            return self.validated_data['quantity']
        except Exception as ex:
            logger.debug(f"[{self.__class__.__name__}][{self.client_id}][{self.instance.pk}][quantity] {ex}")
            return self.instance.quantity

    @property
    def event(self):
        return self.kwargs.get('event', None)

    def extra_kwargs(self):
        self.kwargs.update({
            'fulfillment_type': self.fulfillment_type,
            'is_prime': self.is_prime,
            'quantity': self.quantity,
            "event": self.event
        })

    def format_trans_amount(self, amount):
        amount = abs(amount)
        amount = round_currency(amount)
        return Decimal(f"{amount}")

    def get_brand_setting(self):
        cond = dict(
            client_id=self.instance.client_id,
            channel=self.instance.sale.channel
        )
        try:
            assert self.instance.brand is not None, f"The brand of instance is not None"
            brand_setting = BrandSetting.objects.tenant_db_for(self.client_id).get(brand=self.instance.brand, **cond)
        except BrandSetting.DoesNotExist:
            logger.debug(f"[{self.__class__.__name__}][{self.client_id}][{self.instance.pk}][get_brand_setting] "
                         f"Brand setting not setting")
            brand_setting = BrandSetting.objects.tenant_db_for(self.client_id).filter(brand=None, **cond) \
                .order_by("-created").first()
        except Exception as ex:
            logger.debug(f"[{self.__class__.__name__}][{self.client_id}][{self.instance.pk}][get_brand_setting] {ex}")
            brand_setting = None
        return brand_setting

    def get_brand_setting_esc_accuracy(self):
        brand_setting = self.get_brand_setting()
        accuracy = None
        if brand_setting is None:
            return brand_setting, accuracy
        if brand_setting.brand is not None:
            accuracy = SHIPPING_COST_ACCURACY_BY_SOURCE[BRAND_SETTING_SOURCE_KEY] \
                .get(self.fulfillment_type_name, EVALUATED_SHIPPING_COST_ACCURACY_SPECIFIC_BRAND)
        else:
            accuracy = EVALUATED_SHIPPING_COST_ACCURACY_DEFAULT_BRAND
        return brand_setting, accuracy

    def get_fedex_shipment(self):
        fedex_shipment = None
        try:
            queryset_item_ship_carrier = self.sale_instance.saleitem_set.tenant_db_for(self.sale_instance.client_id) \
                .filter(ship_carrier__icontains=SHIP_CARRIER_FEDEX, tracking_fedex_id__isnull=False)
            tracking_fedex_ids = []
            for item in queryset_item_ship_carrier:
                tracking_fedex_ids += item.tracking_fedex_id.split(" , ")
            #
            fedex_shipment_query_set = FedExShipment.objects.tenant_db_for(self.client_id) \
                .filter(client_id=self.instance.client_id)
            return fedex_shipment_query_set.filter(
                reduce(operator.or_, (Q(tracking_id=x) for x in tracking_fedex_ids)))
        except Exception as ex:
            logger.debug(f"[{self.__class__.__name__}][{self.client_id}][{self.instance.pk}][get_fedex_shipment] {ex}")
        return fedex_shipment


class TransBaseSaleItemFinancialCalculate(TransBaseSaleItemCalculate):
    model_instance = SaleItemFinancial

    def validate(self):
        super().validate()
        # validate event required
        if self.event is None or self.event not in TRANS_EVENT_LIST:
            logger.debug(
                f"[{self.__class__.__name__}] {self.event} "
                f"is required or {self.event} not in {TRANS_EVENT_LIST}"
            )
            raise NotImplementedError


class CalculateFieldManage:
    JOB_ACCEPT = []
    CALCULATED_CONFIG = []

    def __init__(self, client_id: str, job_action: str, instance: Union[Sale, SaleItem, SaleItemFinancial], *args,
                 **kwargs):
        assert client_id is not None, f"[{self.__class__.__name__}] Client ID is required"
        self.client_id = client_id
        self.job_action = self.is_valid_job_action(job_action)
        self.instance = instance
        self.args = args
        self.kwargs = kwargs

        self.data = {}

        self.total_financial_amount = 0

    def is_valid_job_action(self, job_action):
        assert len(job_action) > 0 and job_action in self.JOB_ACCEPT, \
            f"The job accept not defined or job action {job_action} not in {self.JOB_ACCEPT}"
        return job_action

    def process(self):
        raise NotImplementedError
