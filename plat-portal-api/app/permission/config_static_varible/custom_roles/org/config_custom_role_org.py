from app.permission.config_static_varible.common import ROLE_ADMIN_KEY, ROLE_STAFF_KEY

custom_role_org_system_default_created = {
    ROLE_ADMIN_KEY: {
        'name': 'Full Access Custom Role',
        'access_rules': [ROLE_ADMIN_KEY]
    },
    ROLE_STAFF_KEY: {
        'name': 'Read Only Custom Role',
        'access_rules': [ROLE_STAFF_KEY]
    }
}
