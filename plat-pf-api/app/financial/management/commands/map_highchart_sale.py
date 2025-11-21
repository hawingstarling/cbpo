import time

from django.core.management import BaseCommand
from django.db import transaction

from app.financial.models import Sale
from app.financial.services.highchart_mapping import HighChartMappingService


class Command(BaseCommand):
    help = 'Command map high-chart keys to sale'

    """
    mapping state_key, county_key to sale by country, state, city, postal_code
    """

    def add_arguments(self, parser):
        parser.add_argument('-c', '--client_id', type=str,
                            help='Provide client id for sync sale items data to table flatten', required=True)

    def handle(self, *args, **options):
        with transaction.atomic():

            client_id = options['client_id']
            if client_id:
                print("Client ID is required")
                return
            sales = Sale.objects.tenant_db_for(client_id).filter(country__isnull=False, state__isnull=False)

            print('---- Begin mapping high-chart keys to sale data: {} sales ----'.format(sales.count()))
            print('---- Client ID: {} ----'.format(client_id)) if client_id else None
            start_time = time.time()
            updated_sales = []
            mapped_count, total_mapped_count = 0, 0
            hc_mapping_service = HighChartMappingService()
            for sale in sales.iterator(1000):
                state_key, county_key = hc_mapping_service.get_hc_keys(country=sale.country, state=sale.state,
                                                                       county=sale.city, postal_code=sale.postal_code)
                sale.state_key = state_key
                sale.county_key = county_key

                updated_sales.append(sale)

                if state_key or county_key:
                    mapped_count += 1

                if len(updated_sales) >= 1000:
                    Sale.objects.tenant_db_for(client_id).bulk_update(updated_sales, ['state_key', 'county_key'])
                    print('Mapped high-chart keys to {} sales'.format(mapped_count))
                    updated_sales = []
                    total_mapped_count += mapped_count
                    mapped_count = 0

        if len(updated_sales) > 0:
            Sale.objects.tenant_db_for(client_id).bulk_update(updated_sales, ['state_key', 'county_key'])
            print('Mapped high-chart keys to {} Sales'.format(mapped_count))
            total_mapped_count += mapped_count
        time_exc = time.time() - start_time
        print('---- End mapping high-chart keys to Sale - Result: {}/{} Sales was mapped - Time executed: {}s'.format(
            total_mapped_count, sales.count(), time_exc))
