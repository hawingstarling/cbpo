from app.financial.permissions.abstract_permission import AbstractMicroServicePermission

VIEW_ITEM_KEY = 'PF_ITEM_VIEW'
CREATE_ITEM_KEY = 'PF_ITEM_CREATE'
EDIT_ITEM_KEY = 'PF_ITEM_EDIT'
BULK_EDIT_ITEM_KEY = 'PF_ITEM_BULK_EDIT'
DELETE_ITEM_KEY = 'PF_ITEM_DELETE'
BULK_DELETE_ITEM_KEY = 'PF_ITEM_BULK_DELETE'
IMPORT_ITEM_KEY = 'PF_ITEM_IMPORT'


class ViewItemJwtPermission(AbstractMicroServicePermission):
    def _permission_key(self) -> str:
        return VIEW_ITEM_KEY


class CreateItemJwtPermission(AbstractMicroServicePermission):
    def _permission_key(self) -> str:
        return CREATE_ITEM_KEY


class EditItemJwtPermission(AbstractMicroServicePermission):
    def _permission_key(self) -> str:
        return EDIT_ITEM_KEY


class BulkEditItemJwtPermission(AbstractMicroServicePermission):
    def _permission_key(self) -> str:
        return BULK_EDIT_ITEM_KEY


class DeleteItemJwtPermission(AbstractMicroServicePermission):
    def _permission_key(self) -> str:
        return DELETE_ITEM_KEY


class BulkDeleteItemJwtPermission(AbstractMicroServicePermission):
    def _permission_key(self) -> str:
        return BULK_DELETE_ITEM_KEY


class ImportItemJwtPermission(AbstractMicroServicePermission):
    def _permission_key(self) -> str:
        return IMPORT_ITEM_KEY
