import copy
import pandas as pd
import pytz
from abc import ABC
from datetime import datetime, timedelta
from typing import Dict, List
from django.utils import timezone

from app.es.services.documents.sources.sale_item import SaleItemDocument
from app.financial.services.utils.common import get_id_data_source_3rd_party
from app.financial.services.utils.helper import get_analysis_es_service
from app.financial.sql_generator.flat_sql_schema_generator import FlatSchemaSQLGenerator, logger
from dateutil.relativedelta import relativedelta

from app.financial.variable.data_flatten_variable import FLATTEN_PG_SOURCE, FLATTEN_ES_SOURCE


class FlatFulfillmentMonthlySaleSQLGenerator(FlatSchemaSQLGenerator, ABC):
    months_number = 20
    fulfillment_type_number = 3
    filter_fulfilment_type = [
        [{"prefix": {"fulfillment_type.keyword": "MFN"}}],
        [{"term": {"fulfillment_type.keyword": "FBA"}}],
        [{"term": {"is_prime": True}}]
    ]

    @property
    def config_statement_source(self):
        fulfillment_type_schema = self.build_range_column_schema(number=self.fulfillment_type_number, prefix_column="f",
                                                                 type="numeric")
        return {
            # {source column : alias name column}
            # ----------------------------------------------------------------
            "_source_table_.date": {
                "name": "date",
                "pg": {
                    "type": "date not null"
                },
                "es": {
                    "type": "date"
                }
            },
            # -----------------------------------------------------------------
            **fulfillment_type_schema,
            # -----------------------------------------------------------------
            "_source_table_.f_total": {
                "name": "f_total",
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

    def build_df_series_days(self):
        # Set timezone
        pt = pytz.timezone(self.ds_tz_calculate)

        # Get yesterday's date in PT and set to the first of its month
        yesterday_pt = datetime.now(pt).date() - timedelta(days=1)
        end_date = yesterday_pt.replace(day=1)

        # Generate a range of 20 months ending at `end_date`
        dates = pd.date_range(end=end_date, periods=20, freq='MS')[::-1]

        # Create DataFrame
        df = pd.DataFrame({'date': dates})
        # Sort by date descending
        df = df.sort_values(by='date', ascending=False).reset_index(drop=True)

        # print(df)
        # print(df["date"].dtypes)

        return df

    def build_query_for_number_sync_rows(self, client_id, **kwargs):
        """
        build a query for counting the number of dirty rows in the original table
        :return:
        """
        sql = f"""
            SELECT {self.months_number};
        """
        return sql

    def _aggregate_analysis_es(
            self,
            analysis_3rd_party: SaleItemDocument,
            sale_dates: List[List[str]],
            conditions: List[Dict] = None
    ):
        base_cond = {
            "must": [
                {"term": {"channel_name.keyword": self.ds_channel_default}},
                {"terms": {"item_sale_status.keyword": self.sale_status_accept_generate}},
                {
                    "range": {
                        "sale_date": {
                            "gte": sale_dates[0][0],  # YYYY-MM-DD
                            "lte": sale_dates[0][1],  # YYYY-MM-DD
                            "format": "yyyy-MM-dd HH:mm:ss",
                            "time_zone": self.ds_tz_calculate
                        }
                    }
                }
            ]
        }

        cond = copy.deepcopy(base_cond)

        if conditions:
            cond["must"] += conditions

        query = {
            "size": 0,
            "query": {
                "bool": cond
            },
            "aggs": {
                "sales_by_month": {
                    "date_histogram": {
                        "field": "sale_date",
                        "calendar_interval": "month",
                        "format": "yyyy-MM-dd",
                        "time_zone": self.ds_tz_calculate
                    },
                    "aggs": {
                        "distinct_sales_count": {
                            "cardinality": {
                                "field": "sale_id"
                            }
                        }
                    }
                }
            }
        }
        res = analysis_3rd_party.search(query=query)
        logger.debug(
            f"[{self.__class__.__name__}][_aggregate_analysis_es][{analysis_3rd_party.index}]"
            f"[{sale_dates}] Response: {res}"
        )
        buckets = res["aggregations"]["sales_by_month"]["buckets"]
        data = [[bucket["key_as_string"], bucket["distinct_sales_count"]["value"]]
                for bucket in buckets]
        return data

    def _aggregate(self, client_id: str, analysis_3rd_party: SaleItemDocument, external_id: str, total: int = 0,
                   page: int = 1, size: int = 500, modified_filter: str = None):

        df = self.build_df_series_days()
        # df["date"] = pd.to_datetime(df['date'])

        _date_20m_ago = self.yesterday - \
            relativedelta(months=self.months_number - 1)
        from_date = _date_20m_ago.replace(day=1).strftime("%Y-%m-%d 00:00:00")
        to_date = self.yesterday.strftime("%Y-%m-%d 23:59:59")
        for i in range(len(self.filter_fulfilment_type)):
            condition = self.filter_fulfilment_type[i]
            agg = self._aggregate_analysis_es(
                analysis_3rd_party=analysis_3rd_party,
                sale_dates=[
                    [from_date, to_date]
                ],
                conditions=condition
            )
            logger.debug(
                f"[{self.__class__.__name__}][{external_id}][_process_batch][analysis_3rd_party][sale_by_month_f{i}] "
                f"[{from_date}][{to_date}] Result: {agg}"
            )
            columns = ["date", f"f{i}"]
            _df = pd.DataFrame(agg, columns=columns)
            _df["date"] = pd.to_datetime(_df["date"])
            df = pd.merge(df, _df, on=["date"], how="left")

        df = df.fillna(0).infer_objects(copy=False)
        df["f_total"] = df["f0"] + df["f1"] + df["f2"]
        data = df.to_dict(orient="records")

        # print(df)

        return data

    def process_batch(self, client_id: str, analysis_3rd_party: SaleItemDocument, external_id: str, source_type: str,
                      total: int = 0, page: int = 1, size: int = 500, modified_filter: str = None):

        data = []

        agg_data = self._aggregate(
            client_id=client_id, analysis_3rd_party=analysis_3rd_party, external_id=external_id)

        logger.info(
            f"[{self.__class__.__name__}][{external_id}][process_batch] Total agg asins: {len(agg_data)}"
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

    def build_flat_query_insert_table(self, client_id: str, table_name: str, index_fields: str,
                                      source_type: str = FLATTEN_PG_SOURCE, modified_filter: str = None, **kwargs):
        analysis_3rd_party = get_analysis_es_service(client_id=client_id)
        external_id = get_id_data_source_3rd_party(
            source=FLATTEN_ES_SOURCE, client_id=client_id)

        data = self.process_batch(client_id=client_id, analysis_3rd_party=analysis_3rd_party, external_id=external_id,
                                  source_type=source_type)
        data = self.reformat_data_source_type(
            table_name, index_fields, data, source_type)
        logger.debug(
            f"[{self.__class__.__name__}][{client_id}][build_flat_query_insert_table] "
            f"Data of the source {source_type}: {data}"
        )
        return data
