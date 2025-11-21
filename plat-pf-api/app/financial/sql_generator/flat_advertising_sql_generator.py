from abc import ABC
from typing import List

from app.financial.services.utils.common import get_flatten_source_name
from app.financial.sql_generator.flat_items_sql_generator import FlatItemsSQLGenerator
from app.financial.sql_generator.flat_sql_schema_generator import FlatSchemaSQLGenerator
from app.financial.variable.sale_status_static_variable import SALE_SHIPPED_STATUS, SALE_COMPLETED_STATUS


class FlatAdvertisingSQLGenerator(FlatSchemaSQLGenerator, ABC):
    @property
    def config_statement_source(self):
        return {
            # {source column : alias name column}
            # ----------------------------------------------------------------
            "_source_table_.date": {
                "name": "date",
                "pg": {
                    "type": "timestamp without time zone not null"
                },
                "es": {
                    "type": "date"
                }
            },
            "_source_table_.brand_name": {
                "name": "brand_name",
                "pg": {
                    "type": "varchar(255) not null"
                },
                "es": {
                    "type": "text"
                }
            },
            "_source_table_.profit": {
                "name": "profit",
                "pg": {
                    "type": "numeric"
                },
                "es": {
                    "type": "float"
                }
            },
            "_source_table_.revenue": {
                "name": "revenue",
                "pg": {
                    "type": "numeric"
                },
                "es": {
                    "type": "float"
                }
            },
            "_source_table_.ad_spend": {
                "name": "ad_spend",
                "pg": {
                    "type": "numeric"
                },
                "es": {
                    "type": "float"
                }
            },
            "_source_table_.ad_revenue": {
                "name": "ad_revenue",
                "pg": {
                    "type": "numeric"
                },
                "es": {
                    "type": "float"
                }
            },
            "_source_table_.modified": {
                "name": "modified",
                "pg": {
                    "type": "timestamp with time zone not null"
                },
                "es": {
                    "type": "date"
                }
            }
        }

    def get_sql_query_analysis(self, client_id):
        return FlatItemsSQLGenerator().build_flat_query(client_id=client_id)

    def build_flat_query(self, client_id: str = None, ids: List[str] = None, **kwargs):
        flatten_base_for_calculate = get_flatten_source_name(client_id)
        sql_query_analysis = self.get_sql_query_analysis(client_id)

        sql = f"""
            WITH adventising_view AS (
                SELECT 
                    financial_adspendinformation.date AS date_compared,
                    (financial_adspendinformation.date + time '00:00:00')::timestamp AT TIME ZONE '{self.ds_tz_calculate}' AS date, 
                    financial_brand.name AS brand_name, 
                    financial_adspendinformation.spend AS ad_spend, 
                    financial_adspendinformation.ad_revenue_1_day AS ad_revenue
                FROM financial_adspendinformation 
                    LEFT JOIN financial_brand ON financial_adspendinformation.brand_id = financial_brand.id
            ), analysis_view AS (
                SELECT 
                    (sale_date AT TIME ZONE '{self.ds_tz_calculate}')::date AS date_compared,
                    brand::text AS brand_name, 
                    SUM(item_profit)::numeric AS profit,
                    SUM(item_sale_charged)::numeric AS revenue
                FROM ({sql_query_analysis}) AS {flatten_base_for_calculate}
                WHERE 
                    item_sale_status IN ('{SALE_SHIPPED_STATUS}', '{SALE_COMPLETED_STATUS}')
                    AND channel_name = '{self.ds_channel_default}'
                GROUP BY brand_name, date_compared
            )

            SELECT 
                adventising_view.date AS date, 
                adventising_view.brand_name,
                analysis_view.profit,
                analysis_view.revenue,
                adventising_view.ad_spend, 
                adventising_view.ad_revenue,
                now() AS modified
            FROM adventising_view 
                LEFT JOIN analysis_view ON adventising_view.date_compared = analysis_view.date_compared AND adventising_view.brand_name = analysis_view.brand_name
            ORDER BY adventising_view.date ASC;
            """
        return sql
