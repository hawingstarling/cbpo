import logging
from decimal import Decimal
from django.db.models import Sum, Q
from django.utils import timezone
from app.financial.models import SaleItemTransaction, FulfillmentChannel, SaleItem, SaleStatus
from app.financial.services.brand_settings.ship_cost_calculation_adapter import ShipCostCalculationAdapter
from app.financial.services.fedex_shipment.config import FEDEX_SHIPMENT_ONE
from app.financial.variable.fulfillment_type import FULFILLMENT_FBA, FULFILLMENT_MFN, FULFILLMENT_MFN_PRIME, \
    FULFILLMENT_MFN_RA, FULFILLMENT_MFN_DS
from app.financial.variable.job_status import TRANS_DATA_EVENT_JOB, BULK_SYNC_LIVE_FEED_JOB, LIVE_FEED_JOB, \
    BULK_SYNC_TRANS_DATA_EVENT_JOB
from app.financial.services.transaction.calculate.base import TransBaseSaleItemCalculate, CalculateFieldManage
from app.financial.services.utils.common import round_currency
from app.financial.variable.sale_status_static_variable import SALE_REFUNDED_STATUS, SALE_PARTIALLY_REFUNDED_STATUS
from app.financial.variable.shipping_cost_source import AMZ_POSTAGE_BILLING_SOURCE_KEY, \
    AMZ_FBA_FULFILLMENT_FEE_SOURCE_KEY, AMZ_SELLER_CENTRAL_SOURCE_KEY, BRAND_SETTING_SOURCE_KEY, SHIP_CARRIER_FEDEX, \
    FEDEX_SHIPMENT_SOURCE_KEY, SHIPPING_COST_ACCURACY_BY_SOURCE

logger = logging.getLogger(__name__)


class ShippingCostCalculate(TransBaseSaleItemCalculate):
    field = 'actual_shipping_cost'
    estimated_field = 'estimated_shipping_cost'
    field_accuracy = 'shipping_cost_accuracy'
    field_source = 'shipping_cost_source'

    def __init__(self, client_id: str, filters: dict, instance: SaleItem, *args, **kwargs):
        super().__init__(client_id=client_id, filters=filters, instance=instance, *args, **kwargs)
        self.sale_item_queryset = self.sale_instance.saleitem_set.tenant_db_for(self.client_id) \
            .filter(~Q(ship_carrier=SHIP_CARRIER_FEDEX))
        self.is_calculated_by_fedex = self.get_status_calculated_by_fedex()

    @property
    def accuracy_original(self):
        values = (
            getattr(self.instance, self.field_accuracy) or 0,
            self.validated_data.get(self.field_accuracy) or 0
        )
        return max(values)

    @property
    def total_item(self):
        return self.sale_item_queryset.count()

    @property
    def total_quantity(self):
        agg = self.sale_item_queryset.aggregate(count=Sum('quantity'))
        return agg['count']

    def _split_by_amount_by_quantity(self, amount: any = None):
        try:
            assert amount is not None, \
                "The amount/amount_refund_postage_billing must exist one value numeric"
            if self.fulfillment_type_name == FULFILLMENT_FBA:
                self._data[self.field_source] = AMZ_FBA_FULFILLMENT_FEE_SOURCE_KEY
            else:
                self._data[self.field_source] = AMZ_POSTAGE_BILLING_SOURCE_KEY
            self._data[self.field_accuracy] = SHIPPING_COST_ACCURACY_BY_SOURCE[self._data[self.field_source]]
        except Exception as ex:
            logger.debug(f"[{self.__class__.__name__}][{self.client_id}][{self.instance.pk}]"
                         f"[_split_by_amount_by_quantity][set_source_and_accuracy] {ex}")
        try:
            if amount is not None and self.fulfillment_type_name.startswith(FULFILLMENT_MFN) and \
                    self._data[self.field_source] == AMZ_POSTAGE_BILLING_SOURCE_KEY:
                self.sale_item_queryset = self.sale_item_queryset \
                    .filter(fulfillment_type__name__startswith=FULFILLMENT_MFN)
                amount_item = amount / self.total_quantity
                amount = amount_item * self.instance.quantity
        except Exception as ex:
            logger.debug(f"[{self.__class__.__name__}][{self.client_id}][{self.instance.pk}]"
                         f"[_split_by_amount_by_quantity][calculate_amount] {ex}")
        return amount

    def _get_shipping_cost_other_source(self):
        amount = None
        try:
            # priority if source ins is BrandSetting
            if self.instance.estimated_shipping_cost is not None \
                    and self.instance.brand is not None \
                    and self.instance.shipping_cost_source == BRAND_SETTING_SOURCE_KEY \
                    and self.sale_status.value not in [SALE_REFUNDED_STATUS]:
                amount = self.instance.estimated_shipping_cost * -1
                self._data[self.field_source] = BRAND_SETTING_SOURCE_KEY
                self._data[self.field_accuracy] = self.instance.shipping_cost_accuracy
                return amount
            brand_setting, accuracy = self.get_brand_setting_esc_accuracy()
            if brand_setting is None or ((accuracy or 0) < self.min_accuracy_value
                                         and self.validated_data.get(self.estimated_field) is not None):
                # calculate from /v1/<sc_method>/sale_items
                amount = self.validated_data[self.estimated_field] * -1
                self._data[self.field_source] = AMZ_SELLER_CENTRAL_SOURCE_KEY
                self._data[self.field_accuracy] = SHIPPING_COST_ACCURACY_BY_SOURCE[self._data[self.field_source]]
            else:
                # calculate from brand setting
                if self.fulfillment_type_name.startswith(FULFILLMENT_MFN):
                    sale_stats = self.sale_instance.saleitem_set \
                        .tenant_db_for(self.sale_instance.client_id).values("sale_id", "brand_id") \
                        .annotate(sum_sku_quantity=Sum('quantity'))
                    if self.fulfillment_type_name == FULFILLMENT_MFN_RA:
                        amount = ShipCostCalculationAdapter.calc_for_mfn_for_rapid_access(brand_setting,
                                                                                          self.instance, sale_stats)
                    elif self.fulfillment_type_name == FULFILLMENT_MFN_DS:
                        amount = ShipCostCalculationAdapter.calc_for_mfn_for_drop_ship(brand_setting, self.instance)
                    else:
                        amount = ShipCostCalculationAdapter.calc_for_mfn(brand_setting, self.instance, sale_stats)
                elif self.fulfillment_type_name == FULFILLMENT_FBA:
                    amount = ShipCostCalculationAdapter.calc_for_fba(brand_setting, self.instance)
                else:
                    pass
                amount = Decimal(f"{amount}") * -1
                self._data[self.field_source] = BRAND_SETTING_SOURCE_KEY
                self._data[self.field_accuracy] = accuracy
        except Exception as ex:
            logger.debug(f"[{self.__class__.__name__}][{self.client_id}][{self.instance.pk}]"
                         f"[_get_shipping_cost_other_source] {ex}")
        return amount

    def _get_shipping_cost_fedex_source(self):
        amount = None
        try:
            if self.instance.shipping_cost_source == FEDEX_SHIPMENT_SOURCE_KEY:
                amount = self.instance.shipping_cost * -1
                self._data[self.field_source] = FEDEX_SHIPMENT_SOURCE_KEY
                self._data[self.field_accuracy] = SHIPPING_COST_ACCURACY_BY_SOURCE[FEDEX_SHIPMENT_SOURCE_KEY]
                return amount
            fedex_shipments = self.get_fedex_shipment()
            assert fedex_shipments is not None, "FedEx shipment is not empty"
            agg = self.sale_instance.saleitem_set.tenant_db_for(self.sale_instance.client_id) \
                .filter(ship_carrier__icontains=SHIP_CARRIER_FEDEX) \
                .aggregate(count=Sum('quantity'))
            net_charge_amount = fedex_shipments.aggregate(amount=Sum('net_charge_amount'))
            amount = (net_charge_amount['amount'] / agg["count"]) * self.instance.quantity * -1
            #
            self._data[self.field_source] = FEDEX_SHIPMENT_SOURCE_KEY
            self._data[self.field_accuracy] = SHIPPING_COST_ACCURACY_BY_SOURCE[FEDEX_SHIPMENT_SOURCE_KEY]
            #
            if fedex_shipments.filter(~Q(status=FEDEX_SHIPMENT_ONE)).count() > 0:
                fedex_shipments.update(status=FEDEX_SHIPMENT_ONE, matched_sales=[self.sale_instance.id],
                                       matched_channel_sale_ids=[self.sale_instance.channel_sale_id],
                                       matched_time=timezone.now())
        except Exception as ex:
            logger.debug(f"[{self.__class__.__name__}][{self.client_id}][{self.instance.pk}]"
                         f"[_get_shipping_cost_fedex_source] {ex}")
        return amount

    def summary_amount(self, amount):
        if amount is None:
            amount = self._get_shipping_cost_other_source()
        try:
            assert self.fulfillment_type_name.startswith(FULFILLMENT_MFN) and \
                   self.fulfillment_type_name != FULFILLMENT_MFN_PRIME and \
                   self.sale_status.value in [SALE_REFUNDED_STATUS], f"The amount not enough conditions double"
            amount *= 2
        except Exception as ex:
            logger.debug(f"[{self.__class__.__name__}][{self.client_id}][{self.instance.pk}]"
                         f"[summary_amount] {ex}")

        assert amount is not None, \
            f"The amount/amount_refund_postage_billing must exist one value numeric"

        if amount is not None:
            amount = Decimal(f"{amount}")
        return amount

    def get_status_calculated_by_fedex(self) -> bool:
        try:
            return self.fulfillment_type_name.startswith(FULFILLMENT_MFN) \
                and ((self.instance.ship_carrier and SHIP_CARRIER_FEDEX in self.instance.ship_carrier)
                     or SHIP_CARRIER_FEDEX in self.validated_data['ship_carrier'])
        except Exception as ex:
            logger.debug(f"[{self.__class__.__name__}][{self.client_id}][{self.instance.pk}]"
                         f"[is_accept_calculated_by_event] {ex}")
        return False

    def get_trans_amount(self):
        try:
            if self.is_calculated_by_fedex:
                amount = self._get_shipping_cost_fedex_source()
            else:
                amount = SaleItemTransaction().shipping_cost(self.client_id, self.filters, **self.kwargs)
                amount = self._split_by_amount_by_quantity(amount)
            amount = self.summary_amount(amount)
            if self.data[self.field_source] in [
                AMZ_POSTAGE_BILLING_SOURCE_KEY,
                AMZ_FBA_FULFILLMENT_FEE_SOURCE_KEY,
                FEDEX_SHIPMENT_SOURCE_KEY,
                AMZ_SELLER_CENTRAL_SOURCE_KEY
            ]:
                self._trans_amount_column = amount
            amount = self.format_trans_amount(amount)
        except Exception as ex:
            logger.debug(f"[{self.__class__.__name__}][{self.client_id}][{self.instance.pk}]get_trans_amount {ex}")
            amount = None
        return amount

    def _handler_popular_data(self):
        # calculate accuracy
        amount = self.get_trans_amount()
        assert amount is not None, f"amount calculated is not None"
        if self.data[self.field_accuracy] == self.max_accuracy_value:
            self._data[self.field] = amount
        else:
            self._data[self.estimated_field] = amount


class TaxChargedCalculate(TransBaseSaleItemCalculate):
    field = 'tax_charged'

    def get_trans_amount(self):
        try:
            amount = SaleItemTransaction().tax_charged(self.client_id, self.filters, **self.kwargs)
        except Exception as ex:
            logger.debug(f"[{self.__class__.__name__}][{self.client_id}][{self.instance.pk}]get_trans_amount {ex}")
            amount = None
        return amount

    def _handler_popular_data(self):
        amount = self.get_trans_amount()
        if amount is not None:
            #
            self._trans_amount_column = amount
            #
            amount = self.format_trans_amount(amount)
            self._data[self.field] = amount


class ChannelListingFeeCalculate(TransBaseSaleItemCalculate):
    field = 'channel_listing_fee'
    field_accuracy = 'channel_listing_fee_accuracy'
    min_accuracy_value = 80

    @property
    def sale_charged(self):
        try:
            amount = self.validated_data['sale_charged']
        except Exception as ex:
            amount = 0
        return float(amount)

    def get_trans_amount(self):
        try:
            amount = SaleItemTransaction().channel_listing_fee(self.client_id, self.filters,
                                                               **self.kwargs)  # from trans event
        except Exception as ex:
            logger.debug(f"[{self.__class__.__name__}][{self.instance.pk}]get_trans_amount {ex}")
            amount = None
        return amount

    def _handler_popular_data(self):
        amount = self.get_trans_amount()
        if amount is not None:
            #
            self._trans_amount_column = amount
            #
            amount = self.format_trans_amount(amount)
            self._data[self.field] = amount
            self._data[self.field_accuracy] = self.max_accuracy_value
            return
        if self.instance.channel_listing_fee_accuracy < self.max_accuracy_value and self.sale_charged > 0:
            self._data[self.field] = round_currency(self.sale_charged * 0.15)
            self._data[self.field_accuracy] = self.min_accuracy_value
            return


class OtherChannelFeesCalculate(TransBaseSaleItemCalculate):
    field = 'other_channel_fees'

    def get_trans_amount(self):
        try:
            amount = SaleItemTransaction().other_channel_fees(self.client_id, self.filters, **self.kwargs)
        except Exception as ex:
            logger.debug(f"[{self.__class__.__name__}][{self.instance.pk}]get_trans_amount {ex}")
            amount = None
        return amount

    def _handler_popular_data(self):
        amount = self.get_trans_amount()
        if amount is not None:
            #
            self._trans_amount_column = amount
            #
            amount = self.format_trans_amount(amount)
            self._data[self.field] = amount


class SaleStatusCalculate(TransBaseSaleItemCalculate):
    field = 'sale_status'

    @property
    def trans_sale_status(self):
        try:
            value = SaleItemTransaction.sale_status_of_sale_level(self.client_id, self.filters, **self.kwargs)
            if value:
                value = SaleStatus.objects.tenant_db_for(self.client_id).get(value=value)
        except Exception as ex:
            logger.debug(f"[{self.__class__.__name__}][trans_sale_status]: {ex}")
            value = None
        return value

    def _handler_popular_data(self):
        sale_status = self.trans_sale_status
        if sale_status:
            self._data[self.field] = sale_status


class RefundedQuantityCalculate(TransBaseSaleItemCalculate):
    field = 'refunded_quantity'

    def get_trans_amount(self):
        try:
            amount = SaleItemTransaction().refunded_quantity(self.client_id, self.filters, **self.kwargs)
        except Exception as ex:
            logger.debug(f"[{self.__class__.__name__}][{self.client_id}][{self.instance.pk}]"
                         f"[trans_refunded_quantity]: {ex}")
            amount = None
        return amount

    def _handler_popular_data(self):
        quantity = self.get_trans_amount()
        if quantity:
            self._data[self.field] = int(quantity)


class ReimbursementCostsCalculate(TransBaseSaleItemCalculate):
    field = 'reimbursement_costs'

    def get_trans_amount(self):
        try:
            amount = SaleItemTransaction().reimbursement_costs(self.client_id, self.filters, **self.kwargs)
        except Exception as ex:
            logger.debug(f"[{self.__class__.__name__}][{self.client_id}][{self.instance.pk}]get_trans_amount {ex}")
            amount = None
        return amount

    def _handler_popular_data(self, *args, **kwargs):
        amount = self.get_trans_amount()
        if amount is not None:
            #
            self._trans_amount_column = amount
            #
            amount = self.format_trans_amount(amount)
            self._data[self.field] = amount


class ChannelTaxWithheldCalculate(TransBaseSaleItemCalculate):
    field = 'channel_tax_withheld'
    field_accuracy = 'channel_tax_withheld_accuracy'

    def get_trans_amount(self):
        try:
            amount = SaleItemTransaction().channel_tax_withheld(self.client_id, self.filters,
                                                                **self.kwargs)  # from trans event
        except Exception as ex:
            logger.debug(f"[{self.__class__.__name__}][{self.client_id}][{self.instance.pk}]get_trans_amount {ex}")
            amount = None
        return amount

    def _handler_popular_data(self):
        amount = self.get_trans_amount()
        if amount is not None:
            self._trans_amount_column = amount
            self._data[self.field] = self.format_trans_amount(amount)
            self._data[self.field_accuracy] = self.max_accuracy_value


class RefundAdminFeeCalculate(TransBaseSaleItemCalculate):
    field = 'refund_admin_fee'

    def get_trans_amount(self):
        try:
            amount = SaleItemTransaction().refund_admin_fee(self.client_id, self.filters,
                                                            **self.kwargs)  # from trans event
        except Exception as ex:
            logger.debug(f"[{self.__class__.__name__}][{self.client_id}][{self.instance.pk}][get_trans_amount] {ex}")
            amount = None
        return amount

    def _handler_popular_data(self):
        amount = self.get_trans_amount()
        if amount is not None:
            self._trans_amount_column = amount
            self._data[self.field] = self.format_trans_amount(amount)


class SaleChargedCalculate(TransBaseSaleItemCalculate):
    field = 'sale_charged'
    field_accuracy = 'sale_charged_accuracy'

    def get_trans_amount(self):
        try:
            amount = SaleItemTransaction().sale_charged(self.client_id, self.filters, **self.kwargs)  # from trans event
        except Exception as ex:
            logger.debug(f"[{self.__class__.__name__}][{self.client_id}][{self.instance.pk}]"
                         f"[{self.event}][get_trans_amount] {ex}")
            amount = None
        return amount

    def _handler_popular_data(self):
        amount = self.get_trans_amount()
        if amount is not None:
            self._trans_amount_column = amount
            self._data[self.field] = self.format_trans_amount(amount)
            self._data[self.field_accuracy] = self.max_accuracy_value


class InboundFreightCostCalculate(TransBaseSaleItemCalculate):
    field = 'inbound_freight_cost'

    def get_trans_amount(self):
        amount = None
        try:
            if self.sale_status.value in [SALE_REFUNDED_STATUS] and self.fulfillment_type.name not in [FULFILLMENT_MFN]:
                amount = 0
        except Exception as ex:
            logger.debug(f"[{self.__class__.__name__}][{self.client_id}][{self.instance.pk}]"
                         f"[{self.event}]get_trans_amount {ex}")
        return amount

    def _handler_popular_data(self):
        amount = self.get_trans_amount()
        if amount is not None:
            self._data[self.field] = amount


class OutboundFreightCostCalculate(TransBaseSaleItemCalculate):
    field = 'outbound_freight_cost'

    def get_trans_amount(self):
        amount = None
        try:
            if self.sale_status.value in [SALE_REFUNDED_STATUS] and self.fulfillment_type.name not in [FULFILLMENT_MFN]:
                amount = 0
        except Exception as ex:
            logger.debug(f"[{self.__class__.__name__}][{self.client_id}][{self.instance.pk}]"
                         f"[{self.event}]get_trans_amount {ex}")
        return amount

    def _handler_popular_data(self):
        amount = self.get_trans_amount()
        if amount is not None:
            self._data[self.field] = amount


class ReturnPostageBillingCalculate(TransBaseSaleItemCalculate):
    field = 'return_postage_billing'

    def get_trans_amount(self):
        try:
            assert self.fulfillment_type_name.startswith(FULFILLMENT_MFN), \
                f"The fulfillment type is not {FULFILLMENT_MFN}"
            amount_summary = SaleItemTransaction().return_postage_billing(self.client_id, self.filters,
                                                                          **self.kwargs)  # from trans event
            total_quantity = self.sale_instance.saleitem_set.tenant_db_for(self.client_id) \
                .aggregate(count=Sum("quantity"))
            amount_item = amount_summary / total_quantity["count"]
            amount = amount_item * self.instance.quantity
        except Exception as ex:
            logger.debug(f"[{self.__class__.__name__}][{self.client_id}][{self.instance.pk}][get_trans_amount] {ex}")
            amount = None
        return amount

    def _handler_popular_data(self):
        amount = self.get_trans_amount()
        if amount is not None:
            self._trans_amount_column = amount
            self._data[self.field] = self.format_trans_amount(amount)


class CalculateTransSaleItemsManage(CalculateFieldManage):
    JOB_ACCEPT = [LIVE_FEED_JOB, BULK_SYNC_LIVE_FEED_JOB, TRANS_DATA_EVENT_JOB, BULK_SYNC_TRANS_DATA_EVENT_JOB]
    CALCULATED_CONFIG = [ShippingCostCalculate, TaxChargedCalculate, ChannelListingFeeCalculate,
                         OtherChannelFeesCalculate, SaleStatusCalculate, RefundedQuantityCalculate,
                         ReimbursementCostsCalculate, ChannelTaxWithheldCalculate, RefundAdminFeeCalculate,
                         SaleChargedCalculate, InboundFreightCostCalculate, OutboundFreightCostCalculate,
                         ReturnPostageBillingCalculate]

    @property
    def filters(self):
        return {
            'client': self.instance.sale.client,
            'channel_sale_id': self.instance.sale.channel_sale_id,
            'channel': self.instance.sale.channel,
            'sku': self.instance.sku,
        }

    @property
    def validated_data(self):
        return self.kwargs.get('validated_data', {})

    @property
    def is_fulfillment_type_fba(self):
        fulfillment_type = self.instance.fulfillment_type
        if not fulfillment_type or not isinstance(fulfillment_type,
                                                  FulfillmentChannel) or fulfillment_type.name not in ['FBA']:
            return False
        return True

    def calculate_object(self):
        if not self.data:
            return
        self.calculate_cogs_by_sale_status()
        self.calculate_total_financial_amount()
        # set financial_dirty
        self.update_financial_dirty()

    def update_financial_dirty(self):
        if self.data:
            self.data.update({'financial_dirty': True})

    def calculate_total_financial_amount(self):
        # update field total financial amount if value > 0
        total_financial_amount = round_currency(self.total_financial_amount)
        self.data.update({'total_financial_amount': total_financial_amount})

    def calculate_cogs_by_sale_status(self):
        try:
            assert self.kwargs["is_remove_cogs_refunded"] is True, "client not support remove cogs refunded"
            assert "refunded_quantity" in self.data and "sale_status" in self.data \
                   and self.data["refunded_quantity"] > 0 \
                   and self.data["sale_status"].value == SALE_PARTIALLY_REFUNDED_STATUS, \
                "not found refunded_quantity or sale_status"
            cog = self.instance.unit_cog * (self.instance.quantity - self.data["refunded_quantity"])
            self.data.update(dict(cog=cog))
        except Exception as ex:
            logger.debug(f"[{self.__class__.__name__}][{self.client_id}][calculate_cogs_refunded] {ex}")

    def process(self):
        try:
            for class_cal in self.CALCULATED_CONFIG:
                cal = class_cal(client_id=self.client_id, filters=self.filters, instance=self.instance, *self.args,
                                **self.kwargs)
                cal.calculate()
                data = cal.data
                trans_amount_column = cal.trans_amount_column

                if not trans_amount_column and not data:
                    logger.debug(f"[{self.__class__.__name__}][{self.client_id}][process][{cal.__class__.__name__}] "
                                 f"not found data calculated")
                    continue

                # update field calculate if has data
                if data:
                    self.data.update(data)

                # summary trans amount
                if trans_amount_column:
                    self.total_financial_amount += Decimal(f"{trans_amount_column}")

            self.calculate_object()
        except Exception as ex:
            logger.error(f"[{self.__class__.__name__}][{self.client_id}][process] {ex}")
            self.data = {}
        return self.data
