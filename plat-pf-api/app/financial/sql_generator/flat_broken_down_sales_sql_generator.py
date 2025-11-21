from abc import ABC
from django.utils import timezone
from app.core.utils import round_currency
from app.financial.services.utils.common import get_id_data_source_3rd_party
from app.financial.services.utils.helper import get_analysis_3rd_party
from app.financial.sql_generator.flat_sql_schema_generator import FlatSchemaSQLGenerator, logger
from datetime import timedelta, datetime
from app.financial.variable.data_flatten_variable import FLATTEN_ES_SOURCE, FLATTEN_PG_SOURCE


class FlatBrokenDownSalesSQLGenerator(FlatSchemaSQLGenerator, ABC):
    columns_configs = {
        "Unit-Sales": {
            "field_aggregate": "quantity"
        },
        "Sale-Charged": {
            "field_aggregate": "item_sale_charged"
        },
        "Profit": {
            "field_aggregate": "item_profit"
        },
        "Margin": {
            "field_aggregate": "item_margin"
        }
    }

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
            "_source_table_.total_day": {
                "name": "total_day",
                "pg": {
                    "type": "numeric"
                },
                "es": {
                    "type": "float"
                }
            },
            "_source_table_.total_yesterday": {
                "name": "total_yesterday",
                "pg": {
                    "type": "numeric"
                },
                "es": {
                    "type": "float"
                }
            },
            "_source_table_.total_same_day_last_week": {
                "name": "total_same_day_last_week",
                "pg": {
                    "type": "numeric"
                },
                "es": {
                    "type": "float"
                }
            },
            "_source_table_.total_same_day_last_year": {
                "name": "total_same_day_last_year",
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
            "_source_table_.percent_vs_last_year": {
                "name": "percent_vs_last_year",
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

    def build_query_for_number_sync_rows(self, client_id, **kwargs):
        """
        build a query for counting the number of dirty rows in the original table
        :return:
        """
        sql = f"""
            SELECT {len(self.columns_configs)};
        """
        return sql

    def build_flat_query_insert_table(self, client_id: str, table_name: str, index_fields: str,
                                      source_type: str = FLATTEN_PG_SOURCE, modified_filter: str = None, **kwargs):
        today_from = self.date_now.strftime("%Y-%m-%d 00:00:00")
        today_to = self.date_now.strftime("%Y-%m-%d 23:59:59")

        logger.info(
            f"[{self.__class__.__name__}][build_flat_query_insert_table] Today: ({today_from}, {today_to})"
        )

        yesterday_from = self.yesterday.strftime("%Y-%m-%d 00:00:00")
        yesterday_to = self.yesterday.strftime("%Y-%m-%d 23:59:59")

        logger.info(
            f"[{self.__class__.__name__}][build_flat_query_insert_table] Yesterday: ({yesterday_from}, {yesterday_to})"
        )

        week_prior_today = self.date_now - timedelta(days=7)
        week_prior_today_from = week_prior_today.strftime("%Y-%m-%d 00:00:00")
        week_prior_today_to = week_prior_today.strftime("%Y-%m-%d 23:59:59")

        logger.info(
            f"[{self.__class__.__name__}][build_flat_query_insert_table] "
            f"Week Prior Today: ({week_prior_today_from}, {week_prior_today_to})"
        )

        last_year = self.date_now.year - 1
        year_prior_today = self.date_now.replace(year=last_year)
        year_prior_today_from = year_prior_today.strftime("%Y-%m-%d 00:00:00")
        year_prior_today_to = year_prior_today.strftime("%Y-%m-%d 23:59:59")

        logger.info(
            f"[{self.__class__.__name__}][build_flat_query_insert_table] "
            f"Year Prior Today: ({year_prior_today_from}, {year_prior_today_to})"
        )

        data = []

        def convert_amount(amount):
            if amount is None:
                amount = 0
            return amount

        modified_time = timezone.now().isoformat()
        analysis_3rd_party = get_analysis_3rd_party(client_id=client_id)
        external_id = get_id_data_source_3rd_party(
            source=FLATTEN_ES_SOURCE, client_id=client_id)

        for column, config in self.columns_configs.items():

            groups = {
                "columns": [],
                "aggregations": [
                    {
                        "column": config["field_aggregate"],
                        "alias": config["field_aggregate"].replace("_", " ").title(),
                        "aggregation": "sum"
                    }
                ]
            }

            today = self._aggregate_analysis_3rd_party(
                analysis_3rd_party=analysis_3rd_party,
                external_id=external_id,
                groups=groups,
                sale_dates=[
                    [today_from, today_to]
                ]
            )
            logger.debug(
                f"[{self.__class__.__name__}][build_flat_query_insert_table][analysis_3rd_party][today] Result: {today}"
            )
            today = round_currency(convert_amount(today["rows"][0][0]))

            yesterday = self._aggregate_analysis_3rd_party(
                analysis_3rd_party=analysis_3rd_party,
                external_id=external_id,
                groups=groups,
                sale_dates=[
                    [yesterday_from, yesterday_to]
                ]
            )
            logger.debug(
                f"[{self.__class__.__name__}][build_flat_query_insert_table][analysis_3rd_party][yesterday] "
                f"Result: {yesterday}"
            )
            yesterday = round_currency(convert_amount(yesterday["rows"][0][0]))

            week_prior_today = self._aggregate_analysis_3rd_party(
                analysis_3rd_party=analysis_3rd_party,
                external_id=external_id,
                groups=groups,
                sale_dates=[
                    [week_prior_today_from, week_prior_today_to]
                ]
            )
            logger.debug(
                f"[{self.__class__.__name__}][build_flat_query_insert_table][analysis_3rd_party][week_prior_today] "
                f"Result: {week_prior_today}"
            )
            week_prior_today = round_currency(
                convert_amount(week_prior_today["rows"][0][0]))

            year_prior_today = self._aggregate_analysis_3rd_party(
                analysis_3rd_party=analysis_3rd_party,
                external_id=external_id,
                groups=groups,
                sale_dates=[
                    [year_prior_today_from, year_prior_today_to]
                ]
            )
            logger.debug(
                f"[{self.__class__.__name__}][build_flat_query_insert_table][analysis_3rd_party][year_prior_today] "
                f"Result: {year_prior_today}"
            )
            year_prior_today = round_currency(
                convert_amount(year_prior_today["rows"][0][0]))

            if yesterday == 0:
                percent_vs_yesterday = 0
            else:
                percent_vs_yesterday = ((today - yesterday) / yesterday) * 100

            if week_prior_today == 0:
                percent_vs_last_week = 0
            else:
                percent_vs_last_week = (
                    (today - week_prior_today) / week_prior_today) * 100

            if year_prior_today == 0:
                percent_vs_last_year = 0
            else:
                percent_vs_last_year = (
                    (today - year_prior_today) / year_prior_today) * 100

            _data = dict(
                division=column,
                total_day=today,
                total_yesterday=yesterday,
                total_same_day_last_week=week_prior_today,
                total_same_day_last_year=year_prior_today,
                percent_vs_yesterday=round(
                    convert_amount(percent_vs_yesterday), 2),
                percent_vs_last_week=round(
                    convert_amount(percent_vs_last_week), 2),
                percent_vs_last_year=round(
                    convert_amount(percent_vs_last_year), 2),
                modified=modified_time
            )

            if source_type == FLATTEN_PG_SOURCE:
                row_values = [
                    "'{}'".format(str(v).replace("'", "''")) if v is not None else "NULL" for v in _data.values()
                ]
                data.append(f"({','.join(row_values)})")
            else:
                data.append(_data)

        data = self.reformat_data_source_type(
            table_name, index_fields, data, source_type)

        logger.debug(
            f"[{self.__class__.__name__}][{client_id}][build_flat_query_insert_table] "
            f"Data of the source {source_type}: {data}"
        )
        return data
