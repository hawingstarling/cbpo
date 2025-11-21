from django.urls import reverse
from rest_framework import status

from app.permission.models import AccessRule, CustomRole, CustomRoleAccessRule, AccessRulePermission, Permission
from app.tenancies.models import UserClient
from app.tenancies.services import RoleService
from app.tenancies.tests.organization.base import OrganizationBaseTest, EmailAddress, UserService


# Create your tests here.


class AccessRuleTest(OrganizationBaseTest):
    def setUp(self):
        super().setUp()
        self.work_space = self.create_client_organization(organization=self.organization,
                                                          name="TEST-CLIENT-1")
        self.user_client = UserClient.objects.get(user=self.user)

    def test_post_create_access_rule(self):
        self.client.force_authenticate(user=self.user)
        url = reverse(viewname="list-create-access-rule-client-view",
                      kwargs={"client_id": str(self.work_space.id)})
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

    def test_post_create_access_rule_without_permission(self):
        user_2 = UserService.create_user('test2@mailinator.com', '123123123')
        EmailAddress.objects.create(user=user_2)
        UserService.activation(user_2)
        user_client_2 = UserClient.objects.create(client=self.work_space, user=user_2, role=RoleService.role_staff())
        user_client_2.status = 'MEMBER'
        user_client_2.save()
        self.client.force_authenticate(user=user_2)
        url = reverse(viewname="list-create-access-rule-client-view",
                      kwargs={"client_id": str(self.work_space.id)})
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
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_access_rule_detail(self):
        self.client.force_authenticate(user=self.user)

        first_access_rule = AccessRule.objects.create(key='CUSTOM',
                                                      owner=self.user,
                                                      content_object=self.work_space)
        url = reverse(viewname='client-access-rule-retrieve-update-destroy-view',
                      kwargs={"client_id": str(self.work_space.id),
                              "pk": str(first_access_rule.id)})
        res = self.client.get(path=url, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_get_list_access_rule(self):
        self.client.force_authenticate(user=self.user)
        url = reverse(viewname="list-create-access-rule-client-view",
                      kwargs={"client_id": str(self.work_space.id)})
        res = self.client.get(path=url, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_delete_access_rule(self):
        self.client.force_authenticate(user=self.user)
        first_access_rule = AccessRule.objects.create(key='CUSTOM',
                                                      owner=self.user,
                                                      content_object=self.work_space)

        AccessRulePermission.objects.create(access_rule=first_access_rule,
                                            permission=Permission.objects.first())

        second_access_rule = AccessRule.objects.create(key='CUSTOM',
                                                       owner=self.user,
                                                       content_object=self.work_space)

        AccessRulePermission.objects.create(access_rule=second_access_rule,
                                            permission=Permission.objects.first())

        first_custom_role = CustomRole.objects.create(content_object=self.work_space,
                                                      owner=self.user)
        CustomRoleAccessRule.objects.create(access_rule=first_access_rule, custom_role=first_custom_role, priority=1)
        CustomRoleAccessRule.objects.create(access_rule=second_access_rule, custom_role=first_custom_role, priority=2)

        url_grant_permission_user = reverse(viewname="compose-permission-client-view",
                                            kwargs={"client_id": str(self.work_space.id),
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

        url = reverse(viewname='client-access-rule-retrieve-update-destroy-view',
                      kwargs={"client_id": str(self.work_space.id),
                              "pk": str(first_access_rule.id)})
        res = self.client.delete(path=url, format='json')
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_update_access_rule(self):
        self.client.force_authenticate(user=self.user)
        first_access_rule = AccessRule.objects.create(key='CUSTOM',
                                                      owner=self.user,
                                                      content_object=self.work_space)

        AccessRulePermission.objects.create(access_rule=first_access_rule,
                                            permission=Permission.objects.first())

        first_custom_role = CustomRole.objects.create(content_object=self.work_space,
                                                      owner=self.user)
        CustomRoleAccessRule.objects.create(access_rule=first_access_rule, custom_role=first_custom_role, priority=1)

        url_grant_permission_user = reverse(viewname="compose-permission-client-view",
                                            kwargs={"client_id": str(self.work_space.id),
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
        url = reverse(viewname='client-access-rule-retrieve-update-destroy-view',
                      kwargs={"client_id": str(self.work_space.id),
                              "pk": str(first_access_rule.id)})
        res = self.client.put(path=url, data=data, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_delete_access_rule_of_ogr(self):
        self.client.force_authenticate(user=self.user)
        first_access_rule = AccessRule.objects.create(key='CUSTOM',
                                                      owner=self.user,
                                                      content_object=self.organization)
        AccessRulePermission.objects.create(access_rule=first_access_rule,
                                            permission=Permission.objects.first())
        url = reverse(viewname='client-access-rule-retrieve-update-destroy-view',
                      kwargs={"client_id": str(self.work_space.id),
                              "pk": str(first_access_rule.id)})
        res = self.client.delete(path=url, format='json')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
