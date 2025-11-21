from app.permission.config_static_varible.permissions_groups.client.pf.precise_financial import (
    SALE_GROUP_KEY, VIEW_GROUP_KEY, SALE_SINGLE_DELETE, SALE_BULK_DELETE, SALE_VIEW_ALL, SALE_REPORT_DELETE_COLUMN, \
    SALE_REPORT_DELETE_FILTER, VIEW_DELETE_REPORT, VIEW_VIEW_ALL_REPORT)

SALE_FULL_ACCESS_RULE_DEFAULT_KEY = 'SALE_FULL_PERMISSION'
SALE_MANAGER_ACCESS_RULE_DEFAULT_KEY = 'SALE_MANAGER'
SALE_24H_MANAGER_ACCESS_RULE_DEFAULT_KEY = 'SALE_24H_MANAGER'
SALE_REPORTER_ACCESS_RULE_DEFAULT_KEY = 'SALE_REPORTER'
SALE_24H_REPORTER_ACCESS_RULE_DEFAULT_KEY = 'SALE_24H_REPORTER'

access_rules_sale_config = {
    SALE_FULL_ACCESS_RULE_DEFAULT_KEY: {
        'name': 'Sale Full Access',
        'permissions_groups': [
            {
                'key': SALE_GROUP_KEY
            },
            {
                'key': VIEW_GROUP_KEY
            }
        ],
        'permission_config_status': {
            'deny': [],
            'inherit': []
        }
    },
    SALE_MANAGER_ACCESS_RULE_DEFAULT_KEY: {
        'name': 'Sale Manager',
        'permissions_groups': [
            {
                'key': SALE_GROUP_KEY
            }
        ],
        'permission_config_status': {
            'deny': [
                SALE_SINGLE_DELETE,
                SALE_BULK_DELETE
            ],
            'inherit': []
        }

    },
    SALE_24H_MANAGER_ACCESS_RULE_DEFAULT_KEY: {
        'name': 'Sale 24h Manager',
        'permissions_groups': [
            {
                'key': SALE_GROUP_KEY
            }
        ],
        'permission_config_status': {
            'deny': [
                SALE_VIEW_ALL,
                SALE_SINGLE_DELETE,
                SALE_BULK_DELETE
            ],
            'inherit': []
        }

    },
    SALE_REPORTER_ACCESS_RULE_DEFAULT_KEY: {
        'name': 'Sale Reporter',
        'permissions_groups': [
            {
                'key': VIEW_GROUP_KEY
            }
        ],
        'permission_config_status': {
            'deny': [
                SALE_REPORT_DELETE_COLUMN,
                SALE_REPORT_DELETE_FILTER,
                VIEW_DELETE_REPORT
            ],
            'inherit': []
        }

    },
    SALE_24H_REPORTER_ACCESS_RULE_DEFAULT_KEY: {
        'name': 'Sale 24h Reporter',
        'permissions_groups': [
            {
                'key': VIEW_GROUP_KEY
            }
        ],
        'permission_config_status': {
            'deny': [
                SALE_REPORT_DELETE_COLUMN,
                SALE_REPORT_DELETE_FILTER,
                VIEW_DELETE_REPORT,
                VIEW_VIEW_ALL_REPORT
            ],
            'inherit': []
        }

    }
}
