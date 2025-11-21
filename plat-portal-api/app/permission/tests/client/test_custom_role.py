from django.urls import reverse
from rest_framework import status

from app.permission.models import AccessRule, CustomRole, CustomRoleAccessRule
from app.tenancies.models import UserClient
from app.tenancies.services import UserService, RoleService
from app.tenancies.tests.organization.base import OrganizationBaseTest, EmailAddress


class CustomRoleTest(OrganizationBaseTest):
    def setUp(self):
        super().setUp()
        self.work_space = self.create_client_organization(organization=self.organization,
                                                          name="TEST-CLIENT-1")
        self.user_client = UserClient.objects.get(user=self.user)

    def test_get_list_custom_roles(self):
        self.client.force_authenticate(user=self.user)
        url = reverse(viewname="client-custom-role-list-create-view",
                      kwargs={"client_id": str(self.work_space.id)})
        res = self.client.get(path=url, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_post_create_custom_role(self):
        self.client.force_authenticate(user=self.user)
        url = reverse(viewname="client-custom-role-list-create-view",
                      kwargs={"client_id": str(self.work_space.id)})
        first_access_rule = AccessRule.objects.create(key='CUSTOM',
                                                      owner=self.user,
                                                      content_object=self.work_space)
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

    def test_post_create_custom_role_without_permission(self):
        user_2 = UserService.create_user('test2@mailinator.com', '123123123')
        EmailAddress.objects.create(user=user_2)
        UserService.activation(user_2)
        user_client_2 = UserClient.objects.create(client=self.work_space, user=user_2, role=RoleService.role_staff())
        user_client_2.status = 'MEMBER'
        user_client_2.save()
        self.client.force_authenticate(user=user_2)
        url = reverse(viewname="client-custom-role-list-create-view",
                      kwargs={"client_id": str(self.work_space.id)})
        first_access_rule = AccessRule.objects.create(key='CUSTOM',
                                                      owner=self.user,
                                                      content_object=self.work_space)
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
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_detail_custom_role(self):
        self.client.force_authenticate(user=self.user)
        access_rule = AccessRule.objects.create(key='CUSTOM',
                                                owner=self.user,
                                                content_object=self.work_space)
        custom_role = CustomRole.objects.create(content_object=self.work_space,
                                                owner=self.user)
        CustomRoleAccessRule.objects.create(access_rule=access_rule, custom_role=custom_role, priority=1)
        url = reverse(viewname="client-custom-role-retrieve-update-destroy-view",
                      kwargs={"client_id": str(self.work_space.id),
                              "pk": custom_role.id})
        res = self.client.get(path=url, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_delete_custom_role(self):
        self.client.force_authenticate(user=self.user)
        access_rule = AccessRule.objects.create(key='CUSTOM',
                                                owner=self.user,
                                                content_object=self.work_space)
        custom_role = CustomRole.objects.create(content_object=self.work_space,
                                                owner=self.user)
        CustomRoleAccessRule.objects.create(access_rule=access_rule, custom_role=custom_role, priority=1)
        url = reverse(viewname="client-custom-role-retrieve-update-destroy-view",
                      kwargs={"client_id": str(self.work_space.id),
                              "pk": custom_role.id})
        res = self.client.delete(path=url, format='json')
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_update_custom_role(self):
        self.client.force_authenticate(user=self.user)
        access_rule_1 = AccessRule.objects.create(key='CUSTOM',
                                                  owner=self.user,
                                                  content_object=self.work_space)
        access_rule_2 = AccessRule.objects.create(key='CUSTOM',
                                                  owner=self.user,
                                                  content_object=self.work_space)
        custom_role = CustomRole.objects.create(content_object=self.work_space,
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
        url = reverse(viewname="client-custom-role-retrieve-update-destroy-view",
                      kwargs={"client_id": str(self.work_space.id),
                              "pk": custom_role.id})
        res = self.client.put(path=url, data=data, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_delete_custom_role_of_org(self):
        self.client.force_authenticate(user=self.user)
        access_rule = AccessRule.objects.create(key='CUSTOM',
                                                owner=self.user,
                                                content_object=self.organization)
        custom_role = CustomRole.objects.create(content_object=self.organization,
                                                owner=self.user)
        CustomRoleAccessRule.objects.create(access_rule=access_rule, custom_role=custom_role, priority=1)
        url = reverse(viewname="client-custom-role-retrieve-update-destroy-view",
                      kwargs={"client_id": str(self.work_space.id),
                              "pk": custom_role.id})
        res = self.client.delete(path=url, format='json')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
