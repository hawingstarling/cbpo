from django.core.management.base import BaseCommand
from dateutil.parser import parse
from app.financial.jobs.live_feed import handler_trigger_live_feed_sale_item_ws
from app.financial.models import Channel


class Command(BaseCommand):
    help = "Command export data feed sale items."

    def add_arguments(self, parser):
        parser.add_argument('-c', '--client_id', type=str, help='Provide client id for sync data feed data')

    def handle(self, *args, **options):

        print("---- Begin sync sale item to table flatten ----")

        client_id = options['client_id']

        if not client_id:
            print("Please input param client_id. Please python manage.py sync_live_feed --help")
            return

        marketplace = options['marketplace']

        if marketplace:
            marketplaces = [marketplace]
        else:
            marketplaces = list(Channel.objects.tenant_db_for(client_id).filter(is_pull_data=True).values_list('name', flat=True))

        from_date = options['from_date']

        to_date = options['to_date']

        if not from_date or not to_date:
            print("Please input both params from_date & to_date. Please python manage.py sync_live_feed --help")

        from_date += ' ' + '00:00:00'

        to_date += ' ' + '23:59:59'
        track_logs = options['track_logs']

        # check invalid format date time
        parse(from_date)
        parse(to_date)

        for marketplace in marketplaces:
            try:
                handler_trigger_live_feed_sale_item_ws.delay(client_id=client_id, marketplace=marketplace,
                                                                      from_date=from_date, to_date=to_date,
                                                                      track_logs=track_logs)
                print(
                    f'[{client_id}][{marketplace}][{from_date} - {to_date}][handler_trigger_live_feed_sale_item_ws] add to queue ..... ')
            except Exception as ex:
                print(ex)

        print("---- End sync sale item to table flatten ----")
