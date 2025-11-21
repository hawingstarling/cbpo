import copy

from django.utils.translation import gettext_lazy as _

# CharField
string_fields = ['channel_sale_id', 'channel', 'country', 'customer_name', 'recipient_name', 'address_line_1',
                 'address_line_2', 'address_line_3', 'state', 'city', 'postal_code', 'brand', 'upc', 'sku', 'brand_sku',
                 'asin', 'style', 'size', 'title', 'notes', 'fulfillment_type', 'tracking_fedex_id', 'ship_carrier',
                 'product_number', 'product_type', 'parent_asin']

# ChoiceField
choice_fields = ['sale_status', 'profit_status']

# DecimalField
decimal_fields = ['sale_charged', 'shipping_charged', 'tax_charged', 'cog', 'unit_cog', 'actual_shipping_cost',
                  'estimated_shipping_cost', 'tax_cost', 'channel_listing_fee', 'other_channel_fees',
                  'inbound_freight_cost', 'outbound_freight_cost', 'channel_tax_withheld', 'label_cost']

# DateTimeField
datetime_fields = ['ship_date', 'sale_date']

# IntegerField
integer_fields = ['quantity', 'shipping_cost_accuracy', 'sale_charged_accuracy', 'channel_listing_fee_accuracy',
                  'inbound_freight_cost_accuracy', 'outbound_freight_cost_accuracy', 'channel_tax_withheld_accuracy']

# BooleanField
boolean_fields = ['is_prime']

#
fields = string_fields + choice_fields + decimal_fields + datetime_fields + integer_fields + boolean_fields
#
required_fields = ['channel_sale_id', 'channel_name', 'sku', 'title', 'sale_charged']
#
not_required_fields = list(set(fields) - set(required_fields))

extra_kwargs_import = {}
for field in required_fields:
    extra_kwargs_import.update({field: {'required': True}})

for field in not_required_fields:
    extra_kwargs_import.update({field: {'required': False}})

field_label = {
    'channel_sale_id': _('Channel Sale ID'),
    'channel': _('Channel'),
    'country': _('Country'),
    'state': _('State'),
    'city': _('City'),
    'postal_code': _('Postal Code'),
    'is_prime': _('Prime'),
    'brand': _('Brand'),
    'upc': _('UPC'),
    'brand_sku': _('Brand SKU'),
    'sku': _('SKU'),
    'asin': _('ASIN'),
    'quantity': _('Quantity'),
    'style': _('Style'),
    'size': _('Size'),
    'title': _('Title'),
    'notes': _('Notes'),
    'sale_charged': _('Sale Charged'),
    'shipping_charged': _('Additional Shipping Charged'),
    'tax_charged': _('Tax Charged'),
    'sale_status': _('Sale Status'),
    'profit_status': _('Profit Status'),
    'cog': _('COG'),
    'unit_cog': _('Unit COG'),
    'actual_shipping_cost': _('Actual Shipping Cost'),
    'estimated_shipping_cost': _('Estimated Shipping Cost'),
    'shipping_cost': _('Shipping Cost'),
    'shipping_cost_accuracy': _('Shipping Cost Accuracy'),
    'sale_charged_accuracy': _('Sale Charged Accuracy'),
    'channel_listing_fee_accuracy': _('Channel Commission Fee Accuracy'),
    'inbound_freight_cost': _('Inbound Freight Cost'),
    'outbound_freight_cost': _('Outbound Freight Cost'),
    'inbound_freight_cost_accuracy': _('Inbound Freight Cost Accuracy'),
    'outbound_freight_cost_accuracy': _('Outbound Freight Cost Accuracy'),
    'channel_tax_withheld': _('Channel Tax Withheld'),
    'channel_tax_withheld_accuracy': _('Channel Tax Withheld Accuracy'),
    'tax_cost': _('Tax Cost'),
    'channel_listing_fee': _('Channel Commission Fee'),
    'other_channel_fees': _('Other Channel Fees'),
    'ship_date': _('Ship Date'),
    'sale_date': _('Sale Date'),
    'fulfillment_type': _('Fulfilment Type'),
    'tracking_fedex_id': _('Tracking ID'),
    'ship_carrier': _('Ship Carrier'),
    'product_number': _('Product Number'),
    'product_type': _('Product Type'),
    'parent_asin': _('Parent ASIN'),
    'label_cost': _('Label Cost'),
}


def get_label(field):
    try:
        return str(field_label[field])
    except Exception as ex:
        return field.replace('_', ' ').title()


default_error_messages_extra = {
    'asin': {
        'required': _('ASIN is required'),
        'null': _('ASIN cannot be null'),
        'invalid': _('ASIN a valid string'),
        'blank': _('ASIN may not be blank'),
        'max_length': _('ASIN is invalid'),
        'min_length': _('ASIN has at least {min_length} characters'),
    },
    'upc': {
        'required': _('UPC/EAN is required'),
        'null': _('UPC/EAN cannot be null'),
        'invalid': _('UPC/EAN a valid string'),
        'blank': _('UPC/EAN may not be blank'),
        'max_length': _('UPC/EAN is invalid'),
        'min_length': _('UPC/EAN has at least {min_length} characters'),
    }
}

default_error_message_string = {
    'required': _('is required'),
    'null': _('cannot be null'),
    'invalid': _('a valid string'),
    'blank': _('may not be blank'),
    'max_length': _('length is {max_length} maximum'),
    'min_length': _('has at least {min_length} characters.'),
}

default_error_messages_choice = {
    'required': _('is required'),
    'null': _('cannot be null'),
    'invalid_choice': _('is invalid'),
}

default_error_messages_decimal = {
    'required': _('is required'),
    'null': _('cannot be null'),
    'invalid': _('is invalid'),
    'max_value': _('is less than or equal to {max_value}'),
    'min_value': _('value is greater than or equal to {min_value}.'),
    'max_digits': _('there are no more than {max_digits} digits in total'),
    'max_decimal_places': _('there are no more than {max_decimal_places} decimal places'),
    'max_whole_digits': _('there are no more than {max_whole_digits} digits before the decimal point'),
    'max_string_length': _('string value too large'),
}

default_error_messages_datetime = {
    'required': _('is required'),
    'null': _('cannot be null'),
    'invalid': _('datetime has wrong format. Use one of these formats instead: {format}'),
    'date': _('expected a datetime but got a date'),
    'make_aware': _('invalid datetime for the timezone "{timezone}"'),
    'overflow': _('datetime value out of range'),
}

default_error_messages_integer = {
    'required': _('is required'),
    'null': _('cannot be null'),
    'invalid': _('is invalid'),
    'max_value': _('value is less than or equal to {max_value}'),
    'min_value': _('value is greater than or equal to {min_value}'),
    'max_string_length': _('value too large.')
}

default_error_messages_boolean = {
    'required': _('is required.'),
    'null': _('not be null.'),
    'invalid': _('is invalid.')
}

default_error_messages = {}


def handler_string_fields(field):
    if field in default_error_messages_extra:
        default_error_messages[field] = default_error_messages_extra[field]
        return
    error_messages = copy.deepcopy(default_error_message_string)
    generate = {}
    for key in error_messages.keys():
        content = error_messages[key]
        generate[key] = _(get_label(field) + " " + str(content))
    default_error_messages[field] = generate


def handler_choice_fields(field):
    error_messages = copy.deepcopy(default_error_messages_choice)
    generate = {}
    for key in error_messages.keys():
        content = error_messages[key]
        generate[key] = _(get_label(field) + " " + str(content))
    default_error_messages[field] = generate


def handler_decimal_fields(field):
    error_messages = copy.deepcopy(default_error_messages_decimal)
    generate = {}
    for key in error_messages.keys():
        content = error_messages[key]
        generate[key] = _(get_label(field) + " " + str(content))
    default_error_messages[field] = generate


def handler_datetime_fields(field):
    error_messages = copy.deepcopy(default_error_messages_datetime)
    generate = {}
    for key in error_messages.keys():
        content = error_messages[key]
        generate[key] = _(get_label(field) + " " + str(content))
    default_error_messages[field] = generate


def handler_integer_fields(field):
    error_messages = copy.deepcopy(default_error_messages_integer)
    generate = {}
    for key in error_messages.keys():
        content = error_messages[key]
        generate[key] = _(get_label(field) + " " + str(content))
    default_error_messages[field] = generate


def handler_boolean_fields(field):
    error_messages = copy.deepcopy(default_error_messages_boolean)
    generate = {}
    for key in error_messages.keys():
        content = error_messages[key]
        generate[key] = _(get_label(field) + " " + str(content))
    default_error_messages[field] = generate


for field in fields:
    if field in string_fields:
        handler_string_fields(field)
    if field in choice_fields:
        handler_choice_fields(field)
    if field in decimal_fields:
        handler_decimal_fields(field)
    if field in datetime_fields:
        handler_datetime_fields(field)
    if field in integer_fields:
        handler_integer_fields(field)
    if field in boolean_fields:
        handler_boolean_fields(field)
