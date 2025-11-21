from django.core.management import BaseCommand
from django.db import transaction

from app.financial.jobs.data_flatten import flat_sale_items_bulks_sync_task
from app.financial.models import DataFlattenTrack
from app.financial.services.data_flatten import DataFlatten
from app.financial.sql_generator.flat_sql_generator_container import SqlGeneratorContainer


class Command(BaseCommand):
    args = '<foo bar ...>'
    help = 'our help string comes here'

    """
    test performance sql flatten
    just for testing
    """

    def handle(self, *args, **options):
        with transaction.atomic():
            client_id = '1dd0bded-e981-4d2f-9bef-2874016661e7'
            data_flatten_track = DataFlattenTrack.objects.tenant_db_for(using=client_id).get(
                client_id='1dd0bded-e981-4d2f-9bef-2874016661e7',
                type='SALE_ITEMS')
            index_fields = ['sale_item_id']
            data_source_handler = DataFlatten(client_id=client_id, type_flatten='SALE_ITEMS',
                                              sql_generator=SqlGeneratorContainer.flat_sale_items(),
                                              index_fields=index_fields)
            data_source_handler.do_flatten()
            flat_sale_items_bulks_sync_task(client_id)
