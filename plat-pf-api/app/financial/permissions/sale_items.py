from app.financial.permissions.base import JwtTokenPermission
from app.financial.services.user_permission import UserPermissionManage


class SaleItemSingleUpdatePermission(JwtTokenPermission):

    def has_permission(self, request, view):
        super().has_permission(request, view)
        permission = UserPermissionManage()
        permission.has_single_edit_sale_item()
        return True


class SaleItemSingleDeletePermission(JwtTokenPermission):

    def has_permission(self, request, view):
        super().has_permission(request, view)
        permission = UserPermissionManage()
        permission.has_single_delete_sale_item()
        return True


class SaleItemBulkUpdatePermission(JwtTokenPermission):

    def has_permission(self, request, view):
        super().has_permission(request, view)
        permission = UserPermissionManage()
        permission.has_bulk_edit_sale_item()
        return True


class SaleItemBulkDeletePermission(JwtTokenPermission):

    def has_permission(self, request, view):
        super().has_permission(request, view)
        permission = UserPermissionManage()
        permission.has_bulk_delete_sale_item()
        return True
