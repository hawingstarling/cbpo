from django.core.management.base import BaseCommand
from dateparser import parse
from app.financial.jobs.event import handler_trigger_trans_event_sale_item_ws
from app.financial.models import Channel
from app.financial.variable.job_status import MODIFIED_FILTER_MODE


class Command(BaseCommand):
    help = "Command sync data trans event sale items from SC."

    def add_arguments(self, parser):
        parser.add_argument('-c', '--client_id', type=str, help='Provide client id for sync trans event data',
                            required=True)

        # range with data modified_from and to_modified

        parser.add_argument('-fd', '--from_date', type=str,
                            help='Provide start date for sync trans event. Format YYYY-MM-DD')

        parser.add_argument('-td', '--to_date', type=str,
                            help='Provide end date for sync trans event. Format YYYY-MM-DD')

        parser.add_argument('-mk', '--marketplace', type=str,
                            help='Provide marketplace amazon.com, amazon.ca, amazon.com.mx ...')

        parser.add_argument('-fm', '--filter_mode', type=str,
                            help='Provide filter mode [posted, modified]')

        parser.add_argument('-logs', '--track_logs', action='store_true', help='Enable/Disable track logs')

    def handle(self, *args, **options):

        print("---- Begin sync sale item to table flatten ----")

        client_id = options['client_id']

        marketplace = options['marketplace']

        if marketplace:
            marketplaces = [marketplace]
        else:
            marketplaces = list(
                Channel.objects.tenant_db_for(client_id).filter(is_pull_data=True).values_list('name', flat=True))

        filter_mode = options['filter_mode']

        if not filter_mode:
            filter_mode = MODIFIED_FILTER_MODE

        from_date = options['from_date']
        to_date = options['to_date']

        track_logs = options['track_logs']

        if not client_id:
            print("Please input param client_id. Please python manage.py sync_trans_event --help")
            return

        # check invalid format date time
        parse(from_date)
        parse(to_date)

        from_date = f'{from_date} 00:00:00'
        to_date = f'{to_date} 23:59:59'
        for marketplace in marketplaces:
            try:
                Channel.objects.tenant_db_for(client_id).get(name__iexact=marketplace)
            except Channel.DoesNotExist:
                print(f'[{marketplace}] not exist in table Channel')
                continue
            handler_trigger_trans_event_sale_item_ws.delay(client_id=client_id, marketplace=marketplace,
                                                                       from_date=from_date, to_date=to_date,
                                                                       track_logs=track_logs,
                                                                       filter_mode=filter_mode)
            print(
                f'[{client_id}][{marketplace}][{from_date} - {to_date}][handler_trigger_trans_event_sale_item_ws][{filter_mode}] add to queue ..... ')

        print("---- End sync sale item to table flatten ----")
