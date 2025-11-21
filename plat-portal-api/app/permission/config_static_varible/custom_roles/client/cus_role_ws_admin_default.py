from app.permission.config_static_varible.common import CUSTOM_ROLE_ACCESS_RULE_DICT, ROLE_ADMIN_KEY
from app.permission.config_static_varible.access_rules.client.sale_access_rule import SALE_FULL_ACCESS_RULE_DEFAULT_KEY

custom_role_ws_admin_default = {
    'key': ROLE_ADMIN_KEY,
    'name': CUSTOM_ROLE_ACCESS_RULE_DICT[ROLE_ADMIN_KEY],
    'access_rule_config': [
        {
            'key': SALE_FULL_ACCESS_RULE_DEFAULT_KEY
        }
    ]
}
