from app.financial.permissions.base import JwtTokenPermission
from app.financial.services.user_permission import UserPermissionManage

class ViewFedExShipmentPermission(JwtTokenPermission):

    def has_permission(self, request, view):
        super().has_permission(request, view)
        permission = UserPermissionManage()
        permission.has_view_fedex_shipment()
        return True

class FedExShipmentImportPermission(JwtTokenPermission):

    def has_permission(self, request, view):
        return super().has_permission(request, view)