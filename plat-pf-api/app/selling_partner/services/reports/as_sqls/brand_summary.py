from app.core.variable.marketplace import CHANNEL_DEFAULT
from app.financial.variable.sale_status_static_variable import SALE_PARTIALLY_REFUNDED_STATUS, SALE_REFUNDED_STATUS, \
    RETURN_REVERSED_STATUS, SALE_CANCELLED_STATUS

SQL_PLAINTEXT = f"""
SELECT 
  "financial_brand"."name" AS "brand__name", 
  SUM(
    COALESCE(
      "financial_$CLIENT_ID_DB$_saleitem"."sale_charged", 
      0
    )
  ):: numeric(10, 2) AS "sum_sale_charged", 
  SUM(
    COALESCE(
      "financial_$CLIENT_ID_DB$_saleitem"."cog", 
      0
    )
  ):: numeric(10, 2) AS "sum_cog", 
  SUM(
    COALESCE(
      "financial_$CLIENT_ID_DB$_saleitem"."actual_shipping_cost", 
      0
    )
  ):: numeric(10, 2) AS "sum_actual_shipping_cost", 
  SUM(
    COALESCE(
      "financial_$CLIENT_ID_DB$_saleitem"."estimated_shipping_cost", 
      0
    )
  ):: numeric(10, 2) AS "sum_estimated_shipping_cost", 
  SUM(lateral_item_profit.total):: numeric(10, 2) AS "sum_profit", 
  CASE WHEN SUM(
    COALESCE(
      "financial_$CLIENT_ID_DB$_saleitem"."sale_charged", 
      0
    )
  ) = 0 THEN 0.00 ELSE (
    (
      SUM(lateral_item_profit.total) / SUM(
        "financial_$CLIENT_ID_DB$_saleitem".sale_charged
      )
    )
  ) END AS "sum_margin" 
FROM 
  "financial_$CLIENT_ID_DB$_saleitem" 
  INNER JOIN "financial_brand" ON "financial_$CLIENT_ID_DB$_saleitem"."brand_id" = "financial_brand"."id" 
  LEFT OUTER JOIN "financial_salestatus" ON "financial_$CLIENT_ID_DB$_saleitem"."sale_status_id" = "financial_salestatus"."id" 
  LEFT JOIN "financial_$CLIENT_ID_DB$_sale" ON "financial_$CLIENT_ID_DB$_saleitem"."sale_id" = "financial_$CLIENT_ID_DB$_sale"."id" 
  LEFT JOIN "financial_channel" ON "financial_$CLIENT_ID_DB$_sale"."channel_id" = "financial_channel"."id" 
  LEFT JOIN LATERAL (
    SELECT 
      CASE WHEN "financial_salestatus".value IN ('{SALE_REFUNDED_STATUS}') THEN 0 ELSE COALESCE(
        "financial_$CLIENT_ID_DB$_saleitem".cog, 
        0
      ) END AS cog
  ) AS lateral_item_should_use_cog ON TRUE 
  LEFT JOIN LATERAL (
    SELECT 
      (
        "lateral_item_should_use_cog".cog + COALESCE(
          "financial_$CLIENT_ID_DB$_saleitem".shipping_cost, 
          0
        ) + COALESCE(
          "financial_$CLIENT_ID_DB$_saleitem".warehouse_processing_fee, 
          0
        ) + COALESCE(
          "financial_$CLIENT_ID_DB$_saleitem".channel_listing_fee, 
          0
        ) + COALESCE(
          "financial_$CLIENT_ID_DB$_saleitem".freight_cost, 
          0
        ) + COALESCE(
          "financial_$CLIENT_ID_DB$_saleitem".user_provided_cost, 
          0
        )
      ):: numeric(10, 2) AS total
  ) AS lateral_item_origin_total_cost ON TRUE 
  LEFT JOIN LATERAL (
    SELECT 
      (
        COALESCE(
          "financial_$CLIENT_ID_DB$_saleitem".other_channel_fees, 
          0
        ) + COALESCE(
          "financial_$CLIENT_ID_DB$_saleitem".reimbursement_costs, 
          0
        ) + COALESCE(
          "financial_$CLIENT_ID_DB$_saleitem".refund_admin_fee, 
          0
        )
      ):: numeric(10, 2) AS total
  ) AS lateral_reversed_cost_profit ON TRUE 
  LEFT JOIN LATERAL (
    SELECT 
      CASE WHEN "financial_salestatus".value NOT IN (
        '{SALE_PARTIALLY_REFUNDED_STATUS}', '{SALE_REFUNDED_STATUS}', '{RETURN_REVERSED_STATUS}'
      ) THEN COALESCE(
        "lateral_item_origin_total_cost".total, 
        0
      ) ELSE (
        COALESCE(
          "lateral_item_origin_total_cost".total, 
          0
        ) + COALESCE(
          "lateral_reversed_cost_profit".total, 
          0
        )
      ):: numeric(10, 2) END AS total
  ) AS lateral_item_total_cost_profit ON TRUE 
  LEFT JOIN LATERAL (
    SELECT 
      CASE WHEN "financial_salestatus".value IN ('{SALE_CANCELLED_STATUS}') THEN COALESCE(
        "financial_$CLIENT_ID_DB$_saleitem".total_financial_amount, 
        0
      ):: numeric(10, 2) ELSE (
        COALESCE(
          "financial_$CLIENT_ID_DB$_saleitem".sale_charged, 
          0
        ) - COALESCE(
          "lateral_item_total_cost_profit".total, 
          0
        )
      ):: numeric(10, 2) END AS total
  ) AS lateral_item_profit ON TRUE 
WHERE 
  NOT "financial_$CLIENT_ID_DB$_saleitem"."is_removed" 
  AND "financial_channel".name = '{CHANNEL_DEFAULT}' 
  AND "financial_$CLIENT_ID_DB$_saleitem"."brand_id" IS NOT NULL 
  AND "financial_$CLIENT_ID_DB$_saleitem"."sale_date" >= '$SALE_DATE_FROM$' 
  AND "financial_$CLIENT_ID_DB$_saleitem"."sale_date" <= '$SALE_DATE_TO$'
  AND "financial_salestatus"."value" IN $SALE_STATUS_ORDERS$ 
GROUP BY 
  "financial_brand"."name" 
ORDER BY 
  "financial_brand"."name"
"""
