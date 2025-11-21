import copy
from datetime import datetime
import math
from typing import List
import pandas as pd
from abc import ABC
from django.core.paginator import Paginator
from django.utils import timezone
from app.financial.models import TopClientASINs
from app.financial.services.data_source import DataSource
from app.financial.services.utils.common import get_id_data_source_3rd_party
from app.financial.services.utils.helper import get_analysis_3rd_party
from app.financial.sql_generator.flat_sql_schema_generator import FlatSchemaSQLGenerator, logger
from app.financial.variable.data_flatten_variable import FLATTEN_PG_SOURCE, FLATTEN_ES_SOURCE


class FlatTopPerformingStylesBaseSQLGenerator(FlatSchemaSQLGenerator, ABC):

    @property
    def config_statement_source(self):
        return {
            # {source column : alias name column}
            "_source_table_.parent_asin": {
                "name": "parent_asin",
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
                    "type": "varchar(255) not null"
                },
                "es": {
                    "type": "text"
                }
            },
            "_source_table_.child_asin": {
                "name": "child_asin",
                "pg": {
                    "type": "varchar(255) not null"
                },
                "es": {
                    "type": "text"
                }
            },
            "_source_table_.ff_type": {
                "name": "ff_type",
                "pg": {
                    "type": "varchar(255) not null"
                },
                "es": {
                    "type": "text"
                }
            },
            "_source_table_.segment": {
                "name": "segment",
                "pg": {
                    "type": "varchar(255)"
                },
                "es": {
                    "type": "text"
                }
            },
            "_source_table_.product_description": {
                "name": "product_description",
                "pg": {
                    "type": "varchar(500)"
                },
                "es": {
                    "type": "text"
                }
            },
            "_source_table_.price": {
                "name": "price",
                "pg": {
                    "type": "numeric(10, 2)"
                },
                "es": {
                    "type": "float"
                }
            },
            "_source_table_.current_unit": {
                "name": "current_unit",
                "pg": {
                    "type": "integer"
                },
                "es": {
                    "type": "integer"
                }
            },
            "_source_table_.previous_unit": {
                "name": "previous_unit",
                "pg": {
                    "type": "integer"
                },
                "es": {
                    "type": "integer"
                }
            },
            "_source_table_.current_sale": {
                "name": "current_sale",
                "pg": {
                    "type": "numeric(10, 2)"
                },
                "es": {
                    "type": "float"
                }
            },
            "_source_table_.previous_sale": {
                "name": "previous_sale",
                "pg": {
                    "type": "numeric(10, 2)"
                },
                "es": {
                    "type": "float"
                }
            },
            "_source_table_.percent_diff_unit": {
                "name": "percent_diff_unit",
                "pg": {
                    "type": "numeric(10, 2)"
                },
                "es": {
                    "type": "float"
                }
            },
            "_source_table_.percent_diff_dollar": {
                "name": "percent_diff_dollar",
                "pg": {
                    "type": "numeric(10, 2)"
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

    def _aggregate(self, client_id: str, analysis_3rd_party: DataSource, external_id: str, channel_ids: List[str],
                   top_asin_keys: List[str], total: int = 0, page: int = 1, size: int = 500,
                   modified_filter: str = None):
        fields_agg_top_asins = [
            {
                "name": "parent_asin",
                "alias": 0
            },
            {
                "name": "asin",
                "alias": 0
            },
            {
                "name": "sku",
                "alias": 0
            },
            {
                "name": "fulfillment_type",
                "alias": 0
            }
        ]

        fields_agg_sku_title = [
            {
                "name": "sku",
                "alias": 0
            },
            {
                "name": "product_description",
                "alias": 0
            }
        ]

        fields_agg_current = fields_agg_top_asins + [
            {
                "name": "cog",
                "alias": "price"
            },
            {
                "name": "quantity",
                "alias": "current_unit"
            },
            {
                "name": "item_sale_charged",
                "alias": "current_sale"
            }
        ]

        fields_agg_previous = fields_agg_top_asins + [
            {
                "name": "quantity",
                "alias": "previous_unit"
            },
            {
                "name": "item_sale_charged",
                "alias": "previous_sale"
            }
        ]

        groups_top_asin_keys = {
            "columns": [
                {
                    "name": "parent_asin"
                },
                {
                    "name": "asin"
                },
                {
                    "name": "sku"
                },
                {
                    "name": "fulfillment_type"
                }
            ],
            "aggregations": []
        }

        groups_sku_product_description = {
            "columns": [
                {
                    "name": "sku"
                }
            ],
            "aggregations": [
                {
                    "column": "title",
                    "alias": "product_description",
                    "aggregation": "concat"
                }
            ]
        }

        groups_agg_current = copy.deepcopy(groups_top_asin_keys)
        groups_agg_current["aggregations"] = [
            {
                "column": "cog",
                "alias": "price",
                "aggregation": "sum"
            },
            {
                "column": "quantity",
                "alias": "current_unit",
                "aggregation": "sum"
            },
            {
                "column": "item_sale_charged",
                "alias": "current_sale",
                "aggregation": "sum"
            }
        ]

        groups_agg_previous = copy.deepcopy(groups_top_asin_keys)
        groups_agg_previous["aggregations"] = [
            {
                "column": "quantity",
                "alias": "previous_unit",
                "aggregation": "sum"
            },
            {
                "column": "item_sale_charged",
                "alias": "previous_sale",
                "aggregation": "sum"
            }
        ]

        conditions = [
            {
                "column": "parent_child_asin",
                "operator": "not_null",
                "value": ""
            },
            {
                "column": "parent_child_asin",
                "operator": "in",
                "value": top_asin_keys
            },
        ]

        # Set the Option to Accept Future Behavior (opt-in)
        # This will silence the warning and enforce stricter behavior, preparing your code for future pandas versions.
        pd.set_option('future.no_silent_downcasting', True)

        agg_parent_asin = self._aggregate_analysis_3rd_party(
            analysis_3rd_party=analysis_3rd_party,
            external_id=external_id,
            groups=groups_top_asin_keys,
            conditions=conditions,
            distinct=False,
            orders=[],
            fields=fields_agg_top_asins
        )
        logger.debug(
            f"[{self.__class__.__name__}][_aggregate][analysis_3rd_party][agg_parent_asin] "
            f"Result: {agg_parent_asin}"
        )
        columns = [item["name"] for item in agg_parent_asin["cols"]]
        df = pd.DataFrame(agg_parent_asin["rows"], columns=columns)

        fd_current, td_current = self.get_current_date_calculated()
        fd_previous, td_previous = self.get_previous_date_calculated()

        agg_sku_title = self._aggregate_analysis_3rd_party(
            analysis_3rd_party=analysis_3rd_party,
            external_id=external_id,
            groups=groups_sku_product_description,
            sale_dates=[
                [fd_previous, td_current]
            ],
            conditions=conditions,
            distinct=True,
            orders=[],
            fields=fields_agg_sku_title
        )
        logger.debug(
            f"[{self.__class__.__name__}][_aggregate][analysis_3rd_party][agg_sku_title] "
            f"Result: {agg_sku_title}"
        )
        columns = [item["name"] for item in agg_sku_title["cols"]]
        _df = pd.DataFrame(agg_sku_title["rows"], columns=columns)
        df = pd.merge(df, _df, on=["sku"], how="left")

        logger.info(
            f"[{self.__class__.__name__}][_aggregate][analysis_3rd_party][current_date] "
            f"From Date: {fd_current} - To Date: {td_current}"
        )
        agg_current_date = self._aggregate_analysis_3rd_party(
            analysis_3rd_party=analysis_3rd_party,
            external_id=external_id,
            groups=groups_agg_current,
            sale_dates=[
                [fd_current, td_current]
            ],
            conditions=conditions,
            distinct=True,
            orders=[],
            fields=fields_agg_current
        )
        logger.debug(
            f"[{self.__class__.__name__}][_aggregate][analysis_3rd_party][agg_current_date] "
            f"Result: {agg_current_date}"
        )
        columns = [item["name"] for item in agg_current_date["cols"]]
        _df = pd.DataFrame(agg_current_date["rows"], columns=columns)
        df = pd.merge(df, _df, on=["parent_asin", "sku",
                      "asin", "fulfillment_type"], how="left")

        logger.info(
            f"[{self.__class__.__name__}][_aggregate][analysis_3rd_party][previous_date] "
            f"From Date: {fd_previous} - To Date: {td_previous}"
        )
        agg_previous_date = self._aggregate_analysis_3rd_party(
            analysis_3rd_party=analysis_3rd_party,
            external_id=external_id,
            groups=groups_agg_previous,
            sale_dates=[
                [fd_previous, td_previous]
            ],
            conditions=conditions,
            distinct=True,
            orders=[],
            fields=fields_agg_previous
        )
        logger.debug(
            f"[{self.__class__.__name__}][_aggregate][analysis_3rd_party][agg_previous_date] "
            f"Result: {agg_previous_date}"
        )
        columns = [item["name"] for item in agg_previous_date["cols"]]
        _df = pd.DataFrame(agg_previous_date["rows"], columns=columns)
        df = pd.merge(df, _df, on=["parent_asin", "sku",
                      "asin", "fulfillment_type"], how="left")
        df = df[(df["current_unit"].notna()) |
                (df["previous_unit"].notna())]

        # Fill only selected columns
        df[["current_unit", "previous_unit",
            "current_sale", "previous_sale"]] = df[["current_unit", "previous_unit",
                                                    "current_sale", "previous_sale"]].fillna(0)
        df[["product_description"]] = df[["product_description"]].fillna("")
        # Optionally infer object types
        df = df.infer_objects(copy=False)
        # df = df.fillna(0).infer_objects(copy=False)
        data = df.to_dict(orient="records")
        return data

    def get_current_date_calculated(self):
        raise NotImplementedError

    def get_previous_date_calculated(self):
        raise NotImplementedError

    def process_batch(self, client_id: str, analysis_3rd_party: DataSource, external_id: str, source_type: str,
                      batch: [TopClientASINs], total: int = 0, page: int = 1, size: int = 500, modified_filter: str = None):
        # Extract distinct values
        channel_ids = set()
        top_asins_configs = dict()

        for item in batch:
            channel_ids.add(item.channel_id)
            top_asins_configs.update(
                {
                    f"{item.parent_asin}-{item.child_asin}": item.segment
                }
            )

        # Get aggregated data
        data = []
        agg_asins = self._aggregate(client_id=client_id, analysis_3rd_party=analysis_3rd_party, external_id=external_id,
                                    channel_ids=list(channel_ids), top_asin_keys=list(top_asins_configs.keys()))
        logger.info(
            f"[{self.__class__.__name__}][{external_id}][process_batch] Total agg asins: {len(agg_asins)}")

        modified_time = timezone.now().isoformat()

        for agg in agg_asins:
            try:
                logger.debug(
                    f"[{self.__class__.__name__}][{external_id}][process_batch] agg: {agg}")
                top_asin_key = f"{agg['parent_asin']}-{agg['asin']}"
                # if agg["current_unit"] == 0 and agg["previous_unit"] == 0:
                #     logger.debug(
                #         f"[{self.__class__.__name__}][{client_id}][process_batch] "
                #         f"Not found data aggregate"
                #     )
                #     continue

                if agg["previous_unit"] == 0:
                    percent_diff_unit = 0.0
                else:
                    percent_diff_unit = (
                        agg["current_unit"] - agg["previous_unit"]) / agg["previous_unit"] * 100

                if agg["previous_sale"] == 0:
                    percent_diff_dollar = 0.0
                else:
                    percent_diff_dollar = (
                        agg["current_sale"] - agg["previous_sale"]) / agg["previous_sale"] * 100

                agg = dict(
                    parent_asin=agg["parent_asin"],
                    sku=agg["sku"],
                    child_asin=agg["asin"],
                    ff_type=agg["fulfillment_type"],
                    segment=top_asins_configs.get(top_asin_key),
                    product_description=agg["product_description"][:500],
                    price=round(float(agg["price"]), 2)
                    if agg.get("price") is not None and not pd.isna(agg["price"]) and math.isfinite(float(agg["price"]))
                    else 0.0,
                    current_unit=int(agg["current_unit"]),
                    previous_unit=int(agg["previous_unit"]),
                    current_sale=agg["current_sale"],
                    previous_sale=agg["previous_sale"],
                    percent_diff_unit=percent_diff_unit,
                    percent_diff_dollar=percent_diff_dollar,
                    modified=modified_time
                )

                logger.debug(
                    f"[{self.__class__.__name__}][{external_id}][process_batch] agg normalize: {agg}")

                if source_type == FLATTEN_PG_SOURCE:
                    row_values = [
                        "'{}'".format(str(v).replace("'", "''")
                                      ) if v is not None else "NULL"
                        for v in agg.values()
                    ]
                    data.append(f"({','.join(row_values)})")
                else:
                    agg.update(
                        id=f"{agg['parent_asin']}-{agg['sku']}-{agg['child_asin']}-{agg['ff_type']}"
                    )
                    data.append(agg)
            except Exception as ex:
                logger.error(
                    f"[{self.__class__.__name__}][{external_id}][process_batch] {ex}")
                logger.error(
                    f"[{self.__class__.__name__}][{external_id}][process_batch] agg: {agg}")
        return data

    def build_query_for_number_sync_rows(self, client_id, **kwargs):
        """
        build a query for counting the number of dirty rows in the original table
        :return:
        """
        query = f"""
            SELECT COUNT(*)
            FROM financial_topclientasins
            WHERE financial_topclientasins.client_id = '{client_id}';
        """
        return query

    def build_flat_query_insert_segment_table(self, client_id: str, table_name: str, index_fields: str,
                                              total: int, page: int, size: int = 500,
                                              source_type: str = FLATTEN_PG_SOURCE, modified_filter: str = None,
                                              **kwargs):
        # Get queryset
        queryset = TopClientASINs.objects.filter(
            client_id=client_id).order_by("created")
        # Initialize paginator
        paginator = Paginator(queryset, size)
        top_asins = paginator.page(page).object_list
        analysis_3rd_party = get_analysis_3rd_party(client_id=client_id)
        external_id = get_id_data_source_3rd_party(
            source=FLATTEN_ES_SOURCE, client_id=client_id)

        data = self.process_batch(client_id=client_id, analysis_3rd_party=analysis_3rd_party, external_id=external_id,
                                  source_type=source_type, batch=top_asins)
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
        """
            Builds an SQL INSERT query with ON CONFLICT for bulk inserting aggregated data into a flat table.

            :param client_id: The client ID for filtering data.
            :param table_name: The target table name.
            :param index_fields: The fields used for conflict resolution.
            :param source_type: The fields used for conflict resolution.
            :return: SQL query string for insertion.
            """
        # Fetch Top ASINs for the client
        top_asins = TopClientASINs.objects.filter(client_id=client_id)
        if not top_asins.exists():
            raise ValueError(
                f"[{self.__class__.__name__}][{client_id}][build_flat_query_insert_table] Please configure Top ASINs")

        top_asins = top_asins.order_by(
            "created").iterator()  # Ensure ordered iteration
        analysis_3rd_party = get_analysis_3rd_party(client_id=client_id)
        external_id = get_id_data_source_3rd_party(
            source=FLATTEN_ES_SOURCE, client_id=client_id)
        # @TODO
        # @METHOD1: process per top asins
        # for asin in top_asins:
        #     self.process_batch(client_id=client_id,analysis_3rd_party=analysis_3rd_party, external_id=external_id,
        #                                   source_type=source_type, batch=top_asins_qs)

        # @METHOD2: process multi top asins
        data = self.process_batch(client_id=client_id, analysis_3rd_party=analysis_3rd_party, external_id=external_id,
                                  source_type=source_type, batch=top_asins)
        data = self.reformat_data_source_type(
            table_name, index_fields, data, source_type)
        logger.debug(
            f"[{self.__class__.__name__}][{client_id}][build_flat_query_insert_table] "
            f"Data of the source {source_type}: {data}"
        )
        return data

    @property
    def columns_update(self):
        return list(item['name'] for item in self.config_statement_source.values())
