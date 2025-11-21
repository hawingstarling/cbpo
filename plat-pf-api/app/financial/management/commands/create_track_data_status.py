from datetime import timedelta

from django.core.management.base import BaseCommand
from dateutil.parser import parse

from app.financial.models import Channel, DataStatus, CacheTransaction
from app.core.variable.pf_trust_ac import TIME_CONTROl_TYPE_LIST, OPEN_STATUS


class Command(BaseCommand):
    help = "Command create record tracking data status from SC."

    def add_arguments(self, parser):
        parser.add_argument('-c', '--client_id', type=str, help='Provide client id for sync live feed data')

        parser.add_argument('-fd', '--from_date', type=str,
                            help='Provide start date for sync live feed. Format YYYY-MM-DD')

        parser.add_argument('-td', '--to_date', type=str,
                            help='Provide end date for sync live feed. Format YYYY-MM-DD')

        parser.add_argument('-reset', '--reset_all_open', action='store_true',
                            help='Provide reset status to Open for all record tracking of data')

    def handle(self, *args, **options):

        print("---- Begin create record tracking data status from SC ----")

        client_id = options['client_id']

        if not client_id:
            print("Please input param client_id. Please python manage.py sync_live_feed --help")
            return

        from_date = options['from_date']

        to_date = options['to_date']

        if not from_date or not to_date:
            print("Please input both params from_date & to_date. Please python manage.py sync_live_feed --help")

        _from_date = f'{from_date} 00:00:00'

        _to_date = f'{to_date} 00:00:00'

        # check invalid format date time
        _from_date = parse(_from_date)
        _to_date = parse(_to_date)

        if _from_date > _to_date:
            print(f'From Date do not accept great than To Date')

        channels = Channel.objects.tenant_db_for(client_id).filter(is_pull_data=True)

        while _from_date <= _to_date:
            for tracking_type in TIME_CONTROl_TYPE_LIST:
                for channel in channels:
                    try:
                        DataStatus.objects.tenant_db_for(client_id).get_or_create(client_id=client_id, channel=channel, type=tracking_type,
                                                         date=_from_date.date())
                        print(
                            f'[{client_id}][{channel.name}][{_from_date.date().strftime("%Y-%m-%d")}] add track')
                    except Exception as ex:
                        print(ex)
            _from_date = _from_date + timedelta(days=1)

        # set status Open
        reset_all_open = options['reset_all_open']
        if reset_all_open:
            print(f'----> Reset to Open All Data Status [{from_date} - {to_date}] ....')
            DataStatus.objects.tenant_db_for(client_id).filter(client_id=client_id, date__gte=from_date, date__lte=to_date).update(
                status=OPEN_STATUS)

            print(f'----> Clear hash cache transaction event for sync new data ....')
            CacheTransaction.all_objects.all().delete()

        print("---- End create record tracking data status from SC ----")
