from app.permission.services.organization import OrganizationPermissionManager
from app.tenancies.observer.interface_listener import IListener


class CreateOrgMemberEffectListener(IListener):
    def run(self, **kwargs):
        """
        grant permission OrganizationUser
        """
        user_id, organization_id = kwargs.get("user_id"), kwargs.get("organization_id")
        permission_process = OrganizationPermissionManager(organization_id)
        permission_process.run_with_org_user([user_id])
