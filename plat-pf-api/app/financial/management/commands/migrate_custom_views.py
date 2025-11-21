import json
import uuid

from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from django.core.paginator import Paginator
from django.db.utils import DEFAULT_DB_ALIAS
from django.forms.models import model_to_dict

from app.financial.models import CustomColumn, CustomView, CustomFilter, ClientPortal, ShareCustom
from app.database.helper import get_connection_workspace
from config.settings.common import ROOT_DIR


class Command(BaseCommand):
    help = "Sync custom columns, custom filters and share to model custom views."

    def __init__(self, stdout=None, stderr=None, no_color=False, force_color=False):
        super().__init__(stdout, stderr, no_color, force_color)
        APPS_DIR = ROOT_DIR.path('app')

        json_data = open(f"{APPS_DIR}/financial/management/commands/fixtures/ds_filters_default.json")
        self.ds_filters_default = json.load(json_data)
        json_data.close()

        json_data = open(f"{APPS_DIR}/financial/management/commands/fixtures/ds_columns_default.json")
        self.ds_columns_default = json.load(json_data)
        json_data.close()

    def add_arguments(self, parser):
        parser.add_argument('-c', '--client_id', type=str, help='Provide client id for sync')

    def move_objects_to_views(self, client_id: str, model_instance: any):
        """
        - move custom filters, columns to custom views
            - name of custom view is name custom move
                - e.g name custom filter = 'A-filter' so custom view name = 'A-filter'
                - e.g name custom column = 'A-column' so custom view name = 'A-column'
        - move share custom filters , columns to custom views
        """
        model_name = model_instance._meta.model_name
        queryset = model_instance.objects.tenant_db_for(client_id) \
            .filter(client_id=client_id).order_by('created')

        total_items = queryset.count()
        print(f'[{client_id}][{model_name}] total sync to views = {total_items}')
        if total_items == 0:
            return

        p = Paginator(queryset, 100, allow_empty_first_page=False)
        num_pages = p.num_pages

        for page in range(num_pages):
            page_current = page + 1
            cp_objs = p.page(number=page_current).object_list
            print(f'[{client_id}][{model_name}][{page_current}] processing sync ..... ')
            #
            objs = []
            objs_share = []
            for item in cp_objs:
                # sync custom model
                data = model_to_dict(item)
                data.update({'client_id': data['client']})
                del data['client']
                data.update({'user_id': data['user']})
                del data['user']
                obj = CustomView(**data)
                obj.pk = item.pk
                if model_instance._meta.model_name == 'customcolumn':
                    obj.ds_filter = self.ds_filters_default
                else:
                    obj.ds_column = self.ds_columns_default
                objs.append(obj)

                # sync share custom model
                client_db = get_connection_workspace(client_id)
                content_type_id = ContentType.objects.db_manager(using=client_db).get_for_model(model_instance).pk
                shares = ShareCustom.objects.tenant_db_for(client_id) \
                    .filter(client_id=client_id, object_id=obj.pk,
                            content_type_id=content_type_id)
                for share in shares:
                    share_data = model_to_dict(share)
                    share_data.update({'client_id': share_data['client']})
                    del share_data['client']
                    del share_data['content_type']
                    obj_share = ShareCustom(**share_data, content_object=obj)
                    obj_share.pk = uuid.uuid4()
                    objs_share.append(obj_share)

            print(f"number sync {model_instance._meta.model_name} to views = {len(objs)}")
            if objs:
                CustomView.objects.tenant_db_for(client_id).bulk_create(objs, ignore_conflicts=True)
            print(f"number sync share action {model_instance._meta.model_name} to views = {len(objs_share)}")
            if objs_share:
                ShareCustom.objects.tenant_db_for(client_id).bulk_create(objs_share, ignore_conflicts=True)

    def handle(self, *args, **options):
        print("---- Begin sync sale item to table flatten ----")
        client_id = options['client_id']
        if client_id:
            client_ids = [client_id]
        else:
            client_ids = ClientPortal.objects.tenant_db_for(DEFAULT_DB_ALIAS).values_list("id", flat=True)
        stat = {'total client_ids ': len(client_ids), 'success': 0, 'error': 0}
        for client_id in client_ids:
            print(f"begin sync {client_id} ... ")
            # move columns to views
            try:
                self.move_objects_to_views(client_id, CustomColumn)
                self.move_objects_to_views(client_id, CustomFilter)
                stat['success'] += 1
            except Exception as ex:
                print(f"errors sync : {ex}")
                stat['error'] += 1
                continue
        print(stat)
        print(f"completed sync {client_id} ... ")
