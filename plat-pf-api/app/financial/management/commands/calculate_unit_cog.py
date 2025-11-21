from django.core.management.base import BaseCommand
from app.financial.models import SaleItem

from app.financial.services.utils.common import round_currency
from django.core.paginator import Paginator
from app.financial.jobs.data_flatten import flat_sale_items_bulks_sync_task
from django.db import transaction

class Command(BaseCommand):
    help = "Command calculate file unit cog."

    def add_arguments(self, parser):
        parser.add_argument('-c', '--client_id', type=str, help='Provide client id for calculate unit cog')

        parser.add_argument('-cs', '--chunk_size', type=int, help='Provide chunk size data per page for calculate unit cog')

    def handle(self, *args, **options):

        print("---- Begin sync unit cog ----")

        client_id = options['client_id']

        if not client_id:
            print("Please input param client_id. Please python manage.py calculate_unit_cog --help")
            return

        chunk_size = options.get('chunk_size', 50000)

        query_set = SaleItem.objects.tenant_db_for(client_id).filter(client_id=client_id, cog__isnull=False, unit_cog__isnull=True).order_by('-sale')

        print(f'------ query set : {query_set.query} -------')

        with transaction.atomic():

            p = Paginator(query_set, chunk_size)

            num_pages = p.num_pages

            for page in range(num_pages):

                objs_updated = []
        
                page_current = page + 1

                objs = p.page(number=page_current).object_list

                length = len(objs)

                print(f'------- calculate page = {page_current} , length = {length} ....')

                for obj in objs:
                    try:
                        unit_cog = obj.cog / obj.quantity

                        unit_cog = round_currency(unit_cog)

                        obj.unit_cog = unit_cog
                        obj.dirty = True

                        objs_updated.append(obj)

                    except Exception as ex:
                        print(ex)

                if len(objs_updated) > 0:
                    SaleItem.objects.tenant_db_for(client_id).bulk_update(objs_updated, fields=['unit_cog', 'dirty'])

                    # sync to flatten
                    count_dirty = SaleItem.objects.tenant_db_for(client_id).filter(client_id=client_id, dirty=True).count()
                    if count_dirty > 0:
                        flat_sale_items_bulks_sync_task(client_id)

                    print(f'------ complete page = {page_current} -------')

        print("---- End sync sale item to table flatten ----")
