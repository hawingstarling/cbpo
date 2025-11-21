from django.core.management.base import BaseCommand
from django.db import DEFAULT_DB_ALIAS
from elasticsearch import Elasticsearch
from app.es.helper import get_es_host_client
from app.es.variables.config import ES_TIMEOUT
from app.es.variables.template import INDEX_TEMPLATE_CONFIGS
from app.financial.models import ClientPortal


class Command(BaseCommand):
    help = "Elasticsearch Update By Query."

    def add_arguments(self, parser):
        parser.add_argument("-c", "--client_id", type=str, help="Provide client id")
        parser.add_argument("-t", "--timeout", type=int, help="Provide timeout")

    def handle(self, *args, **options):
        print(f"Begin {self.help}")
        client_id_rq = options.get("client_id")
        es_time_out = options.get("timeout", ES_TIMEOUT)
        queryset = ClientPortal.objects.tenant_db_for(DEFAULT_DB_ALIAS).all()
        if client_id_rq is not None:
            queryset = queryset.filter(id=client_id_rq)
        stats = dict(
            workspaces=queryset.count(),
            success=0,
            errors=0,
            messages=[],
        )
        for obj in queryset.order_by("-active", "name"):
            client_id = str(obj.pk)
            try:
                #
                print(f"Running {self.help.lower()} of workspace {client_id} ......")
                host = get_es_host_client(client_id)
                es = Elasticsearch(hosts=[host], timeout=es_time_out)
                for k, v in INDEX_TEMPLATE_CONFIGS.items():
                    index = v.format(client_id=client_id.replace('-', '_'))
                    for body in self.body_contents:
                        rs = es.update_by_query(body=body, index=index)
                        print(f"[ws={obj.name}][index={index}] Response {rs}")
                stats["success"] += 1
            except Exception as ex:
                stats["errors"] += 1
                stats["messages"].append(f"[ws={obj.pk}-{obj.name}] errors {ex}")
        print(f"Stats {self.help}: {stats}")

    @property
    def body_contents(self):
        return [
            {
                "script": {
                    "lang": "painless",
                    "source": "ctx._source.actual_shipping_cost = ctx._source.item_shipping_cost;"
                },
                "query": {
                    "match": {
                        "shipping_cost_accuracy": 100
                    }
                }
            },
            {
                "script": {
                    "lang": "painless",
                    "source": "ctx._source.estimated_shipping_cost = ctx._source.item_shipping_cost;"
                },
                "query": {
                    "bool": {
                        "should": [
                            {
                                "bool": {
                                    "must_not": [
                                        {
                                            "exists": {
                                                "field": "shipping_cost_accuracy"
                                            }
                                        }
                                    ]
                                }
                            },
                            {
                                "range": {
                                    "shipping_cost_accuracy": {
                                        "gte": 0,
                                        "lt": 100
                                    }
                                }
                            }
                        ]
                    }
                }
            }
        ]
