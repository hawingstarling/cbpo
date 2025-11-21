import copy
import numpy as np
import pandas as pd
from abc import ABC
from django.utils import timezone
from app.financial.services.data_source import DataSource
from app.financial.services.utils.common import get_id_data_source_3rd_party
from app.financial.services.utils.helper import get_analysis_es_service, get_analysis_3rd_party
from app.financial.sql_generator.flat_sql_schema_generator import FlatSchemaSQLGenerator, logger
from datetime import timedelta, datetime
from dateutil.relativedelta import relativedelta

from app.financial.variable.data_flatten_variable import FLATTEN_PG_SOURCE, FLATTEN_ES_SOURCE
from app.financial.variable.sale_status_static_variable import SALE_SHIPPED_STATUS


class FlatSaleBigMovesSQLGenerator(FlatSchemaSQLGenerator, ABC):

    @property
    def config_statement_source(self):
        return {
            # {source column : alias name column}
            # ----------------------------------------------------------------
            "_source_table_.product_number": {
                "name": "product_number",
                "pg": {
                    "type": "varchar(255) not null"
                },
                "es": {
                    "type": "text"
                }
            },
            # -----------------------------------------------------------------
            "_source_table_.total_quantity_day": {
                "name": "total_quantity_day",
                "pg": {
                    "type": "numeric"
                },
                "es": {
                    "type": "float"
                }
            },
            "_source_table_.total_quantity_30d": {
                "name": "total_quantity_30d",
                "pg": {
                    "type": "numeric"
                },
                "es": {
                    "type": "float"
                }
            },
            "_source_table_.total_avg_quantity_30d": {
                "name": "total_avg_quantity_30d",
                "pg": {
                    "type": "numeric"
                },
                "es": {
                    "type": "float"
                }
            },
            "_source_table_.total_avg_quantity_12m": {
                "name": "total_avg_quantity_12m",
                "pg": {
                    "type": "numeric"
                },
                "es": {
                    "type": "float"
                }
            },
            "_source_table_.quantity_d_vs_quantity_avg_30d": {
                "name": "quantity_d_vs_quantity_avg_30d",
                "pg": {
                    "type": "numeric"
                },
                "es": {
                    "type": "float"
                }
            },
            "_source_table_.quantity_30d_vs_quantity_avg_12m": {
                "name": "quantity_30d_vs_quantity_avg_12m",
                "pg": {
                    "type": "numeric"
                },
                "es": {
                    "type": "float"
                }
            },
            "_source_table_.distance_day_vs_avg_30d": {
                "name": "distance_day_vs_avg_30d",
                "pg": {
                    "type": "numeric"
                },
                "es": {
                    "type": "float"
                }
            },
            "_source_table_.distance_30d_vs_avg_12m": {
                "name": "distance_30d_vs_avg_12m",
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

    def build_count_aggregations_unique_combinations(self, client_id, **kwargs):
        analysis_es_service = get_analysis_es_service(client_id)
        from_date_12m_ago = self.yesterday - relativedelta(months=12)
        from_date = from_date_12m_ago.strftime("%Y-%m-%d 00:00:00")
        to_date = self.yesterday.strftime("%Y-%m-%d 23:59:59")
        query = {
            "size": 0,
            "query": {
                "bool": {
                    "must": [
                        {"term": {"channel_name.keyword": self.ds_channel_default}},
                        {"terms": {"item_sale_status.keyword": [
                            SALE_SHIPPED_STATUS]}},
                        {
                            "range": {
                                "sale_date": {
                                    "gte": from_date,
                                    "lte": to_date,
                                    "format": "yyyy-MM-dd HH:mm:ss",
                                    "time_zone": self.ds_tz_calculate
                                }
                            }
                        },
                        {"exists": {"field": "product_number"}},
                        {
                            "script": {
                                "script": """
                                  doc['product_number.keyword'].size() > 0 && doc['product_number.keyword'].value != ''
                                """
                            }
                        }
                    ]
                }
            },
            "aggs": {
                "unique_combinations": {
                    "cardinality": {
                        "script": {
                            "source": "doc['product_number.keyword'].value",
                            "lang": "painless"
                        }
                    }
                }
            }
        }
        res = analysis_es_service.search(query=query)
        count = res["aggregations"]["unique_combinations"]["value"]
        return count

    def build_query_for_number_sync_rows(self, client_id, **kwargs):
        """
        build a query for counting the number of dirty rows in the original table
        :return:
        """
        count = self.build_count_aggregations_unique_combinations(
            client_id=client_id, **kwargs)
        sql = f"""
            SELECT {count};
        """
        return sql

    def _aggregate(self, client_id: str, analysis_3rd_party: DataSource, external_id: str, total: int = 0,
                   page: int = 1, size: int = 500, modified_filter: str = None):
        # Set the Option to Accept Future Behavior (opt-in)
        # This will silence the warning and enforce stricter behavior, preparing your code for future pandas versions.
        pd.set_option('future.no_silent_downcasting', True)

        conditions = [
            {
                "column": "product_number",
                "operator": "not_null",
                "value": ""
            },
            {
                "column": "product_number",
                "operator": "$ne",
                "value": "''"
            },
            {
                "column": "product_number",
                "operator": "not_empty",
                "value": "''"
            }
        ]

        groups_keys = {
            "columns": [
                {
                    "name": "product_number"
                }
            ],
            "aggregations": []
        }

        fields_agg = [
            {
                "name": "product_number",
                "alias": 0
            }
        ]

        paging = {
            "current": page,
            "limit": size
        }

        orders = [
            {
                "column": "product_number",
                "direction": "asc"
            }
        ]

        # All Keys and AVG 12 Month
        from_date_12m_ago = self.yesterday - relativedelta(months=12)
        from_date = from_date_12m_ago.strftime("%Y-%m-%d 00:00:00")
        to_date = self.yesterday.strftime("%Y-%m-%d 23:59:59")

        group_avg_keys = copy.deepcopy(groups_keys)
        group_avg_keys["aggregations"] = [
            {
                "column": "quantity",
                "alias": "total_avg_quantity_12m",
                "aggregation": "avg"
            }
        ]
        fields_12m_agg = copy.deepcopy(fields_agg)
        fields_12m_agg.append(
            {
                "name": "total_avg_quantity_12m",
                "alias": 0
            }
        )

        agg_keys = self._aggregate_analysis_3rd_party(
            analysis_3rd_party=analysis_3rd_party,
            external_id=external_id,
            groups=group_avg_keys,
            fields=fields_12m_agg,
            sale_dates=[
                [from_date, to_date]
            ],
            sale_status=[SALE_SHIPPED_STATUS],
            conditions=conditions,
            distinct=False,
            paging=paging,
            orders=orders
        )
        logger.debug(
            f"[{self.__class__.__name__}][_aggregate][analysis_3rd_party][agg_keys][{from_date}][{to_date}] "
            f"Result: {agg_keys}"
        )
        columns = [item["name"] for item in agg_keys["cols"]]
        df = pd.DataFrame(agg_keys["rows"], columns=columns)

        paging_agg = {
            "current": 1,
            "limit": total
        }
        # Days
        group_day_keys = copy.deepcopy(groups_keys)
        group_day_keys["aggregations"] = [
            {
                "column": "quantity",
                "alias": "total_quantity_day",
                "aggregation": "sum"
            }
        ]

        fields_day_agg = copy.deepcopy(fields_agg)
        fields_day_agg.append(
            {
                "name": "total_quantity_day",
                "alias": 0
            }
        )

        agg_day = self._aggregate_analysis_3rd_party(
            analysis_3rd_party=analysis_3rd_party,
            external_id=external_id,
            groups=group_day_keys,
            fields=fields_day_agg,
            sale_dates=[
                [self.yesterday.strftime(
                    "%Y-%m-%d 00:00:00"), self.yesterday.strftime("%Y-%m-%d 23:59:59")]
            ],
            sale_status=[SALE_SHIPPED_STATUS],
            conditions=conditions,
            distinct=False,
            paging=paging_agg
        )
        logger.debug(
            f"[{self.__class__.__name__}][_aggregate][analysis_3rd_party][agg_day] "
            f"Result: {agg_day}"
        )
        columns = [item["name"] for item in agg_day["cols"]]
        _df = pd.DataFrame(agg_day["rows"], columns=columns)
        df = pd.merge(df, _df, on=["product_number"], how="left")

        # 30 Days
        group_30day_keys = copy.deepcopy(groups_keys)
        group_30day_keys["aggregations"] = [
            {
                "column": "quantity",
                "alias": "total_quantity_30d",
                "aggregation": "sum"
            },
            {
                "column": "quantity",
                "alias": "total_avg_quantity_30d",
                "aggregation": "avg"
            }
        ]

        fields_30day_agg = copy.deepcopy(fields_agg)
        fields_30day_agg += [
            {
                "name": "total_quantity_30d",
                "alias": 0
            },
            {
                "name": "total_avg_quantity_30d",
                "alias": 0
            }
        ]

        from_date_30d_ago = self.yesterday - timedelta(days=30)
        agg_30day = self._aggregate_analysis_3rd_party(
            analysis_3rd_party=analysis_3rd_party,
            external_id=external_id,
            groups=group_30day_keys,
            fields=fields_30day_agg,
            sale_dates=[
                [from_date_30d_ago.strftime(
                    "%Y-%m-%d 00:00:00"), self.yesterday.strftime("%Y-%m-%d 23:59:59")]
            ],
            sale_status=[SALE_SHIPPED_STATUS],
            conditions=conditions,
            distinct=False,
            paging=paging_agg
        )
        logger.debug(
            f"[{self.__class__.__name__}][_aggregate][analysis_3rd_party][agg_30day] "
            f"Result: {agg_30day}"
        )
        columns = [item["name"] for item in agg_30day["cols"]]
        _df = pd.DataFrame(agg_30day["rows"], columns=columns)
        df = pd.merge(df, _df, on=["product_number"], how="left")

        df = df[(df['total_quantity_day'].notna())
                | (df['total_quantity_30d'].notna())
                | (df['total_avg_quantity_12m'].notna())]

        df = df.fillna(0).infer_objects(copy=False)

        # quantity_d_vs_quantity_avg_30d
        q = df['total_quantity_day']
        avg = df['total_avg_quantity_30d']
        conditions = [
            (q == 0) & (avg == 0),
            (q > avg) & (q == 0),
            (avg > q) & (avg == 0),
            (q > avg)
        ]
        choices = [
            0,
            0,
            0,
            np.round((1.00 - (avg / q)) * 100, 2)
        ]
        # Else clause:
        else_case = np.round((1.00 - (q / avg)) * 100, 2)
        df["quantity_d_vs_quantity_avg_30d"] = np.select(
            conditions, choices, default=else_case)

        # quantity_30d_vs_quantity_avg_12m
        q = df['total_quantity_30d']
        avg = df['total_avg_quantity_12m']
        conditions = [
            (q == 0) & (avg == 0),
            (q > avg) & (q == 0),
            (avg > q) & (avg == 0),
            (q > avg)
        ]
        choices = [
            0,
            0,
            0,
            np.round((1.00 - (avg / q)) * 100, 2)
        ]
        # Else clause:
        else_case = np.round((1.00 - (q / avg)) * 100, 2)
        df["quantity_30d_vs_quantity_avg_12m"] = np.select(
            conditions, choices, default=else_case)

        df["distance_day_vs_avg_30d"] = df["total_quantity_day"] - \
            df["total_avg_quantity_30d"]
        df["distance_30d_vs_avg_12m"] = df["total_quantity_30d"] - \
            df["total_avg_quantity_12m"]

        data = df.to_dict(orient="records")
        # print(df)

        return data

    def process_batch(self, client_id: str, analysis_3rd_party: DataSource, external_id: str, source_type: str,
                      total: int = 0, page: int = 1, size: int = 500, modified_filter: str = None):
        data = []

        agg_data = self._aggregate(client_id=client_id, analysis_3rd_party=analysis_3rd_party, external_id=external_id,
                                   total=total, page=page, size=size)

        logger.info(
            f"[{self.__class__.__name__}][{external_id}][process_batch] Total agg: {len(agg_data)}"
        )

        modified_time = timezone.now().isoformat()
        for agg in agg_data:
            try:
                logger.debug(
                    f"[{self.__class__.__name__}][{external_id}][process_batch] agg: {agg}")

                _data = dict(
                    product_number=agg["product_number"],
                    total_quantity_day=agg["total_quantity_day"],
                    total_quantity_30d=agg["total_quantity_30d"],
                    total_avg_quantity_30d=agg["total_avg_quantity_30d"],
                    total_avg_quantity_12m=agg["total_avg_quantity_12m"],
                    quantity_d_vs_quantity_avg_30d=agg["quantity_d_vs_quantity_avg_30d"],
                    quantity_30d_vs_quantity_avg_12m=agg["quantity_30d_vs_quantity_avg_12m"],
                    distance_day_vs_avg_30d=agg["distance_day_vs_avg_30d"],
                    distance_30d_vs_avg_12m=agg["distance_30d_vs_avg_12m"],
                    modified=modified_time
                )

                logger.debug(
                    f"[{self.__class__.__name__}][{external_id}][process_batch] Agg normalize: {_data}"
                )

                if source_type == FLATTEN_PG_SOURCE:
                    row_values = [
                        "'{}'".format(str(v).replace("'", "''")
                                      ) if v is not None else "NULL"
                        for v in _data.values()
                    ]
                    data.append(f"({','.join(row_values)})")
                else:
                    data.append(_data)
            except Exception as ex:
                logger.error(
                    f"[{self.__class__.__name__}][{external_id}][process_batch] {ex}")

        logger.debug(
            f"[{self.__class__.__name__}][{external_id}][process_batch] Data: {data}"
        )

        return data

    def build_flat_query_insert_segment_table(self, client_id: str, table_name: str, index_fields: str,
                                              total: int, page: int, size: int = 500,
                                              source_type: str = FLATTEN_PG_SOURCE,
                                              modified_filter: str = None, **kwargs):
        analysis_3rd_party = get_analysis_3rd_party(client_id=client_id)
        external_id = get_id_data_source_3rd_party(
            source=FLATTEN_ES_SOURCE, client_id=client_id)

        data = self.process_batch(client_id=client_id, analysis_3rd_party=analysis_3rd_party, external_id=external_id,
                                  source_type=source_type, total=total, page=page, size=size)

        logger.debug(
            f"[{self.__class__.__name__}][{client_id}][build_flat_query_insert_segment_table] "
            f"Data: {data}"
        )

        # Construct SQL Query
        data = self.reformat_data_source_type(
            table_name, index_fields, data, source_type)
        return data

    def build_flat_query_insert_table(self, client_id: str, table_name: str, index_fields: str,
                                      source_type: str = FLATTEN_PG_SOURCE, modified_filter: str = None, **kwargs):
        size = self.build_count_aggregations_unique_combinations(
            client_id=client_id, **kwargs)
        if size == 0:
            raise ValueError(
                f"[{self.__class__.__name__}][{client_id}][build_flat_query_insert_table] Not found data"
            )

        logger.info(
            f"[{self.__class__.__name__}][{client_id}][build_flat_query_insert_table] "
            f"Total: {size}"
        )

        analysis_3rd_party = get_analysis_3rd_party(client_id=client_id)
        external_id = get_id_data_source_3rd_party(
            source=FLATTEN_ES_SOURCE, client_id=client_id)

        data = self.process_batch(client_id=client_id, analysis_3rd_party=analysis_3rd_party, external_id=external_id,
                                  source_type=source_type, total=size, page=1, size=size)
        data = self.reformat_data_source_type(
            table_name, index_fields, data, source_type)
        logger.debug(
            f"[{self.__class__.__name__}][{client_id}][build_flat_query_insert_table] "
            f"Data of the source {source_type}: {data}"
        )
        return data
