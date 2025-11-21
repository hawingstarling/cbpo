from app.core.context import AppContext
from app.core.exceptions import AnalysisDataException, FedExException
from app.core.services.user_permission import get_user_permission
from app.core.variable.permission import ROLE_ACCEPT


class UserPermissionManage:
    def __init__(self):
        context = AppContext().instance()
        self.client_id = context.client_id
        self.user_id = context.user_id
        self.jwt_token = context.jwt_token

    def has_single_edit_sale_item(self):
        permission_user = get_user_permission(self.jwt_token, self.client_id, self.user_id)
        role = permission_user.role
        permissions = permission_user.permissions
        if not permissions.get('SALE_SINGLE_EDIT') or role not in ROLE_ACCEPT:
            raise AnalysisDataException(message="You can not permission edit record")
        return True

    def has_single_delete_sale_item(self):
        permission_user = get_user_permission(self.jwt_token, self.client_id, self.user_id)
        role = permission_user.role
        permissions = permission_user.permissions
        if not permissions.get('SALE_SINGLE_DELETE') or role not in ROLE_ACCEPT:
            raise AnalysisDataException(message="You can not permission edit record")
        return True

    def has_bulk_edit_sale_item(self):
        permission_user = get_user_permission(self.jwt_token, self.client_id, self.user_id)
        role = permission_user.role
        permissions = permission_user.permissions
        if not permissions.get('SALE_BULK_EDIT') or role not in ROLE_ACCEPT:
            raise AnalysisDataException(message="You can not permission edit record")
        return True

    def has_bulk_delete_sale_item(self):
        permission_user = get_user_permission(self.jwt_token, self.client_id, self.user_id)
        role = permission_user.role
        permissions = permission_user.permissions
        if not permissions.get('SALE_BULK_DELETE') or role not in ROLE_ACCEPT:
            raise AnalysisDataException(message="You can not permission edit record")
        return True

    def has_view_fedex_shipment(self):
        permission_user = get_user_permission(self.jwt_token, self.client_id, self.user_id)
        role = permission_user.role
        permissions = permission_user.permissions
        if not permissions.get('PF_FEDEX_VIEW') or role not in ROLE_ACCEPT:
            raise FedExException(message="You don't have permission to view FedEx shipment")
        return True

    def has_import_fedex_shipment(self):
        permission_user = get_user_permission(self.jwt_token, self.client_id, self.user_id)
        role = permission_user.role
        permissions = permission_user.permissions
        if not permissions.get('PF_FEDEX_IMPORT') or role not in ROLE_ACCEPT:
            raise FedExException(message="You don't have permission to import FedEx shipment")
        return True
