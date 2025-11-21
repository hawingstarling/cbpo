import logging
from decimal import Decimal

from app.financial.variable.fulfillment_type import FULFILLMENT_MFN_PRIME, FULFILLMENT_MFN
from app.financial.services.transaction.calculate.sale_item import CalculateTransSaleItemsManage, \
    ReturnPostageBillingCalculate
from app.financial.services.transaction.calculate.base import TransBaseSaleItemFinancialCalculate
from app.financial.models import SaleItemTransaction, SaleItemFinancial
from app.financial.services.transaction.calculate.sale_item_shipped import ChannelTaxWithheldShippedCalculate, \
    RefundAdminFeeShippedCalculate, TaxChargedShippedCalculate, ChannelListingFeeShippedCalculate, \
    SaleChargedShippedCalculate, ShippingCostShippedCalculate, OtherChannelFeesShippedCalculate, \
    RefundedQuantityShippedCalculate, InboundFreightCostShippedCalculate, OutboundFreightCostShippedCalculate
from app.financial.variable.job_status import TRANS_DATA_EVENT_JOB, BULK_SYNC_LIVE_FEED_JOB, LIVE_FEED_JOB, \
    SALE_ITEM_FINANCIAL_JOB, BULK_SYNC_TRANS_DATA_EVENT_JOB
from app.financial.variable.sale_status_static_variable import SALE_REFUNDED_STATUS, SALE_PARTIALLY_REFUNDED_STATUS

logger = logging.getLogger(__name__)


class SaleDateReturnedCalculate(TransBaseSaleItemFinancialCalculate):
    field = 'sale_date'

    @property
    def trans_sale_date_event(self):
        #
        try:
            value = SaleItemTransaction().get_sale_date_event(self.client_id, self.filters, **self.kwargs)
        except Exception as ex:
            logger.debug(f"[{self.__class__.__name__}][{self.client_id}][{self.instance.pk}]"
                         f"[trans_sale_date_event] {ex}")
            value = None
        return value

    def _handler_popular_data(self):
        sale_status = self.trans_sale_date_event
        if sale_status:
            self._data[self.field] = sale_status


class SaleChargedReturnedCalculate(SaleChargedShippedCalculate):
    def get_trans_amount(self):
        amount = super().get_trans_amount()
        try:
            if amount is None:
                if self.sale_status.value == SALE_PARTIALLY_REFUNDED_STATUS:
                    amount = (self.instance.unit_cog * self.instance.refunded_quantity) * -1
                else:
                    amount = self.instance.sale_charged * -1
        except Exception as ex:
            logger.debug(f"[{self.__class__.__name__}][{self.client_id}][{self.instance.pk}]"
                         f"[get_trans_amount] {ex}")
        return amount

    def _handler_popular_data(self):
        super()._handler_popular_data()
        self._data[self.field] = abs(self._trans_amount_column) * -1


class RefundAdminFeeReturnedCalculate(RefundAdminFeeShippedCalculate):
    def get_trans_amount(self):
        amount = super().get_trans_amount()
        try:
            if amount is None:
                amount = self.instance.refund_admin_fee
        except Exception as ex:
            logger.debug(f"[{self.__class__.__name__}][{self.client_id}][{self.instance.pk}]"
                         f"[get_trans_amount] {ex}")
            amount = 0
        return amount


class ShippingCostReturnedCalculate(ShippingCostShippedCalculate):

    def summary_amount(self, amount, amount_refund_postage_billing):
        if amount is None and not self.amz_source:
            amount = self._get_shipping_cost_other_source()
        if amount_refund_postage_billing is None:
            amount_refund_postage_billing = 0
        if self.fulfillment_type_name.startswith('MFN') and self.fulfillment_type_name != FULFILLMENT_MFN_PRIME and \
                self.sale_status.value in [SALE_REFUNDED_STATUS]:
            amount = sum(filter(None, [amount, amount_refund_postage_billing]))
            amount = Decimal(f"{amount}")
        else:
            amount = amount_refund_postage_billing
        return amount


class CogReturnedCalculate(TransBaseSaleItemFinancialCalculate):
    field = 'cog'

    def _handler_popular_data(self):
        self._data[self.field] = self.instance.cog * -1


class InboundFreightCostReturnedCalculate(InboundFreightCostShippedCalculate):
    def get_trans_amount(self):
        amount = 0
        try:
            if self.fulfillment_type.name not in [FULFILLMENT_MFN]:
                amount = super().get_trans_amount() * -1
        except Exception as ex:
            logger.debug(f"[{self.__class__.__name__}][{self.client_id}][{self.instance.pk}]"
                         f"[get_trans_amount] {ex}")
        return amount


class OutboundFreightCostReturnedCalculate(OutboundFreightCostShippedCalculate):
    def get_trans_amount(self):
        amount = 0
        try:
            if self.fulfillment_type.name not in [FULFILLMENT_MFN]:
                amount = super().get_trans_amount() * -1
        except Exception as ex:
            logger.debug(f"[{self.__class__.__name__}][{self.client_id}][{self.instance.pk}]"
                         f"[get_trans_amount] {ex}")
        return amount


class ChannelTaxWithheldReturnedCalculate(ChannelTaxWithheldShippedCalculate):
    def _handler_popular_data(self):
        try:
            super()._handler_popular_data()
            if self._trans_amount_column is None:
                self._trans_amount_column = self.instance.channel_tax_withheld
            self._data[self.field] = abs(self._trans_amount_column) * -1
        except Exception as ex:
            logger.debug(f"[{self.__class__.__name__}][{self.client_id}][{self.instance.pk}]"
                         f"[_handler_popular_data] {ex}")
            self._data[self.field] = 0
            self._trans_amount_column = None


class ChannelListingFeeReturnedCalculate(ChannelListingFeeShippedCalculate):
    def _handler_popular_data(self):
        try:
            super()._handler_popular_data()
            if self._trans_amount_column is None:
                self._trans_amount_column = self.instance.channel_listing_fee
            self._data[self.field] = abs(self._trans_amount_column) * -1
        except Exception as ex:
            logger.debug(f"[{self.__class__.__name__}][{self.client_id}][{self.instance.pk}]"
                         f"[_handler_popular_data] {ex}")
            self._data[self.field] = 0
            self._trans_amount_column = None


class TaxChargedReturnedCalculate(TaxChargedShippedCalculate):
    def _handler_popular_data(self):
        try:
            super()._handler_popular_data()
            if self._trans_amount_column is None:
                self._trans_amount_column = self.instance.tax_charged
            self._data[self.field] = abs(self._trans_amount_column) * -1
        except Exception as ex:
            logger.debug(f"[{self.__class__.__name__}][{self.client_id}][{self.instance.pk}]"
                         f"[_handler_popular_data] {ex}")
            self._data[self.field] = 0
            self._trans_amount_column = None


class DropshipFeeReturnedCalculate(TransBaseSaleItemFinancialCalculate):
    field = 'warehouse_processing_fee'

    def _handler_popular_data(self):
        self._data[self.field] = 0


class ShippingChargedReturnedCalculate(TransBaseSaleItemFinancialCalculate):
    field = 'shipping_charged'

    def _handler_popular_data(self):
        self._data[self.field] = 0


class OtherChannelFeesReturnedCalculate(OtherChannelFeesShippedCalculate):
    pass


class RefundedQuantityReturnedCalculate(RefundedQuantityShippedCalculate):
    def get_trans_amount(self):
        amount = super().get_trans_amount()
        if amount is None:
            amount = self.instance.refunded_quantity
        return amount


class ReturnPostageBillingReturnedCalculate(ReturnPostageBillingCalculate):
    model_instance = SaleItemFinancial


class CalculateTransSaleItemsReturnedManage(CalculateTransSaleItemsManage):
    JOB_ACCEPT = [TRANS_DATA_EVENT_JOB, BULK_SYNC_LIVE_FEED_JOB, LIVE_FEED_JOB, SALE_ITEM_FINANCIAL_JOB,
                  BULK_SYNC_TRANS_DATA_EVENT_JOB]
    CALCULATED_CONFIG = [SaleDateReturnedCalculate, SaleChargedReturnedCalculate, RefundAdminFeeReturnedCalculate,
                         ShippingCostReturnedCalculate, CogReturnedCalculate, InboundFreightCostShippedCalculate,
                         OutboundFreightCostShippedCalculate, ChannelTaxWithheldReturnedCalculate,
                         ChannelListingFeeReturnedCalculate, TaxChargedReturnedCalculate, DropshipFeeReturnedCalculate,
                         ShippingChargedReturnedCalculate, OtherChannelFeesReturnedCalculate,
                         RefundedQuantityReturnedCalculate, ReturnPostageBillingReturnedCalculate]
