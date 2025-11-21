from app.financial.permissions.abstract_permission import AbstractMicroServicePermission

CLIENT_SETTINGS_VIEW_KEY = 'CLIENT_SETTINGS_VIEW'
CLIENT_SETTINGS_CHANGE_KEY = 'CLIENT_SETTINGS_CHANGE'


class ViewClientSettingsJwtPermission(AbstractMicroServicePermission):
    def _permission_key(self) -> str:
        return CLIENT_SETTINGS_VIEW_KEY


class ChangeClientSettingsJwtPermission(AbstractMicroServicePermission):
    def _permission_key(self) -> str:
        return CLIENT_SETTINGS_CHANGE_KEY
