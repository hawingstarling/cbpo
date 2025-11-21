MODULE_DC_KEY = 'DC'
MODULE_DC_NAME = 'Data Central'

#  ASIN
DC_ASIN_GROUP_KEY = 'ASIN_GROUP'
DC_ASIN_GROUP_NAME = 'ASIN'

DC_ASIN_GROUP_ENUM = (DC_ASIN_GROUP_KEY, DC_ASIN_GROUP_NAME)

DC_ASIN_VIEW_KEY = 'dc_asin_view'
DC_ASIN_EDIT_KEY = 'dc_asin_edit'
DC_ASIN_BULK_EDIT_KEY = 'dc_asin_edit_bulk'
DC_ASIN_IMPORT_KEY = 'dc_asin_import'

#  BRAND
DC_BRAND_GROUP_KEY = 'BRAND_GROUP'
DC_BRAND_GROUP_NAME = 'Brand'

DC_BRAND_GROUP_ENUM = (DC_BRAND_GROUP_KEY, DC_BRAND_GROUP_NAME)

DC_BRAND_VIEW_KEY = 'dc_brand_view'
DC_BRAND_EXPORT_KEY = 'dc_brand_export'
DC_BRAND_EDIT_KEY = 'dc_brand_edit'

#  DD REPORT
DC_DD_REPORT_GROUP_KEY = 'DD_REPORT_GROUP'
DC_DD_REPORT_GROUP_NAME = 'Demand Data Report'

DC_DD_REPORT_GROUP_ENUM = (DC_DD_REPORT_GROUP_KEY, DC_DD_REPORT_GROUP_NAME)

DC_DD_REPORT_VIEW_KEY = 'dc_dd_report_view'
DC_DD_REPORT_MANAGEMENT_KEY = 'dc_dd_report_man'

#  PO
DC_PO_GROUP_KEY = 'PO_GROUP'
DC_PO_GROUP_NAME = 'Purchase Order'

DC_PO_GROUP_ENUM = (DC_PO_GROUP_KEY, DC_PO_GROUP_NAME)

DC_PO_VIEW_KEY = 'dc_po_view'
DC_PO_MANAGEMENT_KEY = 'dc_po_man'

# Product Review
DC_PRODUCT_REVIEW_GROUP_KEY = 'PRODUCT_REVIEW_GROUP'
DC_PRODUCT_REVIEW_GROUP_NAME = 'Product Reviews'

DC_PRODUCT_REVIEW_GROUP_ENUM = (DC_PRODUCT_REVIEW_GROUP_KEY, DC_PRODUCT_REVIEW_GROUP_NAME)

DC_PRODUCT_REVIEW_VIEW_KEY = 'dc_pr_view'

# Profile
DC_PROFILE_GROUP_KEY = 'PROFILE_GROUP'
DC_PROFILE_GROUP_NAME = 'Profiles'

DC_PROFILE_GROUP_ENUM = (DC_PROFILE_GROUP_KEY, DC_PROFILE_GROUP_NAME)

DC_PROFILE_VIEW_KEY = 'dc_profile_view'
DC_PROFILE_MANAGEMENT_KEY = 'dc_profile_man'

# Inventory
DC_INV_GROUP_KEY = 'INVENTORY_GROUP'
DC_INV_GROUP_NAME = 'Inventory'

DC_INV_GROUP_ENUM = (DC_INV_GROUP_KEY, DC_INV_GROUP_NAME)

DC_INV_SELLER_VIEW_KEY = 'dc_inv_sellers_view'
DC_INV_SELLER_MANAGEMENT_KEY = 'dc_inv_sellers_man'
DC_INV_SUMMARY_VIEW_KEY = 'dc_inv_summary_view'

# Administration
DC_ADMIN_GROUP_KEY = 'DC_ADMIN_GROUP'
DC_ADMIN_GROUP_NAME = 'Administration'

DC_ADMIN_GROUP_ENUM = (DC_ADMIN_GROUP_KEY, DC_ADMIN_GROUP_NAME)

DC_ADMIN_CLIENT_MANAGEMENT_KEY = 'dc_client_man'
DC_ADMIN_SETTING_MANAGEMENT_KEY = 'dc_settings_man'
DC_ADMIN_SYSTEM_MONITOR_KEY = 'dc_sys_monitor'
DC_ADMIN_INDEXING_TOOL_KEY = 'dc_tool_index_man'

permission_module_dc_config = {
    DC_ASIN_GROUP_KEY: {
        'name': DC_ASIN_GROUP_NAME,
        'module': MODULE_DC_KEY,
        'permissions': [
            {
                'key': DC_ASIN_VIEW_KEY,
                'name': 'View'
            },
            {
                'key': DC_ASIN_EDIT_KEY,
                'name': 'Edit'
            },
            {
                'key': DC_ASIN_BULK_EDIT_KEY,
                'name': 'Bulk Edit'
            },
            {
                'key': DC_ASIN_IMPORT_KEY,
                'name': 'Import'
            },
        ]
    },
    DC_BRAND_GROUP_KEY: {
        'name': DC_BRAND_GROUP_NAME,
        'module': MODULE_DC_KEY,
        'permissions': [
            {
                'key': DC_BRAND_VIEW_KEY,
                'name': 'View'
            },
            {
                'key': DC_BRAND_EXPORT_KEY,
                'name': 'Export'
            },
            {
                'key': DC_BRAND_EDIT_KEY,
                'name': 'Bulk Edit'
            },
        ]
    },
    DC_DD_REPORT_GROUP_KEY: {
        'name': DC_DD_REPORT_GROUP_NAME,
        'module': MODULE_DC_KEY,
        'permissions': [
            {
                'key': DC_DD_REPORT_VIEW_KEY,
                'name': 'View'
            },
            {
                'key': DC_DD_REPORT_MANAGEMENT_KEY,
                'name': 'Management'
            },
        ]
    },
    DC_PO_GROUP_KEY: {
        'name': DC_PO_GROUP_NAME,
        'module': MODULE_DC_KEY,
        'permissions': [
            {
                'key': DC_PO_VIEW_KEY,
                'name': 'View'
            },
            {
                'key': DC_PO_MANAGEMENT_KEY,
                'name': 'Management'
            },
        ]
    },
    DC_PRODUCT_REVIEW_GROUP_KEY: {
        'name': DC_PRODUCT_REVIEW_GROUP_ENUM,
        'module': MODULE_DC_KEY,
        'permissions': [
            {
                'key': DC_PRODUCT_REVIEW_VIEW_KEY,
                'name': 'View'
            }
        ]
    },
    DC_INV_GROUP_KEY: {
        'name': DC_INV_GROUP_NAME,
        'module': MODULE_DC_KEY,
        'permissions': [
            {
                'key': DC_INV_SELLER_VIEW_KEY,
                'name': 'Seller View'
            },
            {
                'key': DC_INV_SELLER_MANAGEMENT_KEY,
                'name': 'Seller Management'
            },
            {
                'key': DC_INV_SUMMARY_VIEW_KEY,
                'name': 'Summary View'
            }
        ]
    },
    DC_PROFILE_GROUP_KEY: {
        'name': DC_PROFILE_GROUP_NAME,
        'module': MODULE_DC_KEY,
        'permissions': [
            {
                'key': DC_PROFILE_VIEW_KEY,
                'name': 'View'
            },
            {
                'key': DC_PROFILE_MANAGEMENT_KEY,
                'name': 'Management'
            }
        ]
    },
    DC_ADMIN_GROUP_KEY: {
        'name': DC_ADMIN_GROUP_NAME,
        'module': MODULE_DC_KEY,
        'permissions': [
            {
                'key': DC_ADMIN_CLIENT_MANAGEMENT_KEY,
                'name': 'Client Management'
            },
            {
                'key': DC_ADMIN_SETTING_MANAGEMENT_KEY,
                'name': 'Setting Management'
            },
            {
                'key': DC_ADMIN_SYSTEM_MONITOR_KEY,
                'name': 'System Monitor'
            },
            {
                'key': DC_ADMIN_INDEXING_TOOL_KEY,
                'name': 'Indexing Tool'
            }
        ]
    }
}
