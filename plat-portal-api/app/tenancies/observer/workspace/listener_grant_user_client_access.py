from app.permission.services.organization import OrganizationPermissionManager
from app.tenancies.config_static_variable import IS_MEMBER
from app.tenancies.models import OrganizationUser, UserClient, Client, Organization
from app.tenancies.observer.interface_listener import IListener
from app.tenancies.services import (
    OrganizationRoleActionService,
    RoleService,
)


class GrantUserClientAccessListener(IListener):
    def run(self, **kwargs):
        """Assign admin and owner in the ORG to new Client"""
        client_id, organization_id = (
            kwargs.get("client_id"),
            kwargs.get("organization_id"),
        )
        client = Client.objects.get(id=client_id)
        organization = Organization.objects.get(id=organization_id)
        if client.active is False:
            # no access
            return

        # users in organization
        user_ids = OrganizationUser.objects.filter(
            organization=organization,
            role__key__in=OrganizationRoleActionService.get_role_action_with_all_organization(),
            status=IS_MEMBER,
        ).values_list("user_id", flat=True)
        role_owner = RoleService.role_owner()
        # create user in client
        _ = UserClient.objects.bulk_create(
            [
                UserClient(
                    client_id=client.id,
                    user_id=_user_id,
                    status=IS_MEMBER,
                    role=role_owner,
                )
                for _user_id in user_ids
            ]
        )
        # assign access permission for user client
        permission_manager = OrganizationPermissionManager(organization)
        permission_manager.process_user_in_ws([client.id])
