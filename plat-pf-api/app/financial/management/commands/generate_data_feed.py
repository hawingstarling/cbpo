import time
from datetime import datetime

from django.core.management.base import BaseCommand
from app.financial.models import DataFlattenTrack
from app.financial.services.feeds.sale_item_data_feed import SaleItemDataFeed
from app.financial.tasks import auto_generate_sale_items_data_feed
from app.financial.variable.data_flatten_variable import FLATTEN_SALE_ITEM_KEY


class Command(BaseCommand):
    help = "Command to generate latest data_feed of specified type and client_id."

    def add_arguments(self, parser):
        parser.add_argument('-a', '--auto', action='store_true', help='Generate data_feed from auto_feed_brand')
        parser.add_argument('-c', '--client_id', type=str, help='Provide client_id for generating data_feed')
        parser.add_argument('--channel', type=str,
                            help='Provide channel_name for generating data_feed')
        parser.add_argument('--brand', type=str, help='Provide brand_name for generating data_feed')

    def handle(self, *args, **options):
        if options['auto']:
            auto_generate_sale_items_data_feed()
            return

        if options.get('client_id'):
            client_id = options.get('client_id')
        else:
            print("Please input client_id (-c --client_id). Run python manage.py generate_data_feed --help")
            return

        if options.get('channel'):
            channel_name = options.get('channel')
        else:
            print("Please input channel name (--channel). Run python manage.py generate_data_feed --help")
            return

        if options.get('brand'):
            brand_name = options.get('brand')
        else:
            print("Please input brand name (--brand). Run python manage.py generate_data_feed --help")
            return

        print(f"---- Begin generating data_feed for [{client_id}][{channel_name}][{brand_name}] ----")
        start = time.time()
        try:
            year = datetime.now().year
            DataFlattenTrack.objects.tenant_db_for(client_id).get(client_id=client_id, type=FLATTEN_SALE_ITEM_KEY)
            SaleItemDataFeed(client_id, 2020, channel_name=channel_name, brand_name=brand_name).generate()
        except DataFlattenTrack.DoesNotExist:
            print(f'The specified client <{client_id}> is not valid to generate data_feed')

        end = time.time()
        print(f"---- End generating data_feed for {client_id} - Time executed: {end - start} ----")
