from abc import ABC
from typing import List

from app.financial.sql_generator.flat_sql_schema_generator import FlatSchemaSQLGenerator
from app.financial.variable.sale_status_static_variable import SALE_REFUNDED_STATUS, SALE_CANCELLED_STATUS, \
    SALE_PARTIALLY_REFUNDED_STATUS, RETURN_REVERSED_STATUS


class FlatItemsSQLGenerator(FlatSchemaSQLGenerator, ABC):

    def _select_statement_analysis(self, client_id: str):
        client_id_db = client_id.replace("-", "_")
        return super()._select_statement_analysis(client_id).replace("_source_table_",
                                                                     f"financial_{client_id_db}_saleitem")

    def _build_reduce_sub_query(self, client_id: str, ids: List[str], **kwargs):
        client_id_db = client_id.replace("-", "_")
        _build_cond_query_sale_item = self._build_cond_query_sale_item(client_id, ids, **kwargs).replace(
            '_source_table_', f'financial_{client_id_db}_saleitem')
        query = f"""
        SELECT *
        FROM financial_{client_id_db}_saleitem
        WHERE {_build_cond_query_sale_item}
        {self._build_order_by_sql(client_id, **kwargs)}
        {self._build_limit_offset_by_sql(client_id, **kwargs)}
        """
        return query

    def _build_order_by_sql(self, client_id: str, **kwargs):
        if kwargs.get("order_by_query") is not None:
            return kwargs.get("order_by_query")
        client_id_db = client_id.replace("-", "_")
        return f""" ORDER BY financial_{client_id_db}_saleitem.created ASC """

    def _build_join_sql(self, client_id: str):
        client_id_db = client_id.replace("-", "_")
        query = f"""
        INNER JOIN financial_{client_id_db}_sale AS joined_sale ON joined_sale.id = financial_{client_id_db}_saleitem.sale_id
        INNER JOIN financial_channel AS joined_channel ON joined_channel.id = joined_sale.channel_id
        LEFT JOIN financial_brand AS joined_brand ON joined_brand.id = financial_{client_id_db}_saleitem.brand_id
        LEFT JOIN financial_variant AS joined_size ON joined_size.id = financial_{client_id_db}_saleitem.size_id
        LEFT JOIN financial_variant AS joined_style ON joined_style.id = financial_{client_id_db}_saleitem.style_id
        LEFT JOIN financial_salestatus AS joined_sale_status ON joined_sale_status.id = financial_{client_id_db}_saleitem.sale_status_id
        LEFT JOIN financial_profitstatus AS joined_profit_status ON joined_profit_status.id = financial_{client_id_db}_saleitem.profit_status_id
        LEFT JOIN financial_fulfillmentchannel AS joined_fulfillment_channel ON joined_fulfillment_channel.id = financial_{client_id_db}_saleitem.fulfillment_type_id
        LEFT JOIN financial_statepopulation AS joined_population ON joined_population.id = joined_sale.population_id
        LEFT JOIN financial_appeagleprofile AS joined_appeagleprofile ON joined_appeagleprofile.profile_id = financial_{client_id_db}_saleitem.strategy_id AND joined_appeagleprofile.client_id = financial_{client_id_db}_saleitem.client_id
        LEFT JOIN LATERAL(
            SELECT (
                COALESCE(financial_{client_id_db}_saleitem.sale_charged, 0) +
                COALESCE(financial_{client_id_db}_saleitem.shipping_charged, 0) +
                COALESCE(financial_{client_id_db}_saleitem.tax_charged, 0))::numeric(10, 2) AS total
            ) AS lateral_item_total_charge ON TRUE
        LEFT JOIN LATERAL (
                SELECT
                    CASE
                        WHEN joined_sale_status.value IN ('{SALE_REFUNDED_STATUS}') THEN 0
                        ELSE COALESCE(financial_{client_id_db}_saleitem.cog, 0)
                    END AS cog
        ) AS lateral_item_should_use_cog ON TRUE
        LEFT JOIN LATERAL(
            SELECT (
                    lateral_item_should_use_cog.cog +
                    COALESCE(financial_{client_id_db}_saleitem.shipping_cost, 0) +
                    COALESCE(financial_{client_id_db}_saleitem.warehouse_processing_fee, 0) +
                    COALESCE(financial_{client_id_db}_saleitem.channel_listing_fee, 0) +
                    COALESCE(financial_{client_id_db}_saleitem.reimbursement_costs, 0) +
                    COALESCE(financial_{client_id_db}_saleitem.other_channel_fees, 0) +
                    COALESCE(financial_{client_id_db}_saleitem.inbound_freight_cost, 0) +
                    COALESCE(financial_{client_id_db}_saleitem.outbound_freight_cost, 0) +
                    COALESCE(financial_{client_id_db}_saleitem.user_provided_cost, 0) +
                    COALESCE(financial_{client_id_db}_saleitem.refund_admin_fee, 0) +
                    COALESCE(financial_{client_id_db}_saleitem.return_postage_billing, 0)
                )::numeric(10, 2) AS total
            ) AS lateral_item_origin_total_cost ON TRUE
        LEFT JOIN LATERAL (
            SELECT
                    (
                        COALESCE(financial_{client_id_db}_saleitem.other_channel_fees, 0) +
                        COALESCE(financial_{client_id_db}_saleitem.reimbursement_costs, 0) +
                        COALESCE(financial_{client_id_db}_saleitem.refund_admin_fee, 0)
                    )::numeric(10, 2) AS total
            ) AS lateral_exclude_cost_profit ON TRUE
        LEFT JOIN LATERAL (
                SELECT
                    CASE
                        WHEN joined_sale_status.value IN ('{SALE_PARTIALLY_REFUNDED_STATUS}', '{SALE_REFUNDED_STATUS}', '{RETURN_REVERSED_STATUS}') THEN COALESCE(lateral_item_origin_total_cost.total, 0)
                        ELSE (COALESCE(lateral_item_origin_total_cost.total, 0) - COALESCE(lateral_exclude_cost_profit.total, 0))::numeric(10, 2)
                    END AS total
                ) AS lateral_item_total_cost_profit ON TRUE
        LEFT JOIN LATERAL (
                SELECT
                    CASE
                        WHEN joined_sale_status.value IN ('{SALE_CANCELLED_STATUS}') THEN COALESCE(financial_{client_id_db}_saleitem.total_financial_amount, 0)::numeric(10, 2)
                        ELSE (COALESCE(financial_{client_id_db}_saleitem.sale_charged, 0) - COALESCE(lateral_item_total_cost_profit.total, 0))::numeric(10, 2)
                    END AS total
            ) AS lateral_item_profit ON TRUE
        LEFT JOIN LATERAL (
                SELECT
                    CASE
                       WHEN joined_sale_status.value IN ('{SALE_CANCELLED_STATUS}') THEN NULL
                       WHEN COALESCE(financial_{client_id_db}_saleitem.sale_charged, 0) = 0 THEN 0
                       ELSE ROUND((lateral_item_profit.total / financial_{client_id_db}_saleitem.sale_charged) * 100, 2)::numeric(10, 2)
                    END AS total
                ) AS lateral_item_margin ON TRUE
        LEFT JOIN LATERAL (
                SELECT
                    CASE
                        WHEN joined_population IS NULL OR joined_population.est = 0
                            THEN 0
                        ELSE financial_{client_id_db}_saleitem.quantity::numeric / (joined_population.est::numeric / 1000000)
                    END AS value
                ) AS lateral_spmr ON TRUE
        """
        return query

    def build_flat_query(self, client_id: str = None, ids: List[str] = None, **kwargs) -> str:
        client_id_db = client_id.replace("-", "_")
        return super().build_flat_query(client_id, ids, **kwargs).replace("_source_table_",
                                                                          f"financial_{client_id_db}_saleitem")

    def build_query_for_number_sync_rows(self, client_id, is_resync: bool = False, **kwargs):
        """
        build a query for counting the number of dirty rows in the original table
        :return:
        """
        client_id_db = client_id.replace("-", "_")
        cond = f"""dirty = TRUE"""
        if is_resync:
            cond = f"""
                dirty = FALSE AND resync = TRUE
            """

        query = f"""
        SELECT COUNT(*)
        FROM financial_{client_id_db}_saleitem
        WHERE {cond};
        """
        return query

    def build_query_for_number_flatten_rows(self, table_flatten):
        """
        build a query for counting the number of tables flatten
        :return:
        """
        query = f"""
        SELECT COUNT(*)
        FROM {table_flatten};"""
        return query

    def build_revert_dirty_query(self, client_id: str = None, ids: List[str] = None, modified_at: str = None,
                                 is_resync: bool = False, **kwargs) -> str:
        """
        build a query to revert a dirty flag in the original table
        :param ids:
        :param client_id:
        :param modified_at:
        :param is_resync:
        :return:
        """
        client_id_db = client_id.replace("-", "_")
        cond = f"""dirty = TRUE"""
        set_values = f"""dirty = FALSE , resync = FALSE"""

        if is_resync:
            cond = f"""dirty = FALSE AND resync = TRUE"""
            set_values = f"""resync = FALSE"""

        if modified_at is not None:
            cond += f" AND modified <= '{modified_at}'::timestamptz"

        if bool(ids):
            ids = tuple(ids) if len(ids) > 1 else f"""('{ids[0]}')"""
            cond += f" AND id IN {ids}"

        sql = f"""
            UPDATE financial_{client_id_db}_saleitem
            SET {set_values}
            WHERE {cond}
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
