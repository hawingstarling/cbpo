import logging
from django.core.management.base import BaseCommand
from django.db import DEFAULT_DB_ALIAS

from app.financial.models import ProfitStatus
from app.financial.variable.profit_status_static_variable import PROFIT_STATUS_ORDER_DICT, \
    PROFIT_STATUS_ENUM, PROFIT_STATUS

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "This command using for init profit status."

    def add_arguments(self, parser):
        parser.add_argument('-over', '--override', type=bool, default=False,
                            help='--override init config sale status of financial')
        parser.add_argument('-db', '--db_config', type=str, help='Provide database name')

    def handle(self, *args, **options):
        try:
            print("Start run init profit status")
            _override = options.get('over', False)
            _db = options.get('db_config', DEFAULT_DB_ALIAS)
            _total = ProfitStatus.objects.db_manager(using=_db).all().count()
            print("Override profit status init {}".format(_override))
            print("Database config profit status init {}".format(_db))
            print("Number profit status now {}".format(_total))
            if _total == len(PROFIT_STATUS) and not _override:
                return
            for _item in list(PROFIT_STATUS_ENUM):
                print('Init for profit status : {}'.format(_item))
                print('Order number of profit {}'.format(PROFIT_STATUS_ORDER_DICT[_item[0]]))
                value = _item[0]
                name = _item[0]
                order = PROFIT_STATUS_ORDER_DICT[_item[0]]
                default = {
                    'name': name,
                    'order': order
                }
                ProfitStatus.objects.db_manager(using=_db).update_or_create(value=value, defaults=default)
            print("End init profit status")
        except Exception as ex:
            logger.error('Command init profit status errors : {}'.format(ex))
            print("Command init profit status errors : {}".format(ex))
