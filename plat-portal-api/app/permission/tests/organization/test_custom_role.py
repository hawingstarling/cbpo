from django.core.management import call_command
from django.urls import reverse
from rest_framework import status

from app.permission.models import AccessRule, CustomRole, CustomRoleAccessRule
from app.tenancies.models import UserClient
from app.tenancies.tests.organization.base import OrganizationBaseTest


class CustomRoleTest(OrganizationBaseTest):
    def setUp(self):
        super().setUp()
        self.work_space = self.create_client_organization(organization=self.organization,
                                                          name="TEST-CLIENT-1")
        self.user_client = UserClient.objects.get(user=self.user)
        call_command('config_permission')

    def test_get_list_custom_roles(self):
        self.client.force_authenticate(user=self.user)
        url = reverse(viewname="org-custom-role-list-create-view",
                      kwargs={"organization_id": str(self.organization.id)})
        res = self.client.get(path=url, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_post_create_custom_role(self):
        self.client.force_authenticate(user=self.user)
        url = reverse(viewname="org-custom-role-list-create-view",
                      kwargs={"organization_id": str(self.organization.id)})
        first_access_rule = AccessRule.objects.create(key='CUSTOM',
                                                      owner=self.user,
                                                      content_object=self.organization)
        data = {
            "name": "string",
            "access_rules": [
                {
                    "id": first_access_rule.id,
                    "priority": 1
                }
            ]
        }
        res = self.client.post(path=url, data=data, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_get_detail_custom_role(self):
        self.client.force_authenticate(user=self.user)
        access_rule = AccessRule.objects.create(key='CUSTOM',
                                                owner=self.user,
                                                content_object=self.organization)
        custom_role = CustomRole.objects.create(content_object=self.organization,
                                                owner=self.user)
        CustomRoleAccessRule.objects.create(access_rule=access_rule, custom_role=custom_role, priority=1)
        url = reverse(viewname="org-custom-role-retrieve-update-destroy-view",
                      kwargs={"organization_id": str(self.organization.id),
                              "pk": custom_role.id})
        res = self.client.get(path=url, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_delete_custom_role(self):
        self.client.force_authenticate(user=self.user)
        access_rule = AccessRule.objects.create(key='CUSTOM',
                                                owner=self.user,
                                                content_object=self.organization)
        custom_role = CustomRole.objects.create(content_object=self.organization,
                                                owner=self.user)
        CustomRoleAccessRule.objects.create(access_rule=access_rule, custom_role=custom_role, priority=1)
        url = reverse(viewname="org-custom-role-retrieve-update-destroy-view",
                      kwargs={"organization_id": str(self.organization.id),
                              "pk": custom_role.id})
        res = self.client.delete(path=url, format='json')
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_update_custom_role(self):
        self.client.force_authenticate(user=self.user)
        access_rule_1 = AccessRule.objects.create(key='CUSTOM',
                                                  owner=self.user,
                                                  content_object=self.organization)
        access_rule_2 = AccessRule.objects.create(key='CUSTOM',
                                                  owner=self.user,
                                                  content_object=self.organization)
        custom_role = CustomRole.objects.create(content_object=self.organization,
                                                owner=self.user)
        CustomRoleAccessRule.objects.create(access_rule=access_rule_1, custom_role=custom_role, priority=1)
        CustomRoleAccessRule.objects.create(access_rule=access_rule_2, custom_role=custom_role, priority=2)
        data = {
            "name": "string",
            "access_rules": [
                {
                    "id": access_rule_1.id,
                    "priority": 1
                },
                {
                    "id": access_rule_2.id,
                    "priority": 2
                }
            ]
        }
        url = reverse(viewname="org-custom-role-retrieve-update-destroy-view",
                      kwargs={"organization_id": str(self.organization.id),
                              "pk": custom_role.id})
        res = self.client.put(path=url, data=data, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
