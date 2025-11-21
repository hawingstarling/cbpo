from app.permission.config_static_varible.common import (
    get_all_permissions_groups_from_module_config,
    ROLE_ADMIN_KEY,
    ROLE_STAFF_KEY,
    STATUS_PERMISSION_ALLOW_KEY,
    STATUS_PERMISSION_INHERIT_KEY,
    STATUS_PERMISSION_DENY_KEY,
)
from app.permission.config_static_varible.config import (
    PERMISSIONS_GROUPS_CONFIG_CLIENT_LEVEL,
)
from app.permission.config_static_varible.permissions_groups.client.data_central.data_central import (
    DC_ASIN_VIEW_KEY,
    DC_BRAND_VIEW_KEY,
    DC_DD_REPORT_VIEW_KEY,
    DC_PO_VIEW_KEY,
    permission_module_dc_config,
    DC_PRODUCT_REVIEW_VIEW_KEY,
    DC_PROFILE_VIEW_KEY,
    DC_INV_SELLER_VIEW_KEY,
    DC_INV_SUMMARY_VIEW_KEY,
    MODULE_DC_KEY,
)
from app.permission.config_static_varible.permissions_groups.client.data_sources.data_sources import (
    permission_module_ds_config,
    MODULE_DS_KEY,
)
from app.permission.config_static_varible.permissions_groups.client.map_watcher.map_watcher import (
    permission_module_map_watcher_config,
    MAP_EMAIL_NOTIFICATION_KEY,
    MW_SALE_ENFORCEMENT_VIEW,
    MODULE_MAP_KEY,
)
from app.permission.config_static_varible.permissions_groups.client.matrix.matrix import (
    MT_OVERVIEW_VIEW_KEY,
    MT_CUSTOM_DASHBOARD_VIEW_KEY,
    # MT_OPERATIONAL_ANALYTICS_VIEW_KEY,
    # MT_PRODUCT_LISTING_VIEW_KEY,
    # MT_MARKETING_PERFORMANCE_VIEW_KEY,
    # MT_CATEGORY_MARKET_SHARE_VIEW_KEY,
    MT_ADVERTISING_VIEW_KEY,
    permission_module_mt_config,
    MT_ADMIN_SETTING_EDIT_KEY,
    MT_ADMIN_DS_GENERATE_KEY,
    MT_ADMIN_DS_DASHBOARD_GENERATE_KEY,
    MT_CUSTOM_DASHBOARD_MANAGEMENT_KEY,
    MT_BRAND_INTEGRITY_VIEW_KEY,
    MT_GEOGRAPHIC_ANALYSIS_VIEW_KEY,
    MODULE_MT_KEY,
)
from app.permission.config_static_varible.permissions_groups.client.pf.precise_financial import (
    SALE_VIEW_24H,
    SALE_REPORT_VIEW_FILTER,
    SALE_REPORT_VIEW_COLUMN,
    SALE_IMPORT_KEY,
    SALE_SINGLE_EDIT,
    SALE_BULK_EDIT,
    SALE_VIEW_ALL,
    SALE_SINGLE_DELETE,
    SALE_BULK_DELETE,
    SALE_VIEW_AUDIT_LOG,
    permission_module_pf_config,
    VIEW_VIEW_ALL_REPORT,
    SALE_REPORT_CREATE_FILTER,
    SALE_REPORT_EDIT_FILTER,
    SALE_REPORT_DELETE_FILTER,
    SALE_REPORT_CREATE_COLUMN,
    SALE_REPORT_EDIT_COLUMN,
    SALE_REPORT_DELETE_COLUMN,
    VIEW_CREATE_REPORT,
    VIEW_EDIT_REPORT,
    VIEW_DELETE_REPORT,
    PF_ITEM_VIEW_KEY,
    MODULE_PF_KEY,
)
from app.permission.config_static_varible.permissions_groups.client.report_application.report_application import (
    permission_module_ra_config,
    MODULE_RA_KEY,
)
from app.permission.config_static_varible.permissions_groups.client.skuflex.skuflex import (
    SKUF_SALE_REPORT_VIEW_FILTER,
    SKUF_SALE_REPORT_VIEW_COLUMN,
    SALE_ORDER_IMPORT_KEY,
    SALE_ORDER_SINGLE_EDIT,
    SALE_ORDER_BULK_EDIT,
    SALE_ORDER_VIEW_ALL,
    SALE_ORDER_SINGLE_DELETE,
    SALE_ORDER_BULK_DELETE,
    SALE_ORDER_VIEW_AUDIT_LOG,
    permission_module_skuflex_config,
    SKUF_VIEW_VIEW_ALL_REPORT,
    SKUF_ITEM_VIEW_KEY,
    SALE_ORDER_MARK_AS_FULFILLED,
    SALE_ORDER_MOVE_TO_FT,
    MODULE_SKUF_KEY,
)
from app.permission.config_static_varible.permissions_groups.client.transit.transit import (
    TR_2D_BARCODE_VIEW_KEY,
    TR_FNSKU_VIEW_KEY,
)

"""
ROLE_ADMIN_KEY, ROLE_STAFF_KEY are default for coding purpose
"""

#  MAP Watcher
MAP_WATCHER_FULL_ACCESS_RULE_KEY = "MW_FULL"
MAP_WATCHER_READ_ONLY_ACCESS_RULE_KEY = "MW_READ_ONLY"
MAP_WATCHER_UPDATE_NOT = "MW_UPDATE_NOTIFICATION"
# PF
PF_SALE_FULL_ACCESS_RULE_KEY = "PF_SALE_FULL"
PF_SALE_READ_ONLY_ACCESS_RULE_KEY = "PF_SALE_READ_ONLY"
PF_FILTER_COLUMN_SETTING_VIEW_FULL_ACCESS_RULE_KEY = "PF_FIL_COL_VIEW_FULL"
PF_FILTER_COLUMN_SETTING_VIEW_READ_ONLY_ACCESS_RULE_KEY = "PF_FIL_COL_VIEW_READ_ONLY"
# DC
DC_FULL_ACCESS_RULE_KEY = "DC_FULL"
DC_READ_ONLY_ACCESS_RULE_KEY = "DC_READ_ONLY"
# RA
RA_FULL_ACCESS_RULE_KEY = "RA_FULL"
RA_READ_ONLY_ACCESS_RULE_KEY = "RA_READ_ONLY"
# DS
DS_FULL_ACCESS_RULE_KEY = "DS_FULL"
DS_READ_ONLY_ACCESS_RULE_KEY = "DS_READ_ONLY"
# MT
MT_STATIC_DASHBOARD_FULL_ACCESS_RULE_KEY = "MT_STATIC_DASHBOARD_FULL"
MT_STATIC_DASHBOARD_READ_ONLY_ACCESS_RULE_KEY = "MT_STATIC_DASHBOARD_READ_ONLY"
MT_CUSTOM_DASHBOARD_FULL_ACCESS_RULE_KEY = "MT_CUSTOM_DASHBOARD_FULL"
MT_CUSTOM_DASHBOARD_READ_ONLY_ACCESS_RULE_KEY = "MT_CUSTOM_DASHBOARD_READ_ONLY"
MT_ADMIN_FULL_ACCESS_RULE_KEY = "MT_ADMIN_FULL"
# SKUF
SKUF_SALE_FULL_ACCESS_RULE_KEY = "SKUF_SALE_FULL"
SKUF_SALE_READ_ONLY_ACCESS_RULE_KEY = "SKUF_SALE_READ_ONLY"
SKUF_FILTER_COLUMN_SETTING_VIEW_FULL_ACCESS_RULE_KEY = "SKUF_FIL_COL_VIEW_FULL"
SKUF_FILTER_COLUMN_SETTING_VIEW_READ_ONLY_ACCESS_RULE_KEY = (
    "SKUF_FIL_COL_VIEW_READ_ONLY"
)

access_rule_client_system_default_created = {
    ROLE_ADMIN_KEY: {
        "name": "Full Access Rule",
        "permissions_groups": get_all_permissions_groups_from_module_config(
            module_config=PERMISSIONS_GROUPS_CONFIG_CLIENT_LEVEL,
            priority_config_dict={
                MAP_EMAIL_NOTIFICATION_KEY: STATUS_PERMISSION_DENY_KEY
            },
        ),
    },
    ROLE_STAFF_KEY: {
        "name": "Staff Default Access Rule",
        "permissions_groups": get_all_permissions_groups_from_module_config(
            module_config=PERMISSIONS_GROUPS_CONFIG_CLIENT_LEVEL,
            priority_config_dict={
                DC_ASIN_VIEW_KEY: STATUS_PERMISSION_ALLOW_KEY,
                DC_BRAND_VIEW_KEY: STATUS_PERMISSION_ALLOW_KEY,
                DC_DD_REPORT_VIEW_KEY: STATUS_PERMISSION_ALLOW_KEY,
                DC_PO_VIEW_KEY: STATUS_PERMISSION_ALLOW_KEY,
                DC_PRODUCT_REVIEW_VIEW_KEY: STATUS_PERMISSION_ALLOW_KEY,
                DC_PROFILE_VIEW_KEY: STATUS_PERMISSION_ALLOW_KEY,
                DC_INV_SELLER_VIEW_KEY: STATUS_PERMISSION_ALLOW_KEY,
                DC_INV_SUMMARY_VIEW_KEY: STATUS_PERMISSION_ALLOW_KEY,
                MT_OVERVIEW_VIEW_KEY: STATUS_PERMISSION_ALLOW_KEY,
                MT_CUSTOM_DASHBOARD_VIEW_KEY: STATUS_PERMISSION_ALLOW_KEY,
                # MT_OPERATIONAL_ANALYTICS_VIEW_KEY: STATUS_PERMISSION_ALLOW_KEY,
                # MT_PRODUCT_LISTING_VIEW_KEY: STATUS_PERMISSION_ALLOW_KEY,
                # MT_MARKETING_PERFORMANCE_VIEW_KEY: STATUS_PERMISSION_ALLOW_KEY,
                # MT_CATEGORY_MARKET_SHARE_VIEW_KEY: STATUS_PERMISSION_ALLOW_KEY,
                MT_BRAND_INTEGRITY_VIEW_KEY: STATUS_PERMISSION_ALLOW_KEY,
                MT_ADVERTISING_VIEW_KEY: STATUS_PERMISSION_ALLOW_KEY,
                MT_GEOGRAPHIC_ANALYSIS_VIEW_KEY: STATUS_PERMISSION_ALLOW_KEY,
                SALE_REPORT_VIEW_FILTER: STATUS_PERMISSION_ALLOW_KEY,
                SALE_REPORT_VIEW_COLUMN: STATUS_PERMISSION_ALLOW_KEY,
                SALE_REPORT_CREATE_FILTER: STATUS_PERMISSION_ALLOW_KEY,
                SALE_REPORT_EDIT_FILTER: STATUS_PERMISSION_ALLOW_KEY,
                SALE_REPORT_DELETE_FILTER: STATUS_PERMISSION_ALLOW_KEY,
                SALE_REPORT_CREATE_COLUMN: STATUS_PERMISSION_ALLOW_KEY,
                SALE_REPORT_EDIT_COLUMN: STATUS_PERMISSION_ALLOW_KEY,
                SALE_REPORT_DELETE_COLUMN: STATUS_PERMISSION_ALLOW_KEY,
                SALE_VIEW_24H: STATUS_PERMISSION_ALLOW_KEY,
                SALE_VIEW_ALL: STATUS_PERMISSION_ALLOW_KEY,
                VIEW_CREATE_REPORT: STATUS_PERMISSION_ALLOW_KEY,
                VIEW_EDIT_REPORT: STATUS_PERMISSION_ALLOW_KEY,
                VIEW_DELETE_REPORT: STATUS_PERMISSION_ALLOW_KEY,
                PF_ITEM_VIEW_KEY: STATUS_PERMISSION_ALLOW_KEY,
                SKUF_ITEM_VIEW_KEY: STATUS_PERMISSION_ALLOW_KEY,
                MW_SALE_ENFORCEMENT_VIEW: STATUS_PERMISSION_ALLOW_KEY,
                TR_2D_BARCODE_VIEW_KEY: STATUS_PERMISSION_ALLOW_KEY,
                TR_FNSKU_VIEW_KEY: STATUS_PERMISSION_ALLOW_KEY,
            },
            priority_status_for_left=STATUS_PERMISSION_DENY_KEY,
        ),
    },
    MAP_WATCHER_FULL_ACCESS_RULE_KEY: {
        "name": "MAP Watcher – Full Access",
        "module": MODULE_MAP_KEY,
        "permissions_groups": get_all_permissions_groups_from_module_config(
            module_config=permission_module_map_watcher_config,
            priority_config_dict={
                MAP_EMAIL_NOTIFICATION_KEY: STATUS_PERMISSION_INHERIT_KEY
            },
        ),
    },
    MAP_WATCHER_READ_ONLY_ACCESS_RULE_KEY: {
        "name": "MAP Watcher – Read Only",
        "module": MODULE_MAP_KEY,
        "permissions_groups": get_all_permissions_groups_from_module_config(
            module_config=permission_module_map_watcher_config,
            priority_config_dict={
                MW_SALE_ENFORCEMENT_VIEW: STATUS_PERMISSION_ALLOW_KEY
            },
            priority_status_for_left=STATUS_PERMISSION_DENY_KEY,
        ),
    },
    MAP_WATCHER_UPDATE_NOT: {
        "name": "MAP Watcher – MAP Price Update Notification",
        "module": MODULE_MAP_KEY,
        "permissions_groups": get_all_permissions_groups_from_module_config(
            module_config=permission_module_map_watcher_config,
            priority_config_dict={
                MAP_EMAIL_NOTIFICATION_KEY: STATUS_PERMISSION_ALLOW_KEY
            },
        ),
    },
    PF_SALE_FULL_ACCESS_RULE_KEY: {
        "name": "Precise Financial – Sales – Full Access",
        "module": MODULE_PF_KEY,
        "permissions_groups": get_all_permissions_groups_from_module_config(
            module_config=permission_module_pf_config,
            priority_config_dict={
                SALE_IMPORT_KEY: STATUS_PERMISSION_ALLOW_KEY,
                SALE_SINGLE_EDIT: STATUS_PERMISSION_ALLOW_KEY,
                SALE_BULK_EDIT: STATUS_PERMISSION_ALLOW_KEY,
                SALE_VIEW_ALL: STATUS_PERMISSION_ALLOW_KEY,
                SALE_VIEW_24H: STATUS_PERMISSION_ALLOW_KEY,
                SALE_SINGLE_DELETE: STATUS_PERMISSION_ALLOW_KEY,
                SALE_BULK_DELETE: STATUS_PERMISSION_ALLOW_KEY,
                SALE_VIEW_AUDIT_LOG: STATUS_PERMISSION_ALLOW_KEY,
            },
            priority_status_for_left=STATUS_PERMISSION_DENY_KEY,
        ),
    },
    PF_SALE_READ_ONLY_ACCESS_RULE_KEY: {
        "name": "Precise Financial – Sales – Read Only",
        "module": MODULE_PF_KEY,
        "permissions_groups": get_all_permissions_groups_from_module_config(
            module_config=permission_module_pf_config,
            priority_config_dict={
                SALE_VIEW_ALL: STATUS_PERMISSION_ALLOW_KEY,
            },
            priority_status_for_left=STATUS_PERMISSION_DENY_KEY,
        ),
    },
    PF_FILTER_COLUMN_SETTING_VIEW_FULL_ACCESS_RULE_KEY: {
        "name": "Precise Financial – Filters, Column Sets, Views – Full Access",
        "module": MODULE_PF_KEY,
        "permissions_groups": get_all_permissions_groups_from_module_config(
            module_config=permission_module_pf_config,
            priority_config_dict={
                SALE_IMPORT_KEY: STATUS_PERMISSION_DENY_KEY,
                SALE_SINGLE_EDIT: STATUS_PERMISSION_DENY_KEY,
                SALE_BULK_EDIT: STATUS_PERMISSION_DENY_KEY,
                SALE_VIEW_ALL: STATUS_PERMISSION_DENY_KEY,
                SALE_VIEW_24H: STATUS_PERMISSION_DENY_KEY,
                SALE_SINGLE_DELETE: STATUS_PERMISSION_DENY_KEY,
                SALE_BULK_DELETE: STATUS_PERMISSION_DENY_KEY,
                SALE_VIEW_AUDIT_LOG: STATUS_PERMISSION_DENY_KEY,
            },
            priority_status_for_left=STATUS_PERMISSION_ALLOW_KEY,
        ),
    },
    PF_FILTER_COLUMN_SETTING_VIEW_READ_ONLY_ACCESS_RULE_KEY: {
        "name": "Precise Financial – Filters, Column Sets, Views – Read Only",
        "module": MODULE_PF_KEY,
        "permissions_groups": get_all_permissions_groups_from_module_config(
            module_config=permission_module_pf_config,
            priority_config_dict={
                SALE_REPORT_VIEW_FILTER: STATUS_PERMISSION_ALLOW_KEY,
                SALE_REPORT_VIEW_COLUMN: STATUS_PERMISSION_ALLOW_KEY,
                VIEW_VIEW_ALL_REPORT: STATUS_PERMISSION_ALLOW_KEY,
            },
            priority_status_for_left=STATUS_PERMISSION_DENY_KEY,
        ),
    },
    DC_FULL_ACCESS_RULE_KEY: {
        "name": "Data Central – Full Access",
        "module": MODULE_DC_KEY,
        "permissions_groups": get_all_permissions_groups_from_module_config(
            permission_module_dc_config
        ),
    },
    DC_READ_ONLY_ACCESS_RULE_KEY: {
        "name": "Data Central – Read Only",
        "module": MODULE_DC_KEY,
        "permissions_groups": get_all_permissions_groups_from_module_config(
            module_config=permission_module_dc_config,
            priority_config_dict={
                DC_ASIN_VIEW_KEY: STATUS_PERMISSION_ALLOW_KEY,
                DC_BRAND_VIEW_KEY: STATUS_PERMISSION_ALLOW_KEY,
                DC_DD_REPORT_VIEW_KEY: STATUS_PERMISSION_ALLOW_KEY,
                DC_PO_VIEW_KEY: STATUS_PERMISSION_ALLOW_KEY,
                DC_PROFILE_VIEW_KEY: STATUS_PERMISSION_ALLOW_KEY,
                DC_INV_SELLER_VIEW_KEY: STATUS_PERMISSION_ALLOW_KEY,
                DC_INV_SUMMARY_VIEW_KEY: STATUS_PERMISSION_ALLOW_KEY,
                DC_PRODUCT_REVIEW_VIEW_KEY: STATUS_PERMISSION_ALLOW_KEY,
            },
            priority_status_for_left=STATUS_PERMISSION_DENY_KEY,
        ),
    },
    RA_FULL_ACCESS_RULE_KEY: {
        "name": "Reporting Application – Full Access",
        "module": MODULE_RA_KEY,
        "permissions_groups": get_all_permissions_groups_from_module_config(
            permission_module_ra_config
        ),
    },
    RA_READ_ONLY_ACCESS_RULE_KEY: {
        "name": "Reporting Application – Read Only",
        "module": MODULE_DC_KEY,
        "permissions_groups": get_all_permissions_groups_from_module_config(
            module_config=permission_module_ra_config,
            priority_config_dict=None,
            priority_status_for_left=STATUS_PERMISSION_DENY_KEY,
        ),
    },
    DS_FULL_ACCESS_RULE_KEY: {
        "name": "Data Source – Full Access",
        "module": MODULE_DS_KEY,
        "permissions_groups": get_all_permissions_groups_from_module_config(
            permission_module_ds_config
        ),
    },
    DS_READ_ONLY_ACCESS_RULE_KEY: {
        "name": "Data Source – Read Only",
        "module": MODULE_DS_KEY,
        "permissions_groups": get_all_permissions_groups_from_module_config(
            module_config=permission_module_ds_config,
            priority_config_dict=None,
            priority_status_for_left=STATUS_PERMISSION_DENY_KEY,
        ),
    },
    MT_STATIC_DASHBOARD_FULL_ACCESS_RULE_KEY: {
        "name": "Matrix – Static Dashboards – Full Access",
        "module": MODULE_MT_KEY,
        "permissions_groups": get_all_permissions_groups_from_module_config(
            module_config=permission_module_mt_config,
            priority_config_dict={
                MT_ADMIN_SETTING_EDIT_KEY: STATUS_PERMISSION_DENY_KEY,
                MT_ADMIN_DS_GENERATE_KEY: STATUS_PERMISSION_DENY_KEY,
                MT_ADMIN_DS_DASHBOARD_GENERATE_KEY: STATUS_PERMISSION_DENY_KEY,
                MT_CUSTOM_DASHBOARD_VIEW_KEY: STATUS_PERMISSION_DENY_KEY,
                MT_CUSTOM_DASHBOARD_MANAGEMENT_KEY: STATUS_PERMISSION_DENY_KEY,
            },
            priority_status_for_left=STATUS_PERMISSION_ALLOW_KEY,
        ),
    },
    MT_STATIC_DASHBOARD_READ_ONLY_ACCESS_RULE_KEY: {
        "name": "Matrix – Static Dashboards – Read Only",
        "module": MODULE_MT_KEY,
        "permissions_groups": get_all_permissions_groups_from_module_config(
            module_config=permission_module_mt_config,
            priority_config_dict={
                MT_OVERVIEW_VIEW_KEY: STATUS_PERMISSION_ALLOW_KEY,
                # MT_OPERATIONAL_ANALYTICS_VIEW_KEY: STATUS_PERMISSION_ALLOW_KEY,
                # MT_PRODUCT_LISTING_VIEW_KEY: STATUS_PERMISSION_ALLOW_KEY,
                # MT_MARKETING_PERFORMANCE_VIEW_KEY: STATUS_PERMISSION_ALLOW_KEY,
                # MT_CATEGORY_MARKET_SHARE_VIEW_KEY: STATUS_PERMISSION_ALLOW_KEY,
                MT_ADVERTISING_VIEW_KEY: STATUS_PERMISSION_ALLOW_KEY,
            },
            priority_status_for_left=STATUS_PERMISSION_DENY_KEY,
        ),
    },
    MT_CUSTOM_DASHBOARD_FULL_ACCESS_RULE_KEY: {
        "name": "Matrix – Custom Dashboards – Full Access",
        "module": MODULE_MT_KEY,
        "permissions_groups": get_all_permissions_groups_from_module_config(
            module_config=permission_module_mt_config,
            priority_config_dict={
                MT_CUSTOM_DASHBOARD_VIEW_KEY: STATUS_PERMISSION_ALLOW_KEY,
                MT_CUSTOM_DASHBOARD_MANAGEMENT_KEY: STATUS_PERMISSION_ALLOW_KEY,
            },
            priority_status_for_left=STATUS_PERMISSION_DENY_KEY,
        ),
    },
    MT_CUSTOM_DASHBOARD_READ_ONLY_ACCESS_RULE_KEY: {
        "name": "Matrix – Custom Dashboards – Read Only",
        "module": MODULE_MT_KEY,
        "permissions_groups": get_all_permissions_groups_from_module_config(
            module_config=permission_module_mt_config,
            priority_config_dict={
                MT_CUSTOM_DASHBOARD_VIEW_KEY: STATUS_PERMISSION_ALLOW_KEY,
            },
            priority_status_for_left=STATUS_PERMISSION_DENY_KEY,
        ),
    },
    MT_ADMIN_FULL_ACCESS_RULE_KEY: {
        "name": "Matrix – Administration – Full Access",
        "module": MODULE_MT_KEY,
        "permissions_groups": get_all_permissions_groups_from_module_config(
            module_config=permission_module_mt_config,
            priority_config_dict=None,
            priority_status_for_left=STATUS_PERMISSION_ALLOW_KEY,
        ),
    },
    SKUF_SALE_FULL_ACCESS_RULE_KEY: {
        "name": "SKUFlex – Sales – Full Access",
        "module": MODULE_SKUF_KEY,
        "permissions_groups": get_all_permissions_groups_from_module_config(
            module_config=permission_module_skuflex_config,
            priority_config_dict={
                SALE_ORDER_IMPORT_KEY: STATUS_PERMISSION_ALLOW_KEY,
                SALE_ORDER_SINGLE_EDIT: STATUS_PERMISSION_ALLOW_KEY,
                SALE_ORDER_BULK_EDIT: STATUS_PERMISSION_ALLOW_KEY,
                SALE_ORDER_VIEW_ALL: STATUS_PERMISSION_ALLOW_KEY,
                SALE_ORDER_SINGLE_DELETE: STATUS_PERMISSION_ALLOW_KEY,
                SALE_ORDER_BULK_DELETE: STATUS_PERMISSION_ALLOW_KEY,
                SALE_ORDER_VIEW_AUDIT_LOG: STATUS_PERMISSION_ALLOW_KEY,
                SALE_ORDER_MOVE_TO_FT: STATUS_PERMISSION_ALLOW_KEY,
                SALE_ORDER_MARK_AS_FULFILLED: STATUS_PERMISSION_ALLOW_KEY,
            },
            priority_status_for_left=STATUS_PERMISSION_DENY_KEY,
        ),
    },
    SKUF_FILTER_COLUMN_SETTING_VIEW_FULL_ACCESS_RULE_KEY: {
        "name": "SKUFlex – Filters, Column Sets, Views – Full Access",
        "module": MODULE_SKUF_KEY,
        "permissions_groups": get_all_permissions_groups_from_module_config(
            module_config=permission_module_skuflex_config,
            priority_config_dict={
                SALE_ORDER_IMPORT_KEY: STATUS_PERMISSION_DENY_KEY,
                SALE_ORDER_SINGLE_EDIT: STATUS_PERMISSION_DENY_KEY,
                SALE_ORDER_BULK_EDIT: STATUS_PERMISSION_DENY_KEY,
                SALE_ORDER_VIEW_ALL: STATUS_PERMISSION_DENY_KEY,
                SALE_ORDER_SINGLE_DELETE: STATUS_PERMISSION_DENY_KEY,
                SALE_ORDER_BULK_DELETE: STATUS_PERMISSION_DENY_KEY,
                SALE_ORDER_VIEW_AUDIT_LOG: STATUS_PERMISSION_DENY_KEY,
            },
            priority_status_for_left=STATUS_PERMISSION_ALLOW_KEY,
        ),
    },
    SKUF_FILTER_COLUMN_SETTING_VIEW_READ_ONLY_ACCESS_RULE_KEY: {
        "name": "SKUFlex – Filters, Column Sets, Views – Read Only",
        "module": MODULE_SKUF_KEY,
        "permissions_groups": get_all_permissions_groups_from_module_config(
            module_config=permission_module_skuflex_config,
            priority_config_dict={
                SKUF_SALE_REPORT_VIEW_FILTER: STATUS_PERMISSION_ALLOW_KEY,
                SKUF_SALE_REPORT_VIEW_COLUMN: STATUS_PERMISSION_ALLOW_KEY,
                SKUF_VIEW_VIEW_ALL_REPORT: STATUS_PERMISSION_ALLOW_KEY,
            },
            priority_status_for_left=STATUS_PERMISSION_DENY_KEY,
        ),
    },
}
