import copy
import os
from decimal import Decimal
from urllib.parse import urlparse
from django.utils import timezone
from plat_import_lib_api.static_variable.config import MEDIA_URL, BASE_URL, MEDIA_ROOT

from app.financial.import_template.base_custom_module import BaseCustomModule
from app.financial.permissions.fedex_shipment_permissions import FedExShipmentImportPermission
import logging
from app.financial.models import FedExShipment, ShippingInvoice, SaleItem
from app.financial.services.activity import ActivityService
from app.core.services.audit_logs.base import AuditLogCoreManager, SALE_SHIPPING_INVOICE_LEVEL
from app.financial.services.fedex_shipment.config import FEDEX_SHIPMENT_PENDING, FEDEX_SHIPMENT_ONE, \
    FEDEX_SHIPMENT_COMPLETED
from app.financial.sub_serializers.fedex_shipment_serializer import FedEdShipmentImportSerializer
from app.financial.variable.shipping_cost_source import SHIP_CARRIER_FEDEX

logger = logging.getLogger(__name__)


class FedExShipmentModule(BaseCustomModule):
    __NAME__ = 'FedExShipmentModule'
    __MODEL__ = FedExShipment
    __LABEL__ = 'Shipping Invoices'
    __SERIALIZER_CLASS__ = FedEdShipmentImportSerializer
    __PERMISSION_CLASS__ = [FedExShipmentImportPermission]
    __TEMPLATE_VERSION__ = '1.8'
    __TEMPLATE_NUMBER_RECORD__ = 3
    __MODULE_TEMPLATE_NAME__ = "ShippingInvoices"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.source_file_url = None
        self.source_file_name = None
        self.shipping_invoices_bulk_create = {}
        self.shipping_invoices_bulk_update = {}
        self.revert_matched_ones_bulk_update = {}
        self.time_now = timezone.now()
        self.shipping_invoice_fields_changes = ['invoice_date', 'payee_account_id']

    @property
    def data_sample(self):
        tracking_id = ['123456789012', '123456789013', '123456789014']
        shipper_company = ['Helly Hansen', 'ODW Logistics - FitFlop', 'ALTRA WHOLESALE']
        invoice_number = ['1234567890', '1234567891', '1234567892']
        transaction_id = ['5555555555', '6666666666', '7777777777']
        payer_account_id = ['TEST-12345']
        payee_account_id = ['111111111']
        shipment_date = ['20201112', '20201106', '20201110']
        invoice_date = ['20201112', '20201106', '20201110']
        recipient_name = ['STEVEN  WELCH', 'HILDA ZERMENO', 'MELISSA MOORE']
        shipper_name = ['BOB', 'JACK', 'JANE']
        recipient_address_line_1 = ['590 TREETOP LN', '1021 ZEB HELMS RD', '102 WEST ST']
        recipient_address_line_2 = ['1130 BROADWAY ST', '']
        recipient_state = ['IL', 'NC', 'NY']
        recipient_country = ['US']
        recipient_city = ['Chicago', 'Charlotte', 'New York']
        recipient_zip_code = ["600315658", "281127509", "129531120"]
        service_types = ["FedEx Express", "FedEx Ground", "FedEx SmartPost"]
        po_number = ["11111", "22222", "33333"]
        customer_ref = ["RLP-W501-W-WH", "RLP-W502-W-WH", "RLP-W503-W-WH"]
        return {
            'tracking_id': tracking_id,
            'transaction_id': transaction_id,
            'payer_account_id': payer_account_id,
            'payee_account_id': payee_account_id,
            'shipper_company': shipper_company,
            'shipment_date': shipment_date,
            'recipient_name': recipient_name,
            'shipper_name': shipper_name,
            'recipient_address_line_1': recipient_address_line_1,
            'recipient_address_line_2': recipient_address_line_2,
            'recipient_state': recipient_state,
            'recipient_country': recipient_country,
            'recipient_city': recipient_city,
            'recipient_zip_code': recipient_zip_code,
            'service_type': service_types,
            'invoice_number': invoice_number,
            'invoice_date': invoice_date,
            'po_number': po_number,
            'customer_ref': customer_ref
        }

    def set_source_file_info(self, lib_import_id: str):
        try:
            assert self.source_file_url is None, "Source File Url is Empty"
            self.source_file_url = self.lib_import_instance.file_url_cloud
            if not self.source_file_url:
                self.source_file_url = f'{self.lib_import_instance.temp_file_path.replace(f"{MEDIA_ROOT}/", f"{BASE_URL}{MEDIA_URL}")}'
            self.source_file_name = self.lib_import_instance.meta.get("file_name")
            if not self.source_file_name:
                file_parse = urlparse(self.source_file_url)
                self.source_file_name = os.path.basename(file_parse.path)
        except Exception as ex:
            pass

    def handler_validated_data(self, lib_import_id: str, validated_data: dict, **kwargs):
        self.set_source_file_info(lib_import_id)
        #
        validated_data.update(dict(source_file_url=self.source_file_url, source_file_name=self.source_file_name))
        return super().handler_validated_data(lib_import_id, validated_data, **kwargs)

    def filter_instance(self, lib_import_id: str, validated_data, **kwargs):
        cond = {
            'client': validated_data['client'],
            'transaction_id': validated_data['transaction_id'],
            'shipping_invoice': validated_data['shipping_invoice'],
        }
        return cond

    def get_or_create_shipping_invoice(self, validated_data):
        invoice_data = dict(
            client=validated_data.get('client'),
            invoice_number=validated_data.get('invoice_number'),
            invoice_date=validated_data.get('invoice_date'),
            payee_account_id=validated_data.pop('payee_account_id'),
            payer_account_id=validated_data.get('payer_account_id'),
        )
        parent_key_map = f"{invoice_data['invoice_number']}_$_{invoice_data['payee_account_id']}"
        try:
            invoice = ShippingInvoice.objects.tenant_db_for(self.client_id).get(
                invoice_number=invoice_data['invoice_number'],
                payee_account_id=invoice_data['payee_account_id'])
            #
            invoice_changes = copy.deepcopy(invoice)
            for key in self.shipping_invoice_fields_changes:
                setattr(invoice_changes, key, invoice_data[key])
            #
            res_changes = AuditLogCoreManager(self.client_id).get_diff(invoice, invoice_changes,
                                                                       level=SALE_SHIPPING_INVOICE_LEVEL)
            if res_changes and parent_key_map not in self.shipping_invoices_bulk_update:
                self.shipping_invoices_bulk_update.update({parent_key_map: invoice_changes})
        except Exception as ex:
            if parent_key_map not in self.shipping_invoices_bulk_create:
                invoice = ShippingInvoice(**invoice_data)
                self.shipping_invoices_bulk_create.update({parent_key_map: invoice})
            invoice = self.shipping_invoices_bulk_create[parent_key_map]
        return invoice

    def verify_revert_matched_one_sale(self, obj):
        try:
            #
            if obj.status == FEDEX_SHIPMENT_ONE:
                is_diff_tracking_id = self.instance_model_origin.tracking_id != obj.tracking_id
                is_diff_net_charge_amount = Decimal(f"{self.instance_model_origin.net_charge_amount}") != Decimal(
                    f"{obj.net_charge_amount}")
                #
                is_completed_status = obj.po_number and obj.customer_ref
                if is_diff_tracking_id or is_diff_net_charge_amount:
                    obj.status = FEDEX_SHIPMENT_PENDING
                    obj.matched_sales = []
                    obj.matched_channel_sale_ids = []
                    obj.matched_time = None
                    if is_diff_tracking_id:
                        queryset_items = SaleItem.objects.tenant_db_for(self.client_id) \
                            .filter(ship_carrier=SHIP_CARRIER_FEDEX, tracking_fedex_id__icontains=obj.tracking_id)
                        # reset sale item shipping to null for auto fetch by brand settings
                        for item in queryset_items:
                            _id = str(item.pk)
                            item.shipping_cost = None
                            item.estimated_shipping_cost = None
                            item.actual_shipping_cost = None
                            item.shipping_cost_accuracy = None
                            item.shipping_cost_source = None
                            item.modified = self.time_now
                            if _id not in self.revert_matched_ones_bulk_update:
                                self.revert_matched_ones_bulk_update.update({_id: item})
                elif is_completed_status:
                    obj.status = FEDEX_SHIPMENT_COMPLETED
                else:
                    pass
        except Exception as ex:
            pass

    @property
    def fields_model_ignore_compared(self):
        fields = super().fields_model_ignore_compared
        fields += ["source_file_url", "source_file_name"]
        return fields

    def make_instance(self, lib_import_id: str, validated_data: dict, **kwargs):
        # handler shipping invoice
        shipping_invoice = self.get_or_create_shipping_invoice(validated_data)
        validated_data.update(dict(shipping_invoice=shipping_invoice))
        #
        obj, created = super().make_instance(lib_import_id, validated_data, **kwargs)
        #
        self.verify_revert_matched_one_sale(obj)
        return obj, created

    def bulk_process_shipping_invoice(self):
        if self.shipping_invoices_bulk_create:
            ShippingInvoice.objects.tenant_db_for(self.client_id).bulk_create(
                list(self.shipping_invoices_bulk_create.values()), ignore_conflicts=True)
            self.shipping_invoices_bulk_create = {}

        if self.shipping_invoices_bulk_update:
            ShippingInvoice.objects.tenant_db_for(self.client_id).bulk_update(
                list(self.shipping_invoices_bulk_update.values()), fields=self.shipping_invoice_fields_changes)
            self.shipping_invoices_bulk_update = {}

    def bulk_process_revert_matched_ones(self):
        if self.revert_matched_ones_bulk_update:
            SaleItem.objects.tenant_db_for(self.client_id) \
                .bulk_update(list(self.revert_matched_ones_bulk_update.values()),
                             fields=[
                                 'shipping_cost',
                                 'actual_shipping_cost',
                                 'estimated_shipping_cost',
                                 'shipping_cost_accuracy',
                                 'shipping_cost_source',
                                 'modified'
                             ])
            self.revert_matched_ones_bulk_update = {}

    def bulk_process(self, lib_import_id: str, bulk_insert: list, bulk_update: list, **kwargs):
        self.bulk_process_shipping_invoice()
        #
        super().bulk_process(lib_import_id, bulk_insert, bulk_update, **kwargs)
        self.bulk_process_revert_matched_ones()
        #

    def keys_raw_map_config(self, lib_import_id: str, validated_data, **kwargs):
        return {
            'key_map': ['transaction_id', 'invoice_number', 'payee_account_id'],
            'parent_key_map': []
        }

    def process(self, lib_import_id: str, **kwargs) -> any:
        super().process(lib_import_id, **kwargs)
        #
        ActivityService(client_id=self.client_id, user_id=self.user_id).create_activity_import_fedex_shipment()

    @property
    def regex_pattern_map_config(self):
        return {
            'shipment_date': ['shipment date', 'ship date'],
            'net_charge_amount': ['net charge amount', f'(net chrg|net charge)'],
            'recipient_address_line_1': ['recipient address line 1', 'recipient address 1'],
            'recipient_address_line_2': ['recipient address line 2', 'recipient address 2'],
            'recipient_state': ['recipient state', 'st2'],
            'recipient_postal': ['recipient state', 'st2'],
            'recipient_country': ['recipient country', 'cntry2'],
            'recipient_zip_code': ['recipient zip code', 'postal2'],
            'service_type': ['service type', f'(co.cd|Co Cd)'],
            'tracking_id': ['express or ground tracking id', 'tracking id'],
            'payee_account_id': [f'(Bill to Account Number|Payee ID)', 'payee account id']
        }
