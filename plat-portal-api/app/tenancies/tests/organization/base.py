import json
from unittest.mock import patch

from allauth.account.models import EmailAddress
from django.urls import reverse
from rest_framework.test import APITestCase

from app.core.utils import *
from app.tenancies.models import *
from app.tenancies.tests.base import *


@patch("app.core.context.AppContext", init_app_context())
class OrganizationBaseTest(APITestCase):
    fixtures = fixtures

    def setUp(self):
        self.user = self.init_user()
        self.organization = self.create_organization(name="CBPO", user=self.user)

    def init_list_users(
        self,
        email_format: str = "test{}@test.com",
        password: str = "1234567890",
        number: int = 10,
    ):
        for item in range(1, number, 1):
            self.init_user(email=email_format.format(item), password=password)

    def init_user(self, email: str = "test@demo.com", password="123456"):
        user, _ = init_user(email=email, password=password)
        EmailAddress.objects.get_or_create(user=user, email=user.email, verified=True)
        return user

    def create_organization(self, name: str = None, user: User = None):
        if user:
            user.can_create_client = True
            user.save()
        url = reverse("register-organization")
        data = {"name": name}
        self.client.force_authenticate(user=user)
        rs = self.client.post(url, data=data, format="json")
        print(rs)
        self.assertEqual(rs.status_code, status.HTTP_201_CREATED)
        content = json.loads(rs.content.decode("utf-8"))
        return Organization.objects.get(pk=content["id"])

    def create_client_organization(
        self, name: str = None, organization: Organization = None
    ):
        url = reverse(
            "list-create-organization-client", kwargs={"pk": str(organization.pk)}
        )
        data = {"name": name}
        rs = self.client.post(url, data=data, format="json")
        self.assertEqual(rs.status_code, status.HTTP_201_CREATED)
        content = json.loads(rs.content.decode("utf-8"))
        self.assertEqual(content is not None, True)
        return Client.objects.get(pk=content["id"])

    def verify_grant_access_user_organization_sucess(
        self, user: User = None, organization: Organization = None, role: Role = None
    ):
        user_organization = OrganizationUser.objects.filter(
            user=user, organization=organization, role=role
        )
        self.assertEqual(user_organization.exists(), True)
        #
        clients = Client.objects.filter(organization=organization, active=True)
        user_clients = UserClient.objects.filter(
            user=user,
            client_id__in=clients.values_list("id", flat=True),
            status=MEMBER_STATUS[0][0],
            role=RoleService.role_owner(),
        )
        self.assertEqual(user_clients.count(), clients.count())

    def verify_grant_access_user_organization_normal(
        self, user: User = None, organization: Organization = None, role: Role = None
    ):
        user_organization = OrganizationUser.objects.filter(
            user=user, organization=organization, role=role
        )
        self.assertEqual(user_organization.exists(), True)
        #
        clients = Client.objects.filter(organization=organization, active=True)
        user_clients = UserClient.objects.filter(
            user=user,
            client_id__in=clients.values_list("id", flat=True),
            status=MEMBER_STATUS[0][0],
            role=RoleService.role_owner(),
        )
        self.assertEqual(user_clients.count(), 0)
        #
        modules_app_profile = AppService.get_all_modules_app()

    def invitation_organization_user(
        self,
        organization: Organization = None,
        user_invitation: User = None,
        user_create: User = None,
        role_name: str = None,
    ):
        if not role_name:
            role_name = "staff"
        self.client.force_authenticate(user=user_create)
        url = reverse(
            "organization-invitation-users", kwargs={"pk": str(organization.pk)}
        )
        data = {
            "role": role_name,
            "email": user_invitation.email,
            "first_name": "invitation",
            "last_name": "Test",
            "activation_link_template": "http://localhost.com/?token={token}",
        }
        rs = self.client.post(path=url, data=data, format="json")
        print(rs)
        self.assertEqual(rs.status_code, status.HTTP_200_OK)
        #
        user_organization = OrganizationUser.objects.get(
            organization=organization, user=user_invitation
        )
        self.assertEqual(user_organization.status, MEMBER_STATUS[1][0])
        return user_organization

    def invitation_organization_accept(
        self,
        user_invitation: User = None,
        organization: Organization = None,
        user_create: User = None,
        role_name: str = None,
    ):
        user_organization = self.invitation_organization_user(
            organization=organization,
            user_invitation=user_invitation,
            user_create=user_create,
            role_name=role_name,
        )
        # accept invitation organization
        token = OrganizationService.generate_token_invitation(
            user=user_invitation, organization=organization
        )
        #
        self.client.force_authenticate(user=user_invitation)
        url = reverse(
            "organization-invitation-users-validate-token", kwargs={"token": token}
        )
        rs = self.client.get(path=url, format="json")
        content = json.loads(rs.content.decode("utf-8"))
        print("Validate token {}".format(content))
        self.assertEqual(rs.status_code, status.HTTP_200_OK)
        self.assertEqual(content["status"], None)
        #
        rs = self.client.get(path=url, format="json")
        self.assertEqual(rs.status_code, status.HTTP_200_OK)
        content = json.loads(rs.content.decode("utf-8"))
        print("Content validate token : {}".format(content))
        self.assertEqual(content["status"], "Accept")
        #
        user_organization.refresh_from_db()
        self.assertEqual(user_organization.status, MEMBER_STATUS[0][0])

    def invitation_organization_denied(
        self,
        user_invitation: User = None,
        organization: Organization = None,
        user_create: User = None,
    ):
        self.invitation_organization_user(
            organization=organization,
            user_invitation=user_invitation,
            user_create=user_create,
        )
        # accept invitation organization
        notification = Notification.objects.filter(
            type=TYPE_NOTIFICATION[0][0],
            object_id=str(organization.pk),
            object_type=ContentType.objects.get_for_model(organization),
            user=user_invitation,
            is_seen=False,
            status=NOTIFICATION_STATUS[0][0],
        ).first()
        print("Notification : {}".format(str(notification.pk)))
        self.assertNotEqual(notification, None, msg="Notification is not None")
        #
        self.client.force_authenticate(user=user_invitation)
        url = reverse(
            "user-notification-update-is-seen-denied",
            kwargs={"notification_id": str(notification.pk)},
        )
        rs = self.client.put(path=url)
        self.assertEqual(rs.status_code, status.HTTP_200_OK)
        #
        url = reverse(
            "organization-invitation-users-validate-token",
            kwargs={"token": notification.meta.get("invitation_token", None)},
        )
        rs = self.client.get(path=url, format="json")
        self.assertEqual(rs.status_code, status.HTTP_200_OK)
        content = json.loads(rs.content.decode("utf-8"))
        print("Content validate token : {}".format(content))
        self.assertEqual(content["status"], "Decline")

    def verify_manage_client_organization(
        self,
        organization: Organization = None,
        client: Client = None,
        user: User = None,
    ):
        OrganizationUser.objects.get(user=user, organization=organization)
        #
        modules_app_profile = get_modules_app_profile()
        client_modules = ClientModule.objects.filter(
            client=client, module__in=modules_app_profile, enabled=True
        )
        self.assertEqual(client_modules.count() > 0, True)
        #
        # LEGACY PERMISSION -> REMOVE
        # client_module_permissions = UserModulePermission.objects.filter(user=user, client=client, enabled=True,
        #                                                                 module__in=modules_app_profile)
        # self.assertEqual(client_module_permissions.count() > 0, True)
