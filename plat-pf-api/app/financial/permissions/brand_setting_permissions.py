from app.financial.permissions.abstract_permission import AbstractMicroServicePermission

BRAND_SETTING_VIEW_KEY = 'PF_BRAND_SETTING_VIEW'
BRAND_SETTING_EDIT_KEY = 'PF_BRAND_SETTING_EDIT'
BRAND_SETTING_DELETE_KEY = 'PF_BRAND_SETTING_DELETE'
BRAND_SETTING_IMPORT_KEY = 'PF_BRAND_SETTING_IMPORT'
BRAND_SETTING_EXPORT_KEY = 'PF_BRAND_SETTING_EXPORT'
BRAND_SETTING_UPDATE_ITEM_KEY = 'PF_BRAND_SETTING_UPDATE_ITEMS'
BRAND_SETTING_UPDATE_SALE_KEY = 'PF_BRAND_SETTING_UPDATE_SALES'


class ViewBrandSettingJwtPermission(AbstractMicroServicePermission):
    def _permission_key(self) -> str:
        return BRAND_SETTING_VIEW_KEY


class CreateBrandSettingJwtPermission(AbstractMicroServicePermission):
    def _permission_key(self) -> str:
        return BRAND_SETTING_IMPORT_KEY


class ExportBrandSettingJwtPermission(AbstractMicroServicePermission):

    def _permission_key(self) -> str:
        return BRAND_SETTING_EXPORT_KEY


class EditBrandSettingJwtPermission(AbstractMicroServicePermission):
    def _permission_key(self) -> str:
        return BRAND_SETTING_EDIT_KEY


class DeleteBrandSettingJwtPermission(AbstractMicroServicePermission):
    def _permission_key(self) -> str:
        return BRAND_SETTING_DELETE_KEY


class UpdateSaleBrandSettingJwtPermission(AbstractMicroServicePermission):
    def _permission_key(self) -> str:
        return BRAND_SETTING_UPDATE_SALE_KEY


class UpdateItemBrandSettingJwtPermission(AbstractMicroServicePermission):
    def _permission_key(self) -> str:
        pass
