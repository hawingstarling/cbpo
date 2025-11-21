from app.permission.config_static_varible.common import ROLE_STAFF_KEY, CUSTOM_ROLE_ACCESS_RULE_DICT
from app.permission.config_static_varible.access_rules.client.sale_access_rule import \
    SALE_24H_MANAGER_ACCESS_RULE_DEFAULT_KEY, SALE_24H_REPORTER_ACCESS_RULE_DEFAULT_KEY

custom_role_ws_staff_default = {
    'key': ROLE_STAFF_KEY,
    'name': CUSTOM_ROLE_ACCESS_RULE_DICT[ROLE_STAFF_KEY],
    'access_rule_config': [
        {
            'key': SALE_24H_MANAGER_ACCESS_RULE_DEFAULT_KEY
        },
        {
            'key': SALE_24H_REPORTER_ACCESS_RULE_DEFAULT_KEY
        }
    ]
}
