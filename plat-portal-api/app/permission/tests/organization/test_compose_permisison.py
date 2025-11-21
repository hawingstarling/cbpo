from django.core.management import call_command
from django.urls import reverse
from rest_framework import status

from app.permission.models import AccessRule, CustomRole, CustomRoleAccessRule, AccessRulePermission, Permission
from app.tenancies.models import UserClient
from app.tenancies.tests.organization.base import OrganizationBaseTest


# Create your tests here.


class ComposePermissionTest(OrganizationBaseTest):
    def setUp(self):
        super().setUp()
        self.work_space = self.create_client_organization(organization=self.organization,
                                                          name="TEST-CLIENT-1")
        self.user_client = UserClient.objects.get(user=self.user)
        call_command('config_permission')
        access_rule = AccessRule.objects.create(key='CUSTOM',
                                                owner=self.user,
                                                content_object=self.organization)
        first_permission = Permission.objects.first()
        AccessRulePermission.objects.create(access_rule=access_rule, permission=first_permission)
        self.custom_role = CustomRole.objects.create(content_object=self.organization,
                                                     owner=self.user)
        CustomRoleAccessRule.objects.create(access_rule=access_rule, custom_role=self.custom_role, priority=1)

    def test_compose_permission_preview(self):
        self.client.force_authenticate(user=self.user)
        url = reverse(viewname="compose-permission-org-view",
                      kwargs={"organization_id": str(self.organization.id),
                              "user_id": self.user.id})
        data = {
            "type": "PREVIEW",
            "roles": [
                {
                    "id": self.custom_role.id,
                    "priority": 1
                }
            ]
        }
        res = self.client.post(path=url, data=data, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_compose_permission_preview_addtional_permissions_groups(self):
        self.client.force_authenticate(user=self.user)
        url = reverse(viewname="compose-permission-org-view",
                      kwargs={"organization_id": str(self.organization.id),
                              "user_id": self.user.id})
        data = {
            "type": "PREVIEW",
            "roles": [
                {
                    "id": self.custom_role.id,
                    "priority": 1
                }
            ],
            "permissions_groups": [
                {
                    "group": {
                        "key": "SALE_GROUP",
                        "name": "SALE_GROUP"
                    },
                    "module": {
                        "key": "PF",
                        "name": 'Precise Financial'
                    },
                    "permissions": [
                        {
                            "key": "SALE_IMPORT",
                            "status": "DENY"
                        }
                    ]
                },
                {
                    "group": {
                        "key": "MW_REPORT_GROUP",
                        "name": 'Map Watcher'
                    },
                    "module": {
                        "key": "MAP",
                        "name": "MAP Watcher"
                    },
                    "permissions": [
                        {
                            "key": "BRAMAN",
                            "status": "DENY"
                        }
                    ]
                }
            ]
        }
        res = self.client.post(path=url, data=data, format='json')
        print(res)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_compose_permission_approve(self):
        self.client.force_authenticate(user=self.user)
        url = reverse(viewname="compose-permission-org-view",
                      kwargs={"organization_id": str(self.organization.id),
                              "user_id": self.user.id})
        data = {
            "type": "APPROVE",
            "roles": [
                {
                    "id": self.custom_role.id,
                    "priority": 1
                }
            ]
        }
        res = self.client.post(path=url, data=data, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
