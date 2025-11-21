from app.tenancies.tests.organization.base import *


class OrganizationUserStaffTest(OrganizationBaseTest):

    def test_create_client_organization(self):
        organization = self.create_organization(name="TEST-CREATE-ORG", user=self.user)
        # invite user to staff
        #
        user1 = self.init_user(email='testdemo2@test.com', password='1234567890')
        self.invitation_organization_accept(organization=organization, user_invitation=user1,
                                            user_create=self.user, role_name='staff')

        self.verify_grant_access_user_organization_normal(user=user1, organization=organization,
                                                          role=RoleService.role_staff())
        # CAES 1: enabled all modules
        self.client.force_authenticate(user=user1)
        url = reverse('list-create-organization-client', kwargs={'pk': str(organization.pk)})
        data = {
            'name': "WS STAFF 1"
        }
        rs = self.client.post(url, data=data, format='json')
        self.assertEqual(rs.status_code, status.HTTP_201_CREATED)
        content = json.loads(rs.content.decode('utf-8'))
        print("Client is created : {}".format(content))
        self.assertEqual(content is not None, True)
        self.assertEqual(content['active'], False)
        # active client
        url = reverse(viewname="organization-approval-client-to-active",
                      kwargs={'pk': str(organization.pk), 'client_id': content['id']})
        self.client.force_authenticate(user=self.user)
        rs = self.client.post(path=url, format='json')
        self.assertEqual(rs.status_code, status.HTTP_200_OK)
        #
        self.verify_grant_access_user_organization_sucess(user=user1, organization=organization,
                                                          role=RoleService.role_staff())

        # CASE 2 : edit enabled modules
        self.client.force_authenticate(user=user1)
        url = reverse('list-create-organization-client', kwargs={'pk': str(organization.pk)})
        data = {
            'name': "WS STAFF 2"
        }
        rs = self.client.post(url, data=data, format='json')
        self.assertEqual(rs.status_code, status.HTTP_201_CREATED)
        content = json.loads(rs.content.decode('utf-8'))
        print("Client is created : {}".format(content))
        self.assertEqual(content is not None, True)
        self.assertEqual(content['active'], False)
        #
        clients_modules = ClientModule.objects.filter(client_id=content['id'])
        num_module = clients_modules.count()
        self.assertEqual(num_module > 0, True)
        num_module_enable = clients_modules.filter(enabled=True).count()
        # there is one module enable -> MAP
        self.assertEqual(1, num_module_enable)
        #
        self.client.force_authenticate(user=self.user)
        data = {
            "client": content['id'],
            "module": "MAP",
            "enabled": False
        }
        url = reverse(viewname="client-module-switching", kwargs={'client_id': content['id'], 'module': 'MAP'})
        rs = self.client.put(path=url, data=data, format='json')
        self.assertEqual(rs.status_code, status.HTTP_200_OK)
        # turn off module  MAP -> none of enable modules
        self.assertEqual(0, clients_modules.filter(enabled=True).count())
        # active client
        url = reverse(viewname="organization-approval-client-to-active",
                      kwargs={'pk': str(organization.pk), 'client_id': content['id']})
        rs = self.client.post(path=url, format='json')
        self.assertEqual(rs.status_code, status.HTTP_200_OK)
        #
        self.verify_grant_access_user_organization_sucess(user=user1, organization=organization,
                                                          role=RoleService.role_staff())

    def test_change_role_to_manager(self):
        organization = self.create_organization(name="TEST-CREATE-ORG1", user=self.user)
        # invite user to staff
        #
        user1 = self.init_user(email='testdemo3@test.com', password='1234567890')
        self.invitation_organization_accept(organization=organization, user_invitation=user1,
                                            user_create=self.user, role_name='staff')

        self.verify_grant_access_user_organization_normal(user=user1, organization=organization,
                                                          role=RoleService.role_staff())
        #
        self.client.force_authenticate(user=user1)
        url = reverse('list-create-organization-client', kwargs={'pk': str(organization.pk)})
        data = {
            'name': "WS STAFF 2"
        }
        rs = self.client.post(url, data=data, format='json')
        self.assertEqual(rs.status_code, status.HTTP_201_CREATED)
        content = json.loads(rs.content.decode('utf-8'))
        print("Client is created : {}".format(content))
        self.assertEqual(content is not None, True)
        self.assertEqual(content['active'], False)
        # active client
        url = reverse(viewname="organization-approval-client-to-active",
                      kwargs={'pk': str(organization.pk), 'client_id': content['id']})
        self.client.force_authenticate(user=self.user)
        rs = self.client.post(path=url, format='json')
        self.assertEqual(rs.status_code, status.HTTP_200_OK)
        #
        self.verify_grant_access_user_organization_sucess(user=user1, organization=organization,
                                                          role=RoleService.role_staff())
        #

        self.client.force_authenticate(user=user1)
        url = reverse('list-create-organization-client', kwargs={'pk': str(organization.pk)})
        data = {
            'name': "WS STAFF 3"
        }
        rs = self.client.post(url, data=data, format='json')
        self.assertEqual(rs.status_code, status.HTTP_201_CREATED)
        content = json.loads(rs.content.decode('utf-8'))
        print("Client is created : {}".format(content))
        self.assertEqual(content is not None, True)
        self.assertEqual(content['active'], False)

        # Change role user staff
        self.client.force_authenticate(user=self.user)
        url = reverse(viewname="role-user-manage-organization",
                      kwargs={'pk': str(organization.pk), 'user_id': str(user1.pk)})
        data = {
            "status": "MEMBER",
            "role_update": "admin"
        }
        rs = self.client.put(path=url, data=data, format='json')
        self.assertEqual(rs.status_code, status.HTTP_200_OK)
        # check role again user1
        self.verify_grant_access_user_organization_sucess(user=user1, organization=organization,
                                                          role=RoleService.role_admin())
