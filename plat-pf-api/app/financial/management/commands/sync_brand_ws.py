import copy
import uuid

from django.core.management.base import BaseCommand
from django.core.paginator import Paginator
from django.db.utils import DEFAULT_DB_ALIAS
from django.utils import timezone

from app.financial.models import ClientPortal, Brand, BrandSetting


class Command(BaseCommand):
    help = "Command sync brand ws"

    def add_arguments(self, parser):
        parser.add_argument('-c', '--client_id', type=str, help='Provide client id for sync brand')
        parser.add_argument('-cp_from', '--copy_from', type=str, help='Provide client id copy')
        parser.add_argument('-cp_setting', '--copy_setting', action='store_true',
                            help='True/False cp brand setting. default = False')

    def cp_brands(self, client_id, client_cp_id):
        queryset = Brand.objects.tenant_db_for(client_id) \
            .filter(client_id=client_cp_id).order_by('-created')
        p = Paginator(queryset, 500, allow_empty_first_page=False)
        num_pages = p.num_pages
        print(f"Begin cp brands {client_cp_id} total = {queryset.count()} to ws {client_id}")
        for page in range(num_pages):
            page_current = page + 1
            inserts = []
            objects = p.page(number=page_current).object_list
            #
            print(f'------- sync page = {page_current} , length = {len(objects)} ....')
            for obj in objects:
                find = Brand.objects.tenant_db_for(client_id).filter(client_id=client_id, name=obj.name)
                if find.exists():
                    continue
                cp = copy.deepcopy(obj)
                cp.id = uuid.uuid4()
                cp.client_id = client_id
                inserts.append(cp)
            Brand.objects.tenant_db_for(client_id).bulk_create(inserts, ignore_conflicts=True)

    def cp_brand_settings(self, client_id, client_cp_id):
        queryset = BrandSetting.objects.tenant_db_for(client_cp_id).filter(client_id=client_cp_id).order_by('-created')
        p = Paginator(queryset, 500, allow_empty_first_page=False)
        num_pages = p.num_pages
        print(f"Begin cp brand_settings {client_cp_id} total = {queryset.count()} to ws {client_id}")
        for page in range(num_pages):
            page_current = page + 1
            inserts = []
            objects = p.page(number=page_current).object_list
            #
            print(f'------- sync page = {page_current} , length = {len(objects)} ....')
            for obj in objects:
                if not obj.brand:
                    continue
                brand = Brand.objects.tenant_db_for(client_id) \
                    .filter(client_id=client_id, name=obj.brand.name).first()
                if not brand:
                    continue
                find = BrandSetting.objects.tenant_db_for(client_id) \
                    .filter(client_id=client_id, channel=obj.channel, brand=brand)
                if find.exists():
                    continue
                cp = copy.deepcopy(obj)
                cp.id = uuid.uuid4()
                cp.client_id = client_id
                cp.brand_id = brand.pk
                inserts.append(cp)
            BrandSetting.objects.tenant_db_for(client_id).bulk_create(inserts, ignore_conflicts=True)

    def handle(self, *args, **options):
        print("---- Begin sync brand ----")
        client_id = options['client_id']
        if not client_id:
            client_ids = list(ClientPortal.objects.tenant_db_for(DEFAULT_DB_ALIAS).values_list('pk', flat=True))
        else:
            client_ids = [str(client_id)]
        if len(client_ids) == 0:
            print("Not found clients for sync brand")
            return
        client_cp_id = options['copy_from']
        copy_setting = options['copy_setting']
        brands_none_ws = Brand.objects.tenant_db_for(client_id) \
            .filter(client_id__isnull=True).all().order_by('-created')
        stat = {'total': len(client_ids), 'success': 0, 'error': 0}
        for client_id in client_ids:
            print(f"Begin sync brand for ws : {client_id}")
            try:
                if client_cp_id:
                    self.cp_brands(client_id, client_cp_id)
                    if copy_setting:
                        self.cp_brand_settings(client_id, client_cp_id)
                elif brands_none_ws:
                    brands_none_ws.update(client_id=client_id, modified=timezone.now())
                    brands_none_ws = None
                else:
                    print(f"{client_id} not found client cp id for sync brand")
                    stat['error'] += 1
                    continue
                #
                stat['success'] += 1
            except Exception as ex:
                print(f"[{client_id}] {ex}")
                stat['error'] += 1
        print(stat)
        print("---- End sync brand ----")
