from app.permission.services.organization import OrganizationPermissionManager
from app.tenancies.models import Client
from app.tenancies.observer.interface_listener import IListener


class OrgMemberPermissionEffectListener(IListener):
    def run(self, **kwargs):
        """
        grant permission for user in all clients
        """
        user_id, organization_id = kwargs.get("user_id"), kwargs.get("organization_id")

        client_ids = Client.objects.filter(organization_id=organization_id).values_list(
            "id", flat=True)
        permission_process = OrganizationPermissionManager(organization_id)
        permission_process.run_with_user_client(client_ids=client_ids, user_ids=[user_id])
        permission_process.run_with_org_user(user_ids=[user_id])
        return
