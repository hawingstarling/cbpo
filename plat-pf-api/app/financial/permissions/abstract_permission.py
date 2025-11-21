from abc import abstractmethod
from rest_framework.permissions import AllowAny
from app.core.services.authentication_service import AuthenticationService
from app.core.services.user_permission import get_user_permission
from app.core.variable.permission import ROLE_ACCEPT


class AbstractMicroServicePermission(AllowAny):

    def has_permission(self, request, view):
        client_id_req = view.kwargs.get('client_id')
        jwt_token = AuthenticationService.get_jwt_request(request)
        user_id = AuthenticationService.get_user_id_jwt_token(jwt_token)
        permission_user = get_user_permission(jwt_token, client_id_req, user_id)
        return self.__authorize_permission_customization(permission_user)

    def __authorize_permission_customization(self, permission_user: [dict]) -> bool:
        role = permission_user.role
        permissions = permission_user.permissions
        if not permissions.get(self._permission_key()) or role not in ROLE_ACCEPT:
            return False
        return True

    @abstractmethod
    def _permission_key(self) -> str:
        raise NotImplemented
