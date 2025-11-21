from rest_framework.permissions import AllowAny, IsAuthenticated, BasePermission

from app.core.context import AppContext
from app.core.exceptions import JwtTokenRequiredException, ClientUserException, InternalTokenRequiredException
from app.core.logger import logger
from app.core.services.portal_service import PortalService
from app.financial.models import UserPermission
from config.settings.common import INTERNAL_TOKEN


class JwtTokenPermission(AllowAny):
    def has_permission(self, request, view):
        jwt_token = AppContext.instance().jwt_token
        if not jwt_token:
            raise JwtTokenRequiredException()
        return True


class ClientUserPermission(JwtTokenPermission):
    def has_permission(self, request, view):
        super().has_permission(request, view)
        jwt_token = AppContext.instance().jwt_token
        client_id = AppContext.instance().client_id
        user_id = AppContext.instance().user_id
        try:
            PortalService(client_id=client_id, jwt_token=jwt_token).get_client_setting_user_ps(user_id=user_id)
        except Exception as ex:
            raise ClientUserException(message="Invalid param client or token")
        return True


class ClientUserSyncPermission(JwtTokenPermission):
    def has_permission(self, request, view):
        super().has_permission(request, view)
        client_id = AppContext.instance().client_id
        user_id = AppContext.instance().user_id
        num_permissions_module = UserPermission.objects.tenant_db_for(client_id).filter(user_id=user_id)
        if num_permissions_module == 0:
            raise ClientUserException(message="Invalid param client or token")
        return True
