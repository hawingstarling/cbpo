from django.core.management.base import BaseCommand
from django.db import DEFAULT_DB_ALIAS, DatabaseError, connections

from app.database.helper import get_connection_workspace
from app.es.helper import get_es_sources_configs
from app.financial.models import ClientPortal


class Command(BaseCommand):
    help = "This is command separate freight cost to Inbound & Outbound."

    def add_arguments(self, parser):
        parser.add_argument("-c", "--client_id", type=str, help="Provide client id for separate freight cost")
        parser.add_argument("-f", "--trans_to_freight", type=str,
                            help="Provide Inbound or Outbound for migrate Freight Cost")

    def handle(self, *args, **options):
        print("---- Begin separate shipping cost to Inbound & Outbound ----")
        client_id = options.get("client_id")
        trans_to_freight = options.get("trans_to_freight")
        if trans_to_freight is None:
            print(f"Please Inbound or Outbound for migrate Freight Cost ...")
            return
        assert trans_to_freight in ["inbound", "outbound"], f"Please Inbound or Outbound for migrate Freight Cost ..."
        if client_id is None:
            client_ids = ClientPortal.objects.tenant_db_for(DEFAULT_DB_ALIAS).values_list("id", flat=True)
        else:
            client_ids = [client_id]
        es_sources_configs = get_es_sources_configs()
        for client_id in client_ids:
            client_id = str(client_id)
            print(f"---- [{client_id}][PG][{trans_to_freight}] Migrate Freight Cost into {trans_to_freight} "
                  f"Freight Cost workspace ----")
            client_id_db = str(client_id).replace("-", "_")
            _sql = f"""
                        UPDATE financial_{client_id_db}_saleitem 
                        SET {trans_to_freight}_freight_cost = freight_cost, 
                            {trans_to_freight}_freight_cost_accuracy = freight_cost_accuracy    
                        WHERE freight_cost IS NOT NULL;

                        UPDATE financial_{client_id_db}_itemfinancial 
                        SET {trans_to_freight}_freight_cost = freight_cost, 
                            {trans_to_freight}_freight_cost_accuracy = freight_cost_accuracy    
                        WHERE freight_cost IS NOT NULL;
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
            print(f"---- [{client_id}][ES][{trans_to_freight}] Migrate Freight Cost into {trans_to_freight} "
                  f"Freight Cost workspace ----")
            for key, es_source_class in es_sources_configs.items():
                try:
                    es_service = es_source_class(client_id)
                    response = es_service.es.update_by_query(
                        index=es_service.index, body={
                            "script": {
                                "source": f"""
                                        ctx._source['{trans_to_freight}_freight_cost'] = ctx._source['freight_cost'];
                                        ctx._source['{trans_to_freight}_freight_cost_accuracy'] = ctx._source['freight_cost_accuracy'];
                                    """,
                                "lang": "painless"
                            },
                            "query": {
                                "bool": {
                                    "filter": [
                                        {
                                            "exists": {
                                                "field": "freight_cost"
                                            }
                                        },
                                        {
                                            "range": {
                                                "freight_cost": {
                                                    "gt": 0
                                                }
                                            }
                                        }
                                    ]
                                }
                            }
                        }
                    )
                    print(f"---- [{client_id}][ES][{key}] Response {response} ----")
                except Exception as ex:
                    print(f"---- [{client_id}][ES][{key}] Error {ex} ----")
