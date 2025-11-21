from datetime import date

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from app.financial.models import FedExShipment
from app.financial.services.fedex_shipment.config import FEDEX_EDI_SERVICE_TYPE_MAPPING
from app.financial.sub_serializers.default_message_serializer import default_error_message
from app.database.sub_serializers.tenant_db_for_serializer import TenantDBForSerializer


class FedEdShipmentImportSerializer(TenantDBForSerializer):
    transaction_id = serializers.CharField(error_messages=default_error_message('Transaction ID'),
                                           label="Transaction ID",
                                           required=True)
    payer_account_id = serializers.CharField(error_messages=default_error_message('Payer Account ID'),
                                             label="Payer Account ID",
                                             required=False, allow_null=True, allow_blank=True)
    payee_account_id = serializers.CharField(error_messages=default_error_message('Bill to Account Number'),
                                             label="Bill to Account Number",
                                             required=True)
    tracking_id = serializers.CharField(error_messages=default_error_message('Tracking ID'), label="Tracking ID",
                                        required=True)
    invoice_number = serializers.CharField(error_messages=default_error_message('Invoice Number'),
                                           label="Invoice Number", required=True)
    invoice_date = serializers.CharField(error_messages=default_error_message('Invoice Date'), required=True)
    shipment_date = serializers.CharField(error_messages=default_error_message('Shipment Date'))
    service_type = serializers.CharField(error_messages=default_error_message('Service Type', 100), required=False,
                                         allow_null=True, allow_blank=True)
    shipper_name = serializers.CharField(error_messages=default_error_message('Shipper Name', 256),
                                         label="Shipper Name", required=True)

    class Meta:
        model = FedExShipment
        fields = ['transaction_id', 'payer_account_id', 'payee_account_id', 'invoice_number', 'invoice_date',
                  'po_number', 'customer_ref', 'tracking_id', 'shipper_company', 'shipment_date', 'net_charge_amount',
                  'recipient_name', 'shipper_name', 'recipient_address_line_1', 'recipient_address_line_2',
                  'recipient_state', 'recipient_city', 'recipient_country', 'recipient_zip_code', 'service_type']

        extra_kwargs = {
            'recipient_name': {
                "error_messages": default_error_message('Recipient Name')
            },
            'recipient_address_line_1': {
                "error_messages": default_error_message('Recipient Address Line 1')
            },
            'recipient_address_line_2': {
                "error_messages": default_error_message('Recipient Address Line 2'),
            },
            'net_charge_amount': {
                "error_messages": default_error_message('Net Charge Amount')
            },
            'recipient_country': {
                "error_messages": default_error_message('Recipient Country', 15),
                "label": "Recipient Country/Territory",
            },
            'recipient_state': {
                "error_messages": default_error_message('Recipient State', 15)
            },
            'recipient_city': {
                "error_messages": default_error_message('Recipient City')
            },
            'recipient_zip_code': {
                "error_messages": default_error_message('Recipient Zip Code', 15)
            },
            'shipper_company': {
                "error_messages": default_error_message('Shipper Company', 256)
            },
            'po_number': {
                "error_messages": default_error_message('PO Number', 256)
            },
            'customer_ref': {
                "error_messages": default_error_message('Customer Reference', 256)
            },
        }

    def validate_shipment_date(self, value):
        try:
            assert len(value) == 8, "Value wrong format"
            return date(year=int(value[0:4]), month=int(value[4:6]), day=int(value[6:8]))
        except BaseException as exc:
            raise ValidationError("Shipment date is invalid", code="shipment_date")

    def validate_invoice_date(self, value):
        try:
            assert len(value) == 8, "Value wrong format"
            return date(year=int(value[0:4]), month=int(value[4:6]), day=int(value[6:8]))
        except BaseException as exc:
            raise ValidationError("Invoice date is invalid", code="invoice_date")

    def is_service_type_numeric(self, value):
        try:
            int(value)
            return True
        except:
            return False

    def validate_service_type(self, value):
        if not value:
            return value
        try:
            if self.is_service_type_numeric(value):
                value = FEDEX_EDI_SERVICE_TYPE_MAPPING[int(value)]
            return value
        except BaseException as exc:
            raise ValidationError("Service type is invalid", code="service_type")

    def validate(self, attrs):
        country_code = attrs.get('recipient_country')
        postal_code = attrs.get('recipient_zip_code')
        postal_code = self.__format_postal_code(country_code, postal_code)
        attrs.update({"recipient_zip_code": postal_code})
        return attrs

    def __format_postal_code(self, country_code, postal_code):
        if country_code == 'US':
            return self.__us_postal_code(postal_code)
        return postal_code

    @classmethod
    def __us_postal_code(cls, postal_code):
        if postal_code and len(postal_code) == 9:
            return f'{postal_code[:5]}-{postal_code[5:]}'
        return postal_code


class FedEdShipmentFTPSerializer(FedEdShipmentImportSerializer):
    class Meta(FedEdShipmentImportSerializer.Meta):
        fields = FedEdShipmentImportSerializer.Meta.fields + ['orig_recipient_name', 'orig_recipient_address_line_1',
                                                              'orig_recipient_address_line_2', 'orig_recipient_state',
                                                              'orig_recipient_city', 'orig_recipient_country',
                                                              'orig_recipient_zip_code']
        extra_kwargs = {
            **FedEdShipmentImportSerializer.Meta.extra_kwargs,
            'orig_recipient_name': {
                "error_messages": default_error_message('Original Recipient Name')
            },
            'orig_recipient_address_line_1': {
                "error_messages": default_error_message('Original Recipient Address Line 1')
            },
            'orig_recipient_address_line_2': {
                "error_messages": default_error_message('Original Recipient Address Line 2'),
            },
            'orig_recipient_country': {
                "error_messages": default_error_message('Original Recipient Country', 15),
                "label": "Recipient Country/Territory",
            },
            'orig_recipient_state': {
                "error_messages": default_error_message('Original Recipient State', 15)
            },
            'orig_recipient_city': {
                "error_messages": default_error_message('Original Recipient City')
            },
            'orig_recipient_zip_code': {
                "error_messages": default_error_message('Original Recipient Zip Code', 15)
            },
        }


class FedExShipmentSerializer(TenantDBForSerializer):
    class Meta:
        model = FedExShipment
        exclude = ['client']
