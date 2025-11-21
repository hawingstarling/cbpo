MODULE_DS_KEY = 'DS'
MODULE_DS_NAME = 'Data Source'

DS_GROUP_KEY = 'DS_GROUP'
DS_GROUP_NAME = 'Data Sources'

DS_GROUP_ENUM = (DS_GROUP_KEY, DS_GROUP_NAME)

DS_MANAGEMENT_KEY = 'ds_man'
DS_FEED_MANAGEMENT_KEY = 'ds_feed_man'
DS_FEED_EXECUTION_KEY = 'ds_feed_exe'

permission_module_ds_config = {
    DS_GROUP_KEY: {
        'name': DS_GROUP_NAME,
        'module': MODULE_DS_KEY,
        'permissions': [
            {
                'key': DS_MANAGEMENT_KEY,
                'name': 'Data Source Management',
            },
            {
                'key': DS_FEED_MANAGEMENT_KEY,
                'name': 'Data Feed Management'
            },
            {
                'key': DS_FEED_EXECUTION_KEY,
                'name': 'Data Feed Execution'
            },
        ]
    }
}
