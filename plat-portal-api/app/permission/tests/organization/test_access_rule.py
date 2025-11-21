from django.core.management import call_command
from django.urls import reverse
from rest_framework import status

from app.permission.models import AccessRule, CustomRole, CustomRoleAccessRule, AccessRulePermission, Permission
from app.tenancies.models import UserClient
from app.tenancies.tests.organization.base import OrganizationBaseTest


# Create your tests here.


class AccessRuleTest(OrganizationBaseTest):
    def setUp(self):
        super().setUp()
        self.work_space = self.create_client_organization(organization=self.organization,
                                                          name="TEST-CLIENT-1")
        self.user_client = UserClient.objects.get(user=self.user)
        call_command('config_permission')

    def test_post_create_access_rule(self):
        self.client.force_authenticate(user=self.user)
        url = reverse(viewname="org-list-create-access-rule-view",
                      kwargs={"organization_id": str(self.organization.id)})
        data = {
            "permissions_groups": [
                {
                    "group": {
                        'key': "SALE_GROUP",
                        'name': 'SALE_GROUP'
                    },
                    "permissions": [
                        {
                            "key": "SALE_IMPORT",
                            "status": "DENY"
                        }
                    ]
                }
            ],
            "name": "string"
        }
        res = self.client.post(path=url, data=data, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_get_access_rule_detail(self):
        self.client.force_authenticate(user=self.user)

        first_access_rule = AccessRule.objects.create(key='CUSTOM',
                                                      owner=self.user,
                                                      content_object=self.organization)
        url = reverse(viewname='org-retrieve-update-delete-access-rule-view',
                      kwargs={"organization_id": str(self.organization.id),
                              "pk": str(first_access_rule.id)})
        res = self.client.get(path=url, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_get_list_access_rule(self):
        self.client.force_authenticate(user=self.user)
        url = reverse(viewname="org-list-create-access-rule-view",
                      kwargs={"organization_id": str(self.organization.id)})
        res = self.client.get(path=url, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_delete_access_rule(self):
        self.client.force_authenticate(user=self.user)
        first_access_rule = AccessRule.objects.create(key='CUSTOM',
                                                      owner=self.user,
                                                      content_object=self.organization)

        AccessRulePermission.objects.create(access_rule=first_access_rule,
                                            permission=Permission.objects.first())

        first_custom_role = CustomRole.objects.create(content_object=self.organization,
                                                      owner=self.user)

        second_access_rule = AccessRule.objects.create(key='CUSTOM',
                                                       owner=self.user,
                                                       content_object=self.work_space)

        AccessRulePermission.objects.create(access_rule=second_access_rule,
                                            permission=Permission.objects.first())

        CustomRoleAccessRule.objects.create(access_rule=first_access_rule, custom_role=first_custom_role, priority=1)
        CustomRoleAccessRule.objects.create(access_rule=second_access_rule, custom_role=first_custom_role, priority=2)

        url_grant_permission_user = reverse(viewname="compose-permission-org-view",
                                            kwargs={"organization_id": str(self.organization.id),
                                                    "user_id": self.user.id})
        data = {
            "type": "APPROVE",
            "roles": [
                {
                    "id": first_custom_role.id,
                    "priority": 1
                }
            ]
        }
        res = self.client.post(path=url_grant_permission_user, data=data, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        url = reverse(viewname='org-retrieve-update-delete-access-rule-view',
                      kwargs={"organization_id": str(self.organization.id),
                              "pk": str(first_access_rule.id)})
        res = self.client.delete(path=url, format='json')
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_update_access_rule(self):
        self.client.force_authenticate(user=self.user)
        first_access_rule = AccessRule.objects.create(key='CUSTOM',
                                                      owner=self.user,
                                                      content_object=self.organization)

        AccessRulePermission.objects.create(access_rule=first_access_rule,
                                            permission=Permission.objects.first())

        first_custom_role = CustomRole.objects.create(content_object=self.organization,
                                                      owner=self.user)
        CustomRoleAccessRule.objects.create(access_rule=first_access_rule, custom_role=first_custom_role, priority=1)

        url_grant_permission_user = reverse(viewname="compose-permission-org-view",
                                            kwargs={"organization_id": str(self.organization.id),
                                                    "user_id": self.user.id})
        data = {
            "type": "APPROVE",
            "roles": [
                {
                    "id": first_custom_role.id,
                    "priority": 1
                }
            ]
        }
        res = self.client.post(path=url_grant_permission_user, data=data, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        data = {
            "permissions_groups": [
                {
                    "group": {
                        'key': "SALE_GROUP",
                        'name': 'SALE_GROUP'
                    },
                    "permissions": [
                        {
                            "key": "SALE_IMPORT",
                            "status": "ALLOW"
                        }
                    ]
                }
            ],
            "name": "string"
        }
        url = reverse(viewname='org-retrieve-update-delete-access-rule-view',
                      kwargs={"organization_id": str(self.organization.id),
                              "pk": str(first_access_rule.id)})
        res = self.client.put(path=url, data=data, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
