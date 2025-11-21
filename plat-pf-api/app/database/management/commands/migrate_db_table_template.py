from django.core.management.base import BaseCommand
from django.db.utils import DEFAULT_DB_ALIAS

from ...jobs.db_table_template import sync_db_table_template_workspace


class Command(BaseCommand):
    help = "Command sync multi db table."

    def add_arguments(self, parser):
        parser.add_argument('-c', '--client_id', type=str, help='Provide client id')
        parser.add_argument('-new_tb', '--new_table', action='store_true', help='ON/OFF create new table schema')
        parser.add_argument('-sync_column', '--sync_new_column', action='store_true', help='ON/OFF create new table schema')

    def handle(self, *args, **options):
        print("---- Begin sync multi db table ----")

        client_id = options['client_id']
        new_table = options['new_table']
        sync_column = options['sync_new_column']
        if client_id:
            client_ids = [client_id]
        else:
            from app.financial.models import ClientPortal
            client_ids = ClientPortal.objects.tenant_db_for(DEFAULT_DB_ALIAS).values_list('id', flat=True)

        for client_id in client_ids:
            client_id = str(client_id)
            print(f"[{client_id}] Begin sync db table template ...")
            sync_db_table_template_workspace(client_id=client_id, new_table=new_table, sync_column=sync_column)

        print("---- End sync multi db table ----")
