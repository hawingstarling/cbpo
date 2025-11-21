import logging
from rest_framework import serializers
from app.core.utils import get_nested_attr
from app.financial.sub_serializers.client_serializer import ClientSaleItemSerializer, ClientSaleSerializer
from app.financial.models import SaleItemFinancial, AppEagleProfile, SaleItem

logger = logging.getLogger(__name__)


# LOG INFO SALE
class ClientSaleLogSerializer(ClientSaleSerializer):
    class Meta(ClientSaleSerializer.Meta):
        fields = ['channel_sale_id', 'channel', 'sale_status', 'profit_status', 'date', 'customer_name',
                  'recipient_name', 'address_line_1', 'address_line_2', 'address_line_3', 'state', 'city', 'country',
                  'postal_code', 'state_key', 'county_key', 'is_prime', 'is_removed', 'is_replacement_order',
                  'replaced_order_id']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['channel'] = get_nested_attr(instance, 'channel.name')
        data['sale_status'] = get_nested_attr(instance, 'sale_status.value')
        data['profit_status'] = get_nested_attr(
            instance, 'profit_status.value')
        return data

    @property
    def log_data(self):
        if self.instance:
            data = self.data
        else:
            data = self.data
            data['channel'] = None
            data['sale_status'] = None
            data['profit_status'] = None
            data['date'] = None
            data['state'] = None
            data['city'] = None
            data['country'] = None
            data['postal_code'] = None
            data['state_key'] = None
            data['county_key'] = None
            data['customer_name'] = None
            data['address_line_1'] = None
            data['address_line_2'] = None
            data['address_line_3'] = None
            data['is_prime'] = False
        rs = {key: str(data[key]) if data[key]
                                     is not None else None for key in sorted(data.keys())}
        return rs


# LOG INFO SALE ITEM
class SaleItemLogSerializer(ClientSaleItemSerializer):
    sale_date = serializers.DateTimeField(default=None)
    quantity = serializers.IntegerField(default=1)
    additional_shipping_charged = serializers.SerializerMethodField(
        read_only=True)

    class Meta(ClientSaleItemSerializer.Meta):
        fields = ['sku', 'upc', 'brand', 'brand_sku', 'asin', 'quantity', 'size', 'style', 'title', 'sale_charged',
                  'sale_charged_accuracy', 'additional_shipping_charged', 'tax_charged', 'cog', 'unit_cog',
                  'cog_source', 'estimated_shipping_cost', 'actual_shipping_cost', 'shipping_cost_accuracy',
                  'shipping_cost_source', 'notes', 'sale_status', 'profit_status', 'channel_listing_fee',
                  'channel_listing_fee_accuracy', 'other_channel_fees', 'ship_date', 'sale_date', 'refunded_quantity',
                  'fulfillment_type', 'fulfillment_type_accuracy', 'is_removed', 'total_financial_amount',
                  'warehouse_processing_fee', 'warehouse_processing_fee_accuracy', 'reimbursement_costs', 'segment',
                  'inbound_freight_cost', 'inbound_freight_cost_accuracy', 'outbound_freight_cost',
                  'outbound_freight_cost_accuracy', 'strategy_id', 'channel_tax_withheld',
                  'channel_tax_withheld_accuracy', 'refund_admin_fee', 'tracking_fedex_id', 'user_provided_cost',
                  'ship_carrier', 'product_number', 'product_type', 'parent_asin', 'return_postage_billing',
                  'label_cost', 'label_type']
        read_only_fields = []

    @classmethod
    def get_additional_shipping_charged(cls, instance) -> dict:
        return instance.shipping_charged

    @property
    def log_data(self):
        if self.instance:
            data = self.data
        else:
            data = self.data
            data['additional_shipping_charged'] = None
            data['size'] = None
            data['style'] = None
            data['brand'] = None
            data['sale_status'] = None
            data['profit_status'] = None
            data['fulfillment_type'] = None
            data['refunded_quantity'] = None
            data['ae_profile_name'] = None
        rs = {
            key: str(data[key]) if data[key] else None for key in sorted(data.keys())
        }
        return rs

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['size'] = get_nested_attr(instance, 'size.value')
        data['style'] = get_nested_attr(instance, 'style.value')
        data['brand'] = get_nested_attr(instance, 'brand.name')
        data['sale_status'] = get_nested_attr(instance, 'sale_status.value')
        data['profit_status'] = get_nested_attr(
            instance, 'profit_status.value')
        data['fulfillment_type'] = get_nested_attr(
            instance, 'fulfillment_type.name')
        data['ae_profile_name'] = self.get_appeagle_attr(instance)
        self.reformat_fields_accuracy(instance, data)
        return data

    def reformat_fields_accuracy(self, instance: SaleItem, data: dict) -> None:
        for key, value in data.items():
            if key.endswith("_accuracy"):
                try:
                    if value is None:
                        value = 0
                    data[key] = f"{value}%"
                except Exception as ex:
                    logger.debug(
                        f"[{self.__class__.__name__}][reformat_fields_accuracy][{instance}][{key}] {ex}")

    def get_appeagle_attr(self, instance) -> str:
        try:
            assert instance.strategy_id is not None, f"The strategy_id is not None"
            val = AppEagleProfile.objects.tenant_db_for(self.client_id) \
                .get(client_id=instance.client_id,
                     profile_id=instance.strategy_id).profile_name
        except Exception as ex:
            logger.debug(
                f"[{self.__class__.__name__}][get_appeagle_attr][{instance}] {ex}")
            val = None
        return val


class SaleItemFinancialLogSerializer(SaleItemLogSerializer):
    class Meta(SaleItemLogSerializer.Meta):
        model = SaleItemFinancial
