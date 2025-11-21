import logging
from app.financial.import_template.custom_report import SaleItemCustomReport
from app.financial.models import SaleItem, ShippingInvoice
from app.financial.services.fedex_shipment.utils import get_query_set_filter_shipping_invoice
from app.financial.services.sale_item_bulk.custom_report_type.base import BaseCustomReportModuleService
from app.financial.sub_serializers.sale_item_bulk_edit_serializer import ClientSaleItemBulkEditSerializer

logger = logging.getLogger(__name__)


class ShippingInvoiceCustomReportModuleService(BaseCustomReportModuleService):
    module = SaleItemCustomReport
    serializer_class = ClientSaleItemBulkEditSerializer
    model = ShippingInvoice

    def __init__(self, bulk_id: str = None, jwt_token: str = None, user_id: str = None, client_id: str = None):
        super().__init__(bulk_id=bulk_id, jwt_token=jwt_token,
                         user_id=user_id, client_id=client_id)

    def get_columns_export(self):
        columns = {
            'tracking_id': 'Express or Ground Tracking ID',
            'invoice_number': 'Invoice Number',
            'invoice_date': 'Invoice Date',
            'po_number': 'PO Number',
            'customer_ref': 'Customer Reference',
            'recipient_name': 'Recipient Name',
            'shipper_company': 'Shipper Company',
            'shipper_name': 'Shipper Name',
            'brand': 'Brand',
            'segment': 'Segment',
            'fulfillment_type': 'Classification',
            'net_charge_amount': 'Net Charge Amount'
        }
        self.columns_as_type = {
            'tracking_id': 'string',
            'invoice_number': 'string',
            'invoice_date': 'date',
            'po_number': 'string',
            'customer_ref': 'string',
            'recipient_name': 'string',
            'shipper_company': 'string',
            'shipper_name': 'string',
            'brand': 'string',
            'segment': 'string',
            'fulfillment_type': 'string',
            'net_charge_amount': 'number'
        }
        return columns

    def get_total_ids(self):
        status = self.update_operations.get('status', {}).get('value', None)
        source = self.update_operations.get('source', {}).get('value', None)
        from_date = self.update_operations.get('from_date', {}).get('value', None)
        to_date = self.update_operations.get('to_date', {}).get('value', None)
        keyword = self.update_operations.get('keyword', {}).get('value', None)
        queryset = get_query_set_filter_shipping_invoice(client_id=self.client_id, ids=self.ids, status=status,
                                                         source=source, from_date=from_date, to_date=to_date,
                                                         sort_field='invoice_date', sort_direction='asc',
                                                         keyword=keyword)
        meta_data = list(queryset.values_list('invoice_number', flat=True)[:10])
        self._update_meta_custom_report(meta_data)
        #
        total_ids = queryset.values_list('id', flat=True)

        return list(total_ids)

    def _get_instances(self, ids, **kwargs):
        self.instance_ids = ids
        return self.model.objects.tenant_db_for(self.client_id) \
            .filter(id__in=self.instance_ids, client__id=self.client_id).order_by('invoice_date')

    def _validate_update_data(self, instance, **kwargs):
        return self.serializer_class(), [], {}

    def _validate_data_context(self, instance, raw_ins):
        return True, {}

    def _process_data_item(self, instance: ShippingInvoice, validated_data, export_data, **kwargs):
        #
        transactions = instance.fedexshipment_set.tenant_db_for(self.client_id).order_by('shipment_date')
        # print(f"count transaction : {instance.fedexshipment_set.tenant_db_for(self.client_id).count()}")
        for tran in transactions:
            try:
                sale_items = SaleItem.objects.tenant_db_for(self.client_id) \
                    .filter(client_id=self.client_id, sale_id=tran.matched_sales[0], tracking_fedex_id__isnull=False) \
                    .order_by('sale_date') \
                    .values('tracking_fedex_id', 'brand__name', 'fulfillment_type__name', 'segment')
                #
                items_matched = list(
                    filter(lambda x: tran.tracking_id in x['tracking_fedex_id'], list(sale_items)))
                # priority get item has brand name
                brand_matched = list(
                    filter(lambda x: x['brand__name'] is not None, items_matched))
                if len(brand_matched) > 0:
                    item_data = brand_matched[0]
                else:
                    item_data = items_matched[0]
                data = [{
                    'tracking_id': tran.tracking_id,
                    'invoice_number': instance.invoice_number,
                    'invoice_date': instance.invoice_date,
                    'po_number': tran.po_number,
                    'customer_ref': tran.customer_ref,
                    'recipient_name': tran.recipient_name,
                    'shipper_company': tran.shipper_company,
                    'shipper_name': tran.shipper_name,
                    'brand': item_data['brand__name'],
                    'segment': item_data['segment'],
                    'fulfillment_type': item_data['fulfillment_type__name'],
                    'net_charge_amount': tran.net_charge_amount
                }]
                # data = unique_everseen(data)
            except Exception as ex:
                # logger.error(
                #     f"[{self.__class__.__name__}][_process_data_item] {ex}")
                data = [{
                    'tracking_id': tran.tracking_id,
                    'invoice_number': instance.invoice_number,
                    'invoice_date': instance.invoice_date,
                    'po_number': tran.po_number,
                    'customer_ref': tran.customer_ref,
                    'recipient_name': tran.recipient_name,
                    'shipper_company': tran.shipper_company,
                    'shipper_name': tran.shipper_name,
                    'brand': None,
                    'segment': None,
                    'fulfillment_type': None,
                    'net_charge_amount': tran.net_charge_amount
                }]
            export_data += data
