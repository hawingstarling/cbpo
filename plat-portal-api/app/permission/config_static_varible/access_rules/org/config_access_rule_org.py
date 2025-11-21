from app.permission.config_static_varible.common import (
    get_all_permissions_groups_from_module_config,
    ROLE_ADMIN_KEY,
    ROLE_STAFF_KEY,
    STATUS_PERMISSION_ALLOW_KEY,
    STATUS_PERMISSION_DENY_KEY,
)
from app.permission.config_static_varible.config import (
    PERMISSIONS_GROUPS_CONFIG_CLIENT_LEVEL,
)
from app.permission.config_static_varible.permissions_groups.client.data_central.data_central import (
    DC_ASIN_GROUP_KEY,
    DC_ASIN_VIEW_KEY,
    DC_BRAND_GROUP_KEY,
    DC_BRAND_VIEW_KEY,
    DC_DD_REPORT_GROUP_KEY,
    DC_DD_REPORT_VIEW_KEY,
    DC_PO_GROUP_KEY,
    DC_PO_VIEW_KEY,
)
from app.permission.config_static_varible.permissions_groups.client.data_sources.data_sources import (
    DS_GROUP_KEY,
)
from app.permission.config_static_varible.permissions_groups.client.map_watcher.map_watcher import (
    MW_REPORT_GROUP_KEY,
    MW_PRICE_GROUP_KEY,
    MW_SI_GROUP_KEY,
    MW_DASHBOARD_GROUP_KEY,
    MW_ADMIN_GROUP_KEY,
    MAP_EMAIL_NOTIFICATION_KEY,
)
from app.permission.config_static_varible.permissions_groups.client.matrix.matrix import (
    MT_OVERVIEW_GROUP_KEY,
    MT_OVERVIEW_VIEW_KEY,
    MT_CUSTOM_DASHBOARD_VIEW_KEY,
    # MT_OA_GROUP_KEY,
    # MT_OPERATIONAL_ANALYTICS_VIEW_KEY,
    # MT_PL_GROUP_KEY,
    # MT_PRODUCT_LISTING_VIEW_KEY,
    # MT_MP_GROUP_KEY,
    # MT_MARKETING_PERFORMANCE_VIEW_KEY,
    # MT_CM_GROUP_KEY,
    # MT_CATEGORY_MARKET_SHARE_VIEW_KEY,
    MT_ADMIN_GROUP_KEY,
    MT_ADVERTISING_GROUP_KEY,
    MT_ADVERTISING_VIEW_KEY,
    MT_CD_GROUP_KEY,
)
from app.permission.config_static_varible.permissions_groups.client.pf.precise_financial import (
    SALE_GROUP_KEY,
    SALE_VIEW_24H,
    FILTER_GROUP_KEY,
    SALE_REPORT_VIEW_FILTER,
    COLUMN_SET_GROUP_KEY,
    SALE_REPORT_VIEW_COLUMN,
    VIEW_GROUP_KEY,
)
from app.permission.config_static_varible.permissions_groups.client.report_application.report_application import (
    RA_DASHBOARD_GROUP_KEY,
    RA_VISUALIZATION_GROUP_KEY,
)

access_rule_org_system_default_created = {
    ROLE_ADMIN_KEY: {
        "name": "Full Access Rule",
        #  TODO: change to PERMISSIONS_GROUPS_CONFIG_ORG_LEVEL
        "permissions_groups": get_all_permissions_groups_from_module_config(
            module_config=PERMISSIONS_GROUPS_CONFIG_CLIENT_LEVEL,
            priority_config_dict={
                MAP_EMAIL_NOTIFICATION_KEY: STATUS_PERMISSION_DENY_KEY
            },
        ),
    },
    ROLE_STAFF_KEY: {
        "name": "Read Only Access Rule",
        "permissions_groups": {
            DC_ASIN_GROUP_KEY: [
                {"key": DC_ASIN_VIEW_KEY, "status": STATUS_PERMISSION_ALLOW_KEY}
            ],
            DC_BRAND_GROUP_KEY: [
                {"key": DC_BRAND_VIEW_KEY, "status": STATUS_PERMISSION_ALLOW_KEY}
            ],
            DC_DD_REPORT_GROUP_KEY: [
                {"key": DC_DD_REPORT_VIEW_KEY, "status": STATUS_PERMISSION_ALLOW_KEY}
            ],
            DC_PO_GROUP_KEY: [
                {"key": DC_PO_VIEW_KEY, "status": STATUS_PERMISSION_ALLOW_KEY}
            ],
            DS_GROUP_KEY: [],
            MW_REPORT_GROUP_KEY: [],
            MW_PRICE_GROUP_KEY: [],
            MW_SI_GROUP_KEY: [],
            MW_DASHBOARD_GROUP_KEY: [],
            MW_ADMIN_GROUP_KEY: [],
            MT_OVERVIEW_GROUP_KEY: [
                {"key": MT_OVERVIEW_VIEW_KEY, "status": STATUS_PERMISSION_ALLOW_KEY},
            ],
            # MT_OA_GROUP_KEY: [
            #     {
            #         'key': MT_OPERATIONAL_ANALYTICS_VIEW_KEY,
            #         'status': STATUS_PERMISSION_ALLOW_KEY
            #     }
            # ],
            # MT_PL_GROUP_KEY: [
            #     {
            #         'key': MT_PRODUCT_LISTING_VIEW_KEY,
            #         'status': STATUS_PERMISSION_ALLOW_KEY
            #     }
            # ],
            # MT_MP_GROUP_KEY: [
            #     {
            #         'key': MT_MARKETING_PERFORMANCE_VIEW_KEY,
            #         'status': STATUS_PERMISSION_ALLOW_KEY
            #     }
            # ],
            # MT_CM_GROUP_KEY: [
            #     {
            #         'key': MT_CATEGORY_MARKET_SHARE_VIEW_KEY,
            #         'status': STATUS_PERMISSION_ALLOW_KEY
            #     }
            # ],
            MT_ADVERTISING_GROUP_KEY: [
                {"key": MT_ADVERTISING_VIEW_KEY, "status": STATUS_PERMISSION_ALLOW_KEY}
            ],
            MT_CD_GROUP_KEY: [
                {
                    "key": MT_CUSTOM_DASHBOARD_VIEW_KEY,
                    "status": STATUS_PERMISSION_ALLOW_KEY,
                }
            ],
            MT_ADMIN_GROUP_KEY: [],
            SALE_GROUP_KEY: [
                {"key": SALE_VIEW_24H, "status": STATUS_PERMISSION_ALLOW_KEY}
            ],
            FILTER_GROUP_KEY: [
                {"key": SALE_REPORT_VIEW_FILTER, "status": STATUS_PERMISSION_ALLOW_KEY}
            ],
            COLUMN_SET_GROUP_KEY: [
                {"key": SALE_REPORT_VIEW_COLUMN, "status": STATUS_PERMISSION_ALLOW_KEY}
            ],
            VIEW_GROUP_KEY: [],
            RA_DASHBOARD_GROUP_KEY: [],
            RA_VISUALIZATION_GROUP_KEY: [],
        },
    },
}
