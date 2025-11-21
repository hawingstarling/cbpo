from django.core.management.base import BaseCommand
from django.db import DEFAULT_DB_ALIAS, connections, DatabaseError
from app.database.helper import get_connection_workspace
from app.financial.models import ClientPortal


class Command(BaseCommand):
    help = "Separate shipping cost to Actual shipping cost and Estimated shipping cost."

    def add_arguments(self, parser):
        parser.add_argument("-c", "--client_id", type=str, help="Provide client id for separate shipping cost")

    def handle(self, *args, **options):
        print("---- Begin separate shipping cost to ASC & ESC ----")
        client_id = options.get("client_id")
        if client_id is None:
            client_ids = ClientPortal.objects.tenant_db_for(DEFAULT_DB_ALIAS).values_list("id", flat=True)
        else:
            client_ids = [client_id]
        for client_id in client_ids:
            print(f"---- Calculating ASC & ESC workspace {client_id} ----")
            client_id_db = str(client_id).replace("-", "_")
            _sql = f"""
                UPDATE financial_{client_id_db}_saleitem 
                SET actual_shipping_cost = shipping_cost 
                WHERE shipping_cost_accuracy IS NOT NULL 
                  AND shipping_cost_accuracy = 100 AND actual_shipping_cost IS NULL;
                  
                UPDATE financial_{client_id_db}_saleitem 
                SET estimated_shipping_cost = shipping_cost 
                WHERE (shipping_cost_accuracy IS NOT NULL 
                  AND shipping_cost_accuracy < 100 OR shipping_cost_accuracy is NULL) 
                  AND estimated_shipping_cost IS NULL;
                  
                UPDATE financial_{client_id_db}_itemfinancial 
                SET actual_shipping_cost = shipping_cost 
                WHERE shipping_cost_accuracy IS NOT NULL 
                  AND shipping_cost_accuracy = 100 AND actual_shipping_cost IS NULL;
                  
                UPDATE financial_{client_id_db}_itemfinancial 
                SET estimated_shipping_cost = shipping_cost 
                WHERE (shipping_cost_accuracy IS NOT NULL 
                  AND shipping_cost_accuracy < 100 OR shipping_cost_accuracy is NULL) 
                  AND estimated_shipping_cost IS NULL;
            """

            client_db = get_connection_workspace(DEFAULT_DB_ALIAS)
            with connections[client_db].cursor() as cursor:
                try:
                    print(f"SQL: {_sql}")
                    cursor.execute(_sql)
                    print(f"Run SQL is Success")
                except Exception or DatabaseError as err:
                    print(f"Run SQL is Error {err}")
                    cursor.execute("ROLLBACK")
