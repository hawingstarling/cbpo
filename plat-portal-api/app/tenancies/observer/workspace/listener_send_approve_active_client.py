from app.tenancies.config_static_variable import MEMBER_STATUS
from app.tenancies.models import Client, Organization, User
from app.tenancies.observer.interface_listener import IListener
from app.tenancies.services import EmailService, OrganizationService, RoleService


class SendEmailActiveClientListener(IListener):
    def run(self, **kwargs):
        user_id, users_approve, client_id, organization_id = (
            kwargs.get("user_id"),
            kwargs.get("users_approve"),
            kwargs.get("client_id"),
            kwargs.get("organization_id"),
        )
        client = Client.objects.get(id=client_id)
        organization = Organization.objects.get(id=organization_id)
        user = User.objects.get(user_id=user_id)

        if client.active is True:
            return
        # TODO: check setting and celery
        users_approve = OrganizationService.queryset_list_users_organization(
            organization=organization,
            roles=[RoleService.role_owner().key],
            organizationuser__status=MEMBER_STATUS[0][0],
        ).all()
        EmailService.send_approve_active_client_email(
            user_create=user,
            users_approve=users_approve,
            client=client,
            organization=organization,
        )
