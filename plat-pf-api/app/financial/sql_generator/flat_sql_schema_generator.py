import copy
import hashlib
import logging
from abc import ABC
from typing import List, Dict, Union

import pytz

from app.core.variable.marketplace import CHANNEL_DEFAULT

#
from app.es.variables.mapping_types.config import ES_MAPPING_TYPE_FIELDS_CONFIG, ES_TEXT_TYPE
from app.financial.services.data_source import DataSource
from app.financial.services.utils.common import get_flatten_source_name
from app.financial.sql_generator.flat_sql_generator_interface import FlatSqlGeneratorInterface
from app.financial.variable.sale_status_static_variable import (
    SALE_PENDING_STATUS,
    SALE_UNSHIPPED_STATUS,
    SALE_SHIPPED_STATUS,
    SALE_PARTIALLY_REFUNDED_STATUS,
)
from datetime import timedelta, datetime
from django.conf import settings
from app.financial.variable.data_flatten_variable import FLATTEN_ES_SOURCE, FLATTEN_PG_SOURCE, FLATTEN_SOURCES_LIST

logger = logging.getLogger(__name__)


class FlatSchemaSQLGenerator(FlatSqlGeneratorInterface, ABC):
    ds_tz_calculate = settings.DS_TZ_CALCULATE
    ds_tz_pytz = pytz.timezone(settings.DS_TZ_CALCULATE)
    ds_channel_default = CHANNEL_DEFAULT
    sale_status_accept_generate = [
        SALE_PENDING_STATUS,
        SALE_UNSHIPPED_STATUS,
        SALE_SHIPPED_STATUS,
        SALE_PARTIALLY_REFUNDED_STATUS,
    ]

    @property
    def date_now_utc(self):
        return datetime.now(tz=pytz.UTC)

    @property
    def date_now(self):
        return datetime.now(tz=self.ds_tz_pytz)

    @property
    def yesterday(self):
        return self.date_now - timedelta(days=1)

    def sale_status_for_build_sql(self):
        return tuple(self.sale_status_accept_generate)

    @classmethod
    def build_range_column_schema(
            cls, number: int, prefix_column: str, type: str, extra: str = """""", suffix_column: str = """"""
    ):
        schema = {}
        for i in range(number):
            _name = f"{prefix_column}{i}{suffix_column}"
            schema.update(
                {
                    f"_source_table_.{_name}": {
                        "name": _name,
                        "pg": {"type": f"{type} {extra}" if extra else type},
                        "es": {"type": "float"},
                    }
                }
            )
        return schema

    def generate_list_year(self, number: int):
        data = []

        year_now = self.date_now.year

        for i in range(number):
            data.append(year_now - i)

        return data

    def generate_list_month(self):
        data = []
        for i in range(12):
            month = i + 1
            data.append(month)
        return data

    def generate_list_30_day(self):
        for i in range(30):
            # begin calculate data yesterday
            num_day = i + 1
            yield self.date_now - timedelta(days=num_day)

    def _build_reduce_sub_query(self, client_id: str, ids: List[str], **kwargs):
        raise NotImplementedError

    def _build_join_sql(self, client_id: str):
        raise NotImplementedError

    def _build_order_by_sql(self, client_id: str, **kwargs):
        return """"""

    @classmethod
    def _build_limit_offset_by_sql(cls, client_id: str, **kwargs):
        #
        query = """"""
        limit = kwargs.get("limit", None)
        if limit is not None:
            query += f""" LIMIT {limit} """
        offset = kwargs.get("offset", None)
        if offset is not None:
            query += f""" OFFSET {offset} """
        return query

    def _build_cond_query_sale_item(self, client_id: str = None, ids: List[str] = None, **kwargs):
        if bool(ids):
            ids = tuple(ids) if len(ids) > 1 else """('{}')""".format(ids[0])
            query = f"""
                _source_table_.is_removed = FALSE AND _source_table_.id IN {ids}
            """
        else:
            query = f"""
                    _source_table_.is_removed = FALSE
                    """
        # additional query
        additional_query = kwargs.get("additional_query")
        if not bool(additional_query):
            additional_query = """"""
        query += additional_query
        return query

    def build_flat_query_schema_table(self, client_id: str, table_name: str, *kwargs) -> str:
        properties_mapping_source = self.build_properties_mapping_source(
            FLATTEN_PG_SOURCE)
        schema_mapping_source = [
            f"""{k} {v['type'].upper()}""" for k, v in properties_mapping_source.items()]
        final_query = f"""
            CREATE TABLE IF NOT EXISTS {table_name}
            ({', '.join(schema_mapping_source)});
        """
        return final_query

    def build_flat_query(self, client_id: str = None, ids: List[str] = None, **kwargs) -> str:
        """
        build SQL query by for specific client_id, dirty flag
        appropriate_time
        :return:
        """
        final_query = f"""
        SELECT {self._select_statement_analysis(client_id)} 
        FROM ({self._build_reduce_sub_query(client_id, ids, **kwargs)}) AS _source_table_ 
        {self._build_join_sql(client_id)};
        """

        return final_query

    def build_query_for_number_flatten_rows(self, table_flatten):
        """
        build query for counting the number of table flatten
        :return:
        """
        query = f"""
        SELECT COUNT(*)
        FROM {table_flatten};"""
        return query

    def build_base_filter(self, client_id, sale_status=None):
        flatten_base_table = get_flatten_source_name(client_id)
        #
        if sale_status is None:
            sale_status = self.sale_status_for_build_sql()
        #
        sql = f"""
            {flatten_base_table}.channel_name = '{self.ds_channel_default}' 
            AND {flatten_base_table}.item_sale_status IN {sale_status}
        """
        return sql

    def build_sql_to_check_flatten_exists(self, table):
        sql = f"""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                    WHERE  table_schema = 'public'
            AND  table_name   = '{table}')
        """
        return sql

    def build_sql_to_drop_flatten(self, table):
        sql = f"""
        DROP TABLE {table};
        """
        return sql

    def build_query_truncate_flatten(self, table):
        sql = f"""
        TRUNCATE TABLE {table};
        """
        return sql

    def build_query_delete_old_docs(self, table, time_threshold):
        sql = f"""
            DELETE
            FROM {table}
            WHERE modified < '{time_threshold}'::timestamptz;
        """
        return sql

    def hour_dt_tz_vs_utc(self, dt=None):
        if self.ds_tz_calculate is None:
            return 0
        try:
            tz = pytz.timezone(self.ds_tz_calculate)
            if dt is None:
                dt = self.date_now
            dt_tz = dt.astimezone(tz)
            # get hour by timezone set for query
            tz_info = dt_tz.strftime("%z")
            hour = int(tz_info.replace("0", ""))
            # database default UTC
            # need calculate hour (ds_tz_calculate) compare vs UTC
            # UTC vs UTC+7 => hour = -7
            # UTC vs UTC-7 => hour = 7
            # apply : dt = dt + timedelta(hours=hour)
            # E.g dt = 2021-01-01 00:00:00, ds_tz_calculate = America/Dawson -> dt = 2021-01-01 07:00:00
            hour *= -1
        except Exception as ex:
            logger.error(f"[{self.__class__.__name__}]: {ex}")
            hour = 0
        return hour

    def convert_dt_to_tz(self, dt: any, strftime: bool = True, fm_as_time: str = "%Y-%m-%d %H:%M:%S"):
        dt = dt + timedelta(hours=self.hour_dt_tz_vs_utc(dt))
        if strftime:
            dt = dt.strftime(fm_as_time)
        return dt

    def build_query_unique_index_flatten(self, table: str, unique_fields: [str]):
        join_string_fields = ",".join([str(elem) for elem in unique_fields])
        hash_index = hashlib.sha1(
            join_string_fields.encode("UTF-8")).hexdigest()[:6]
        unique_index_name = f"{table[:50]}_{hash_index}_uniq"
        sql_index = f"""CREATE UNIQUE INDEX IF NOT EXISTS {unique_index_name} ON {table} ({join_string_fields});"""
        return sql_index

    def build_query_indexes_flatten(self, table: str, indexes_fields: [dict]):
        sql_index = """"""
        for item in indexes_fields:
            fields = item["columns"]
            index_type = item.get("type", "BTREE")
            join_string_fields = ",".join([str(elem) for elem in fields])
            hash_index = hashlib.sha1(
                join_string_fields.encode("UTF-8")).hexdigest()[:6]
            unique_index_name = f"{table[:50]}_{hash_index}_idx"
            sql = f"""CREATE INDEX IF NOT EXISTS {unique_index_name} ON {table} USING {index_type} ({join_string_fields});"""
            sql_index += sql
        return sql_index

    @property
    def columns_update(self):
        return list(item["name"] for item in self.config_statement_source.values())

    def build_sql_do_update_set_by_conflict(self):
        set_on_column = ["{}=EXCLUDED.{}".format(
            column, column) for column in self.columns_update]
        return ", ".join(set_on_column)

    @property
    def config_statement_source(self):
        return {
            # {source column : alias name column}
            # ----------------- info sale -----------------------------------------------
            "_source_table_.sale_id": {
                "name": "sale_id",
                "pg": {"type": "bigint"},
                "es": {"type": "long"}
            },
            "joined_sale.channel_sale_id": {
                "name": "channel_id",
                "pg": {"type": "varchar(50)"},
                "es": {"type": "text"},
            },
            "joined_channel.name": {
                "name": "channel_name",
                "pg": {"type": "varchar(100)"},
                "es": {"type": "text"}
            },
            "joined_sale.customer_name": {
                "name": "customer_name",
                "pg": {"type": "varchar(100)"},
                "es": {"type": "text"},
            },
            "joined_sale.recipient_name": {
                "name": "recipient_name",
                "pg": {"type": "varchar(100)"},
                "es": {"type": "text"},
            },
            "joined_sale.state": {
                "name": "state",
                "pg": {"type": "varchar(45)"},
                "es": {"type": "text"}
            },
            "joined_sale.city": {
                "name": "city",
                "pg": {"type": "varchar(100)"},
                "es": {"type": "text"}
            },
            "joined_sale.country": {
                "name": "country",
                "pg": {"type": "varchar(100)"},
                "es": {"type": "text"}
            },
            "joined_sale.postal_code": {
                "name": "postal_code",
                "pg": {"type": "varchar(100)"},
                "es": {"type": "text"}
            },
            "joined_sale.is_prime": {
                "name": "is_prime",
                "pg": {"type": "boolean"},
                "es": {"type": "boolean"}
            },
            "joined_sale.state_key": {
                "name": "state_key",
                "pg": {"type": "varchar(50)"},
                "es": {"type": "text"}
            },
            "joined_sale.county_key": {
                "name": "county_key",
                "pg": {"type": "varchar(50)"},
                "es": {"type": "text"}
            },
            "lateral_spmr.value": {
                "name": "spmr",
                "pg": {"type": "numeric(6, 2)"},
                "es": {"type": "float"}
            },
            "joined_population.est": {
                "name": "state_population",
                "pg": {"type": "integer"},
                "es": {"type": "integer"}
            },
            # ----------------- info sale item ------------------------------------------
            "_source_table_.sale_date": {
                "name": "sale_date",
                "pg": {"type": "timestamp with time zone"},
                "es": {"type": "date"},
            },
            "_source_table_.id": {
                "name": "sale_item_id",
                "pg": {"type": "uuid"},
                "es": {"type": "text"}
            },
            "_source_table_.asin": {
                "name": "asin",
                "pg": {"type": "varchar(10)"},
                "es": {"type": "text"}
            },
            "_source_table_.title": {
                "name": "title",
                "pg": {"type": "varchar(255)"},
                "es": {"type": "text"}
            },
            "joined_brand.name": {
                "name": "brand",
                "pg": {"type": "varchar(50)"},
                "es": {"type": "text"}
            },
            "_source_table_.channel_brand": {
                "name": "channel_brand",
                "pg": {"type": "varchar(100)"},
                "es": {"type": "text"},
            },
            "_source_table_.upc": {
                "name": "upc",
                "pg": {"type": "varchar(13)"},
                "es": {"type": "text"}
            },
            "_source_table_.sku": {
                "name": "sku",
                "pg": {"type": "varchar(100)"},
                "es": {"type": "text"}
            },
            "_source_table_.brand_sku": {
                "name": "brand_sku",
                "pg": {"type": "varchar(100)"},
                "es": {"type": "text"}
            },
            "_source_table_.quantity": {
                "name": "quantity",
                "pg": {"type": "integer"},
                "es": {"type": "integer"}
            },
            "_source_table_.refunded_quantity": {
                "name": "refunded_quantity",
                "pg": {"type": "integer"},
                "es": {"type": "integer"},
            },
            "joined_size.value": {
                "name": "size",
                "pg": {"type": "varchar(200)"},
                "es": {"type": "text"}
            },
            "joined_style.value": {
                "name": "style",
                "pg": {"type": "varchar(200)"},
                "es": {"type": "text"}
            },
            "_source_table_.sale_charged": {
                "name": "item_sale_charged",
                "pg": {"type": "numeric(6, 2)"},
                "es": {"type": "float"},
            },
            "_source_table_.sale_charged_accuracy": {
                "name": "sale_charged_accuracy",
                "pg": {"type": "integer"},
                "es": {"type": "integer"},
            },
            "_source_table_.shipping_charged": {
                "name": "item_shipping_charged",
                "pg": {"type": "numeric(6, 2)"},
                "es": {"type": "float"},
            },
            "_source_table_.tax_charged": {
                "name": "item_tax_charged",
                "pg": {"type": "numeric(6, 2)"},
                "es": {"type": "float"},
            },
            "_source_table_.cog": {
                "name": "cog",
                "pg": {"type": "numeric(6, 2)"},
                "es": {"type": "float"}
            },
            "_source_table_.unit_cog": {
                "name": "unit_cog",
                "pg": {"type": "numeric(6, 2)"},
                "es": {"type": "float"}
            },
            "_source_table_.shipping_cost": {
                "name": "item_shipping_cost",
                "pg": {"type": "numeric(6, 2)"},
                "es": {"type": "float"},
            },
            "_source_table_.shipping_cost_accuracy": {
                "name": "shipping_cost_accuracy",
                "pg": {"type": "integer"},
                "es": {"type": "integer"},
            },
            "_source_table_.shipping_cost_source": {
                "name": "shipping_cost_source",
                "pg": {"type": "varchar(100)"},
                "es": {"type": "text"},
            },
            "_source_table_.warehouse_processing_fee": {
                "name": "warehouse_processing_fee",
                "pg": {"type": "numeric(6, 2)"},
                "es": {"type": "float"},
            },
            "_source_table_.warehouse_processing_fee_accuracy": {
                "name": "warehouse_processing_fee_accuracy",
                "pg": {"type": "integer"},
                "es": {"type": "integer"},
            },
            "_source_table_.ship_date": {
                "name": "item_ship_date",
                "pg": {"type": "timestamp with time zone"},
                "es": {"type": "date"},
            },
            "lateral_item_total_charge.total": {
                "name": "item_total_charged",
                "pg": {"type": "numeric(10, 2)"},
                "es": {"type": "float"},
            },
            "lateral_item_origin_total_cost.total": {
                "name": "item_total_cost",
                "pg": {"type": "numeric(10, 2)"},
                "es": {"type": "float"},
            },
            "lateral_item_profit.total": {
                "name": "item_profit",
                "pg": {"type": "numeric(10, 2)"},
                "es": {"type": "float"},
            },
            "lateral_item_margin.total": {
                "name": "item_margin",
                "pg": {"type": "numeric"},
                "es": {"type": "float"}
            },
            "joined_sale_status.value": {
                "name": "item_sale_status",
                "pg": {"type": "varchar(50)"},
                "es": {"type": "text"},
            },
            "joined_profit_status.value": {
                "name": "item_profit_status",
                "pg": {"type": "varchar(50)"},
                "es": {"type": "text"},
            },
            "_source_table_.channel_listing_fee": {
                "name": "item_channel_listing_fee",
                "pg": {"type": "numeric(6, 2)"},
                "es": {"type": "float"},
            },
            "_source_table_.channel_listing_fee_accuracy": {
                "name": "channel_listing_fee_accuracy",
                "pg": {"type": "integer"},
                "es": {"type": "integer"},
            },
            "_source_table_.other_channel_fees": {
                "name": "item_other_channel_fees",
                "pg": {"type": "numeric(6, 2)"},
                "es": {"type": "float"},
            },
            "_source_table_.reimbursement_costs": {
                "name": "item_reimbursement_costs",
                "pg": {"type": "numeric(6, 2)"},
                "es": {"type": "float"},
            },
            "joined_fulfillment_channel.name": {
                "name": "fulfillment_type",
                "pg": {"type": "varchar(45)"},
                "es": {"type": "text"},
            },
            "COALESCE(joined_appeagleprofile.profile_name, null)": {
                "name": "ae_profile_name",
                "pg": {"type": "varchar(500)"},
                "es": {"type": "text"},
            },
            "_source_table_.fulfillment_type_accuracy": {
                "name": "fulfillment_type_accuracy",
                "pg": {"type": "integer"},
                "es": {"type": "integer"},
            },
            "_source_table_.segment": {
                "name": "segment",
                "pg": {"type": "varchar(100)"},
                "es": {"type": "text"}
            },
            "_source_table_.freight_cost": {
                "name": "freight_cost",
                "pg": {"type": "numeric(6, 2)"},
                "es": {"type": "float"},
            },
            "_source_table_.freight_cost_accuracy": {
                "name": "freight_cost_accuracy",
                "pg": {"type": "integer"},
                "es": {"type": "integer"},
            },
            "_source_table_.channel_tax_withheld": {
                "name": "channel_tax_withheld",
                "pg": {"type": "numeric(6, 2)"},
                "es": {"type": "float"},
            },
            "_source_table_.channel_tax_withheld_accuracy": {
                "name": "channel_tax_withheld_accuracy",
                "pg": {"type": "integer"},
                "es": {"type": "integer"},
            },
            "_source_table_.refund_admin_fee": {
                "name": "refund_admin_fee",
                "pg": {"type": "numeric(6, 2)"},
                "es": {"type": "float"},
            },
            "_source_table_.tracking_fedex_id": {
                "name": "tracking_fedex_id",
                "pg": {"type": "varchar(100)"},
                "es": {"type": "text"},
            },
            "_source_table_.notes": {
                "name": "notes",
                "pg": {"type": "text"},
                "es": {"type": "text"}
            },
            "_source_table_.created": {
                "name": "created",
                "pg": {"type": "timestamp with time zone"},
                "es": {"type": "date"},
            },
            "_source_table_.modified": {
                "name": "modified",
                "pg": {"type": "timestamp with time zone"},
                "es": {"type": "date"},
            },
            "_source_table_.user_provided_cost": {
                "name": "user_provided_cost",
                "pg": {"type": "numeric(6, 2)"},
                "es": {"type": "float"},
            },
            "_source_table_.ship_carrier": {
                "name": "ship_carrier",
                "pg": {"type": "varchar(100)"},
                "es": {"type": "text"},
            },
            "_source_table_.estimated_shipping_cost": {
                "name": "estimated_shipping_cost",
                "pg": {"type": "numeric(6, 2)"},
                "es": {"type": "float"},
            },
            "_source_table_.actual_shipping_cost": {
                "name": "actual_shipping_cost",
                "pg": {"type": "numeric(6, 2)"},
                "es": {"type": "float"},
            },
            "_source_table_.inbound_freight_cost": {
                "name": "inbound_freight_cost",
                "pg": {"type": "numeric(6, 2)"},
                "es": {"type": "float"},
            },
            "_source_table_.inbound_freight_cost_accuracy": {
                "name": "inbound_freight_cost_accuracy",
                "pg": {"type": "integer"},
                "es": {"type": "long"},
            },
            "_source_table_.outbound_freight_cost": {
                "name": "outbound_freight_cost",
                "pg": {"type": "numeric(6, 2)"},
                "es": {"type": "float"},
            },
            "_source_table_.outbound_freight_cost_accuracy": {
                "name": "outbound_freight_cost_accuracy",
                "pg": {"type": "integer"},
                "es": {"type": "long"},
            },
            "_source_table_.product_number": {
                "name": "product_number",
                "pg": {"type": "varchar(255)"},
                "es": {"type": "text"},
            },
            "_source_table_.product_type": {
                "name": "product_type",
                "pg": {"type": "varchar(255)"},
                "es": {"type": "text"},
            },
            "_source_table_.parent_asin": {
                "name": "parent_asin",
                "pg": {"type": "varchar(255)"},
                "es": {"type": "text"},
            },
            "_source_table_.return_postage_billing": {
                "name": "return_postage_billing",
                "pg": {"type": "numeric(6, 2)"},
                "es": {"type": "float"},
            },
            "CONCAT(_source_table_.parent_asin, '-', _source_table_.asin)": {
                "name": "parent_child_asin",
                "pg": {"type": "varchar(255)"},
                "es": {"type": "text"},
            },
            "_source_table_.label_cost": {
                "name": "label_cost",
                "pg": {"type": "numeric(6, 2)"},
                "es": {"type": "float"},
            },
            "_source_table_.label_type": {
                "name": "label_type",
                "pg": {"type": "varchar(255)"},
                "es": {"type": "text"}
            },
            "_source_table_.cog_source": {
                "name": "cog_source",
                "pg": {"type": "varchar(100)"},
                "es": {"type": "text"}
            },
            "joined_sale.is_replacement_order": {
                "name": "is_replacement_order",
                "pg": {"type": "boolean"},
                "es": {"type": "boolean"}
            },
            "joined_sale.replaced_order_id": {
                "name": "replaced_order_id",
                "pg": {"type": "varchar(50)"},
                "es": {"type": "text"}
            }
        }

    def _select_statement_analysis(self, client_id: str):
        return """ , """.join(f"{k} AS {v['name']}" for k, v in self.config_statement_source.items())

    def build_properties_mapping_source(self, source_type: str):
        try:
            assert source_type in [FLATTEN_PG_SOURCE,
                                   FLATTEN_ES_SOURCE], "Source not incorrect"
            rs = {}
            for item in self.config_statement_source.values():
                rs.update(self._setup_column_mapping_source(source_type, item))
        except Exception as ex:
            logger.error(
                f"[{self.__class__.__name__}][build_properties_mapping_source] {ex}")
            rs = {}
        return rs

    def _setup_column_mapping_source(self, source_type: str, item: dict):
        _property_type = source_type.lower()
        _col_name = item["name"]
        _col_config = item[_property_type]
        try:
            assert (
                    source_type in FLATTEN_SOURCES_LIST
            ), f"Setup column mapping source only accept for {FLATTEN_SOURCES_LIST}"
            if _col_config["type"] == ES_TEXT_TYPE:
                _special_analyzer = {
                    "fields": ES_MAPPING_TYPE_FIELDS_CONFIG[_col_config["type"]],
                    "analyzer": "special_analyzer",
                }
                _col_config.update(_special_analyzer)
        except Exception as ex:
            logger.error(
                f"[{self.__class__.__name__}][_setup_column_mapping_source] {ex}")
        rs = {_col_name: _col_config}
        return rs

    def _build_base_filter_analysis_3rd_party(
            self, channel: str, sale_status: List[str], sale_dates: List[List[str]] = None, modified_from: str = None
    ):
        val = {
            "type": "AND",
            "conditions": [
                {"column": "channel_name", "operator": "$eq", "value": channel},
                {"column": "item_sale_status",
                 "operator": "in", "value": sale_status},
            ],
        }
        if sale_dates:
            if len(sale_dates) == 1:
                val["conditions"].append(
                    {"column": "sale_date", "operator": "$gte", "value": sale_dates[0][0]})
                val["conditions"].append(
                    {"column": "sale_date", "operator": "$lte", "value": sale_dates[0][1]})

            else:
                conditions_dates = []
                for sale_date in sale_dates:
                    conditions_dates.append(
                        {
                            "type": "AND",
                            "conditions": [
                                {"column": "sale_date",
                                 "value": sale_date[0], "operator": "$gte"},
                                {"column": "sale_date",
                                 "value": sale_date[1], "operator": "$lte"},
                            ],
                        }
                    )
                val["conditions"].append(
                    {"type": "OR", "conditions": conditions_dates})

        if modified_from:
            val["conditions"].append(
                {"column": "modified", "operator": "$gte", "value": modified_from})
        return val

    def _aggregate_analysis_3rd_party(
            self,
            analysis_3rd_party: DataSource,
            external_id: str,
            groups: Dict,
            fields: List[Dict] = None,
            query_type="exec",
            sale_dates: List[List[str]] = None,
            channel: str = None,
            sale_status: List[str] = None,
            conditions: List[Dict] = None,
            paging: Dict = None,
            modified_from: str = None,
            **kwargs,
    ):
        logger.debug(
            f"[{self.__class__.__name__}][_aggregate_analysis_3rd_party][{external_id}]" f"[{sale_dates}] Beginning ..."
        )
        if fields is None:
            fields = []
        if paging is None:
            paging = {"current": 1, "limit": 1000}
        if channel is None:
            channel = self.ds_channel_default
        if sale_status is None:
            sale_status = self.sale_status_accept_generate
        filter_cond = copy.deepcopy(
            self._build_base_filter_analysis_3rd_party(
                channel=channel,
                sale_status=sale_status,
                sale_dates=sale_dates,
                modified_from=modified_from,
            )
        )
        if conditions:
            filter_cond["conditions"] += conditions
        return analysis_3rd_party.call_query(
            external_id=external_id,
            fields=fields,
            group=groups,
            query_type=query_type,
            timezone=self.ds_tz_calculate,
            paging=paging,
            filter=filter_cond,
            **kwargs,
        )

    def reformat_data_source_type(
            self, table_name: str, index_fields: str, data: List[Union[str, Dict]], source_type: str
    ):
        # Construct SQL Query
        if source_type == FLATTEN_PG_SOURCE:
            if not data:
                # raise ValueError(
                #     f"[{self.__class__.__name__}][{table_name}][build_flat_query_insert_table] "
                #     f"Data not found"
                # )
                return """SELECT 1;"""

            set_statement = self.build_sql_do_update_set_by_conflict()
            data = f"""
                INSERT INTO {table_name} ({",".join(self.columns_update)}) 
                VALUES {",".join(data)}
                ON CONFLICT ({index_fields})
                DO UPDATE SET {set_statement};
            """
        return data
