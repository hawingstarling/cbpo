from app.permission.config_static_varible.common import (
    get_all_permission_keys_from_module_config,
)
from app.permission.config_static_varible.permissions_groups.client.data_central.data_central import (
    permission_module_dc_config,
    MODULE_DC_KEY,
)
from app.permission.config_static_varible.permissions_groups.client.data_sources.data_sources import (
    permission_module_ds_config,
    MODULE_DS_KEY,
)
from app.permission.config_static_varible.permissions_groups.client.map_watcher.map_watcher import (
    permission_module_map_watcher_config,
    MODULE_MAP_KEY,
)
from app.permission.config_static_varible.permissions_groups.client.matrix.matrix import (
    permission_module_mt_config,
    MODULE_MT_KEY,
)
from app.permission.config_static_varible.permissions_groups.client.pf.precise_financial import (
    permission_module_pf_config,
    MODULE_PF_KEY,
)
from app.permission.config_static_varible.permissions_groups.client.report_application.report_application import (
    permission_module_ra_config,
    MODULE_RA_KEY,
)
from app.permission.config_static_varible.permissions_groups.client.skuflex.skuflex import (
    permission_module_skuflex_config,
    MODULE_SKUF_KEY,
)
from app.permission.config_static_varible.permissions_groups.client.system_admin.system_admin import (
    MODULE_SA_KEY,
    permission_module_sa_config,
)
from app.permission.config_static_varible.permissions_groups.client.transit.transit import (
    permission_module_tr_config,
    MODULE_TR_KEY,
)

"""
app name from request 
"""
APP_BUILD_TRANSIT = "transit"
APP_BUILD_SKUFLEX = "skuflex"
APP_BUILD_PRECISE_FINANCIAL = "precise_financial"
APP_BUILD_DATA_CENTRAL = "data_central"
APP_BUILD_MWRW = "mwrw"
APP_BUILD_MT = "matrix"
APP_BUILD_SA = "sa"
#

APP_BUILD_PROFILE_CONFIG = {
    APP_BUILD_MWRW: {
        MODULE_MAP_KEY: get_all_permission_keys_from_module_config(
            permission_module_map_watcher_config
        ),
        # 'ROG': MODULE_PERMISSION_ROG
    },
    APP_BUILD_MT: {
        MODULE_DS_KEY: get_all_permission_keys_from_module_config(
            permission_module_ds_config
        ),
        MODULE_RA_KEY: get_all_permission_keys_from_module_config(
            permission_module_ra_config
        ),
        MODULE_MT_KEY: get_all_permission_keys_from_module_config(
            permission_module_mt_config
        ),
        MODULE_MAP_KEY: get_all_permission_keys_from_module_config(
            permission_module_map_watcher_config
        ),
    },
    APP_BUILD_DATA_CENTRAL: {
        MODULE_DC_KEY: get_all_permission_keys_from_module_config(
            permission_module_dc_config
        ),
    },
    APP_BUILD_PRECISE_FINANCIAL: {
        MODULE_PF_KEY: get_all_permission_keys_from_module_config(
            permission_module_pf_config
        ),
    },
    APP_BUILD_TRANSIT: {
        MODULE_TR_KEY: get_all_permission_keys_from_module_config(
            permission_module_tr_config
        )
    },
    APP_BUILD_SKUFLEX: {
        MODULE_SKUF_KEY: get_all_permission_keys_from_module_config(
            permission_module_skuflex_config
        )
    },
    APP_BUILD_SA: {
        MODULE_SA_KEY: get_all_permission_keys_from_module_config(
            permission_module_sa_config
        )
    },
}

#
APP_NAME_BUILD_PROFILE = list(APP_BUILD_PROFILE_CONFIG.keys())
APP_MODULE_BUILD_PROFILE = {
    APP_BUILD_MWRW: list(APP_BUILD_PROFILE_CONFIG[APP_BUILD_MWRW].keys()),
    APP_BUILD_MT: list(APP_BUILD_PROFILE_CONFIG[APP_BUILD_MT].keys()),
    APP_BUILD_DATA_CENTRAL: list(
        APP_BUILD_PROFILE_CONFIG[APP_BUILD_DATA_CENTRAL].keys()
    ),
    APP_BUILD_PRECISE_FINANCIAL: list(
        APP_BUILD_PROFILE_CONFIG[APP_BUILD_PRECISE_FINANCIAL].keys()
    ),
    APP_BUILD_TRANSIT: list(APP_BUILD_PROFILE_CONFIG[APP_BUILD_TRANSIT].keys()),
    APP_BUILD_SKUFLEX: list(APP_BUILD_PROFILE_CONFIG[APP_BUILD_SKUFLEX].keys()),
    APP_BUILD_SA: list(APP_BUILD_PROFILE_CONFIG[APP_BUILD_SA].keys()),
}

# App config
LIST_APP_CONFIG = (
    (APP_BUILD_MWRW, "RW/MW"),
    (APP_BUILD_MT, "Matrix"),
    (APP_BUILD_DATA_CENTRAL, "Data Central"),
    (APP_BUILD_PRECISE_FINANCIAL, "Precise Financial"),
    (APP_BUILD_TRANSIT, "Transit"),
    (APP_BUILD_SKUFLEX, "SKUFlex"),
    (APP_BUILD_SA, "System Admin"),
)

LIST_APP_CONFIG_DICT = {item[0]: item[1] for item in LIST_APP_CONFIG}
