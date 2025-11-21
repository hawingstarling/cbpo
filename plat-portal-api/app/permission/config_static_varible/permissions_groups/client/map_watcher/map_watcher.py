MODULE_MAP_KEY = "MAP"
MODULE_MAP_NAME = "MAP Watcher"

MW_REPORT_GROUP_KEY = "MW_REPORT_GROUP"
MW_REPORT_GROUP_NAME = "Report"

MW_REPORT_GROUP_ENUM = (MW_REPORT_GROUP_KEY, MW_REPORT_GROUP_NAME)

MAP_BRAND_MANAGEMENT_KEY = "BRAMAN"
MAP_BRAND_EXECUTION_KEY = "BRAEXE"

MW_PRICE_GROUP_KEY = "MW_PRICE_GROUP"
MW_PRICE_GROUP_NAME = "Price"

MW_PRICE_GROUP_ENUM = (MW_PRICE_GROUP_KEY, MW_PRICE_GROUP_NAME)

MAP_MANAGEMENT_KEY = "MAPMAN"
MAP_EMAIL_NOTIFICATION_KEY = "NOTIFI"
MAP_GG_SHOPPING_MANAGEMENT_KEY = "GSMAPMAN"
MAP_WALMART_MANAGEMENT_KEY = "WALMARTMAN"

MW_SI_GROUP_KEY = "MW_SI_GROUP"
MW_SI_GROUP_NAME = "Sellers & Investigations"

MW_SI_GROUP_ENUM = (MW_SI_GROUP_KEY, MW_SI_GROUP_NAME)

MAP_SI_VIEW_KEY = "SIVIEW"
MAP_SI_MANAGEMENT_KEY = "SIMAN"

MW_DASHBOARD_GROUP_KEY = "MW_DASHBOARD_GROUP"
MW_DASHBOARD_GROUP_NAME = "Dashboards"

MW_DASHBOARD_GROUP_ENUM = (MW_DASHBOARD_GROUP_KEY, MW_DASHBOARD_GROUP_NAME)

MAP_DASHBOARD_MANAGEMENT_KEY = "DASMAN"

MW_ADMIN_GROUP_KEY = "MW_ADMIN_GROUP"
MW_ADMIN_GROUP_NAME = "Administration"

MW_ADMIN_GROUP_ENUM = (MW_ADMIN_GROUP_KEY, MW_ADMIN_GROUP_NAME)

MAP_ADMIN_MANAGEMENT_KEY = "ADMINMAN"

MW_SALE_ENFORCEMENT_GROUP_KEY = "MW_SALE_ENFORCEMENT_GROUP"
MW_SALE_ENFORCEMENT_GROUP_NAME = "Sale Enforcement"
MW_SALE_ENFORCEMENT_GROUP_ENUM = (
    MW_SALE_ENFORCEMENT_GROUP_KEY,
    MW_SALE_ENFORCEMENT_GROUP_NAME,
)

MW_SALE_ENFORCEMENT_CREATE = "se_create"
MW_SALE_ENFORCEMENT_EDIT = "se_edit"
MW_SALE_ENFORCEMENT_VIEW = "se_view"
MW_SALE_ENFORCEMENT_DELETE = "se_delete"
MW_SALE_ENFORCEMENT_SEND = "se_send"

permission_module_map_watcher_config = {
    MW_REPORT_GROUP_KEY: {
        "name": MW_REPORT_GROUP_NAME,
        "module": MODULE_MAP_KEY,
        "permissions": [
            {"key": MAP_BRAND_MANAGEMENT_KEY, "name": "Management"},
            {"key": MAP_BRAND_EXECUTION_KEY, "name": "Execution"},
        ],
    },
    MW_PRICE_GROUP_KEY: {
        "name": MW_PRICE_GROUP_NAME,
        "module": MODULE_MAP_KEY,
        "permissions": [
            {"key": MAP_MANAGEMENT_KEY, "name": "Management"},
            {
                "key": MAP_GG_SHOPPING_MANAGEMENT_KEY,
                "name": "Google Shopping Management",
            },
            {
                "key": MAP_EMAIL_NOTIFICATION_KEY,
                "name": "MAP Price Update Notification",
            },
            {
                "key": MAP_WALMART_MANAGEMENT_KEY,
                "name": "Walmart Management",
            },
        ],
    },
    MW_SI_GROUP_KEY: {
        "name": MW_SI_GROUP_NAME,
        "module": MODULE_MAP_KEY,
        "permissions": [
            {"key": MAP_SI_VIEW_KEY, "name": "View"},
            {"key": MAP_SI_MANAGEMENT_KEY, "name": "Management"},
        ],
    },
    MW_DASHBOARD_GROUP_KEY: {
        "name": MW_DASHBOARD_GROUP_NAME,
        "module": MODULE_MAP_KEY,
        "permissions": [{"key": MAP_DASHBOARD_MANAGEMENT_KEY, "name": "Management"}],
    },
    MW_ADMIN_GROUP_KEY: {
        "name": MW_ADMIN_GROUP_NAME,
        "module": MODULE_MAP_KEY,
        "permissions": [{"key": MAP_ADMIN_MANAGEMENT_KEY, "name": "Management"}],
    },
    MW_SALE_ENFORCEMENT_GROUP_KEY: {
        "name": MW_SALE_ENFORCEMENT_GROUP_NAME,
        "module": MODULE_MAP_KEY,
        "permissions": [
            {"key": MW_SALE_ENFORCEMENT_CREATE, "name": "Create"},
            {"key": MW_SALE_ENFORCEMENT_EDIT, "name": "Edit"},
            {"key": MW_SALE_ENFORCEMENT_VIEW, "name": "View"},
            {"key": MW_SALE_ENFORCEMENT_DELETE, "name": "Delete"},
            {"key": MW_SALE_ENFORCEMENT_SEND, "name": "Send"},
        ],
    },
}
