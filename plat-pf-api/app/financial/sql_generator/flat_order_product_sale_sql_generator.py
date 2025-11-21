from abc import ABC
from django.utils import timezone
from app.financial.services.utils.common import get_id_data_source_3rd_party, round_currency
from app.financial.services.utils.helper import get_analysis_3rd_party
from app.financial.sql_generator.flat_sql_schema_generator import FlatSchemaSQLGenerator, logger
from datetime import timedelta
from app.financial.variable.data_flatten_variable import FLATTEN_ES_SOURCE, FLATTEN_PG_SOURCE


class FlatOrderProductSaleSQLGenerator(FlatSchemaSQLGenerator, ABC):
    filter_fulfilment_type = {
        "MFN": [
            {
                "column": "fulfillment_type",
                "operator": "starts_with",
                "value": "MFN"
            },
            {
                "column": "is_prime",
                "operator": "is_false",
                "value": ""
            }
        ],
        "INV": [
            {
                "column": "fulfillment_type",
                "operator": "$eq",
                "value": "FBA"
            }
        ],
        "Prime": [
            {
                "column": "is_prime",
                "operator": "is_true",
                "value": ""
            }
        ]
    }

    @property
    def config_statement_source(self):
        return {
            # {source column : alias name column}
            # ----------------------------------------------------------------
            "_source_table_.fulfillment_type": {
                "name": "fulfillment_type",
                "pg": {
                    "type": "varchar(255) not null"
                },
                "es": {
                    "type": "text"
                }
            },
            # -----------------------------------------------------------------
            "_source_table_.amount_d": {
                "name": "amount_d",
                "pg": {
                    "type": "numeric"
                },
                "es": {
                    "type": "float"
                }
            },
            "_source_table_.percent_d": {
                "name": "percent_d",
                "pg": {
                    "type": "numeric"
                },
                "es": {
                    "type": "float"
                }
            },
            "_source_table_.amount_30d": {
                "name": "amount_30d",
                "pg": {
                    "type": "numeric"
                },
                "es": {
                    "type": "float"
                }
            },
            "_source_table_.percent_30d": {
                "name": "percent_30d",
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
            SELECT {len(self.filter_fulfilment_type)};
        """
        return sql

    def build_flat_query_insert_table(self, client_id: str, table_name: str, index_fields: str,
                                      source_type: str = FLATTEN_PG_SOURCE, modified_filter: str = None, **kwargs):
        analysis_3rd_party = get_analysis_3rd_party(client_id=client_id)
        external_id = get_id_data_source_3rd_party(
            source=FLATTEN_ES_SOURCE, client_id=client_id)

        def convert_amount(amount):
            if amount is None:
                amount = 0
            return amount

        def calculate_percent(amount, total):
            try:
                percent = round((float(amount) / float(total)) * 100, 2)
            except Exception:
                percent = 0
            return percent

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

        # Day
        total_d = self._aggregate_analysis_3rd_party(
            analysis_3rd_party=analysis_3rd_party,
            external_id=external_id,
            groups=groups,
            sale_dates=[
                [
                    self.yesterday.strftime("%Y-%m-%d 00:00:00"),
                    self.yesterday.strftime("%Y-%m-%d 23:59:59")
                ]
            ]
        )
        logger.debug(
            f"[{self.__class__.__name__}][build_flat_query_insert_table][analysis_3rd_party][Total Day] "
            f"Result: {total_d}"
        )
        total_d = convert_amount(total_d["rows"][0][0])

        # 30Days
        total_30d = self._aggregate_analysis_3rd_party(
            analysis_3rd_party=analysis_3rd_party,
            external_id=external_id,
            groups=groups,
            sale_dates=[
                [
                    (self.yesterday - timedelta(days=30)
                     ).strftime("%Y-%m-%d 00:00:00"),
                    self.yesterday.strftime("%Y-%m-%d 23:59:59")
                ]
            ]
        )
        logger.debug(
            f"[{self.__class__.__name__}][build_flat_query_insert_table][analysis_3rd_party][Total 30 Days] "
            f"Result: {total_30d}"
        )
        total_30d = convert_amount(total_30d["rows"][0][0])

        data = []

        modified_time = timezone.now().isoformat()
        for key, val in self.filter_fulfilment_type.items():
            filter_fulfilment_type = self.filter_fulfilment_type[key]
            #
            amount_d = self._aggregate_analysis_3rd_party(
                analysis_3rd_party=analysis_3rd_party,
                external_id=external_id,
                groups=groups,
                sale_dates=[
                    [
                        self.yesterday.strftime("%Y-%m-%d 00:00:00"),
                        self.yesterday.strftime("%Y-%m-%d 23:59:59")
                    ]
                ],
                conditions=filter_fulfilment_type
            )
            logger.debug(
                f"[{self.__class__.__name__}][build_flat_query_insert_table][analysis_3rd_party][Amount Days] "
                f"Result: {amount_d}"
            )
            amount_d = convert_amount(amount_d["rows"][0][0])
            percent_d = calculate_percent(amount_d, total_d)
            #
            amount_30d = self._aggregate_analysis_3rd_party(
                analysis_3rd_party=analysis_3rd_party,
                external_id=external_id,
                groups=groups,
                sale_dates=[
                    [
                        (self.yesterday - timedelta(days=30)
                         ).strftime("%Y-%m-%d 00:00:00"),
                        self.yesterday.strftime("%Y-%m-%d 23:59:59")
                    ]
                ],
                conditions=filter_fulfilment_type
            )
            logger.debug(
                f"[{self.__class__.__name__}][build_flat_query_insert_table][analysis_3rd_party][Amount 30 Days] "
                f"Result: {amount_d}"
            )
            amount_30d = convert_amount(amount_30d["rows"][0][0])
            percent_30d = calculate_percent(amount_30d, total_30d)

            _data = dict(
                fulfillment_type=key,
                amount_d=round_currency(amount_d),
                percent_d=percent_d,
                amount_30d=round_currency(amount_30d),
                percent_30d=percent_30d,
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
