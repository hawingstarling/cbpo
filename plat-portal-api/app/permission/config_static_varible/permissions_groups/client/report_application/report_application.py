MODULE_RA_KEY = 'RA'
MODULE_RA_NAME = 'Reporting Application'

RA_DASHBOARD_GROUP_KEY = 'RA_DASHBOARD_GROUP'
RA_DASHBOARD_GROUP_NAME = 'Dashboards'

RA_DASHBOARD_GROUP_ENUM = (RA_DASHBOARD_GROUP_KEY, RA_DASHBOARD_GROUP_NAME)

RA_DASHBOARD_MANAGEMENT_KEY = 'ra_dash_man'
RA_DASHBOARD_ACCESS_MANAGEMENT_KEY = 'ra_dash_access_man'

RA_VISUALIZATION_GROUP_KEY = 'RA_VIZ_GROUP'
RA_VISUALIZATION_GROUP_NAME = 'Visualizations'

RA_VISUALIZATION_GROUP_ENUM = (RA_VISUALIZATION_GROUP_KEY, RA_VISUALIZATION_GROUP_NAME)

RA_VISUALIZATION_MANAGEMENT_KEY = 'ra_viz_man'
RA_VISUALIZATION_ACCESS_MANAGEMENT_KEY = 'ra_viz_access_man'

permission_module_ra_config = {
    RA_DASHBOARD_GROUP_KEY: {
        'name': RA_DASHBOARD_GROUP_NAME,
        'module': MODULE_RA_KEY,
        'permissions': [
            {
                'key': RA_DASHBOARD_MANAGEMENT_KEY,
                'name': 'Dashboard Management'
            },
            {
                'key': RA_DASHBOARD_ACCESS_MANAGEMENT_KEY,
                'name': 'Dashboard Access Management'
            }
        ]
    },
    RA_VISUALIZATION_GROUP_KEY: {
        'name': RA_VISUALIZATION_GROUP_NAME,
        'module': MODULE_RA_KEY,
        'permissions': [
            {
                'key': RA_VISUALIZATION_MANAGEMENT_KEY,
                'name': 'Visualization Management'
            },
            {
                'key': RA_VISUALIZATION_ACCESS_MANAGEMENT_KEY,
                'name': 'Visualization Access Management'
            },
        ]
    }
}
