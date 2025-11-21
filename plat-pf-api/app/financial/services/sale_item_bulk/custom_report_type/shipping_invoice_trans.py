from app.financial.models import FedExShipment, SaleItem
from app.financial.services.fedex_shipment.utils import get_query_set_filter_shipping_invoice_transaction
from app.financial.services.sale_item_bulk.custom_report_type.shipping_invoice import \
    ShippingInvoiceCustomReportModuleService


class ShippingInvoiceTransCustomReportModuleService(ShippingInvoiceCustomReportModuleService):
    model = FedExShipment

    def get_total_ids(self):
        status = self.update_operations.get('status', {}).get('value', None)
        source = self.update_operations.get('source', {}).get('value', None)
        shipping_invoice_id = self.update_operations.get('shipping_invoice_id', {}).get('value', None)
        keyword = self.update_operations.get('keyword', {}).get('value', None)
        queryset = get_query_set_filter_shipping_invoice_transaction(client_id=self.client_id,
                                                                     ids=self.ids,
                                                                     shipping_invoice_id=shipping_invoice_id,
                                                                     status=status, source=source,
                                                                     sort_field='shipment_date', sort_direction='asc',
                                                                     keyword=keyword)
        meta_data = list(queryset.values_list('transaction_id', flat=True)[:10])
        self._update_meta_custom_report(meta_data)
        total_ids = queryset.values_list('id', flat=True)

        return list(total_ids)

    def _get_instances(self, ids, **kwargs):
        self.instance_ids = ids
        return self.model.objects.tenant_db_for(self.client_id) \
            .filter(id__in=self.instance_ids, client__id=self.client_id).order_by('shipment_date')

    def _process_data_item(self, instance: FedExShipment, validated_data, export_data, **kwargs):
        shipping_invoice = instance.shipping_invoice
        try:
            sale_items = SaleItem.objects.tenant_db_for(self.client_id) \
                .filter(client_id=self.client_id, sale_id=instance.matched_sales[0], tracking_fedex_id__isnull=False) \
                .order_by('sale_date') \
                .values('tracking_fedex_id', 'brand__name', 'fulfillment_type__name', 'segment')
            #
            items_matched = list(
                filter(lambda x: instance.tracking_id in x['tracking_fedex_id'], list(sale_items)))
            # priority get item has brand name
            brand_matched = list(
                filter(lambda x: x['brand__name'] is not None, items_matched))
            if len(brand_matched) > 0:
                item_data = brand_matched[0]
            else:
                item_data = items_matched[0]
            data = [{
                'tracking_id': instance.tracking_id,
                'invoice_number': shipping_invoice.invoice_number,
                'invoice_date': shipping_invoice.invoice_date,
                'po_number': instance.po_number,
                'customer_ref': instance.customer_ref,
                'recipient_name': instance.recipient_name,
                'shipper_company': instance.shipper_company,
                'shipper_name': instance.shipper_name,
                'brand': item_data['brand__name'],
                'segment': item_data['segment'],
                'fulfillment_type': item_data['fulfillment_type__name'],
                'net_charge_amount': instance.net_charge_amount
            }]
            # data = unique_everseen(data)
        except Exception as ex:
            # logger.error(
            #     f"[{self.__class__.__name__}][_process_data_item] {ex}")
            data = [{
                'tracking_id': instance.tracking_id,
                'invoice_number': shipping_invoice.invoice_number,
                'invoice_date': shipping_invoice.invoice_date,
                'po_number': instance.po_number,
                'customer_ref': instance.customer_ref,
                'recipient_name': instance.recipient_name,
                'shipper_company': instance.shipper_company,
                'shipper_name': instance.shipper_name,
                'brand': None,
                'segment': None,
                'fulfillment_type': None,
                'net_charge_amount': instance.net_charge_amount
            }]
        export_data += data
