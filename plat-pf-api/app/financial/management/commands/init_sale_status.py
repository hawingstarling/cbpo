import logging

from django.core.management.base import BaseCommand
from django.db.utils import DEFAULT_DB_ALIAS

from ...models import SaleStatus
from ...variable.sale_status_static_variable import SALE_STATUS

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "This command init sale status"

    def add_arguments(self, parser):
        parser.add_argument('-over', '--override', type=bool, default=False,
                            help='--override init config sale status of financial')
        parser.add_argument('-db', '--db_config', type=str, help='Provide database name')

    def handle(self, *args, **options):
        try:
            print("Begin init sale status")
            _override = options.get('over', False)
            _db = options.get('db_config', DEFAULT_DB_ALIAS)
            _total = SaleStatus.objects.db_manager(using=_db).all().count()
            print("Override sale status init {}".format(_override))
            print("Database config sale status init {}".format(_db))
            print("Number sale status now {}".format(_total))
            if _total == len(SALE_STATUS) and not _override:
                return
            for _item in SALE_STATUS:
                print('Init for sale status : {}'.format(_item))
                # make default
                value = _item[0][0]
                name = _item[0][1]
                order = _item[1][0]
                description = _item[1][1]
                default = {
                    'name': name,
                    'order': order,
                    'description': description
                }
                SaleStatus.objects.db_manager(using=_db).update_or_create(value=value, defaults=default)
            print("End init sale status")
        except Exception as ex:
            logger.error('Command init sale status error {}'.format(ex))
            print('Init sale status error {}'.format(ex))
