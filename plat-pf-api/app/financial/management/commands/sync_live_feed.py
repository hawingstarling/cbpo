import json

import maya
from django.core.management.base import BaseCommand
from django.core.paginator import Paginator
from django.db.models import Q

from app.financial.jobs.live_feed import handler_trigger_live_feed_sale_item_ws
from app.financial.models import Channel, SaleItem


class Command(BaseCommand):
    help = "Command sync data live feed sale items from SC."

    def add_arguments(self, parser):
        parser.add_argument('-c', '--client_id', type=str, help='Provide client id for sync live feed data')

        parser.add_argument('-fd', '--from_date', type=str,
                            help='Provide start date for sync live feed. Format YYYY-MM-DD')

        parser.add_argument('-td', '--to_date', type=str,
                            help='Provide end date for sync live feed. Format YYYY-MM-DD')

        parser.add_argument('-mk', '--marketplace', type=str,
                            help='Provide marketplace amazon.com, amazon.ca, amazon.com.mx ...')

        parser.add_argument('-cd', '--condition', type=str,
                            help='Condition filter queryset')

        parser.add_argument('-logs', '--track_logs', action='store_true', help='Enable/Disable track logs')

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
            marketplaces = list(
                Channel.objects.tenant_db_for(client_id).filter(is_pull_data=True).values_list('name', flat=True))

        from_date = options['from_date']

        to_date = options['to_date']

        if not from_date or not to_date:
            print("Please input both params from_date & to_date. Please python manage.py sync_live_feed --help")

        from_date += ' ' + '00:00:00'

        to_date += ' ' + '23:59:59'
        track_logs = options['track_logs']

        # check invalid format date time
        _from_date = maya.parse(from_date).datetime()
        _to_date = maya.parse(to_date).datetime()

        conditions = options['condition']

        for marketplace in marketplaces:
            try:
                if conditions:
                    # using backend for fast update sale item with ranges by conditions filter
                    conditions = json.loads(conditions)
                    cond = Q()
                    for k, v in conditions.get('AND', {}).items():
                        cond.add(Q(**{k: v}), Q.AND)

                    for k, v in conditions.get('OR', {}).items():
                        cond.add(Q(**{k: v}), Q.OR)

                    queryset = SaleItem.objects.tenant_db_for(client_id) \
                        .filter(sale__channel__name=marketplace,
                                sale_date__gte=_from_date,
                                sale_date__lte=_to_date).filter(cond) \
                        .values_list('sale__channel_sale_id', flat=True).order_by('sale_date')
                    # print(queryset.query)
                    p = Paginator(queryset, 1000, allow_empty_first_page=False)
                    num_pages = p.num_pages

                    for page in range(num_pages):
                        page_current = page + 1
                        channel_sale_ids = p.page(number=page_current).object_list
                        print(
                            f'[{client_id}][{marketplace}][{from_date} - {to_date}][{page_current}] add to queue ..... ')
                        # print(f'channel_sale_ids: {channel_sale_ids}')
                        handler_trigger_live_feed_sale_item_ws.delay(client_id=client_id,
                                                                     marketplace=marketplace,
                                                                     channel_sale_ids=list(channel_sale_ids),
                                                                     from_date=from_date, to_date=to_date,
                                                                     track_logs=track_logs)
                else:
                    handler_trigger_live_feed_sale_item_ws.delay(client_id=client_id, marketplace=marketplace,
                                                                 from_date=from_date, to_date=to_date,
                                                                 track_logs=track_logs)
                    print(f'[{client_id}][{marketplace}][{from_date} - {to_date}]'
                          f'[handler_trigger_live_feed_sale_item_ws] add to queue ..... ')
            except Exception as ex:
                print(ex)

        print("---- End sync sale item to table flatten ----")
