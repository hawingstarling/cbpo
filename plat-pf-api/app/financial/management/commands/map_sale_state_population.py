import time

from django.core.management import BaseCommand
from django.db import transaction
from django.db.utils import DEFAULT_DB_ALIAS

from app.financial.models import Sale, StatePopulation
from app.financial.services.highchart_mapping import HighChartMappingService


class Command(BaseCommand):
    help = 'Command map state_population to sale'

    """
    mapping state_population to sale by country, state
    """

    def add_arguments(self, parser):
        parser.add_argument('-c', '--client_id', type=str, required=True,
                            help='Provide client id for mapping state_population to sale')

    def handle(self, *args, **options):
        with transaction.atomic():

            client_id = options['client_id']
            if client_id:
                print(f"Client ID is required for mapping state_population")

            sales = Sale.objects.tenant_db_for(client_id).filter(state_key__isnull=False)

            print('---- Begin mapping state_population to sale data: {} sales ----'.format(sales.count()))
            print('---- Client ID: {} ----'.format(client_id)) if client_id else None
            start_time = time.time()
            hc_mapping_service = HighChartMappingService()
            state_population = StatePopulation.objects.tenant_db_for(DEFAULT_DB_ALIAS).all()
            mapped_count = 0
            for instance in state_population:
                state_key, _ = hc_mapping_service.get_hc_keys(country=instance.country_postal_code,
                                                              state=instance.state_postal_code)
                count = sales.filter(state_key=state_key).update(population=instance)
                mapped_count += count
                print(f"{instance.country_postal_code}-{instance.state_postal_code}: {count} Sales mapped")

        time_exc = time.time() - start_time
        print('---- End mapping population to Sale - Result: {} Sales was mapped - Time executed: {}s'.format(
            mapped_count, time_exc))
