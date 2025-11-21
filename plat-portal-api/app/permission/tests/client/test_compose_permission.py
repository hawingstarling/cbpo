from allauth.account.models import EmailAddress
from django.urls import reverse
from rest_framework import status

from app.permission.models import (
    AccessRule,
    CustomRole,
    CustomRoleAccessRule,
    AccessRulePermission,
    Permission,
)
from app.tenancies.models import UserClient
from app.tenancies.services import UserService, RoleService
from app.tenancies.tests.organization.base import OrganizationBaseTest


# Create your tests here.


class ComposePermissionTest(OrganizationBaseTest):
    def setUp(self):
        super().setUp()
        self.work_space = self.create_client_organization(
            organization=self.organization, name="TEST-CLIENT-1"
        )
        self.user_client = UserClient.objects.get(user=self.user)
        access_rule = AccessRule.objects.create(
            key="CUSTOM", owner=self.user, content_object=self.work_space
        )
        first_permission = Permission.objects.latest("created")
        AccessRulePermission.objects.create(
            access_rule=access_rule, permission=first_permission
        )
        self.custom_role = CustomRole.objects.create(
            content_object=self.work_space, owner=self.user
        )
        CustomRoleAccessRule.objects.create(
            access_rule=access_rule, custom_role=self.custom_role, priority=1
        )

    def test_compose_permission_preview(self):
        self.client.force_authenticate(user=self.user)
        url = reverse(
            viewname="compose-permission-client-view",
            kwargs={"client_id": str(self.work_space.id), "user_id": self.user.id},
        )
        data = {
            "type": "PREVIEW",
            "roles": [{"id": self.custom_role.id, "priority": 1}],
        }
        res = self.client.post(path=url, data=data, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_compose_permission_preview_addtional_permissions_groups(self):
        self.client.force_authenticate(user=self.user)
        url = reverse(
            viewname="compose-permission-client-view",
            kwargs={"client_id": str(self.work_space.id), "user_id": self.user.id},
        )
        data = {
            "type": "PREVIEW",
            "roles": [{"id": self.custom_role.id, "priority": 1}],
            "permissions_groups": [
                {
                    "group": {"key": "SALE_GROUP", "name": "SALE_GROUP"},
                    "module": {"key": "PF", "name": "Precise Financial"},
                    "permissions": [{"key": "SALE_IMPORT", "status": "DENY"}],
                },
                {
                    "group": {"key": "MW_REPORT_GROUP", "name": "MW_REPORT_GROUP"},
                    "module": {"key": "MAP", "name": "MAP Watcher"},
                    "permissions": [{"key": "BRAMAN", "status": "DENY"}],
                },
            ],
        }
        res = self.client.post(path=url, data=data, format="json")
        print(res)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_compose_permission_approve(self):
        self.client.force_authenticate(user=self.user)
        url = reverse(
            viewname="compose-permission-client-view",
            kwargs={"client_id": str(self.work_space.id), "user_id": self.user.id},
        )
        data = {
            "type": "APPROVE",
            "roles": [{"id": self.custom_role.id, "priority": 1}],
        }
        res = self.client.post(path=url, data=data, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_compose_permission_approve_withou_permission(self):
        user_2 = UserService.create_user("test2@mailinator.com", "123123123")
        EmailAddress.objects.create(user=user_2)
        UserService.activation(user_2)
        user_client_2 = UserClient.objects.create(
            client=self.work_space, user=user_2, role=RoleService.role_staff()
        )
        user_client_2.status = "MEMBER"
        user_client_2.save()
        self.client.force_authenticate(user=user_2)
        url = reverse(
            viewname="compose-permission-client-view",
            kwargs={"client_id": str(self.work_space.id), "user_id": self.user.id},
        )
        data = {
            "type": "APPROVE",
            "roles": [{"id": self.custom_role.id, "priority": 1}],
        }
        res = self.client.post(path=url, data=data, format="json")
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
