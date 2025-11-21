from abc import ABC
import copy
from datetime import timedelta, datetime

import numpy as np
import pandas as pd
from dateutil.relativedelta import relativedelta
from django.core.paginator import Paginator
from django.utils import timezone

from app.financial.jobs.settings import handler_init_sync_divisions_widget_clients
from app.financial.models import DivisionClientUserWidget
from app.financial.services.data_source import DataSource
from app.financial.services.utils.common import get_id_data_source_3rd_party
from app.financial.services.utils.helper import get_analysis_3rd_party
from app.financial.sql_generator.flat_sql_schema_generator import FlatSchemaSQLGenerator, logger

from app.financial.variable.data_flatten_variable import FLATTEN_ES_SOURCE, FLATTEN_PG_SOURCE
from app.financial.variable.segment_variable import OVERALL_SALES_CATEGORY, OVERALL_SALES_CALCULATE_DEFAULT


class FlatOverallSalesSQLGenerator(FlatSchemaSQLGenerator, ABC):

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
            "_source_table_.total": {
                "name": "total",
                "pg": {
                    "type": "numeric"
                },
                "es": {
                    "type": "float"
                }
            },
            "_source_table_.percent_vs_yesterday": {
                "name": "percent_vs_yesterday",
                "pg": {
                    "type": "numeric"
                },
                "es": {
                    "type": "float"
                }
            },
            "_source_table_.percent_vs_last_week": {
                "name": "percent_vs_last_week",
                "pg": {
                    "type": "numeric"
                },
                "es": {
                    "type": "float"
                }
            },
            "_source_table_.percent_vs_last_month": {
                "name": "percent_vs_last_month",
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
        queryset = DivisionClientUserWidget.objects.tenant_db_for(client_id) \
            .filter(client_id=client_id, category=OVERALL_SALES_CATEGORY)

        if queryset.count() == 0:
            logger.error(
                f"[{self.__class__.__name__}][{client_id}][build_count_aggregations_unique_combinations] "
                f"Syncing division ..."
            )
            handler_init_sync_divisions_widget_clients(client_ids=[client_id])

        return queryset.count()

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

    def get_day_number_prior_month(self):

        # Calculate the first day of this month
        first_day_this_month = self.yesterday.replace(day=1)

        # Calculate the last day of the previous month
        last_day_prior_month = first_day_this_month - timedelta(days=1)
        first_day_prior_month = last_day_prior_month.replace(day=1)

        # Check if today falls in the prior month
        if first_day_prior_month.day <= self.yesterday.day <= last_day_prior_month.day:
            return self.yesterday.day
        else:
            return last_day_prior_month.day

    def _aggregate(self, client_id: str, analysis_3rd_party: DataSource, external_id: str, total: int = 0,
                   page: int = 1, size: int = 500, modified_filter: str = None):

        queryset = DivisionClientUserWidget.objects.tenant_db_for(client_id) \
            .filter(client_id=client_id, category=OVERALL_SALES_CATEGORY).order_by("key")

        objs = Paginator(queryset, size).page(number=page).object_list

        # Set the Option to Accept Future Behavior (opt-in)
        # This will silence the warning and enforce stricter behavior, preparing your code for future pandas versions.
        pd.set_option('future.no_silent_downcasting', True)

        yesterday_from = self.yesterday.strftime("%Y-%m-%d 00:00:00")
        yesterday_to = self.yesterday.strftime("%Y-%m-%d 23:59:59")

        prior_yesterday = self.yesterday - timedelta(days=1)
        prior_yesterday_from = prior_yesterday.strftime("%Y-%m-%d 00:00:00")
        prior_yesterday_to = prior_yesterday.strftime("%Y-%m-%d 23:59:59")

        week_prior_yesterday = self.yesterday - timedelta(days=7)
        week_prior_yesterday_from = week_prior_yesterday.strftime(
            "%Y-%m-%d 00:00:00")
        week_prior_yesterday_to = week_prior_yesterday.strftime(
            "%Y-%m-%d 23:59:59")

        date_month_ago = self.yesterday - relativedelta(months=1)
        day_prior_month = self.get_day_number_prior_month()
        month_prior_yesterday = self.yesterday.replace(day=day_prior_month, month=date_month_ago.month,
                                                       year=date_month_ago.year)
        month_prior_yesterday_from = month_prior_yesterday.strftime(
            "%Y-%m-%d 00:00:00")
        month_prior_yesterday_to = month_prior_yesterday.strftime(
            "%Y-%m-%d 23:59:59")

        data = []
        for obj in objs:
            division = obj.key
            _config = OVERALL_SALES_CALCULATE_DEFAULT.get(division, {})

            logger.debug(
                f"[{self.__class__.__name__}][build_flat_query_insert_table][analysis_3rd_party][{division}] "
                f"Config: {_config}"
            )

            conditions = []

            if "fulfillment_type" in _config:
                conditions.append(
                    {
                        "column": "fulfillment_type",
                        "operator": "in",
                        "value": _config["fulfillment_type"]
                    }
                )

            groups = {
                "columns": [],
                "aggregations": [
                    {
                        "column": _config["field_aggregate"],
                        "alias": _config["field_aggregate"].replace("_", " ").title(),
                        "aggregation": "sum"
                    }
                ]
            }

            fields_keys = [
                {
                    "name": _config["field_aggregate"],
                    "alias": 0
                }
            ]

            # Agg Yesterday
            agg_yesterday = self._aggregate_analysis_3rd_party(
                analysis_3rd_party=analysis_3rd_party,
                external_id=external_id,
                groups=groups,
                fields=fields_keys,
                sale_dates=[
                    [yesterday_from, yesterday_to]
                ],
                conditions=conditions
            )
            logger.debug(
                f"[{self.__class__.__name__}][build_flat_query_insert_table][analysis_3rd_party][agg_yesterday] "
                f"Division: {division}, Condition: {conditions}, Result: {agg_yesterday}"
            )
            agg_yesterday = agg_yesterday["rows"][0][0]

            # Agg Prior Yesterday
            agg_prior_yesterday = self._aggregate_analysis_3rd_party(
                analysis_3rd_party=analysis_3rd_party,
                external_id=external_id,
                groups=groups,
                fields=fields_keys,
                sale_dates=[
                    [prior_yesterday_from, prior_yesterday_to]
                ],
                conditions=conditions
            )
            logger.debug(
                f"[{self.__class__.__name__}][build_flat_query_insert_table][analysis_3rd_party][agg_prior_yesterday] "
                f"Result: {agg_prior_yesterday}"
            )
            agg_prior_yesterday = agg_prior_yesterday["rows"][0][0]

            # Agg Week Prior Yesterday
            agg_week_prior = self._aggregate_analysis_3rd_party(
                analysis_3rd_party=analysis_3rd_party,
                external_id=external_id,
                groups=groups,
                fields=fields_keys,
                sale_dates=[
                    [week_prior_yesterday_from, week_prior_yesterday_to]
                ],
                conditions=conditions
            )
            logger.debug(
                f"[{self.__class__.__name__}][build_flat_query_insert_table][analysis_3rd_party]"
                f"[agg_week_prior] Result: {agg_week_prior}"
            )
            agg_week_prior = agg_week_prior["rows"][0][0]

            # Agg Month Prior Yesterday
            agg_month_prior = self._aggregate_analysis_3rd_party(
                analysis_3rd_party=analysis_3rd_party,
                external_id=external_id,
                groups=groups,
                fields=fields_keys,
                sale_dates=[
                    [month_prior_yesterday_from, month_prior_yesterday_to]
                ],
                conditions=conditions
            )
            logger.debug(
                f"[{self.__class__.__name__}][build_flat_query_insert_table][analysis_3rd_party][agg_month_prior] "
                f"Result: {agg_month_prior}"
            )
            agg_month_prior = agg_month_prior["rows"][0][0]

            data.append(
                [division, agg_yesterday, agg_prior_yesterday,
                    agg_week_prior, agg_month_prior]
            )

        df = pd.DataFrame(data, columns=["division", "total", "total_prior_yesterday", "total_week_prior",
                                         "total_month_prior"])

        # percent_vs_yesterday
        df["percent_vs_yesterday"] = np.where(
            df["total_prior_yesterday"] != 0,
            ((df["total"] - df["total_prior_yesterday"]) /
             df["total_prior_yesterday"]) * 100,
            0  # or 0 if you prefer
        )

        # percent_vs_last_week
        df["percent_vs_last_week"] = np.where(
            df["total_week_prior"] != 0,
            ((df["total"] - df["total_week_prior"]) /
             df["total_week_prior"]) * 100,
            0  # or 0 if you prefer
        )

        # percent_vs_last_month
        df["percent_vs_last_month"] = np.where(
            df["total_month_prior"] != 0,
            ((df["total"] - df["total_month_prior"]) /
             df["total_month_prior"]) * 100,
            0  # or 0 if you prefer
        )

        columns_to_include = ["division", "total", "percent_vs_yesterday", "percent_vs_last_week",
                              "percent_vs_last_month"]
        data = df[columns_to_include].to_dict(orient="records")

        # print(data)

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
