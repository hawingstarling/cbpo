import calendar
import copy

import numpy as np
import pandas as pd
from abc import ABC
from dateutil.relativedelta import relativedelta
from django.utils import timezone

from app.financial.services.data_source import DataSource
from app.financial.services.utils.common import get_id_data_source_3rd_party
from app.financial.services.utils.helper import get_analysis_3rd_party, get_analysis_es_service

from app.financial.sql_generator.flat_sql_schema_generator import FlatSchemaSQLGenerator, logger
from datetime import timedelta

from app.financial.variable.data_flatten_variable import FLATTEN_PG_SOURCE, FLATTEN_ES_SOURCE


class FlatSaleByUnitSQLGenerator(FlatSchemaSQLGenerator, ABC):
    day_number = 32
    month_number = 4

    @property
    def config_statement_source(self):
        days_schema = self.build_range_column_schema(
            number=self.day_number, prefix_column="d", type="numeric")
        months_schema = self.build_range_column_schema(
            number=self.month_number, prefix_column="m", type="numeric")

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
            "_source_table_.fulfillment_type": {
                "name": "fulfillment_type",
                "pg": {
                    "type": "varchar(255) not null"
                },
                "es": {
                    "type": "text"
                }
            },
            "_source_table_.sku": {
                "name": "sku",
                "pg": {
                    "type": "varchar(100) not null"
                },
                "es": {
                    "type": "text"
                }
            },
            # -----------------------------------------------------------------
            **days_schema,
            **months_schema,
            # -----------------------------------------------------------------
            "_source_table_.sale_total_30d": {
                "name": "sale_total_30d",
                "pg": {
                    "type": "numeric"
                },
                "es": {
                    "type": "float"
                }
            },
            "_source_table_.sale_avg_30d": {
                "name": "sale_avg_30d",
                "pg": {
                    "type": "numeric"
                },
                "es": {
                    "type": "float"
                }
            },
            "_source_table_.sale_total_30d_prior": {
                "name": "sale_total_30d_prior",
                "pg": {
                    "type": "numeric"
                },
                "es": {
                    "type": "float"
                }
            },
            "_source_table_.sale_avg_30d_prior": {
                "name": "sale_avg_30d_prior",
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

    def build_count_aggregations_unique_combinations(self, client_id, modified_filter: str = None, **kwargs):
        analysis_es_service = get_analysis_es_service(client_id)
        from_date_3m_ago = self.yesterday - relativedelta(months=3)
        from_date = from_date_3m_ago.replace(
            day=1).strftime("%Y-%m-%d 00:00:00")
        to_date = self.yesterday.strftime("%Y-%m-%d 23:59:59")

        filter_cond = {
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
                    {"exists": {"field": "fulfillment_type"}},
                    {
                        "script": {
                            "script": """
                                  doc['brand.keyword'].size() > 0 && doc['brand.keyword'].value != '' &&
                                  doc['fulfillment_type.keyword'].size() > 0 && doc['fulfillment_type.keyword'].value != ''
                                """
                        }
                    }
                ]
            }
        }

        if modified_filter:
            filter_cond["bool"]["must"].append(
                {
                    "range": {
                        "modified": {
                            "gte": modified_filter,
                            "format": "yyyy-MM-dd HH:mm:ss",
                            "time_zone": self.ds_tz_calculate
                        }
                    }
                }
            )

        query = {
            "size": 0,
            "query": filter_cond,
            "aggs": {
                "unique_combinations": {
                    "cardinality": {
                        "script": {
                            "source": "doc['brand.keyword'].value + '|' + doc['fulfillment_type.keyword'].value + '|' + doc['sku.keyword'].value",
                            "lang": "painless"
                        }
                    }
                }
            }
        }
        res = analysis_es_service.search(query=query)
        count = res["aggregations"]["unique_combinations"]["value"]
        return count

    def build_query_for_number_sync_rows(self, client_id, modified_filter: str = None, **kwargs):
        """
        build a query for counting the number of dirty rows in the original table
        :return:
        """
        count = self.build_count_aggregations_unique_combinations(
            client_id=client_id, modified_filter=modified_filter, **kwargs)
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
            },
            # ------------------------------
            {
                "column": "fulfillment_type",
                "operator": "not_null",
                "value": ""
            },
            {
                "column": "fulfillment_type",
                "operator": "$ne",
                "value": "''"
            },
            {
                "column": "fulfillment_type",
                "operator": "not_empty",
                "value": "''"
            }
        ]

        groups_keys = {
            "columns": [
                {
                    "name": "brand"
                },
                {
                    "name": "fulfillment_type"
                },
                {
                    "name": "sku"
                }
            ],
            "aggregations": []
        }

        fields_keys = [
            {
                "name": "brand",
                "alias": 0
            },
            {
                "name": "fulfillment_type",
                "alias": 0
            },
            {
                "name": "sku",
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
        from_date_3m_ago = self.yesterday - relativedelta(months=3)
        from_date = from_date_3m_ago.replace(
            day=1).strftime("%Y-%m-%d 00:00:00")
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
            orders=orders,
            modified_from=modified_filter
        )
        logger.debug(
            f"[{self.__class__.__name__}][_aggregate][analysis_3rd_party][agg_keys][{from_date}][{to_date}][{page}] "
            f"Result: {agg_keys}"
        )
        columns = [item["name"] for item in agg_keys["cols"]]
        df = pd.DataFrame(agg_keys["rows"], columns=columns)

        conditions_brands = copy.deepcopy(conditions)
        if modified_filter:
            brand_list = df["brand"].unique().tolist()
            logger.info(
                f"[{self.__class__.__name__}][_aggregate][analysis_3rd_party][agg_keys][{from_date}][{to_date}][{page}] "
                f"Total brand: {len(brand_list)}"
            )
            conditions_brands.append(
                {
                    "column": "brand",
                    "operator": "in",
                    "value": brand_list
                }
            )

        paging_agg = {
            "current": 1,
            "limit": total
        }

        groups_agg_keys = copy.deepcopy(groups_keys)

        for day in range(self.day_number):
            date_agg = self.yesterday - timedelta(days=day)
            from_date = date_agg.strftime("%Y-%m-%d 00:00:00")
            to_date = date_agg.strftime("%Y-%m-%d 23:59:59")
            groups_agg_keys["aggregations"] = [
                {
                    "column": "sale_id",
                    "alias": f"d{day}",
                    "aggregation": "distinct"
                }
            ]
            fields_agg_keys = copy.deepcopy(fields_keys)
            fields_agg_keys.append(
                {
                    "name": f"d{day}",
                    "alias": 0
                }
            )

            agg_keys = self._aggregate_analysis_3rd_party(
                analysis_3rd_party=analysis_3rd_party,
                external_id=external_id,
                groups=groups_agg_keys,
                fields=fields_agg_keys,
                sale_dates=[
                    [from_date, to_date]
                ],
                sale_status=self.sale_status_accept_generate,
                conditions=conditions_brands,
                distinct=False,
                paging=paging_agg,
                orders=orders
            )
            logger.debug(
                f"[{self.__class__.__name__}][_aggregate][analysis_3rd_party][agg_d{day}][{from_date}][{to_date}] "
                f"Result: {agg_keys}"
            )
            columns = [item["name"] for item in agg_keys["cols"]]
            _df = pd.DataFrame(agg_keys["rows"], columns=columns)
            df = pd.merge(
                df, _df, on=["brand", "fulfillment_type", "sku"], how="left")

        for month in range(self.month_number):
            date_agg = self.yesterday - relativedelta(months=month)
            from_date = date_agg.replace(day=1).strftime("%Y-%m-%d 00:00:00")
            number_day = calendar.monthrange(date_agg.year, date_agg.month)[1]
            to_date = date_agg.replace(
                day=number_day).strftime("%Y-%m-%d 23:59:59")

            groups_agg_keys["aggregations"] = [
                {
                    "column": "sale_id",
                    "alias": f"m{month}",
                    "aggregation": "distinct"
                }
            ]
            fields_agg_keys = copy.deepcopy(fields_keys)
            fields_agg_keys.append(
                {
                    "name": f"m{month}",
                    "alias": 0
                }
            )

            agg_keys = self._aggregate_analysis_3rd_party(
                analysis_3rd_party=analysis_3rd_party,
                external_id=external_id,
                groups=groups_agg_keys,
                fields=fields_agg_keys,
                sale_dates=[
                    [from_date, to_date]
                ],
                sale_status=self.sale_status_accept_generate,
                conditions=conditions_brands,
                distinct=False,
                paging=paging_agg,
                orders=orders
            )
            logger.debug(
                f"[{self.__class__.__name__}][_aggregate][analysis_3rd_party][agg_m{month}][{from_date}][{to_date}] "
                f"Result: {agg_keys}"
            )
            columns = [item["name"] for item in agg_keys["cols"]]
            _df = pd.DataFrame(agg_keys["rows"], columns=columns)
            df = pd.merge(
                df, _df, on=["brand", "fulfillment_type", "sku"], how="left")

        # Total, AVG 30 Days
        date_30d_agg = self.yesterday - timedelta(days=30)
        from_date = date_30d_agg.strftime("%Y-%m-%d 00:00:00")
        to_date = self.yesterday.strftime("%Y-%m-%d 23:59:59")

        groups_agg_keys["aggregations"] = [
            {
                "column": "sale_id",
                "alias": "sale_total_30d",
                "aggregation": "distinct"
            }
        ]
        fields_agg_keys = copy.deepcopy(fields_keys)
        fields_agg_keys += [
            {
                "name": f"sale_total_30d",
                "alias": 0
            }
        ]

        agg_keys = self._aggregate_analysis_3rd_party(
            analysis_3rd_party=analysis_3rd_party,
            external_id=external_id,
            groups=groups_agg_keys,
            fields=fields_agg_keys,
            sale_dates=[
                [from_date, to_date]
            ],
            sale_status=self.sale_status_accept_generate,
            conditions=conditions_brands,
            distinct=False,
            paging=paging_agg,
            orders=orders
        )
        logger.debug(
            f"[{self.__class__.__name__}][_aggregate][analysis_3rd_party][agg_30d][{from_date}][{to_date}] "
            f"Result: {agg_keys}"
        )
        columns = [item["name"] for item in agg_keys["cols"]]
        _df = pd.DataFrame(agg_keys["rows"], columns=columns)
        _df["sale_avg_30d"] = np.round(_df["sale_total_30d"] / 30, 2)
        df = pd.merge(
            df, _df, on=["brand", "fulfillment_type", "sku"], how="left")

        # Total, AVG Prior 30Days
        from_date_60d_agg = self.yesterday - timedelta(days=60)
        to_date_60d_agg = date_30d_agg - timedelta(days=1)
        from_date = from_date_60d_agg.strftime("%Y-%m-%d 00:00:00")
        to_date = to_date_60d_agg.strftime("%Y-%m-%d 23:59:59")

        groups_agg_keys["aggregations"] = [
            {
                "column": "sale_id",
                "alias": "sale_total_30d_prior",
                "aggregation": "distinct"
            }
        ]
        fields_agg_keys = copy.deepcopy(fields_keys)
        fields_agg_keys += [
            {
                "name": f"sale_total_30d_prior",
                "alias": 0
            }
        ]

        agg_keys = self._aggregate_analysis_3rd_party(
            analysis_3rd_party=analysis_3rd_party,
            external_id=external_id,
            groups=groups_agg_keys,
            fields=fields_agg_keys,
            sale_dates=[
                [from_date, to_date]
            ],
            sale_status=self.sale_status_accept_generate,
            conditions=conditions_brands,
            distinct=False,
            paging=paging_agg,
            orders=orders
        )
        logger.debug(
            f"[{self.__class__.__name__}][_aggregate][analysis_3rd_party][agg_prior_30d][{from_date}][{to_date}] "
            f"Result: {agg_keys}"
        )
        columns = [item["name"] for item in agg_keys["cols"]]
        _df = pd.DataFrame(agg_keys["rows"], columns=columns)
        _df["sale_avg_30d_prior"] = np.round(
            _df["sale_total_30d_prior"] / 30, 2)
        df = pd.merge(
            df, _df, on=["brand", "fulfillment_type", "sku"], how="left")

        df = df[(df["m0"].notna()) | (df["m1"].notna()) |
                (df["m2"].notna()) | (df["m3"].notna())]
        df = df.fillna(0).infer_objects(copy=False)

        mem_mb = df.memory_usage(deep=True).sum() / (1024 ** 2)
        logger.debug(
            f"[{self.__class__.__name__}][_aggregate] Memory usage load DataFrame: {mem_mb:.2f} MB"
        )

        data = df.to_dict(orient="records")

        return data

    def process_batch(self, client_id: str, analysis_3rd_party: DataSource, external_id: str, source_type: str,
                      total: int = 0, page: int = 1, size: int = 500, modified_filter: str = None):
        data = []
        agg_data = self._aggregate(client_id=client_id, analysis_3rd_party=analysis_3rd_party, external_id=external_id,
                                   total=total, page=page, size=size, modified_filter=modified_filter)

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
                                  source_type=source_type, total=total, page=page, size=size,
                                  modified_filter=modified_filter)

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
