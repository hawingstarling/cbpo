import logging
from app.financial.models import FedExShipment
from app.financial.services.fedex_shipment.config import FEDEX_SHIPMENT_PENDING, FEDEX_SHIPMENT_NONE, \
    FEDEX_SHIPMENT_MULTI
from app.financial.services.sale_item_bulk.custom_report_type.shipping_invoice import \
    ShippingInvoiceCustomReportModuleService

logger = logging.getLogger(__name__)


class ShippingInvoiceTransUnmatchedCustomReportModuleService(ShippingInvoiceCustomReportModuleService):
    model = FedExShipment

    def get_columns_export(self):
        columns = {
            'errors': 'ERRORS',
            'tracking_id': 'Express or Ground Tracking ID',
            'invoice_number': 'Invoice Number',
            'invoice_date': 'Invoice Date',
            'po_number': 'PO Number',
            'customer_ref': 'Customer Reference',
            'recipient_name': 'Recipient Name',
            'shipper_company': 'Shipper Company',
            'shipper_name': 'Shipper Name',
            'net_charge_amount': 'Net Charge Amount'
        }
        self.columns_as_type = {
            'errors': 'string',
            'tracking_id': 'string',
            'invoice_number': 'string',
            'invoice_date': 'date',
            'po_number': 'string',
            'customer_ref': 'string',
            'recipient_name': 'string',
            'shipper_company': 'string',
            'shipper_name': 'string',
            'net_charge_amount': 'number'
        }
        return columns

    def get_total_ids(self):
        shipping_invoice_id = self.update_operations.get('shipping_invoice_id', {}).get('value', None)
        queryset = FedExShipment.objects.tenant_db_for(self.client_id) \
            .filter(client_id=self.client_id, shipping_invoice_id=shipping_invoice_id,
                    status__in=[FEDEX_SHIPMENT_PENDING, FEDEX_SHIPMENT_MULTI, FEDEX_SHIPMENT_NONE]) \
            .order_by('shipment_date')

        # meta_data = list(queryset.values_list('transaction_id', flat=True)[:10])
        # self._update_meta_custom_report(meta_data)
        total_ids = queryset.values_list('id', flat=True)

        return list(total_ids)

    def _get_instances(self, ids, **kwargs):
        self.instance_ids = ids
        return self.model.objects.tenant_db_for(self.client_id) \
            .filter(id__in=self.instance_ids, client__id=self.client_id).order_by('shipment_date')

    def _process_data_item(self, instance: FedExShipment, validated_data, export_data, **kwargs):
        shipping_invoice = instance.shipping_invoice
        try:
            errors = None
            if instance.status == FEDEX_SHIPMENT_PENDING:
                errors = f"The record transaction still is pending in queue, please waiting later"
            elif instance.status == FEDEX_SHIPMENT_MULTI:
                errors = f"The record transaction has found over sale match with tracking id {instance.tracking_id}"
            elif instance.status == FEDEX_SHIPMENT_NONE:
                errors = f"The record transaction not found sale matching with tracking id {instance.tracking_id}"
            data = [{
                'errors': errors,
                'tracking_id': instance.tracking_id,
                'invoice_number': shipping_invoice.invoice_number,
                'invoice_date': shipping_invoice.invoice_date,
                'po_number': instance.po_number,
                'customer_ref': instance.customer_ref,
                'recipient_name': instance.recipient_name,
                'shipper_company': instance.shipper_company,
                'shipper_name': instance.shipper_name,
                'net_charge_amount': instance.net_charge_amount
            }]
            # data = unique_everseen(data)
            export_data += data
        except Exception as ex:
            logger.error(f"[{self.__class__.__name__}][_process_data_item] {ex}")
