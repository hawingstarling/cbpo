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

from app.financial.variable.data_flatten_variable import FLATTEN_PG_SOURCE, FLATTEN_ES_SOURCE


class FlatBrand30DaysSaleSQLGenerator(FlatSchemaSQLGenerator, ABC):

    @property
    def config_statement_source(self):
        return {
            # {source column : alias name column}
            # ----------------------------------------------------------------
            "_source_table_.brand": {
                "name": "brand",
                "pg": {
                    "type": "varchar(255) not null"
                },
                "es": {
                    "type": "text"
                }
            },
            # -----------------------------------------------------------------
            "_source_table_.amount_30d": {
                "name": "amount_30d",
                "pg": {
                    "type": "numeric"
                },
                "es": {
                    "type": "float"
                }
            },
            "_source_table_.amount_30d_prior": {
                "name": "amount_30d_prior",
                "pg": {
                    "type": "numeric"
                },
                "es": {
                    "type": "float"
                }
            },
            "_source_table_.amount_30d_vs_amount_30d_prior": {
                "name": "amount_30d_vs_amount_30d_prior",
                "pg": {
                    "type": "numeric"
                },
                "es": {
                    "type": "float"
                }
            },
            "_source_table_.max_amount_30d": {
                "name": "max_amount_30d",
                "pg": {
                    "type": "numeric"
                },
                "es": {
                    "type": "float"
                }
            },
            "_source_table_.max_amount_30d_prior": {
                "name": "max_amount_30d_prior",
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
        from_date_60d_ago = self.yesterday - timedelta(days=60)
        from_date = from_date_60d_ago.strftime("%Y-%m-%d 00:00:00")
        to_date = self.yesterday.strftime("%Y-%m-%d 23:59:59")
        query = {
            "size": 0,
            "query": {
                "bool": {
                    "must": [
                        {"term": {"channel_name.keyword": self.ds_channel_default}},
                        {"terms": {
                            "item_sale_status.keyword": self.sale_status_accept_generate}},
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
                        {"exists": {"field": "brand"}},
                        {
                            "script": {
                                "script": """
                                  doc['brand.keyword'].size() > 0 && doc['brand.keyword'].value != ''
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
                            "source": "doc['brand.keyword'].value",
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
                "column": "brand",
                "operator": "not_null",
                "value": ""
            },
            {
                "column": "brand",
                "operator": "$ne",
                "value": "''"
            },
            {
                "column": "brand",
                "operator": "not_empty",
                "value": "''"
            }
        ]

        groups_keys = {
            "columns": [
                {
                    "name": "brand"
                }
            ],
            "aggregations": []
        }

        fields_keys = [
            {
                "name": "brand",
                "alias": 0
            }
        ]

        paging = {
            "current": page,
            "limit": size
        }

        orders = [
            {
                "column": "brand",
                "direction": "asc"
            }
        ]

        # All Keys
        from_date_60d_ago = self.yesterday - timedelta(days=60)
        from_date = from_date_60d_ago.strftime("%Y-%m-%d 00:00:00")
        to_date = self.yesterday.strftime("%Y-%m-%d 23:59:59")

        agg_keys = self._aggregate_analysis_3rd_party(
            analysis_3rd_party=analysis_3rd_party,
            external_id=external_id,
            groups=groups_keys,
            fields=fields_keys,
            sale_dates=[
                [from_date, to_date]
            ],
            sale_status=self.sale_status_accept_generate,
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

        # 30 Days
        from_date_30d_ago = self.yesterday - timedelta(days=30)
        from_date = from_date_30d_ago.strftime("%Y-%m-%d 00:00:00")
        to_date = self.yesterday.strftime("%Y-%m-%d 23:59:59")

        groups_agg_keys = copy.deepcopy(groups_keys)
        groups_agg_keys["aggregations"] = [
            {
                "column": "item_sale_charged",
                "alias": "amount_30d",
                "aggregation": "sum"
            }
        ]
        fields_agg_keys = copy.deepcopy(fields_keys)
        fields_agg_keys.append(
            {
                "name": "amount_30d",
                "alias": 0
            }
        )

        agg_30d_keys = self._aggregate_analysis_3rd_party(
            analysis_3rd_party=analysis_3rd_party,
            external_id=external_id,
            groups=groups_agg_keys,
            fields=fields_agg_keys,
            sale_dates=[
                [from_date, to_date]
            ],
            sale_status=self.sale_status_accept_generate,
            conditions=conditions,
            distinct=False,
            paging=paging_agg,
            orders=orders
        )
        logger.debug(
            f"[{self.__class__.__name__}][_aggregate][analysis_3rd_party][agg_30d_keys][{from_date}][{to_date}] "
            f"Result: {agg_30d_keys}"
        )
        columns = [item["name"] for item in agg_30d_keys["cols"]]
        _df = pd.DataFrame(agg_30d_keys["rows"], columns=columns)
        df = pd.merge(df, _df, on=["brand"], how="left")

        # 60 Days
        to_date_30d_prior_ago = from_date_30d_ago - timedelta(days=1)
        from_date = from_date_60d_ago.strftime("%Y-%m-%d 00:00:00")
        to_date = to_date_30d_prior_ago.strftime("%Y-%m-%d 23:59:59")

        groups_agg_keys = copy.deepcopy(groups_keys)
        groups_agg_keys["aggregations"] = [
            {
                "column": "item_sale_charged",
                "alias": "amount_30d_prior",
                "aggregation": "sum"
            }
        ]
        fields_agg_keys = copy.deepcopy(fields_keys)
        fields_agg_keys.append(
            {
                "name": "amount_30d_prior",
                "alias": 0
            }
        )

        agg_30d_prior_keys = self._aggregate_analysis_3rd_party(
            analysis_3rd_party=analysis_3rd_party,
            external_id=external_id,
            groups=groups_agg_keys,
            fields=fields_agg_keys,
            sale_dates=[
                [from_date, to_date]
            ],
            sale_status=self.sale_status_accept_generate,
            conditions=conditions,
            distinct=False,
            paging=paging_agg,
            orders=orders
        )
        logger.debug(
            f"[{self.__class__.__name__}][_aggregate][analysis_3rd_party][agg_30d_prior_keys][{from_date}][{to_date}] "
            f"Result: {agg_30d_prior_keys}"
        )
        columns = [item["name"] for item in agg_30d_prior_keys["cols"]]
        _df = pd.DataFrame(agg_30d_prior_keys["rows"], columns=columns)
        df = pd.merge(df, _df, on=["brand"], how="left")

        df = df[(df["amount_30d"].notna()) | (df["amount_30d_prior"].notna())]
        df = df.fillna(0).infer_objects(copy=False)

        # amount_30d_vs_amount_30d_prior
        df["amount_30d_vs_amount_30d_prior"] = np.where(
            df["amount_30d_prior"] != 0,
            ((df["amount_30d"] - df["amount_30d_prior"]) /
             df["amount_30d_prior"]) * 100,
            0  # or 0 if you prefer
        )

        # Get the max value of the 'sales' column
        df["amount_30d"] = np.round(df["amount_30d"], 2)
        df["amount_30d_prior"] = np.round(df["amount_30d_prior"], 2)
        max_30d_sales = df["amount_30d"].max()
        max_30d_prior_sales = df["amount_30d_prior"].max()
        # Set a new column with that max value for all rows
        df['max_amount_30d'] = max_30d_sales
        df['max_amount_30d_prior'] = max_30d_prior_sales

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

                _data = copy.deepcopy(agg)
                _data.update(
                    dict(
                        modified=modified_time
                    )
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
                    _key_data = f"{_data['brand']}-{_data['fulfillment_type']}-{_data['sku']}"
                    _data.update(id=_key_data)
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
