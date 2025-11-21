import logging

from app.financial.models import SaleStatus, SaleItemFinancial
from app.financial.services.transaction.calculate.sale_item import CalculateTransSaleItemsManage, \
    ChannelListingFeeCalculate, TaxChargedCalculate, ChannelTaxWithheldCalculate, SaleChargedCalculate, \
    ShippingCostCalculate, RefundAdminFeeCalculate, OtherChannelFeesCalculate, RefundedQuantityCalculate, \
    InboundFreightCostCalculate, OutboundFreightCostCalculate, ReturnPostageBillingCalculate
from app.financial.services.transaction.calculate.base import TransBaseSaleItemFinancialCalculate
from app.financial.services.utils.common import round_currency
from app.financial.variable.fulfillment_type import FULFILLMENT_MFN, FULFILLMENT_FBA, FULFILLMENT_MFN_PRIME
from app.financial.variable.sale_status_static_variable import SALE_SHIPPED_STATUS
from app.financial.variable.job_status import TRANS_DATA_EVENT_JOB, BULK_SYNC_LIVE_FEED_JOB, LIVE_FEED_JOB, \
    SALE_ITEM_FINANCIAL_JOB, BULK_SYNC_TRANS_DATA_EVENT_JOB

logger = logging.getLogger(__name__)


class SaleStatusShippedCalculate(TransBaseSaleItemFinancialCalculate):
    field = 'sale_status'

    def _handler_popular_data(self):
        self._data[self.field] = SaleStatus.objects.tenant_db_for(self.client_id).get(value=SALE_SHIPPED_STATUS)


class ReimbursementCostShippedCalculate(TransBaseSaleItemFinancialCalculate):
    field = 'reimbursement_costs'

    def _handler_popular_data(self):
        self._data[self.field] = 0


class RefundAdminFeeShippedCalculate(RefundAdminFeeCalculate):
    model_instance = SaleItemFinancial

    def get_trans_amount(self):
        amount = super().get_trans_amount()
        if amount is None:
            amount = 0
        return amount


class ChannelTaxWithheldShippedCalculate(ChannelTaxWithheldCalculate):
    model_instance = SaleItemFinancial


class TaxChargedShippedCalculate(TaxChargedCalculate):
    model_instance = SaleItemFinancial


class ChannelListingFeeShippedCalculate(ChannelListingFeeCalculate):
    model_instance = SaleItemFinancial


class SaleChargedShippedCalculate(SaleChargedCalculate):
    model_instance = SaleItemFinancial


class ShippingCostShippedCalculate(ShippingCostCalculate):
    model_instance = SaleItemFinancial

    def _get_shipping_cost_other_source(self):
        amount = super()._get_shipping_cost_other_source()
        if amount is None:
            amount = 0
        return amount

    def summary_amount(self, amount, amount_refund_postage_billing):
        if amount is None and not self.amz_source:
            amount = self._get_shipping_cost_other_source()
        return amount


class OtherChannelFeesShippedCalculate(OtherChannelFeesCalculate):
    model_instance = SaleItemFinancial

    def get_trans_amount(self):
        amount = super().get_trans_amount()
        if amount is None:
            amount = 0
        return amount


class RefundedQuantityShippedCalculate(RefundedQuantityCalculate):
    model_instance = SaleItemFinancial

    def get_trans_amount(self):
        return 0


class InboundFreightCostShippedCalculate(InboundFreightCostCalculate):
    model_instance = SaleItemFinancial

    def get_trans_amount(self):
        try:
            if self.fulfillment_type.name in [FULFILLMENT_MFN, FULFILLMENT_MFN_PRIME, FULFILLMENT_FBA]:
                brand_setting = self.get_brand_setting()
                amount = round_currency(brand_setting.est_unit_freight_cost * self.instance.quantity)
            else:
                amount = 0
        except Exception as ex:
            logger.debug(f"[{self.__class__.__name__}][{self.client_id}][{self.instance.pk}]"
                         f"[get_trans_amount] {ex}")
            amount = 0
        return amount


class OutboundFreightCostShippedCalculate(OutboundFreightCostCalculate):
    model_instance = SaleItemFinancial

    def get_trans_amount(self):
        try:
            if self.fulfillment_type.name in [FULFILLMENT_MFN, FULFILLMENT_MFN_PRIME, FULFILLMENT_FBA]:
                brand_setting = self.get_brand_setting()
                amount = round_currency(brand_setting.est_unit_freight_cost * self.instance.quantity)
            else:
                amount = 0
        except Exception as ex:
            logger.debug(f"[{self.__class__.__name__}][{self.client_id}][{self.instance.pk}]"
                         f"[get_trans_amount] {ex}")
            amount = 0
        return amount


class ReturnPostageBillingShippedCalculate(ReturnPostageBillingCalculate):
    model_instance = SaleItemFinancial

    def get_trans_amount(self):
        return 0


class CalculateTransSaleItemsShippedManage(CalculateTransSaleItemsManage):
    JOB_ACCEPT = [TRANS_DATA_EVENT_JOB, BULK_SYNC_LIVE_FEED_JOB, LIVE_FEED_JOB, SALE_ITEM_FINANCIAL_JOB,
                  BULK_SYNC_TRANS_DATA_EVENT_JOB]
    CALCULATED_CONFIG = [SaleStatusShippedCalculate, ReimbursementCostShippedCalculate, RefundAdminFeeShippedCalculate,
                         ChannelTaxWithheldShippedCalculate, TaxChargedShippedCalculate, SaleChargedShippedCalculate,
                         ChannelListingFeeShippedCalculate, ShippingCostShippedCalculate,
                         InboundFreightCostShippedCalculate,
                         OtherChannelFeesShippedCalculate, RefundedQuantityShippedCalculate]
