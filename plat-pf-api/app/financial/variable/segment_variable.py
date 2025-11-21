from app.financial.variable.fulfillment_type import FULFILLMENT_FBA, FULFILLMENT_MFN_DS, FULFILLMENT_MFN_RA, \
    FULFILLMENT_MFN
from app.financial.variable.sale_status_static_variable import SALE_PARTIALLY_REFUNDED_STATUS, SALE_PENDING_STATUS, \
    SALE_SHIPPED_STATUS, SALE_UNSHIPPED_STATUS

DIVISION_CATEGORY = 'divisions'
OVERALL_SALES_CATEGORY = 'overall-sales'

SEGMENT_CATEGORY = (
    (
        DIVISION_CATEGORY,
        'Divisions'
    ),
    (
        OVERALL_SALES_CATEGORY,
        'Overall Sales'
    ),
)

SEGMENT_CATEGORY_LIST = [item[0] for item in SEGMENT_CATEGORY]

MANUAL_SYNC_OPTION = 'Manual'
HISTORICAL_SYNC_OPTION = 'Historical'

SYNC_OPTION_CHOICES = (
    (
        MANUAL_SYNC_OPTION,
        MANUAL_SYNC_OPTION
    ),
    (
        HISTORICAL_SYNC_OPTION,
        HISTORICAL_SYNC_OPTION
    ),
)

OVERALL_SALES_CALCULATE_DEFAULT = {
    "Dropship-Sales": {
        "fulfillment_type": [FULFILLMENT_MFN_DS, FULFILLMENT_MFN_RA],
        "field_aggregate": "item_sale_charged"
    },
    "Total-Sales": {
        "fulfillment_type": [FULFILLMENT_FBA, FULFILLMENT_MFN, FULFILLMENT_MFN_DS, FULFILLMENT_MFN_RA],
        "field_aggregate": "item_sale_charged"
    },
    "Total-Units-Sold": {
        "fulfillment_type": [FULFILLMENT_FBA, FULFILLMENT_MFN, FULFILLMENT_MFN_DS, FULFILLMENT_MFN_RA],
        "field_aggregate": "quantity"
    },
    "FBA-Sales": {
        "fulfillment_type": [FULFILLMENT_FBA],
        "field_aggregate": "item_sale_charged"
    },
    "MFN": {
        "fulfillment_type": [FULFILLMENT_MFN],
        "field_aggregate": "item_sale_charged"
    }
}

DIVISION_CONFIG_CALCULATE_DEFAULT = {
    "mtd_current": {
        "field_aggregate": "item_sale_charged",
        "sale_status": [SALE_SHIPPED_STATUS],
        "aggregation": "sum"
    },
    "mtd_target": {
        "field_aggregate": "item_sale_charged",
        "sale_status": [SALE_SHIPPED_STATUS],
        "aggregation": "sum"
    },
    "mtd_max": {
        "field_aggregate": "item_sale_charged",
        "sale_status": [SALE_SHIPPED_STATUS],
        "aggregation": "sum"
    },
    "ytd_current": {
        "field_aggregate": "item_sale_charged",
        "sale_status": [SALE_SHIPPED_STATUS],
        "aggregation": "sum"
    },
    "ytd_target": {
        "field_aggregate": "item_sale_charged",
        "sale_status": [SALE_SHIPPED_STATUS],
        "aggregation": "sum"
    },
    "ytd_max": {
        "field_aggregate": "item_sale_charged",
        "sale_status": [SALE_SHIPPED_STATUS],
        "aggregation": "sum"
    },
    "total_quantity": {
        "field_aggregate": "quantity",
        "sale_status": [SALE_SHIPPED_STATUS],
        "aggregation": "sum"
    }
}
