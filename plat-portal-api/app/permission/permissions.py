from rest_framework import permissions
from rest_framework.permissions import IsAuthenticated

from app.permission.config_static_varible.common import CLIENT_LEVEL_KEY


class IsAdminOrOwnerForActionRoleAndRule(IsAuthenticated):

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        level = view.get_level_view()
        if level == CLIENT_LEVEL_KEY:
            if obj.object_id != view.content_object.id:
                return False
        return True

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        # user is admin or owner or manager in org or client
        user_in_org_client = view.get_generic_obj_user_current()
        return user_in_org_client.is_admin_or_manager()
