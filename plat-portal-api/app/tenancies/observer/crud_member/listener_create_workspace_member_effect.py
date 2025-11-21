from app.permission.services.organization import OrganizationPermissionManager
from app.tenancies.observer.interface_listener import IListener


class CreateWorkspaceMemberEffectListener(IListener):
    def run(self, **kwargs):
        """
        grant permission UserClient
        """
        user_id, organization_id, client_id = kwargs.get("user_id"), kwargs.get("organization_id"), kwargs.get(
            "client_id")
        permission_process = OrganizationPermissionManager(organization_id)
        permission_process.run_with_user_client([client_id], [user_id])
