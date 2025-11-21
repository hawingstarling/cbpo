from app.core.context import AppContext
from app.core.services.user_permission import get_user_permission
from app.core.variable.permission import ROLE_OWNER
from app.financial.models import Alert
from app.financial.permissions.base import JwtTokenPermission


class DeleteAlertPermission(JwtTokenPermission):

    def has_permission(self, request, view):
        super().has_permission(request, view)
        obj_id = view.kwargs['pk']
        user_id = AppContext.instance().user_id
        client_id = view.kwargs['client_id']
        alert = Alert.objects.tenant_db_for(client_id).get(pk=obj_id)
        user_permission = get_user_permission(AppContext.instance().jwt_token, client_id, user_id)
        if str(user_id) == str(alert.creator_id) or user_permission.role in ROLE_OWNER:
            return True
        return False
