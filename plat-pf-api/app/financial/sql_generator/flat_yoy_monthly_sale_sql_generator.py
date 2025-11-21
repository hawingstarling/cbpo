from abc import ABC
from django.utils import timezone
from app.financial.services.utils.common import get_id_data_source_3rd_party
from app.financial.services.utils.helper import get_analysis_3rd_party
from app.financial.sql_generator.flat_sql_schema_generator import FlatSchemaSQLGenerator, logger
from datetime import datetime
import pytz
import calendar

from app.financial.variable.data_flatten_variable import FLATTEN_ES_SOURCE, FLATTEN_PG_SOURCE


class FlatYOYMonthlySaleSQLGenerator(FlatSchemaSQLGenerator, ABC):
    months_number = 12
    year_number = 4

    @property
    def config_statement_source(self):
        years_schema = self.build_range_column_schema(
            number=self.year_number, prefix_column="y", type="numeric")
        return {
            # {source column : alias name column}
            # ----------------------------------------------------------------
            "_source_table_.date": {
                "name": "date",
                "pg": {
                    "type": "varchar(255) not null"
                },
                "es": {
                    "type": "text"
                }
            },
            # -----------------------------------------------------------------
            **years_schema,
            # -----------------------------------------------------------------
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
            SELECT {self.months_number};
        """
        return sql

    def build_flat_query_insert_table(self, client_id: str, table_name: str, index_fields: str,
                                      source_type: str = FLATTEN_PG_SOURCE, modified_filter: str = None, **kwargs):
        months = self.generate_list_month()
        years = self.generate_list_year(self.year_number)

        data = []

        modified_time = timezone.now().isoformat()
        analysis_3rd_party = get_analysis_3rd_party(client_id=client_id)
        external_id = get_id_data_source_3rd_party(
            source=FLATTEN_ES_SOURCE, client_id=client_id)
        groups = {
            "columns": [],
            "aggregations": [
                {
                    "column": "item_sale_charged",
                    "alias": "Sale Charged",
                    "aggregation": "sum"
                }
            ]
        }
        for month in months:
            _date_month = datetime(year=self.date_now.year, day=1, month=month, hour=0, minute=0, second=0,
                                   tzinfo=pytz.utc)
            _date_month = _date_month.strftime("%m-%d")
            _data = dict(
                date=_date_month
            )
            i = 0
            for year in years:
                number_day = calendar.monthrange(year, month)[1]
                from_date = f"{year}-{month}-01 00:00:00"
                to_date = f"{year}-{month}-{number_day} 23:59:59"
                amount = self._aggregate_analysis_3rd_party(
                    analysis_3rd_party=analysis_3rd_party,
                    external_id=external_id,
                    groups=groups,
                    sale_dates=[
                        [from_date, to_date]
                    ]
                )
                logger.debug(
                    f"[{self.__class__.__name__}][build_flat_query_insert_table][analysis_3rd_party]"
                    f"[{from_date}][{to_date}]Result: {amount}"
                )
                rows = amount.get("rows", []) if isinstance(
                    amount, dict) else []
                amount_val = rows[0][0] if rows and rows[0] and rows[0][0] is not None else 0
                amount = amount_val
                _data.update(
                    dict(
                        **{
                            f"y{year}": amount
                        }
                    )
                )
                i += 1

            _data.update(
                dict(
                    modified=modified_time
                )
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
