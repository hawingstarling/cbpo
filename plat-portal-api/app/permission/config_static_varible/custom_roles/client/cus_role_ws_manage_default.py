from app.permission.config_static_varible.common import ROLE_MANAGER_KEY, CUSTOM_ROLE_ACCESS_RULE_DICT
from app.permission.config_static_varible.access_rules.client.sale_access_rule import \
    SALE_MANAGER_ACCESS_RULE_DEFAULT_KEY, SALE_REPORTER_ACCESS_RULE_DEFAULT_KEY

custom_role_ws_manage_default = {
    'key': ROLE_MANAGER_KEY,
    'name': CUSTOM_ROLE_ACCESS_RULE_DICT[ROLE_MANAGER_KEY],
    'access_rule_config': [
        {
            'key': SALE_MANAGER_ACCESS_RULE_DEFAULT_KEY
        },
        {
            'key': SALE_REPORTER_ACCESS_RULE_DEFAULT_KEY
        }
    ]
}
