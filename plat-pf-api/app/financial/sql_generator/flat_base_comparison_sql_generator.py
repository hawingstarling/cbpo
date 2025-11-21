import copy
from abc import ABC
from typing import Dict

import numpy as np
import pandas as pd
from django.utils import timezone

from app.financial.services.data_source import DataSource
from app.financial.services.utils.common import get_id_data_source_3rd_party
from app.financial.services.utils.helper import get_analysis_3rd_party
from app.financial.sql_generator.flat_sql_schema_generator import FlatSchemaSQLGenerator, logger
from datetime import timedelta

from app.financial.variable.data_flatten_variable import FLATTEN_ES_SOURCE, FLATTEN_PG_SOURCE
from app.financial.variable.sale_status_static_variable import SALE_SHIPPED_STATUS


class FlatBaseComparisonSQLGenerator(FlatSchemaSQLGenerator, ABC):

    @property
    def group_by_fields_mappings(self) -> Dict:
        raise NotImplementedError

    def build_count_aggregations_unique_combinations(self, client_id, **kwargs):
        raise NotImplementedError

    def build_query_for_number_sync_rows(self, client_id, modified_filter: str = None, **kwargs):
        """
        build a query for counting the number of dirty rows in original table
        :return:
        """
        count = self.build_count_aggregations_unique_combinations(
            client_id=client_id, modified_filter=modified_filter, **kwargs)
        sql = f"""
            SELECT {count};
        """
        return sql

    def _aggregate(
        self,
        client_id: str,
        analysis_3rd_party: DataSource,
        external_id: str,
        total: int = 0,
        page: int = 1,
        size: int = 500,
        modified_filter: str = None,
    ):
        # Set the Option to Accept Future Behavior (opt-in)
        # This will silence the warning and enforce stricter behavior, preparing your code for future pandas versions.
        pd.set_option("future.no_silent_downcasting", True)

        df_mapping_fields = list(self.group_by_fields_mappings.values())
        groups_columns = []
        conditions = []
        fields_agg = []

        for column in self.group_by_fields_mappings.values():
            groups_columns += [{"name": column}]

            conditions += [
                {"column": column, "operator": "not_null", "value": ""},
                {"column": column, "operator": "$ne", "value": "''"},
                {"column": column, "operator": "not_empty", "value": "''"},
            ]

            fields_agg += [{"name": column, "alias": 0}]

        groups_keys = {"columns": groups_columns, "aggregations": []}

        paging = {"current": page, "limit": size}

        orders = [{"column": column, "direction": "asc"}
                  for column in df_mapping_fields]

        last_year = self.yesterday.year - 1
        fd = self.yesterday.strftime(f"{last_year}-01-01 00:00:00")
        td = self.yesterday.strftime("%Y-%m-%d 23:59:59")
        agg_keys = self._aggregate_analysis_3rd_party(
            analysis_3rd_party=analysis_3rd_party,
            external_id=external_id,
            groups=groups_keys,
            fields=fields_agg,
            sale_dates=[
                [
                    self.yesterday.strftime(f"{last_year}-01-01 00:00:00"),
                    self.yesterday.strftime(f"{last_year}-%m-%d 23:59:59")
                ],
                [
                    self.yesterday.strftime("%Y-01-01 00:00:00"),
                    self.yesterday.strftime(f"%Y-%m-%d 23:59:59")
                ],
            ],
            sale_status=[SALE_SHIPPED_STATUS],
            conditions=conditions,
            distinct=True,
            paging=paging,
            orders=orders,
            modified_from=modified_filter,
        )
        logger.debug(
            f"[{self.__class__.__name__}][_aggregate][analysis_3rd_party][agg_keys][{fd}][{td}] " f"Result: {agg_keys}"
        )

        if not bool(agg_keys["rows"]):
            return []

        columns = [item["name"] for item in agg_keys["cols"]]
        df = pd.DataFrame(agg_keys["rows"], columns=columns)

        conditions_optional = copy.deepcopy(conditions)
        if modified_filter:
            optional_filter = next(
                iter(self.group_by_fields_mappings.values()))
            optional_values = df[optional_filter].unique().tolist()
            logger.info(
                f"[{self.__class__.__name__}][_aggregate][analysis_3rd_party][agg_keys][{fd}][{td}][{paging}] "
                f"Total optional_values: {len(optional_values)}"
            )
            conditions_optional.append(
                {"column": optional_filter, "operator": "in", "value": optional_values})

        logger.debug(
            f"[{self.__class__.__name__}][_aggregate][analysis_3rd_party][agg_keys][{fd}][{td}] "
            f"Result: {conditions_optional}"
        )

        paging_agg = {"current": 1, "limit": total}
        group_d0_keys = copy.deepcopy(groups_keys)
        group_d0_keys["aggregations"] = [
            {"column": "quantity", "alias": "d0_unit", "aggregation": "sum"},
            {"column": "item_sale_charged",
                "alias": "d0_amount", "aggregation": "sum"},
        ]
        agg_d0 = self._aggregate_analysis_3rd_party(
            analysis_3rd_party=analysis_3rd_party,
            external_id=external_id,
            groups=group_d0_keys,
            fields=fields_agg,
            sale_dates=[
                [
                    self.yesterday.strftime("%Y-%m-%d 00:00:00"),
                    self.yesterday.strftime("%Y-%m-%d 23:59:59")
                ]
            ],
            sale_status=[SALE_SHIPPED_STATUS],
            conditions=conditions_optional,
            distinct=True,
            paging=paging_agg,
        )
        logger.debug(
            f"[{self.__class__.__name__}][_aggregate][analysis_3rd_party][agg_d0] " f"Result: {agg_d0}")
        columns = [item["name"] for item in agg_d0["cols"]]
        _df = pd.DataFrame(agg_d0["rows"], columns=columns)
        df = pd.merge(df, _df, on=df_mapping_fields, how="left")

        group_d1_keys = copy.deepcopy(groups_keys)
        group_d1_keys["aggregations"] = [
            {"column": "quantity", "alias": "d1_unit", "aggregation": "sum"},
            {"column": "item_sale_charged",
                "alias": "d1_amount", "aggregation": "sum"},
        ]
        prior_yesterday = self.yesterday - timedelta(days=1)
        agg_d1 = self._aggregate_analysis_3rd_party(
            analysis_3rd_party=analysis_3rd_party,
            external_id=external_id,
            groups=group_d1_keys,
            fields=fields_agg,
            sale_dates=[[prior_yesterday.strftime(
                "%Y-%m-%d 00:00:00"), prior_yesterday.strftime("%Y-%m-%d 23:59:59")]],
            sale_status=[SALE_SHIPPED_STATUS],
            conditions=conditions_optional,
            distinct=True,
            paging=paging_agg,
        )
        logger.debug(
            f"[{self.__class__.__name__}][_aggregate][analysis_3rd_party][agg_d1] " f"Result: {agg_d1}")
        columns = [item["name"] for item in agg_d1["cols"]]
        _df = pd.DataFrame(agg_d1["rows"], columns=columns)
        df = pd.merge(df, _df, on=df_mapping_fields, how="left")

        group_y0_30d_keys = copy.deepcopy(groups_keys)
        group_y0_30d_keys["aggregations"] = [
            {"column": "quantity", "alias": "y0_30d_unit", "aggregation": "sum"},
            {"column": "item_sale_charged",
                "alias": "y0_30d_amount", "aggregation": "sum"},
        ]
        last_30d_prior = self.yesterday - timedelta(days=30)
        agg_y0_30d = self._aggregate_analysis_3rd_party(
            analysis_3rd_party=analysis_3rd_party,
            external_id=external_id,
            groups=group_y0_30d_keys,
            fields=fields_agg,
            sale_dates=[[last_30d_prior.strftime(
                "%Y-%m-%d 00:00:00"), self.yesterday.strftime("%Y-%m-%d 23:59:59")]],
            sale_status=[SALE_SHIPPED_STATUS],
            conditions=conditions_optional,
            distinct=True,
            paging=paging_agg,
        )
        logger.debug(
            f"[{self.__class__.__name__}][_aggregate][analysis_3rd_party][agg_y0_30d] " f"Result: {agg_y0_30d}"
        )
        columns = [item["name"] for item in agg_y0_30d["cols"]]
        _df = pd.DataFrame(agg_y0_30d["rows"], columns=columns)
        df = pd.merge(df, _df, on=df_mapping_fields, how="left")

        group_y1_30d_keys = copy.deepcopy(groups_keys)
        group_y1_30d_keys["aggregations"] = [
            {"column": "quantity", "alias": "y1_30d_unit", "aggregation": "sum"},
            {"column": "item_sale_charged",
                "alias": "y1_30d_amount", "aggregation": "sum"},
        ]
        agg_y1_30d = self._aggregate_analysis_3rd_party(
            analysis_3rd_party=analysis_3rd_party,
            external_id=external_id,
            groups=group_y1_30d_keys,
            fields=fields_agg,
            sale_dates=[
                [
                    last_30d_prior.strftime(f"{last_year}-%m-%d 00:00:00"),
                    self.yesterday.strftime(f"{last_year}-%m-%d 23:59:59")
                ]
            ],
            sale_status=[SALE_SHIPPED_STATUS],
            conditions=conditions_optional,
            distinct=True,
            paging=paging_agg,
        )
        logger.debug(
            f"[{self.__class__.__name__}][_aggregate][analysis_3rd_party][agg_y1_30d] " f"Result: {agg_y1_30d}"
        )
        columns = [item["name"] for item in agg_y1_30d["cols"]]
        _df = pd.DataFrame(agg_y1_30d["rows"], columns=columns)
        df = pd.merge(df, _df, on=df_mapping_fields, how="left")

        group_y0_ytd_keys = copy.deepcopy(groups_keys)
        group_y0_ytd_keys["aggregations"] = [
            {"column": "quantity", "alias": "y0_ytd_unit", "aggregation": "sum"},
            {"column": "item_sale_charged",
                "alias": "y0_ytd_amount", "aggregation": "sum"},
        ]
        agg_y0_ytd = self._aggregate_analysis_3rd_party(
            analysis_3rd_party=analysis_3rd_party,
            external_id=external_id,
            groups=group_y0_ytd_keys,
            fields=fields_agg,
            sale_dates=[
                [
                    self.yesterday.strftime(f"%Y-01-01 00:00:00"),
                    self.yesterday.strftime(f"%Y-%m-%d 23:59:59")
                ]
            ],
            sale_status=[SALE_SHIPPED_STATUS],
            conditions=conditions_optional,
            distinct=True,
            paging=paging_agg,
        )
        logger.debug(
            f"[{self.__class__.__name__}][_aggregate][analysis_3rd_party][agg_y0_ytd] " f"Result: {agg_y0_ytd}"
        )
        columns = [item["name"] for item in agg_y0_ytd["cols"]]
        _df = pd.DataFrame(agg_y0_ytd["rows"], columns=columns)
        df = pd.merge(df, _df, on=df_mapping_fields, how="left")

        group_y1_ytd_keys = copy.deepcopy(groups_keys)
        group_y1_ytd_keys["aggregations"] = [
            {"column": "quantity", "alias": "y1_ytd_unit", "aggregation": "sum"},
            {"column": "item_sale_charged",
                "alias": "y1_ytd_amount", "aggregation": "sum"},
        ]
        agg_y1_ytd = self._aggregate_analysis_3rd_party(
            analysis_3rd_party=analysis_3rd_party,
            external_id=external_id,
            groups=group_y1_ytd_keys,
            fields=fields_agg,
            sale_dates=[
                [
                    self.yesterday.strftime(f"{last_year}-01-01 00:00:00"),
                    self.yesterday.strftime(f"{last_year}-%m-%d 23:59:59"),
                ]
            ],
            sale_status=[SALE_SHIPPED_STATUS],
            conditions=conditions_optional,
            distinct=True,
            paging=paging_agg,
        )
        logger.debug(
            f"[{self.__class__.__name__}][_aggregate][analysis_3rd_party][agg_y0_ytd] " f"Result: {agg_y1_ytd}"
        )
        columns = [item["name"] for item in agg_y1_ytd["cols"]]
        _df = pd.DataFrame(agg_y1_ytd["rows"], columns=columns)
        df = pd.merge(df, _df, on=df_mapping_fields, how="left")

        df = df[
            (df["d0_unit"].notna())
            | (df["d1_unit"].notna())
            | (df["y0_30d_unit"].notna())
            | (df["y1_30d_unit"].notna())
            | (df["y0_ytd_unit"].notna())
            | (df["y1_ytd_unit"].notna())
        ]

        df = df.fillna(0).infer_objects(copy=False)

        # DAILY Diff
        df["d_diff_unit"] = np.where(
            # or 0 if you prefer
            df["d1_unit"] != 0, ((
                df["d0_unit"] - df["d1_unit"]) / df["d1_unit"]) * 100, 0
        )
        df["d_diff_amount"] = np.where(
            # or 0 if you prefer
            df["d1_amount"] != 0, ((
                df["d0_amount"] - df["d1_amount"]) / df["d1_amount"]) * 100, 0
        )
        # 30 DAYS Diff
        df["y_30d_diff_unit"] = np.where(
            df["y1_30d_unit"] != 0,
            ((df["y0_30d_unit"] - df["y1_30d_unit"]) / df["y1_30d_unit"]) * 100,
            0,  # or 0 if you prefer
        )
        df["y_30d_diff_amount"] = np.where(
            df["y1_30d_amount"] != 0,
            ((df["y0_30d_amount"] - df["y1_30d_amount"]) /
             df["y1_30d_amount"]) * 100,
            0,  # or 0 if you prefer
        )
        # YTD Diff
        df["y_ytd_diff_unit"] = np.where(
            df["y1_ytd_unit"] != 0,
            ((df["y0_ytd_unit"] - df["y1_ytd_unit"]) / df["y1_ytd_unit"]) * 100,
            0,  # or 0 if you prefer
        )
        df["y_ytd_diff_amount"] = np.where(
            df["y1_ytd_amount"] != 0,
            ((df["y0_ytd_amount"] - df["y1_ytd_amount"]) /
             df["y1_ytd_amount"]) * 100,
            0,  # or 0 if you prefer
        )

        data = df.to_dict(orient="records")

        return data

    def process_batch(
        self,
        client_id: str,
        analysis_3rd_party: DataSource,
        external_id: str,
        source_type: str,
        total: int = 0,
        page: int = 1,
        size: int = 500,
        modified_filter: str = None,
    ):
        data = []

        agg_data = self._aggregate(
            client_id=client_id,
            analysis_3rd_party=analysis_3rd_party,
            external_id=external_id,
            total=total,
            page=page,
            size=size,
            modified_filter=modified_filter,
        )

        logger.info(
            f"[{self.__class__.__name__}][{external_id}][process_batch] Total agg asins: {len(agg_data)}")

        modified_time = timezone.now().isoformat()
        for agg in agg_data:
            try:
                logger.debug(
                    f"[{self.__class__.__name__}][{external_id}][process_batch] agg: {agg}")

                _data = {k: agg[v]
                         for k, v in self.group_by_fields_mappings.items()}

                _data.update(
                    dict(
                        d0_unit=agg["d0_unit"],
                        d1_unit=agg["d1_unit"],
                        d0_amount=agg["d0_amount"],
                        d1_amount=agg["d1_amount"],
                        d_diff_unit=agg["d_diff_unit"],
                        d_diff_amount=agg["d_diff_amount"],
                        y0_30d_unit=agg["y0_30d_unit"],
                        y1_30d_unit=agg["y1_30d_unit"],
                        y0_30d_amount=agg["y0_30d_amount"],
                        y1_30d_amount=agg["y1_30d_amount"],
                        y_30d_diff_unit=agg["y_30d_diff_unit"],
                        y_30d_diff_amount=agg["y_30d_diff_amount"],
                        y0_ytd_unit=agg["y0_ytd_unit"],
                        y1_ytd_unit=agg["y1_ytd_unit"],
                        y0_ytd_amount=agg["y0_ytd_amount"],
                        y1_ytd_amount=agg["y1_ytd_amount"],
                        y_ytd_diff_unit=agg["y_ytd_diff_unit"],
                        y_ytd_diff_amount=agg["y_ytd_diff_amount"],
                        modified=modified_time,
                    )
                )
                logger.debug(
                    f"[{self.__class__.__name__}][{external_id}][process_batch] Agg normalize: {_data}")

                if source_type == FLATTEN_PG_SOURCE:
                    row_values = [
                        "'{}'".format(str(v).replace("'", "''")) if v is not None else "NULL" for v in _data.values()
                    ]
                    data.append(f"({','.join(row_values)})")
                else:
                    _key_data = "-".join([_data[k]
                                         for k in self.group_by_fields_mappings.keys()])
                    _data.update(id=_key_data)
                    data.append(_data)
            except Exception as ex:
                logger.error(
                    f"[{self.__class__.__name__}][{external_id}][process_batch] {ex}")

        logger.debug(
            f"[{self.__class__.__name__}][{external_id}][process_batch] Data: {data}")

        return data

    def build_flat_query_insert_segment_table(
        self,
        client_id: str,
        table_name: str,
        index_fields: str,
        total: int,
        page: int,
        size: int = 500,
        source_type: str = FLATTEN_PG_SOURCE,
        modified_filter: str = None,
        **kwargs,
    ):
        analysis_3rd_party = get_analysis_3rd_party(client_id=client_id)
        external_id = get_id_data_source_3rd_party(
            source=FLATTEN_ES_SOURCE, client_id=client_id)

        data = self.process_batch(
            client_id=client_id,
            analysis_3rd_party=analysis_3rd_party,
            external_id=external_id,
            source_type=source_type,
            total=total,
            page=page,
            size=size,
            modified_filter=modified_filter,
        )

        logger.debug(
            f"[{self.__class__.__name__}][{client_id}][build_flat_query_insert_segment_table] " f"Data: {data}"
        )

        # Construct SQL Query
        data = self.reformat_data_source_type(
            table_name, index_fields, data, source_type)
        return data

    def build_flat_query_insert_table(
        self,
        client_id: str,
        table_name: str,
        index_fields: str,
        source_type: str = FLATTEN_PG_SOURCE,
        modified_filter: str = None,
        **kwargs,
    ):
        """
        Builds an SQL INSERT query with ON CONFLICT for bulk inserting aggregated data into a flat table.

        :param client_id: The client ID for filtering data.
        :param table_name: The target table name.
        :param index_fields: The fields used for conflict resolution.
        :param source_type: The fields used for conflict resolution.
        :param modified_filter: The fields used for filter.
        :return: SQL query string for insertion.
        """
        size = self.build_count_aggregations_unique_combinations(
            client_id=client_id, **kwargs)
        if size == 0:
            raise ValueError(
                f"[{self.__class__.__name__}][{client_id}][build_flat_query_insert_table] Not found data")

        logger.info(
            f"[{self.__class__.__name__}][{client_id}][build_flat_query_insert_table] " f"Total: {size}")

        analysis_3rd_party = get_analysis_3rd_party(client_id=client_id)
        external_id = get_id_data_source_3rd_party(
            source=FLATTEN_ES_SOURCE, client_id=client_id)

        data = self.process_batch(
            client_id=client_id,
            analysis_3rd_party=analysis_3rd_party,
            external_id=external_id,
            source_type=source_type,
            total=size,
            page=1,
            size=size,
            modified_filter=modified_filter,
        )
        data = self.reformat_data_source_type(
            table_name, index_fields, data, source_type)
        logger.debug(
            f"[{self.__class__.__name__}][{client_id}][build_flat_query_insert_table] "
            f"Data of the source {source_type}: {data}"
        )
        return data
