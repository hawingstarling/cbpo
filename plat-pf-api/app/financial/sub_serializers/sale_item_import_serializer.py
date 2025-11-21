from datetime import timedelta

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from app.core.context import AppContext
from app.financial.import_template.validation.sale_item import fields as field_import, default_error_messages, get_label
from app.financial.models import SaleItem, Channel, Brand, BrandMissing
from app.financial.sub_serializers.client_serializer import ClientSaleItemSerializer
from app.financial.variable.profit_status_static_variable import PROFIT_STATUS_ENUM, PROFIT_STATUS_ORDER_DICT
from app.financial.variable.sale_status_static_variable import SALE_STATUS_ENUM, SALE_STATUS_ORDER_DICT
from app.financial.variable.shipping_cost_source import SHIP_CARRIER_LIST_TYPE


class ClientSaleItemsImportSerializer(ClientSaleItemSerializer):
    # sale info
    channel_sale_id = serializers.CharField(max_length=100, label=get_label('channel_sale_id'), required=True,
                                            error_messages=default_error_messages['channel_sale_id'],
                                            help_text='Provided by sale channel')
    channel = serializers.CharField(max_length=100, required=True, label=get_label('channel'),
                                    error_messages=default_error_messages['channel'],
                                    help_text="Name of the channel, e.g amazon.com")
    # address line info
    address_line_1 = serializers.CharField(max_length=100, required=False, allow_null=True, allow_blank=True,
                                           error_messages=default_error_messages['address_line_1'],
                                           help_text="The street address")
    address_line_2 = serializers.CharField(max_length=100, required=False, allow_null=True, allow_blank=True,
                                           error_messages=default_error_messages['address_line_2'],
                                           help_text="Additional street address information")
    address_line_3 = serializers.CharField(max_length=100, required=False, allow_null=True, allow_blank=True,
                                           error_messages=default_error_messages['address_line_3'],
                                           help_text="Additional street address information")

    # sale item
    brand = serializers.CharField(max_length=100, required=False, allow_null=True, allow_blank=True,
                                  help_text="Throw error if the value doesn’t exist in the lookup table")
    sku = serializers.CharField(max_length=100, required=True, allow_null=False, allow_blank=False,
                                error_messages=default_error_messages['sku'], label=get_label('sku'),
                                help_text="Stock keeping unit")
    title = serializers.CharField(max_length=255, required=False, allow_null=True, allow_blank=True,
                                  error_messages=default_error_messages['title'], label=get_label('title'))
    asin = serializers.CharField(max_length=10, required=False, allow_null=True, allow_blank=True,
                                 error_messages=default_error_messages['asin'], label=get_label('asin'),
                                 help_text="Amazon Standard Identification Number")
    upc = serializers.CharField(max_length=13, write_only=True, required=False, allow_null=True, allow_blank=True,
                                error_messages=default_error_messages['upc'], label=get_label('upc'),
                                help_text="Universal Product Code or EAN - European Article Number")
    # variations
    size = serializers.CharField(max_length=200, required=False, allow_blank=True, allow_null=True,
                                 error_messages=default_error_messages['size'])
    style = serializers.CharField(max_length=200, required=False, allow_blank=True, allow_null=True,
                                  error_messages=default_error_messages['style'])
    # sale status and profit status
    sale_status = serializers.ChoiceField(choices=SALE_STATUS_ENUM, required=False, allow_blank=True, allow_null=True,
                                          error_messages=default_error_messages['sale_status'],
                                          help_text=', '.join(SALE_STATUS_ORDER_DICT))
    profit_status = serializers.ChoiceField(choices=PROFIT_STATUS_ENUM, required=False, allow_blank=True,
                                            allow_null=True, help_text=', '.join(PROFIT_STATUS_ORDER_DICT),
                                            error_messages=default_error_messages['profit_status'])
    # charge and cost of item
    sale_charged = serializers.DecimalField(max_digits=6, decimal_places=2, allow_null=True, required=False,
                                            error_messages=default_error_messages['sale_charged'])
    shipping_charged = serializers.DecimalField(max_digits=6, decimal_places=2, allow_null=True, required=False,
                                                error_messages=default_error_messages['shipping_charged'],
                                                label=get_label('shipping_charged'))
    tax_charged = serializers.DecimalField(max_digits=6, decimal_places=2, allow_null=True, required=False,
                                           error_messages=default_error_messages['tax_charged'])
    cog = serializers.DecimalField(max_digits=6, decimal_places=2, required=False, allow_null=True,
                                   error_messages=default_error_messages['cog'], label=get_label('cog'))
    unit_cog = serializers.DecimalField(max_digits=6, decimal_places=2, required=False, allow_null=True,
                                        error_messages=default_error_messages['unit_cog'], label=get_label('unit_cog'))
    actual_shipping_cost = serializers.DecimalField(max_digits=6, decimal_places=2, allow_null=True, required=False,
                                                    error_messages=default_error_messages['actual_shipping_cost'])
    estimated_shipping_cost = serializers.DecimalField(max_digits=6, decimal_places=2, allow_null=True, required=False,
                                                       error_messages=default_error_messages['estimated_shipping_cost'])
    shipping_cost_accuracy = serializers.IntegerField(allow_null=True, required=False, min_value=0, max_value=100,
                                                      error_messages=default_error_messages['shipping_cost_accuracy'],
                                                      help_text="Percentage")
    sale_charged_accuracy = serializers.IntegerField(allow_null=True, required=False, min_value=0, max_value=100,
                                                     error_messages=default_error_messages['sale_charged_accuracy'],
                                                     help_text="Percentage")
    channel_listing_fee_accuracy = serializers.IntegerField(allow_null=True, required=False, min_value=0, max_value=100,
                                                            error_messages=default_error_messages[
                                                                'channel_listing_fee_accuracy'],
                                                            help_text="Percentage",
                                                            label=get_label('channel_listing_fee_accuracy'))
    tax_cost = serializers.DecimalField(max_digits=6, decimal_places=2, allow_null=True, required=False,
                                        error_messages=default_error_messages['tax_cost'])
    channel_listing_fee = serializers.DecimalField(max_digits=6, decimal_places=2, allow_null=True, required=False,
                                                   error_messages=default_error_messages['channel_listing_fee'],
                                                   label=get_label('channel_listing_fee'))
    other_channel_fees = serializers.DecimalField(max_digits=6, decimal_places=2, allow_null=True, required=False,
                                                  error_messages=default_error_messages['other_channel_fees'])
    inbound_freight_cost = serializers.DecimalField(max_digits=6, decimal_places=2, allow_null=True, required=False,
                                                    error_messages=default_error_messages['inbound_freight_cost'])
    inbound_freight_cost_accuracy = serializers.IntegerField(allow_null=True, required=False, min_value=0,
                                                             max_value=100,
                                                             error_messages=default_error_messages[
                                                                 'inbound_freight_cost_accuracy'],
                                                             help_text="Percentage")
    outbound_freight_cost = serializers.DecimalField(max_digits=6, decimal_places=2, allow_null=True, required=False,
                                                     error_messages=default_error_messages['outbound_freight_cost'])
    outbound_freight_cost_accuracy = serializers.IntegerField(allow_null=True, required=False, min_value=0,
                                                              max_value=100,
                                                              error_messages=default_error_messages[
                                                                  'outbound_freight_cost_accuracy'],
                                                              help_text="Percentage")
    channel_tax_withheld = serializers.DecimalField(max_digits=6, decimal_places=2, allow_null=True, required=False,
                                                    error_messages=default_error_messages['channel_tax_withheld'])
    channel_tax_withheld_accuracy = serializers.IntegerField(allow_null=True, required=False, min_value=0,
                                                             max_value=100,
                                                             error_messages=default_error_messages[
                                                                 'channel_tax_withheld_accuracy'],
                                                             help_text="Percentage")
    #
    ship_date = serializers.DateTimeField(required=False, allow_null=True,
                                          error_messages=default_error_messages['ship_date'])
    sale_date = serializers.DateTimeField(required=False, allow_null=True,
                                          error_messages=default_error_messages['sale_date'])
    notes = serializers.CharField(required=False, allow_blank=True, allow_null=True,
                                  error_messages=default_error_messages['notes'])
    tracking_fedex_id = serializers.CharField(max_length=100, required=False, allow_blank=True, allow_null=True,
                                              error_messages=default_error_messages['tracking_fedex_id'],
                                              label=get_label('tracking_fedex_id'))

    ship_carrier = serializers.CharField(max_length=100, required=False, allow_blank=True, allow_null=True,
                                         error_messages=default_error_messages['ship_carrier'],
                                         label=get_label('ship_carrier'), help_text=', '.join(SHIP_CARRIER_LIST_TYPE))
    # Style Number & Style Category & Parent ASIN
    product_number = serializers.CharField(
        max_length=255, required=False, allow_null=True, allow_blank=True,
        error_messages=default_error_messages['product_number'],
        label=get_label('product_number'),
        help_text="This will be the Style No. or the Material No. of the item."
    )
    product_type = serializers.CharField(
        max_length=255, required=False, allow_null=True, allow_blank=True,
        error_messages=default_error_messages['product_type'],
        label=get_label('product_type'),
        help_text="A classification or category under which a product is listed."
    )

    parent_asin = serializers.CharField(
        max_length=255, required=False, allow_null=True, allow_blank=True,
        error_messages=default_error_messages['parent_asin'],
        label=get_label('parent_asin'),
        help_text="This is a non-buyable entity that represents a group of related products. "
                  "It acts as a container for the various 'child' ASINs."
    )

    label_cost = serializers.DecimalField(
        max_digits=6, decimal_places=2, allow_null=True, required=False,
        error_messages=default_error_messages['label_cost'],
        help_text="The cost of the shipping label purchased via Amazon's Buy Shipping service for a given order. "
                  "This value is reported by Amazon SP-API and represents the amount charged to the seller. "
                  "It is useful for tracking fulfillment expenses and analyzing shipping efficiency."
    )

    class Meta:
        model = SaleItem
        fields = field_import

    def validate_channel(self, value):
        errors = []
        # validate channel name exist
        try:
            value = Channel.objects.tenant_db_for(self.client_id).get(name=value.lower())
        except Channel.DoesNotExist:
            errors.append('Channel name "{}" does not exist'.format(value))
        if errors:
            raise ValidationError(errors, code="channel_name")
        return value

    def validate_size(self, value):
        return self.validate_size_variant(value)

    def validate_style(self, value):
        return self.validate_style_variant(value)

    def validate(self, attrs):
        ship_date = attrs.get('ship_date')
        sale_date = attrs.get('sale_date')
        if ship_date and sale_date:
            if sale_date > ship_date:
                raise serializers.ValidationError("Ship Date should be greater than of Sale Date")
        product_number = attrs.get('product_number')
        product_type = attrs.get('product_type')
        if product_number or product_type:
            if not product_number:
                raise serializers.ValidationError("Style Number is required", code="product_number")
            if not product_type:
                raise serializers.ValidationError("Style Category is required", code="product_type")
        return attrs


class SaleItemsImportLiveFeedSerializer(ClientSaleItemsImportSerializer):
    channel_brand = serializers.CharField(max_length=100, required=False, allow_null=True, allow_blank=True)
    is_replacement_order = serializers.BooleanField(required=False, allow_null=True)
    replaced_order_id = serializers.CharField(max_length=50, required=False, allow_null=True, allow_blank=True)

    class Meta(ClientSaleItemsImportSerializer.Meta):
        fields = field_import + ['sale_charged_accuracy', 'channel_brand', 'fulfillment_type_accuracy',
                                 'warehouse_processing_fee', 'warehouse_processing_fee_accuracy', 'strategy_id',
                                 'tracking_fedex_id', 'ship_carrier', 'label_cost', 'label_type',
                                 'is_replacement_order', 'replaced_order_id']

    def validate(self, attrs):
        ship_date = attrs.get('ship_date')
        sale_date = attrs.get('sale_date')

        if ship_date and sale_date:
            if ship_date <= sale_date:
                ship_date = sale_date + timedelta(minutes=1)
                attrs.update({"ship_date": ship_date})

        brand = attrs.get('brand')
        # use live feed brand as amazon brand if it is available
        if brand:
            attrs.update({'channel_brand': brand.name})

        return attrs

    def validate_brand(self, value):
        if not value:
            return None
        client_id = AppContext.instance().client_id
        try:
            value = Brand.objects.tenant_db_for(client_id).get(name=value, client_id=client_id)
        except Brand.DoesNotExist:
            brand_missing = BrandMissing.all_objects.tenant_db_for(client_id).get_or_create(
                defaults={"mapped_brand": None, "is_removed": False},
                name=value, client_id=client_id)
            value = brand_missing[0].mapped_brand
        return value
