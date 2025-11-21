import math
from django.core.management.base import BaseCommand
from django.db import connections
from django.utils import timezone

from app.database.helper import get_connection_workspace
from app.financial.models import FedExShipment, SaleItem, FulfillmentChannel
from app.financial.services.fedex_shipment.config import FEDEX_SHIPMENT_ONE, FEDEX_SHIPMENT_PENDING
from app.financial.variable.fulfillment_type import FULFILLMENT_MFN_GROUP
from app.financial.variable.shipping_cost_source import FEDEX_SHIPMENT_SOURCE_KEY


class Command(BaseCommand):
    help = "Consolidate match one Fedex Shipment & Item Analysis"

    def add_arguments(self, parser):
        parser.add_argument('-c', '--client_id', type=str, help='Provide client id')

        parser.add_argument('-fd', '--from_date', type=str,
                            help='Provide start date . Format YYYY-MM-DD')

        parser.add_argument('-td', '--to_date', type=str,
                            help='Provide end date . Format YYYY-MM-DD')

        parser.add_argument('-type', '--date_type', type=str,
                            help='Provide date type in [shipment-date, invoice-date]')

    def handle(self, *args, **options):
        print("---- Begin consolidate match one Fedex Shipment & Item Analysis----")
        try:
            client_id = options['client_id']
            assert client_id is not None, "--client_id is not empty"
            date_type = options.get('date_type', 'shipment-date')

            from_date = options['from_date']
            to_date = options['to_date']

            assert from_date is not None and to_date is not None, "--from_date & --to_date need provide value"

            sql_date_range = """"""
            if date_type == 'invoice-date':
                sql_date_range += f"""fedex.invoice_date >= date('{from_date}') AND fedex.invoice_date <= date('{to_date}')"""
            else:
                sql_date_range += f"""fedex.shipment_date >= date('{from_date}') AND fedex.shipment_date <= date('{to_date}')"""

            client_db_id = client_id.replace('-', '_')

            ff_ids = FulfillmentChannel.objects.tenant_db_for(client_id).filter(
                name__in=FULFILLMENT_MFN_GROUP).values_list('id', flat=True)

            ff_ids = tuple(ff_ids) if len(ff_ids) > 1 else """('{}')""".format(ff_ids[0])

            sql = f"""
                SELECT __PATTERN__
                FROM financial_{client_db_id}_fedexshipment AS fedex INNER JOIN financial_{client_db_id}_saleitem AS si
                        ON fedex.tracking_id = si.tracking_fedex_id
                WHERE 
                    fedex.status in ('{FEDEX_SHIPMENT_ONE}') 
                    AND fedex.tracking_id IS NOT NULL
                    AND si.fulfillment_type_id IN {ff_ids}
                    AND si.shipping_cost_source = '{FEDEX_SHIPMENT_SOURCE_KEY}'
                    AND {sql_date_range}"""

            client_db = get_connection_workspace(client_id)

            with connections[client_db].cursor() as cursor:
                sql_count = sql.replace('__PATTERN__', 'COUNT(*)')
                cursor.execute(sql_count)
                res = cursor.fetchone()
                total = res[0]

            stats = {'total': total, 'not_find': 0, 'not_matched': 0, 'matched': 0}

            total_pages = math.ceil(total / 500)

            bulk_size = 500

            fedex_ids = []
            sale_item_ids = []

            for i in range(total_pages):
                page = i + 1
                offset = i * bulk_size

                print(f"Begin consolidate match one fedex shipment & item analysis page = {page}, offset = {offset}")

                with connections[client_db].cursor() as cursor:
                    sql_get = sql.replace('__PATTERN__',
                                          'fedex.* , si.sale_id, si.id AS sale_item_id,si.tracking_fedex_id')
                    sql_get += """ ORDER BY fedex.created DESC"""
                    sql_get += f""" LIMIT {bulk_size} OFFSET {offset}"""
                    cursor.execute(sql_get)
                    #
                    columns = [col[0] for col in cursor.description]
                    for row in cursor.fetchall():
                        item = dict(zip(columns, row))
                        if not item.get('tracking_fedex_id'):
                            fedex_ids.append(item['id'])
                            stats['not_find'] += 1
                            continue

                        if item['sale_id'] in item['matched_sales']:
                            stats['matched'] += 1
                            continue

                        sale_item_ids.append(item['sale_item_id'])
                        fedex_ids.append(item['id'])
                        stats['not_matched'] += 1

            if fedex_ids:
                FedExShipment.objects.tenant_db_for(client_id).filter(id__in=fedex_ids).update(
                    status=FEDEX_SHIPMENT_PENDING,
                    matched_sales=[],
                    matched_channel_sale_ids=[],
                    matched_time=None
                )

            if sale_item_ids:
                SaleItem.objects.tenant_db_for(client_id).filter(id__in=sale_item_ids).update(
                    shipping_cost_source=None,
                    shipping_cost_accuracy=None,
                    modified=timezone.now(),
                    dirty=True,
                    financial_dirty=True
                )

            print(f"Stat consolidate match one fedex shipment & item analysis {stats}")
        except Exception as ex:
            print(f"Error {ex}")
