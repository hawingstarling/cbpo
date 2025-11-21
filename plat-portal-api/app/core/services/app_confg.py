from app.tenancies.config_app_and_module import APP_NAME_BUILD_PROFILE, APP_BUILD_PROFILE_CONFIG
from app.tenancies.config_static_variable import MODULE_ENUM


class AppService:

    @staticmethod
    def get_all_module_enum():
        return dict(MODULE_ENUM)

    @staticmethod
    def get_permission_by_module(module_permissions_app: list, module_name):
        data = []
        if module_name:
            for module, permission in module_permissions_app:
                if module_name == module:
                    data.append(permission)
        return sorted(data)

    @staticmethod
    def get_permissions_app(app_name: str = None, module_name: str = None):
        module_permissions = AppService.get_module_permissions_app(app_name=app_name)
        data = []
        if module_name:
            for module, permission in module_permissions:
                if module_name == module:
                    data.append(permission)
            return data
        for module, permission in module_permissions:
            data.append(permission)
        return sorted(data)

    @staticmethod
    def get_module_permissions_app(app_name: str = None):
        if not app_name or app_name not in APP_NAME_BUILD_PROFILE:
            return []
        config = APP_BUILD_PROFILE_CONFIG.get(app_name)
        data = ()
        for item in config:
            data += config[item]
        return list(data)

    @staticmethod
    def get_all_module_permissions_app():
        data = []
        for app in APP_NAME_BUILD_PROFILE:
            data += AppService.get_module_permissions_app(app_name=app)
        # remove same item
        data = list(set(data))
        return sorted(data, key=lambda tup: tup[0])

    @staticmethod
    def get_modules_app(app_name: str = None):
        if not app_name or app_name not in APP_NAME_BUILD_PROFILE:
            return []
        config = APP_BUILD_PROFILE_CONFIG.get(app_name)
        return list(sorted(config.keys()))

    @staticmethod
    def get_all_modules_app():
        list_modules = []
        for app in APP_NAME_BUILD_PROFILE:
            list_modules += AppService.get_modules_app(app_name=app)
        # remove same item
        list_modules = list(set(list_modules))
        return sorted(list_modules)
