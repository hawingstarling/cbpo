from django.core.management.base import BaseCommand

from app.core.variable.marketplace import CHANNEL_DEFAULT
from app.financial.models import SaleItem, Sale, SaleChargeAndCost
from django.core.paginator import Paginator
from django.db import transaction
from django.utils import timezone
from app.financial.jobs.data_flatten import flat_sale_items_bulks_sync_task


class Command(BaseCommand):
    help = "Command clean data sale invalid channel amazon us."

    def add_arguments(self, parser):
        parser.add_argument('-c', '--client_id', type=str,
                            help='Provide client id for clean data sale invalid in channel amazon us.')

    def handle(self, *args, **options):

        print("---- Begin clean data invalid channel amazon us ----")

        client_id = options['client_id']

        if not client_id:
            print("Please input param client_id. Please python manage.py sync_live_feed --help")
            return

        now = timezone.now()

        chunk_size = 200

        #### get channel name Altra - Canada & The North Face - Canada in sale item of channel amazon.us

        # get all channel sale id of channel amazon.ca

        with transaction.atomic():

            queryset = Sale.objects.tenant_db_for(client_id).filter(channel__name='amazon.ca',
                                                                    is_removed=False).order_by(
                '-created')

            p = Paginator(queryset, chunk_size)

            num_pages = p.num_pages

            for page in range(num_pages):

                info_clean = []

                sale_ids = []

                sale_items_ids = []

                # channel_ids

                page_current = page + 1

                objs = p.page(number=page_current).object_list

                length = len(objs)

                print(f'------- clean page = {page_current} , length = {length} ....')

                for obj in objs:

                    try:
                        sale = Sale.objects.tenant_db_for(client_id).tenant_db_for(client_id).get(client_id=client_id,
                                                                                                  channel__name=CHANNEL_DEFAULT,
                                                                                                  channel_sale_id=obj.channel_sale_id,
                                                                                                  is_removed=False)

                    except Sale.DoesNotExist:
                        continue

                    # check again to api
                    items = obj.saleitem_set.tenant_db_for(client_id).filter(is_removed=False).order_by('-created')
                    for item in items:
                        try:
                            _find = SaleItem.objects.tenant_db_for(client_id).get(sale=sale, sku=item.sku,
                                                                                  is_removed=False)

                            _info = {
                                'sale_item_id': _find.id,
                                'sale_id': sale.id,
                                'channel_sale_id': sale.channel_sale_id,
                                'sku': _find.sku
                            }

                            info_clean.append(_info)

                            # add id for remove
                            sale_items_ids.append(_find.pk)

                            if sale.saleitem_set.tenant_db_for(sale.client_id).count() == 1:
                                sale_ids.append(sale.pk)
                        except SaleItem.DoesNotExist:
                            continue
                total_sale_item_ids = len(sale_items_ids)
                total_sale_ids = len(sale_ids)

                if total_sale_item_ids > 0:
                    SaleItem.objects.tenant_db_for(client_id).filter(pk__in=sale_items_ids).update(is_removed=True,
                                                                                                   dirty=True,
                                                                                                   modified=now)
                if total_sale_ids > 0:
                    SaleChargeAndCost.objects.tenant_db_for(client_id).filter(sale_id__in=sale_ids).update(
                        is_removed=True, modified=now)
                    Sale.objects.tenant_db_for(client_id).filter(pk__in=sale_ids).update(is_removed=True, modified=now)

                # sync to flatten
                if total_sale_item_ids > 0:
                    flat_sale_items_bulks_sync_task(client_id)

                print(f'Info clean : {info_clean}')

        print("---- End clean data invalid channel amazon us ----")
