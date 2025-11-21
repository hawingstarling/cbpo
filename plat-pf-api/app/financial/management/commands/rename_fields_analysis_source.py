import copy

from django.core.management.base import BaseCommand
from app.financial.models import ClientPortal
from django.db import connections, DatabaseError, DEFAULT_DB_ALIAS
from app.database.helper import get_connection_workspace


class Command(BaseCommand):
    help = "Command rename field table DB/Analysis Source"

    def add_arguments(self, parser):
        parser.add_argument('-c', '--client_id', type=str, help='Provide client_id')
        parser.add_argument('-f', '--from_field', type=str, help='Provide from field')
        parser.add_argument('-t', '--to_field', type=str, help='Provide to field')

    def handle(self, *args, **options):

        client_id_request = options['client_id']
        from_field = options['from_field']
        to_field = options['to_field']

        if client_id_request:
            client_ids = [client_id_request]
        else:
            client_ids = ClientPortal.objects.tenant_db_for(DEFAULT_DB_ALIAS).values_list('pk', flat=True)

        sql_rename_table_base_template = """
            --------- Sale Item ----------
            DO $$
            BEGIN
              IF EXISTS(SELECT *
                FROM information_schema.columns
                WHERE table_name='{sale_item_tbl}' and column_name='{from_field}')
              THEN
                  ALTER TABLE "public"."{sale_item_tbl}" RENAME COLUMN "{from_field}" TO "{to_field}";
              END IF;
            END $$;

            --------- Sale Item Financial ----------

            DO $$
            BEGIN
              IF EXISTS(SELECT *
                FROM information_schema.columns
                WHERE table_name='{sale_item_financial_tbl}' and column_name='{from_field}')
              THEN
                  ALTER TABLE "public"."{sale_item_financial_tbl}" RENAME COLUMN "{from_field}" TO "{to_field}";
              END IF;
            END $$;
        """

        sql_rename_table_default = copy.deepcopy(sql_rename_table_base_template)
        sql_rename_table_default = sql_rename_table_default.format(sale_item_tbl='financial_saleitem',
                                                                   sale_item_financial_tbl='financial_saleitemfinancial',
                                                                   from_field=from_field,
                                                                   to_field=to_field)

        client_db = get_connection_workspace(DEFAULT_DB_ALIAS)

        with connections[client_db].cursor() as cursor:
            try:
                # print(f"sql_rename_table_default: {sql_rename_table_default}")
                cursor.execute(sql_rename_table_default)
                print(f"sql_rename_table_default: Success")
            except Exception or DatabaseError as err:
                print(f"sql_rename_table_default: error {err}")
                cursor.execute("ROLLBACK")

        for client_id in client_ids:
            client_id_db = str(client_id).replace('-', '_')
            sale_item_tbl = f'financial_{client_id_db}_saleitem'
            sale_item_financial_tbl = f'financial_{client_id_db}_itemfinancial'
            sql_rename_table_split = copy.deepcopy(sql_rename_table_base_template)
            sql_rename_table_base_split = sql_rename_table_split.format(sale_item_tbl=sale_item_tbl,
                                                                        sale_item_financial_tbl=sale_item_financial_tbl,
                                                                        from_field=from_field,
                                                                        to_field=to_field)

            sale_item_flatten_tbl = f'flatten_sale_items_{client_id_db}'
            sale_item_financial_flatten_tbl = f'flatten_sale_financial_{client_id_db}'
            sql_rename_table_split = copy.deepcopy(sql_rename_table_base_template)

            sql_rename_table_flatten_split = sql_rename_table_split.format(sale_item_tbl=sale_item_flatten_tbl,
                                                                           sale_item_financial_tbl=sale_item_financial_flatten_tbl,
                                                                           from_field=from_field,
                                                                           to_field=to_field)

            # print(sql_rename_table_split)

            client_db = get_connection_workspace(client_id)

            with connections[client_db].cursor() as cursor:
                try:
                    print(f"sql_rename_table_split [{client_id}] Begin table split ...")
                    cursor.execute(sql_rename_table_base_split)
                    print(f"sql_rename_table_split [{client_id}] Completed table split")
                except Exception or DatabaseError as err:
                    print(f"sql_rename_table_split {client_id}: error {err}")
                    cursor.execute("ROLLBACK")

                try:
                    print(f"sql_rename_table_flatten [{client_id}] Begin table flatten source ...")
                    cursor.execute(sql_rename_table_flatten_split)

                    print(f"sql_rename_table_flatten [{client_id}] Completed table flatten source")
                except Exception or DatabaseError as err:
                    print(f"sql_rename_table_flatten {client_id}: error {err}")
                    cursor.execute("ROLLBACK")
