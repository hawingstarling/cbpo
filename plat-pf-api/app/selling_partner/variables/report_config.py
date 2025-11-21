REPORT_CATEGORIES_CONFIG = [
    {
        "categories": "Orders",
        "categories_value": "ORDER",
        "types": [
            {
                "name": "New Orders",
                "value": "GET_FLAT_FILE_ALL_ORDERS_DATA_BY_ORDER_DATE_GENERAL",
                "note": "Last 15 days usually"
            },
            {
                "name": "Unshipped Orders",
                "value": "GET_FLAT_FILE_ACTIONABLE_ORDER_DATA_SHIPPING",
                "note": None
            }
        ]
    },
    {
        "categories": "Payments",
        "categories_value": "PAYMENT",
        "types": [
            {
                "name": "Date Range Reports - Custom Unified Transaction Report",
                "value": "GET_V2_SETTLEMENT_REPORT_DATA_FLAT_FILE_V2",
                "is_date_range": False,
                "note": "Previous Month's Date Range"
            },
            {
                "name": "Reimbursements",
                "value": "GET_FBA_REIMBURSEMENTS_DATA",
                "note": "FBA only"
            }
        ]
    },
    {
        "categories": "Fulfillments",
        "categories_value": "FULFILLMENT",
        "sub_categories": [
            {
                "name": "Inventory",
                "value": "FULFILLMENT_INVENTORY",
                "types": [
                    {
                        "name": "Inventory Ledger - Detailed View",
                        "value": "GET_LEDGER_DETAIL_VIEW_DATA",
                        "note": None
                    },
                    {
                        "name": "Inventory Ledger - Summary view",
                        "value": "GET_LEDGER_SUMMARY_VIEW_DATA",
                        "note": None
                    },
                    {
                        "name": "Amazon Fulfilled Inventory",
                        "value": "GET_AFN_INVENTORY_DATA",
                        "note": None
                    },
                    {
                        "name": "Monthly Inventory History",
                        "value": "GET_LEDGER_DETAIL_VIEW_DATA",
                        "note": None
                    },
                    {
                        "name": "Inventory Event Detail",
                        "value": "GET_LEDGER_SUMMARY_VIEW_DATA",
                        "note": None
                    },
                    {
                        "name": "Inventory Adjustments",
                        "value": "GET_LEDGER_DETAIL_VIEW_DATA",
                        "meta": {
                            "payload_optional": {
                                "request_options": {
                                    "eventType": "Adjustments"
                                }
                            }
                        },
                        "note": None
                    },
                    {
                        "name": "Received Inventory",
                        "value": "GET_LEDGER_DETAIL_VIEW_DATA",
                        "meta": {
                            "payload_optional": {
                                "request_options": {
                                    "eventType": "Receipts"
                                }
                            }
                        },
                        "note": None
                    },
                    {
                        "name": "Manage FBA Inventory",
                        "value": "GET_FBA_MYI_UNSUPPRESSED_INVENTORY_DATA",
                        "note": None
                    },
                    {
                        "name": "Inbound Performance",
                        "value": "GET_FBA_FULFILLMENT_INBOUND_NONCOMPLIANCE_DATA",
                        "note": None
                    }
                ]
            },
            {
                "name": "Customer Concessions",
                "value": "FULFILLMENT_CUSTOMER_CONCESSION",
                "types": [
                    {
                        "name": "FBA customer returns",
                        "value": "GET_FBA_FULFILLMENT_CUSTOMER_RETURNS_DATA",
                        "note": None
                    }
                ]
            },
            {
                "name": "Removals",
                "value": "FULFILLMENT_REMOVAL",
                "types": [
                    {
                        "name": "Removal Order Detail",
                        "value": "GET_FBA_FULFILLMENT_REMOVAL_ORDER_DETAIL_DATA",
                        "note": None
                    },
                    {
                        "name": "Removal Shipment Detail",
                        "value": "GET_FBA_FULFILLMENT_REMOVAL_SHIPMENT_DETAIL_DATA",
                        "note": None
                    }
                ]
            }
        ]
    },
    {
        "categories": "Inventory",
        "categories_value": "INVENTORY",
        "types": [
            {
                "name": "Inventory Report",
                "value": "GET_FLAT_FILE_OPEN_LISTINGS_DATA",
                "note": None
            },
            {
                "name": "All Listings Report (Custom)",
                "value": "GET_MERCHANT_LISTINGS_ALL_DATA",
                "note": None
            },
            {
                "name": "Active Listings Report (Custom)",
                "value": "GET_MERCHANT_LISTINGS_DATA",
                "note": None
            }
        ]
    },
    {
        "categories": "Brands Summary Data Report",
        "categories_value": "BRANDS_SUMMARY_DATA_REPORT",
        "types": [
            {
                "name": "Brands Summary Monthly Data Report",
                "value": "BRANDS_SUMMARY_MONTHLY_DATA_REPORT",
                "note": "Auto-generate a monthly Summary Data report for "
                        "all the brands in Precise every 15th of the month.",
                "source": "LOCAL"
            }
        ]
    }
]
