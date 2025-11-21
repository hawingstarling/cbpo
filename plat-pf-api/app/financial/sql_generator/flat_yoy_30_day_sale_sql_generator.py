import copy
import logging
from typing import Dict, List
import pandas as pd
from abc import ABC

import pytz
from django.utils import timezone
from app.es.services.documents.sources.sale_item import SaleItemDocument
from app.financial.services.utils.common import get_id_data_source_3rd_party
from app.financial.services.utils.helper import get_analysis_es_service
from app.financial.sql_generator.flat_sql_schema_generator import FlatSchemaSQLGenerator, logger
from datetime import timedelta, datetime

from app.financial.variable.data_flatten_variable import FLATTEN_PG_SOURCE, FLATTEN_ES_SOURCE


class FlatYOY30DaySaleSQLGenerator(FlatSchemaSQLGenerator, ABC):
    day_number = 31

    @property
    def config_statement_source(self):
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
            "_source_table_.prior_month_date": {
                "name": "prior_month_date",
                "pg": {
                    "type": "date not null"
                },
                "es": {
                    "type": "date"
                }
            },
            "_source_table_.prior_month": {
                "name": "prior_month",
                "pg": {
                    "type": "numeric"
                },
                "es": {
                    "type": "float"
                }
            },
            # -----------------------------------------------------------------
            "_source_table_.y0": {
                "name": "y0",
                "pg": {
                    "type": "numeric"
                },
                "es": {
                    "type": "float"
                }
            },
            "_source_table_.y1": {
                "name": "y1",
                "pg": {
                    "type": "numeric"
                },
                "es": {
                    "type": "float"
                }
            },
            "_source_table_.y2": {
                "name": "y2",
                "pg": {
                    "type": "numeric"
                },
                "es": {
                    "type": "float"
                }
            },
            "_source_table_.y3": {
                "name": "y3",
                "pg": {
                    "type": "numeric"
                },
                "es": {
                    "type": "float"
                }
            },
            # ---------------------------------------------------------
            "_source_table_.f0": {
                "name": "f0",
                "pg": {
                    "type": "numeric"
                },
                "es": {
                    "type": "float"
                }
            },
            "_source_table_.f1": {
                "name": "f1",
                "pg": {
                    "type": "numeric"
                },
                "es": {
                    "type": "float"
                }
            },
            "_source_table_.f2": {
                "name": "f2",
                "pg": {
                    "type": "numeric"
                },
                "es": {
                    "type": "float"
                }
            },
            "_source_table_.f_total": {
                "name": "f_total",
                "pg": {
                    "type": "numeric"
                },
                "es": {
                    "type": "float"
                }
            },
            # -----------------------------------------------------------------
            "_source_table_.f0_order": {
                "name": "f0_order",
                "pg": {
                    "type": "integer"
                },
                "es": {
                    "type": "integer"
                }
            },
            "_source_table_.f1_order": {
                "name": "f1_order",
                "pg": {
                    "type": "integer"
                },
                "es": {
                    "type": "integer"
                }
            },
            "_source_table_.f2_order": {
                "name": "f2_order",
                "pg": {
                    "type": "integer"
                },
                "es": {
                    "type": "integer"
                }
            },
            "_source_table_.f_order_total": {
                "name": "f_order_total",
                "pg": {
                    "type": "integer"
                },
                "es": {
                    "type": "integer"
                }
            },
            # ------------------------------------------------------------------
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
        # Set PT timezone
        pt = pytz.timezone(self.ds_tz_calculate)

        # Get yesterday in PT as date only
        yesterday_pt = datetime.now(pt).date() - timedelta(days=1)

        # Create a list of dates (not datetime)
        date_list = [yesterday_pt - timedelta(days=x)
                     for x in range(0, self.day_number)]

        # Build DataFrame
        df = pd.DataFrame({
            'date': date_list,
            'prior_month_date': [d - timedelta(days=30) for d in date_list]
        })

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
            SELECT {self.day_number};
        """
        return sql

    def _aggregate_analysis_es(
            self,
            analysis_3rd_party: SaleItemDocument,
            sale_dates: List[List[str]],
            aggregations: Dict,
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
                            "format": "yyyy-MM-dd",
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
                "by_sale_date": {
                    "date_histogram": {
                        "field": "sale_date",
                        "calendar_interval": "day",
                        "format": "yyyy-MM-dd",
                        "time_zone": self.ds_tz_calculate
                    },
                    "aggs": aggregations
                }
            }
        }
        res = analysis_3rd_party.search(query=query)
        logger.debug(
            f"[{self.__class__.__name__}][_aggregate_analysis_es][{analysis_3rd_party.index}]"
            f"[{sale_dates}] Response: {res}"
        )
        buckets = res["aggregations"]["by_sale_date"]["buckets"]
        agg_fields = aggregations.keys()
        data = []
        for bucket in buckets:
            _data = [bucket["key_as_string"]]
            for agg_field in agg_fields:
                _data.append(
                    bucket[agg_field]["value"]
                )
            data.append(_data)

        return data

    def _aggregate(self, client_id: str, analysis_3rd_party: SaleItemDocument, external_id: str, total: int = 0,
                   page: int = 1, size: int = 500, modified_filter: str = None):

        df = self.build_df_series_days()
        df["date"] = pd.to_datetime(df['date'])
        df["prior_month_date"] = pd.to_datetime(df["prior_month_date"])

        aggregations_amount = {
            "total_amount": {
                "sum": {
                    "field": "item_sale_charged"
                }
            }
        }

        aggregations_unit = {
            "total_quantity": {
                "sum": {
                    "field": "quantity"
                }
            }
        }

        aggregations = {
            **aggregations_amount,
            **aggregations_unit
        }

        # Prio 30Days Year Now
        fd_60_days = self.yesterday - timedelta(days=60)
        from_date = fd_60_days.strftime("%Y-%m-%d")
        to_date = self.yesterday - timedelta(days=31)
        to_date = to_date.strftime("%Y-%m-%d")
        agg = self._aggregate_analysis_es(
            analysis_3rd_party=analysis_3rd_party,
            sale_dates=[
                [from_date, to_date]
            ],
            aggregations=aggregations_amount
        )
        logger.debug(
            f"[{self.__class__.__name__}][{external_id}][_process_batch][analysis_3rd_party][prior_month_date] "
            f"Result: {agg}"
        )
        columns = ["prior_month_date", "prior_month"]
        _df = pd.DataFrame(agg, columns=columns)
        _df["prior_month_date"] = pd.to_datetime(_df["prior_month_date"])
        df = pd.merge(df, _df, on=["prior_month_date"], how="left")

        fd_30_days = self.yesterday - timedelta(days=30)
        # Agg Year Now
        agg = self._aggregate_analysis_es(
            analysis_3rd_party=analysis_3rd_party,
            sale_dates=[
                [fd_30_days.strftime("%Y-%m-%d"),
                 self.yesterday.strftime("%Y-%m-%d")]
            ],
            aggregations=aggregations_amount
        )
        logger.debug(
            f"[{self.__class__.__name__}][{external_id}][_process_batch][analysis_3rd_party][y0] "
            f"Result: {agg}"
        )
        columns = ["date", "y0"]
        _df = pd.DataFrame(agg, columns=columns)
        _df["date"] = pd.to_datetime(_df["date"])
        df = pd.merge(df, _df, on=["date"], how="left")

        # Agg Year Ago
        last_year = self.yesterday.year - 1
        agg = self._aggregate_analysis_es(
            analysis_3rd_party=analysis_3rd_party,
            sale_dates=[
                [fd_30_days.strftime(f"{last_year}-%m-%d"),
                 self.yesterday.strftime(f"{last_year}-%m-%d")]
            ],
            aggregations=aggregations_amount
        )
        logger.debug(
            f"[{self.__class__.__name__}][{external_id}][_process_batch][analysis_3rd_party][y1] "
            f"Result: {agg}"
        )
        columns = ["date", "y1"]
        _df = pd.DataFrame(agg, columns=columns)
        _df["date"] = pd.to_datetime(_df["date"])
        df = pd.merge(df, _df, on=["date"], how="left")

        # Agg 2 Year Ago
        last_2_year = self.yesterday.year - 2
        agg = self._aggregate_analysis_es(
            analysis_3rd_party=analysis_3rd_party,
            sale_dates=[
                [fd_30_days.strftime(f"{last_2_year}-%m-%d"),
                 self.yesterday.strftime(f"{last_2_year}-%m-%d")]
            ],
            aggregations=aggregations_amount
        )
        logger.debug(
            f"[{self.__class__.__name__}][{external_id}][_process_batch][analysis_3rd_party][y2] "
            f"Result: {agg}"
        )
        columns = ["date", "y2"]
        _df = pd.DataFrame(agg, columns=columns)
        _df["date"] = pd.to_datetime(_df["date"])
        df = pd.merge(df, _df, on=["date"], how="left")

        # Agg 3 Year Ago
        last_3_year = self.yesterday.year - 3
        agg = self._aggregate_analysis_es(
            analysis_3rd_party=analysis_3rd_party,
            sale_dates=[
                [fd_30_days.strftime(f"{last_3_year}-%m-%d"),
                 self.yesterday.strftime(f"{last_3_year}-%m-%d")]
            ],
            aggregations=aggregations_amount
        )
        logger.debug(
            f"[{self.__class__.__name__}][{external_id}][_process_batch][analysis_3rd_party][y3] "
            f"Result: {agg}"
        )
        columns = ["date", "y3"]
        _df = pd.DataFrame(agg, columns=columns)
        _df["date"] = pd.to_datetime(_df["date"])
        df = pd.merge(df, _df, on=["date"], how="left")

        # Agg MFN
        conditions = [
            {"term": {"is_prime": False}},
            {"prefix": {"fulfillment_type.keyword": "MFN"}}
        ]
        agg = self._aggregate_analysis_es(
            analysis_3rd_party=analysis_3rd_party,
            sale_dates=[
                [fd_30_days.strftime(f"%Y-%m-%d"),
                 self.yesterday.strftime(f"%Y-%m-%d")]
            ],
            aggregations=aggregations,
            conditions=conditions
        )
        logger.debug(
            f"[{self.__class__.__name__}][{external_id}][_process_batch][analysis_3rd_party][mfn] "
            f"Result: {agg}"
        )
        columns = ["date", "f0", "f0_order"]
        _df = pd.DataFrame(agg, columns=columns)
        _df["date"] = pd.to_datetime(_df["date"])
        df = pd.merge(df, _df, on=["date"], how="left")

        # Agg FBA
        conditions = [
            {"term": {"fulfillment_type.keyword": "FBA"}}
        ]
        agg = self._aggregate_analysis_es(
            analysis_3rd_party=analysis_3rd_party,
            sale_dates=[
                [fd_30_days.strftime(f"%Y-%m-%d"),
                 self.yesterday.strftime(f"%Y-%m-%d")]
            ],
            aggregations=aggregations,
            conditions=conditions
        )
        logger.debug(
            f"[{self.__class__.__name__}][{external_id}][_process_batch][analysis_3rd_party][fba] "
            f"Result: {agg}"
        )
        columns = ["date", "f1", "f1_order"]
        _df = pd.DataFrame(agg, columns=columns)
        _df["date"] = pd.to_datetime(_df["date"])
        df = pd.merge(df, _df, on=["date"], how="left")

        # Agg IS Prime
        conditions = [
            {"term": {"is_prime": True}}
        ]
        agg = self._aggregate_analysis_es(
            analysis_3rd_party=analysis_3rd_party,
            sale_dates=[
                [fd_30_days.strftime(f"%Y-%m-%d"),
                 self.yesterday.strftime(f"%Y-%m-%d")]
            ],
            aggregations=aggregations,
            conditions=conditions
        )
        logger.debug(
            f"[{self.__class__.__name__}][{external_id}][_process_batch][analysis_3rd_party][is_prime] "
            f"Result: {agg}"
        )
        columns = ["date", "f2", "f2_order"]
        _df = pd.DataFrame(agg, columns=columns)
        _df["date"] = pd.to_datetime(_df["date"])
        df = pd.merge(df, _df, on=["date"], how="left")

        df = df.fillna(0).infer_objects(copy=False)

        df["f_total"] = df["f0"] + df["f1"] + df["f2"]
        df["f_order_total"] = df["f0_order"] + df["f1_order"] + df["f2_order"]

        data = df.to_dict(orient="records")

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

                _data = dict(
                    date=agg["date"],
                    prior_month_date=agg["prior_month_date"],
                    prior_month=agg["prior_month"],
                    y0=agg["y0"],
                    y1=agg["y1"],
                    y2=agg["y2"],
                    y3=agg["y3"],
                    f0=agg["f0"],
                    f1=agg["f1"],
                    f2=agg["f2"],
                    f_total=agg["f_total"],
                    f0_order=int(agg["f0_order"]),
                    f1_order=int(agg["f1_order"]),
                    f2_order=int(agg["f2_order"]),
                    f_order_total=int(agg["f_order_total"]),
                    modified=modified_time
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
                    _key_data = f"{_data['date']}-{_data['prior_month_date']}"
                    _data.update(id=_key_data)
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
