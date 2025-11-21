import math
from abc import ABC
import calendar
import copy
from datetime import datetime
from typing import Union, Set, List

import numpy as np
import pandas as pd
from django.core.paginator import Paginator
from django.db.models import QuerySet
from django.utils import timezone

from app.financial.models import DivisionClientUserWidget
from app.financial.services.data_source import DataSource
from app.financial.services.utils.common import get_id_data_source_3rd_party
from app.financial.services.utils.helper import get_analysis_3rd_party, get_analysis_es_service
from app.financial.sql_generator.flat_sql_schema_generator import FlatSchemaSQLGenerator, logger
from app.financial.variable.common import BATCH_SIZE_DATA_SEGMENT

from app.financial.variable.data_flatten_variable import FLATTEN_ES_SOURCE, FLATTEN_PG_SOURCE
from app.financial.variable.segment_variable import DIVISION_CATEGORY, MANUAL_SYNC_OPTION, \
    DIVISION_CONFIG_CALCULATE_DEFAULT


class FlatSaleByDivisionsSQLGenerator(FlatSchemaSQLGenerator, ABC):

    @property
    def config_statement_source(self):
        return {
            # {source column : alias name column}
            # ----------------------------------------------------------------
            "_source_table_.division": {
                "name": "division",
                "pg": {
                    "type": "varchar(255) not null"
                },
                "es": {
                    "type": "text"
                }
            },
            # -----------------------------------------------------------------
            "_source_table_.mtd_current": {
                "name": "mtd_current",
                "pg": {
                    "type": "numeric"
                },
                "es": {
                    "type": "float"
                }
            },
            "_source_table_.mtd_target": {
                "name": "mtd_target",
                "pg": {
                    "type": "numeric"
                },
                "es": {
                    "type": "float"
                }
            },
            "_source_table_.mtd_max": {
                "name": "mtd_max",
                "pg": {
                    "type": "numeric"
                },
                "es": {
                    "type": "float"
                }
            },
            "_source_table_.ytd_current": {
                "name": "ytd_current",
                "pg": {
                    "type": "numeric"
                },
                "es": {
                    "type": "float"
                }
            },
            "_source_table_.ytd_target": {
                "name": "ytd_target",
                "pg": {
                    "type": "numeric"
                },
                "es": {
                    "type": "float"
                }
            },
            "_source_table_.ytd_max": {
                "name": "ytd_max",
                "pg": {
                    "type": "numeric"
                },
                "es": {
                    "type": "float"
                }
            },
            "_source_table_.total_quantity": {
                "name": "total_quantity",
                "pg": {
                    "type": "numeric"
                },
                "es": {
                    "type": "float"
                }
            },
            "_source_table_.mtd_percent": {
                "name": "mtd_percent",
                "pg": {
                    "type": "numeric"
                },
                "es": {
                    "type": "float"
                }
            },
            "_source_table_.ytd_percent": {
                "name": "ytd_percent",
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

    @classmethod
    def sync_product_type_management(cls, client_id: str, product_types: Union[Set, List], divisions_configs: QuerySet):
        for product_type in product_types:
            try:
                divisions_configs.get(key=product_type)
            except Exception as ex:
                logger.error(
                    f"[{cls.__class__.__name__}][{client_id}][sync_product_type_management] {ex}")
                DivisionClientUserWidget.objects.tenant_db_for(client_id) \
                    .create(client_id=client_id,
                            category=DIVISION_CATEGORY,
                            key=product_type,
                            name=product_type,
                            enabled=False,
                            settings=DIVISION_CONFIG_CALCULATE_DEFAULT)

    def build_count_aggregations_unique_combinations(self, client_id, **kwargs):
        analysis_es_service = get_analysis_es_service(client_id)
        query = {
            "size": 0,
            "query": {
                "bool": {
                    "must": [
                        {"term": {"channel_name.keyword": self.ds_channel_default}},
                        {"exists": {"field": "brand"}},
                        {
                            "script": {
                                "script": """
                                  doc['product_type.keyword'].size() > 0 && doc['product_type.keyword'].value != ''
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
                            "source": "doc['product_type.keyword'].value"
                        }
                    }
                }
            }
        }

        agg_keys = {
            "group_by_fields": {
                "composite": {
                    "size": 1000,
                    "sources": [
                        {"product_type": {"terms": {"field": "product_type.keyword"}}}
                    ]
                }
            }
        }

        divisions_configs = DivisionClientUserWidget.objects.tenant_db_for(client_id) \
            .filter(client_id=client_id, category=DIVISION_CATEGORY)

        res = analysis_es_service.search(query=query)

        logger.debug(
            f"[{self.__class__.__name__}][build_count_aggregations_unique_combinations][analysis_3rd_party][count] "
            f"Result: {res}"
        )

        total_records = res["aggregations"]["unique_combinations"]["value"]
        total_pages = math.ceil(total_records / BATCH_SIZE_DATA_SEGMENT)

        if divisions_configs.count() != total_records:
            after_keys = dict()
            # Process data in batches
            for page_num in range(1, total_pages + 1):
                try:
                    logger.info(
                        f"[{self.__class__.__name__}][build_count_aggregations_unique_combinations] "
                        f"Fetching group keys page {page_num}"
                    )

                    if len(after_keys) > 0:
                        # agg_keys["group_by_fields"]["composite"]["after"] = after_keys
                        agg_keys["group_by_fields"]["composite"].update(
                            dict(after=after_keys)
                        )

                    query["aggs"] = agg_keys
                    res = analysis_es_service.search(query=query)

                    logger.debug(
                        f"[{self.__class__.__name__}][build_count_aggregations_unique_combinations]"
                        f"[analysis_3rd_party][count] "
                        f"Result: {res}"
                    )

                    after_keys = res["aggregations"]["group_by_fields"].get(
                        "after_key", {})
                    buckets = res["aggregations"]["group_by_fields"]["buckets"]
                    assert bool(buckets) is True, "Data not found"
                    product_types = [bucket["key"]["product_type"]
                                     for bucket in buckets]

                    product_types_sync = set(product_types) - set(
                        divisions_configs.filter(key__in=product_types).values_list("key", flat=True))
                    if product_types_sync:
                        self.sync_product_type_management(
                            client_id, product_types_sync, divisions_configs)

                except Exception as ex:
                    logger.error(
                        f"[{self.__class__.__name__}][build_count_aggregations_unique_combinations]"
                        f"[fetching_group_keys][{page_num}] {ex}"
                    )

        count = divisions_configs.filter(enabled=True).count()

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

        queryset = DivisionClientUserWidget.objects.tenant_db_for(client_id) \
            .filter(client_id=client_id, category=DIVISION_CATEGORY, enabled=True).order_by("key")

        objs = Paginator(queryset, size).page(number=page).object_list

        pt_all_keys = list()
        pt_manual_data = list()

        for obj in objs:
            pt_all_keys.append(obj.key)
            if obj.sync_option == MANUAL_SYNC_OPTION:
                pt_manual_data.append(
                    [
                        obj.key,
                        float(obj.mtd_target_manual),
                        float(obj.mtd_max_manual),
                        float(obj.ytd_target_manual),
                        float(obj.ytd_max_manual)
                    ]
                )

        logger.debug(
            f"[{self.__class__.__name__}][_aggregate] "
            f"Product Type All Keys: {pt_all_keys} |"
            f"Product Manual Data: {pt_manual_data}"
        )

        columns_manual = ["mtd_target", "mtd_max", "ytd_target", "ytd_max"]
        df_manual = pd.DataFrame(pt_manual_data,
                                 columns=["product_type"] + columns_manual)

        # Set the Option to Accept Future Behavior (opt-in)
        # This will silence the warning and enforce stricter behavior, preparing your code for future pandas versions.
        pd.set_option('future.no_silent_downcasting', True)

        conditions = [
            {
                "column": "product_type",
                "operator": "not_null",
                "value": ""
            },
            {
                "column": "product_type",
                "operator": "$ne",
                "value": "''"
            },
            {
                "column": "product_type",
                "operator": "not_empty",
                "value": "''"
            },
            {
                "column": "product_type",
                "operator": "in",
                "value": pt_all_keys
            }
        ]

        groups_keys = {
            "columns": [
                {
                    "name": "product_type"
                }
            ],
            "aggregations": []
        }

        fields_keys = [
            {
                "name": "product_type",
                "alias": 0
            }
        ]

        paging = {
            "current": page,
            "limit": size
        }

        orders = [
            {
                "column": "product_type",
                "direction": "asc"
            }
        ]

        last_year = self.yesterday.year - 1
        num_days = calendar.monthrange(
            self.yesterday.year, self.yesterday.month)[1]
        num_days_of_month = f"0{num_days}" if num_days < 10 else str(num_days)
        begin_date_of_last_year = f"{last_year}-01-01 00:00:00"

        # All Keys
        from_date = begin_date_of_last_year
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

        if not agg_keys["rows"]:
            return []

        columns = [item["name"] for item in agg_keys["cols"]]
        df = pd.DataFrame(agg_keys["rows"], columns=columns)

        paging_agg = {
            "current": 1,
            "limit": total
        }

        columns_configs = copy.deepcopy(DIVISION_CONFIG_CALCULATE_DEFAULT)

        columns_configs_ranges = {
            "mtd_current": {
                "from_date": self.yesterday.strftime("%Y-%m-01 00:00:00"),
                "to_date": self.yesterday.strftime("%Y-%m-%d 23:59:59")
            },
            "mtd_target": {
                "from_date": self.yesterday.strftime(f"{last_year}-%m-01 00:00:00"),
                "to_date": self.yesterday.strftime(f"{last_year}-%m-%d 23:59:59")
            },
            "mtd_max": {
                "from_date": self.yesterday.strftime(f"{last_year}-%m-01 00:00:00"),
                "to_date": self.yesterday.strftime(f"{last_year}-%m-{num_days_of_month} 23:59:59")
            },
            "ytd_current": {
                "from_date": self.yesterday.strftime("%Y-01-01 00:00:00"),
                "to_date": self.yesterday.strftime("%Y-%m-%d 23:59:59")
            },
            "ytd_target": {
                "from_date": self.yesterday.strftime(f"{last_year}-01-01 00:00:00"),
                "to_date": self.yesterday.strftime(f"{last_year}-%m-%d 23:59:59")
            },
            "ytd_max": {
                "from_date": self.yesterday.strftime(f"{last_year}-01-01 00:00:00"),
                "to_date": self.yesterday.strftime(f"{last_year}-12-31 23:59:59")
            },
            "total_quantity": {
                "from_date": self.yesterday.strftime("%Y-01-01 00:00:00"),
                "to_date": self.yesterday.strftime("%Y-%m-%d 23:59:59")
            }
        }

        for column, config in columns_configs.items():
            from_date = columns_configs_ranges[column]["from_date"]
            to_date = columns_configs_ranges[column]["to_date"]

            groups_agg_keys = copy.deepcopy(groups_keys)
            groups_agg_keys["aggregations"] = [
                {
                    "column": config["field_aggregate"],
                    "alias": column,
                    "aggregation": config["aggregation"]
                }
            ]
            fields_agg_keys = copy.deepcopy(fields_keys)
            fields_agg_keys.append(
                {
                    "name": column,
                    "alias": 0
                }
            )

            agg_column = self._aggregate_analysis_3rd_party(
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
                f"Result: {agg_column}"
            )
            columns = [item["name"] for item in agg_column["cols"]]
            _df = pd.DataFrame(agg_column["rows"], columns=columns)
            df = pd.merge(df, _df, on=["product_type"], how="left")

        if not df_manual.empty:
            for col in columns_manual:
                df[col] = df["product_type"].map(df_manual.set_index(
                    "product_type")[col]).combine_first(df[col])

        df = df[(df["mtd_current"].notna()) | (df["mtd_target"].notna()) |
                (df["ytd_current"].notna()) | (df["ytd_target"].notna())]

        df = df.fillna(0).infer_objects(copy=False)

        # mtd_percent
        df["mtd_percent"] = np.where(
            df["mtd_target"] != 0,
            ((df["mtd_current"] - df["mtd_target"]) / df["mtd_target"]) * 100,
            0  # or 0 if you prefer
        )
        # ytd_percent
        df["ytd_percent"] = np.where(
            df["ytd_target"] != 0,
            ((df["ytd_current"] - df["ytd_target"]) / df["ytd_target"]) * 100,
            0  # or 0 if you prefer
        )
        data = df.to_dict(orient="records")

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
