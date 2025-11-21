from app.permission.config_static_varible.permissions_groups.client.data_central.data_central import (
    permission_module_dc_config,
)
from app.permission.config_static_varible.permissions_groups.client.data_sources.data_sources import (
    permission_module_ds_config,
)
from app.permission.config_static_varible.permissions_groups.client.map_watcher.map_watcher import (
    permission_module_map_watcher_config,
)
from app.permission.config_static_varible.permissions_groups.client.matrix.matrix import (
    permission_module_mt_config,
)
from app.permission.config_static_varible.permissions_groups.client.pf.precise_financial import (
    permission_module_pf_config,
)
from app.permission.config_static_varible.permissions_groups.client.report_application.report_application import (
    permission_module_ra_config,
)
from app.permission.config_static_varible.permissions_groups.client.skuflex.skuflex import (
    permission_module_skuflex_config,
)
from app.permission.config_static_varible.permissions_groups.client.transit.transit import (
    permission_module_tr_config,
)
from app.permission.config_static_varible.permissions_groups.client.system_admin.system_admin import (
    permission_module_sa_config,
)

# List permissions config of client level

PERMISSIONS_GROUPS_CONFIG_CLIENT_LEVEL = {
    **permission_module_pf_config,
    **permission_module_ds_config,
    **permission_module_dc_config,
    **permission_module_ra_config,
    **permission_module_map_watcher_config,
    **permission_module_mt_config,
    **permission_module_tr_config,
    **permission_module_skuflex_config,
    **permission_module_sa_config,
}

# List permissions config of org level
PERMISSIONS_GROUPS_CONFIG_ORG_LEVEL = {}
