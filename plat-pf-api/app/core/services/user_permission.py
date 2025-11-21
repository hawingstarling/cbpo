import logging

from app.core.services.workspace_management import WorkspaceManagement
from app.core.variable.permission import MODULE_PF_KEY
from app.financial.models import UserPermission

logger = logging.getLogger(__name__)


def find_user_permission(client_id, user_id, module: str = MODULE_PF_KEY):
    logger.debug(f"[utils][find_user_permission] client_id={client_id}, user_id={user_id}, module={module}")
    return UserPermission.objects.tenant_db_for(client_id).get(client_id=client_id, user_id=user_id,
                                                               module=module, module_enabled=True)


def get_user_permission(jwt_token, client_id, user_id, module: str = MODULE_PF_KEY):
    assert client_id is not None, f"[utils][get_user_permission] client_id is not empty"
    assert user_id is not None, f"[utils][get_user_permission] user_id is not empty"
    try:
        user_permission = find_user_permission(client_id, user_id, module)
    except UserPermission.DoesNotExist:
        assert jwt_token is not None, f"[utils][get_user_permission] jwt_token is not empty"
        WorkspaceManagement(client_id=client_id, jwt_token=jwt_token) \
            .sync_client_setting_user_ps(user_id=user_id)
        user_permission = find_user_permission(client_id, user_id, module)
    except Exception as ex:
        raise ex
    return user_permission
