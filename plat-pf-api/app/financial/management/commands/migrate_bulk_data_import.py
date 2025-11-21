import hashlib
import json

from django.core.management.base import BaseCommand
from django.db import DEFAULT_DB_ALIAS
from plat_import_lib_api.models import RawDataTemporary
from plat_import_lib_api.static_variable.raw_data_import import RAW_UPDATED_TYPE

from app.financial.models import ClientPortal, BulkData


class Command(BaseCommand):
    help = "Migrate bulk data import command."

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        print(f"Begin migrate bulk data import..... ")
        stats = {'success': 0, 'errors': {}}
        clients = ClientPortal.objects.db_manager(using=DEFAULT_DB_ALIAS).filter(active=True)
        for client in clients:
            bulk_data_queryset = BulkData.objects.tenant_db_for(client.pk).filter(client=client)
            if bulk_data_queryset.count() == 0:
                print(f"[{client.pk}] not found bulk data of client")
                continue
            for bulk in bulk_data_queryset.order_by('-created'):
                try:
                    raws_ins = []
                    lib_import = bulk.data_import
                    obj_ids = bulk.data['sale_item_ids']
                    index = 1
                    for obj_id in obj_ids:
                        raw_ins = RawDataTemporary(
                            lib_import_id=lib_import.pk,
                            index=index,
                            data=dict(id=obj_id),
                            data_map_config=dict(id=obj_id),
                            type=RAW_UPDATED_TYPE,
                            status=lib_import.status,
                            key_map=obj_id,
                            hash_data=hashlib.md5(json.dumps(dict(id=obj_id)).encode('utf-8')).hexdigest()
                        )
                        raws_ins.append(raw_ins)
                        index += 1
                    RawDataTemporary.objects.db_manager(using=DEFAULT_DB_ALIAS).bulk_create(raws_ins,
                                                                                            ignore_conflicts=True)
                    stats['success'] += 1
                except Exception as ex:
                    stats['errors'].update({'bulk_data_id': bulk.pk, 'messages': str(ex)})
        print(f"Complete migrate bulk data import : {stats}")
