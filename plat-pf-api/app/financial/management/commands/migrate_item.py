from django.core.management.base import BaseCommand

from app.core.logger import logger
from app.financial.services.item.item_migration_from_file import ItemMigration


class Command(BaseCommand):
    help = "Command migrate item from file"

    def add_arguments(self, parser):
        parser.add_argument('-c', '--client_id', type=str,
                            help='Provide client id for sync sale items from live feed AC')
        parser.add_argument('-s', '--size', type=int,
                            help='Size')
        parser.add_argument('-p', '--path', type=str,
                            help='File path')

    def handle(self, *args, **options):
        size = options.get('size')
        if not size:
            size = 1000
        client_id = options['client_id']
        if not client_id:
            raise Exception('required client_id')

        file_path = options['path']
        if not file_path:
            raise Exception('required file path')

        logger.info('System Command to migrate item from file')
        handler = ItemMigration(client_id, file_path, size)
        handler.handle()
