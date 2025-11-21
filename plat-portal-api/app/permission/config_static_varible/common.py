from app.permission.config_static_varible.config import (
    PERMISSIONS_GROUPS_CONFIG_CLIENT_LEVEL,
)
from app.permission.config_static_varible.permissions_groups.client.data_central.data_central import (
    DC_ASIN_GROUP_ENUM,
    DC_BRAND_GROUP_ENUM,
    DC_DD_REPORT_GROUP_ENUM,
    DC_PO_GROUP_ENUM,
    MODULE_DC_KEY,
    MODULE_DC_NAME,
    DC_PRODUCT_REVIEW_GROUP_ENUM,
    DC_PROFILE_GROUP_ENUM,
    DC_INV_GROUP_ENUM,
    DC_ADMIN_GROUP_ENUM,
)
from app.permission.config_static_varible.permissions_groups.client.data_sources.data_sources import (
    DS_GROUP_ENUM,
    MODULE_DS_KEY,
    MODULE_DS_NAME,
)
from app.permission.config_static_varible.permissions_groups.client.map_watcher.map_watcher import (
    MODULE_MAP_KEY,
    MODULE_MAP_NAME,
    MW_REPORT_GROUP_ENUM,
    MW_PRICE_GROUP_ENUM,
    MW_SI_GROUP_ENUM,
    MW_DASHBOARD_GROUP_ENUM,
    MW_ADMIN_GROUP_ENUM,
    MW_SALE_ENFORCEMENT_GROUP_ENUM,
)
from app.permission.config_static_varible.permissions_groups.client.matrix.matrix import (
    MT_OVERVIEW_GROUP_ENUM,
    # MT_OA_GROUP_ENUM,
    # MT_PL_GROUP_ENUM,
    # MT_MP_GROUP_ENUM,
    # MT_CM_GROUP_ENUM,
    MT_CD_GROUP_ENUM,
    MODULE_MT_KEY,
    MT_ADMIN_GROUP_ENUM,
    MODULE_MT_NAME,
    MT_ADVERTISING_GROUP_ENUM,
    MT_BRAND_INTEGRITY_GROUP_ENUM,
    MT_GEOGRAPHIC_ANALYSIS_GROUP_ENUM,
)
from app.permission.config_static_varible.permissions_groups.client.pf.precise_financial import (
    MODULE_PF_KEY,
    MODULE_PF_NAME,
    COLUMN_SET_GROUP_ENUM,
    FILTER_GROUP_ENUM,
    VIEW_GROUP_ENUM,
    SALE_GROUP_ENUM,
    PF_ADMIN_GROUP_ENUM,
    PF_ITEM_GROUP_ENUM,
    PF_BRAND_SETTING_GROUP_ENUM,
    PF_OVERVIEW_DASHBOARD_GROUP_ENUM,
    PF_AD_DASHBOARD_GROUP_ENUM,
    PF_FEDEX_GROUP_ENUM,
    PF_REPRICING_GROUP_ENUM,
    PF_CUSTOM_REPORT_GROUP_ENUM,
    PF_TOP_ASINs_GROUP_ENUM,
    PF_EXTENSIV_GROUP_ENUM,
)
from app.permission.config_static_varible.permissions_groups.client.report_application.report_application import (
    MODULE_RA_KEY,
    MODULE_RA_NAME,
    RA_DASHBOARD_GROUP_ENUM,
    RA_VISUALIZATION_GROUP_ENUM,
)
from app.permission.config_static_varible.permissions_groups.client.skuflex.skuflex import (
    MODULE_SKUF_KEY,
    MODULE_SKUF_NAME,
    SKUF_COLUMN_SET_GROUP_ENUM,
    SKUF_FILTER_GROUP_ENUM,
    SKUF_VIEW_GROUP_ENUM,
    SALE_ORDER_GROUP_ENUM,
    SKUF_ADMIN_GROUP_ENUM,
    SKUF_ITEM_GROUP_ENUM,
    SKUF_FT_GROUP_ENUM,
    SKUF_PRODUCT_GROUP_ENUM,
    SKUF_INVENTORY_ITEM_GROUP_ENUM,
)
from app.permission.config_static_varible.permissions_groups.client.system_admin.system_admin import (
    MODULE_SA_KEY,
    MODULE_SA_NAME,
)
from app.permission.config_static_varible.permissions_groups.client.transit.transit import (
    MODULE_TR_NAME,
    MODULE_TR_KEY,
    TR_2D_BARCODE_GROUP_ENUM,
    TR_FNSKU_GROUP_ENUM,
    TR_HISTORY_GROUP_ENUM,
    TR_SETTING_GROUP_ENUM,
    TR_SHIPMENT_PLAN_GROUP_ENUM,
    TR_EFFICIENT_REPORT_GROUP_ENUM,
    TR_CUSTOM_SHIPMENT_GROUP_ENUM,
    TR_VENDOR_CENTRAL_GROUP_ENUM,
    TR_SHIPPING_LABEL_GROUP_ENUM,
    TR_SHIPPING_LABEL_HISTORY_ENUM,
)

ORG_LEVEL_KEY = "ORGANIZATION"
CLIENT_LEVEL_KEY = "CLIENT"

# Level enum
LEVEL_ENUM = (
    (ORG_LEVEL_KEY, "Organization"),
    (CLIENT_LEVEL_KEY, "Client"),
)

# Role custom key define static
ROLE_CUSTOM_KEY = "CUSTOM"
ROLE_ADMIN_KEY = "ADMIN"
ROLE_MANAGER_KEY = "MANAGER"
ROLE_STAFF_KEY = "STAFF"

# Setup custom role default
CUSTOM_ROLE_ACCESS_RULE_ENUM = (
    (ROLE_CUSTOM_KEY, "Custom"),  # Name custom role
    (ROLE_ADMIN_KEY, "Admin default"),  # default name role of ADMIN
    (ROLE_MANAGER_KEY, "Manager default"),  # default name role of MANAGER
    (ROLE_STAFF_KEY, "Staff default"),  # default name role of STAFF
)

# Custom role access rule type of system , convert to dict
CUSTOM_ROLE_ACCESS_RULE_DICT = {
    item[0]: item[1] for item in CUSTOM_ROLE_ACCESS_RULE_ENUM
}

# This is Custom type config is System or User create
CUSTOM_TYPE_CREATED_USER_KEY = "USER"
CUSTOM_TYPE_CREATED_SYSTEM_KEY = "SYSTEM"

# Custom type enum create
CUSTOM_TYPE_CREATED_ENUM = (
    (CUSTOM_TYPE_CREATED_USER_KEY, "Created by user"),
    (CUSTOM_TYPE_CREATED_SYSTEM_KEY, "Created by system"),
)

# Modules

MODULE_ENUM = (
    (MODULE_DC_KEY, MODULE_DC_NAME),
    (MODULE_DS_KEY, MODULE_DS_NAME),
    (MODULE_MAP_KEY, MODULE_MAP_NAME),
    (MODULE_MT_KEY, MODULE_MT_NAME),
    (MODULE_RA_KEY, MODULE_RA_NAME),
    (MODULE_PF_KEY, MODULE_PF_NAME),
    (MODULE_TR_KEY, MODULE_TR_NAME),
    (MODULE_SKUF_KEY, MODULE_SKUF_NAME),
    (MODULE_SA_KEY, MODULE_SA_NAME),
)

MODULE_DICT = {item[0]: item[1] for item in MODULE_ENUM}

# Status key define of permission

STATUS_PERMISSION_DENY_KEY = "DENY"
STATUS_PERMISSION_ALLOW_KEY = "ALLOW"
STATUS_PERMISSION_INHERIT_KEY = "INHERIT"

# Status enum of permission
STATUS_PERMISSION_ENUM = (
    (STATUS_PERMISSION_DENY_KEY, "Deny"),
    (STATUS_PERMISSION_ALLOW_KEY, "Allow"),
    (STATUS_PERMISSION_INHERIT_KEY, "Inherit"),
)

# List permissions client
GROUP_PERMISSION_CLIENT_ENUM = (
    #  pf
    SALE_GROUP_ENUM,
    COLUMN_SET_GROUP_ENUM,
    FILTER_GROUP_ENUM,
    VIEW_GROUP_ENUM,
    PF_ADMIN_GROUP_ENUM,
    PF_ITEM_GROUP_ENUM,
    PF_BRAND_SETTING_GROUP_ENUM,
    PF_OVERVIEW_DASHBOARD_GROUP_ENUM,
    PF_AD_DASHBOARD_GROUP_ENUM,
    PF_FEDEX_GROUP_ENUM,
    PF_REPRICING_GROUP_ENUM,
    PF_CUSTOM_REPORT_GROUP_ENUM,
    PF_TOP_ASINs_GROUP_ENUM,
    PF_EXTENSIV_GROUP_ENUM,
    #  dc
    DC_ASIN_GROUP_ENUM,
    DC_BRAND_GROUP_ENUM,
    DC_DD_REPORT_GROUP_ENUM,
    DC_PO_GROUP_ENUM,
    DC_PRODUCT_REVIEW_GROUP_ENUM,
    DC_PROFILE_GROUP_ENUM,
    DC_INV_GROUP_ENUM,
    DC_ADMIN_GROUP_ENUM,
    #  ds
    DS_GROUP_ENUM,
    #  map watcher
    MW_REPORT_GROUP_ENUM,
    MW_PRICE_GROUP_ENUM,
    MW_SI_GROUP_ENUM,
    MW_DASHBOARD_GROUP_ENUM,
    MW_ADMIN_GROUP_ENUM,
    MW_SALE_ENFORCEMENT_GROUP_ENUM,
    #  ra
    RA_DASHBOARD_GROUP_ENUM,
    RA_VISUALIZATION_GROUP_ENUM,
    #  mt
    MT_OVERVIEW_GROUP_ENUM,
    # MT_OA_GROUP_ENUM,
    # MT_PL_GROUP_ENUM,
    # MT_MP_GROUP_ENUM,
    # MT_CM_GROUP_ENUM,
    MT_CD_GROUP_ENUM,
    MT_ADMIN_GROUP_ENUM,
    MT_BRAND_INTEGRITY_GROUP_ENUM,
    MT_ADVERTISING_GROUP_ENUM,
    MT_GEOGRAPHIC_ANALYSIS_GROUP_ENUM,
    # tr
    TR_2D_BARCODE_GROUP_ENUM,
    TR_FNSKU_GROUP_ENUM,
    TR_HISTORY_GROUP_ENUM,
    TR_SETTING_GROUP_ENUM,
    TR_SHIPMENT_PLAN_GROUP_ENUM,
    TR_EFFICIENT_REPORT_GROUP_ENUM,
    TR_CUSTOM_SHIPMENT_GROUP_ENUM,
    TR_VENDOR_CENTRAL_GROUP_ENUM,
    TR_SHIPPING_LABEL_GROUP_ENUM,
    TR_SHIPPING_LABEL_HISTORY_ENUM,
    #  skuf
    SALE_ORDER_GROUP_ENUM,
    SKUF_FT_GROUP_ENUM,
    SKUF_COLUMN_SET_GROUP_ENUM,
    SKUF_FILTER_GROUP_ENUM,
    SKUF_VIEW_GROUP_ENUM,
    SKUF_ADMIN_GROUP_ENUM,
    SKUF_ITEM_GROUP_ENUM,
    SKUF_PRODUCT_GROUP_ENUM,
    SKUF_INVENTORY_ITEM_GROUP_ENUM,
)

# List permission groups client config
GROUP_PERMISSION_CLIENT_DICT = {
    item[0]: item[1] for item in GROUP_PERMISSION_CLIENT_ENUM
}

# List permissions organization
GROUP_PERMISSION_ORGANIZATION_ENUM = ()

# List permission groups client config
GROUP_PERMISSION_ORGANIZATION_DICT = {
    item[0]: item[1] for item in GROUP_PERMISSION_CLIENT_ENUM
}

# All group dict

GROUP_PERMISSION_DICT = {
    **GROUP_PERMISSION_CLIENT_DICT,
    **GROUP_PERMISSION_ORGANIZATION_DICT,
}

# List permissions enum of Client Level
PERMISSION_CLIENT_ENUM = []
group_keys = list(PERMISSIONS_GROUPS_CONFIG_CLIENT_LEVEL.keys())
for group_key in group_keys:
    group_name = PERMISSIONS_GROUPS_CONFIG_CLIENT_LEVEL[group_key]["name"]
    for permission in PERMISSIONS_GROUPS_CONFIG_CLIENT_LEVEL[group_key]["permissions"]:
        per = (permission["key"], permission["name"])
        PERMISSION_CLIENT_ENUM.append(per)
PERMISSION_CLIENT_ENUM = tuple(PERMISSION_CLIENT_ENUM)

# List permissions enum of Org level
PERMISSION_ORG_ENUM = ()

# List groups of permissions in system = Client Level + Org Level
GROUP_PERMISSION_ENUM = (
    GROUP_PERMISSION_CLIENT_ENUM + GROUP_PERMISSION_ORGANIZATION_ENUM
)

# List all permissions of groups in system
PERMISSION_ENUM = PERMISSION_CLIENT_ENUM + PERMISSION_ORG_ENUM


def get_all_permissions_groups_from_module_config(
    module_config: dict,
    priority_config_dict: dict = None,
    priority_status_for_left: str = STATUS_PERMISSION_ALLOW_KEY,
):
    def get_from_priority(key: str):
        if not priority_config_dict:
            return priority_status_for_left
        _status = priority_config_dict.get(key, None)
        if not _status:
            return priority_status_for_left
        return _status

    res = {}
    _group_keys = module_config.keys()
    for _group_key in _group_keys:
        group_content = module_config[_group_key]
        permissions = [
            {"key": x["key"], "status": get_from_priority(x["key"])}
            for x in group_content["permissions"]
        ]
        res.update({_group_key: permissions})
    return res


def get_all_permission_keys_from_module_config(module_config: dict):
    res = []
    _group_keys = module_config.keys()
    for _group_key in _group_keys:
        group_content = module_config[_group_key]
        permissions = [
            (group_content.get("module"), (x.get("key"), x.get("name")))
            for x in group_content["permissions"]
        ]
        res.extend(permissions)
    return tuple(res)
