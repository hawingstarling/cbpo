from django.core.management.base import BaseCommand
from django.db.models import Q, Max, BigIntegerField
from django.db.models.functions import Coalesce, Cast

from app.financial.models import FedExShipment, ShippingInvoice


class Command(BaseCommand):
    help = "Command sync FedEx Shipment invoice number to table Shipping Invoice"

    def add_arguments(self, parser):
        parser.add_argument('-c', '--client_id', type=str, help='Provide client id for sync')

    def handle(self, *args, **options):
        print("---- Begin sync shipping invoice ----")
        client_id = options['client_id']
        if not client_id:
            print("Missing client id")
            return
        client_ids = [str(client_id)]
        if len(client_ids) == 0:
            print("Not found clients for sync")
            return
        # get all items of fedex shipment
        bulk_fedex_shipment = []
        for client_id in client_ids:
            print(f"---- Begin sync for client {client_id}")
            cond = Q(invoice_number__isnull=False, shipping_invoice__isnull=True)
            #
            queryset = FedExShipment.objects.tenant_db_for(client_id) \
                .filter(cond).order_by('invoice_date').values('invoice_number', 'invoice_date').distinct()
            # payee_id = '368908193'
            agg_trans = FedExShipment.objects.tenant_db_for(client_id).filter(transaction_id__isnull=False) \
                .annotate(trans_id=Cast('transaction_id', BigIntegerField())) \
                .aggregate(max=Coalesce(Max('trans_id'), 1))
            #
            trans_id = agg_trans['max']
            for item in queryset:
                si, _ = ShippingInvoice.objects.tenant_db_for(client_id).get_or_create(
                    invoice_number=item['invoice_number'],
                    payee_account_id='368908193',
                    client_id=client_id, defaults={'invoice_date': item['invoice_date']})
                queryset_fedex = FedExShipment.objects.tenant_db_for(client_id) \
                    .filter(invoice_number=si.invoice_number, shipping_invoice__isnull=True).order_by('created')
                #
                for fedex in queryset_fedex:
                    fedex.transaction_id = trans_id
                    fedex.shipping_invoice = si
                    bulk_fedex_shipment.append(fedex)
                    trans_id += 1
                if len(bulk_fedex_shipment) > 0:
                    FedExShipment.objects.tenant_db_for(client_id).bulk_update(bulk_fedex_shipment,
                                                                               fields=['transaction_id',
                                                                                       'shipping_invoice'])
                    bulk_fedex_shipment = []
        print("---- End sync shipping invoice ----")
