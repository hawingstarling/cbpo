from app.core.pagination import OrganizationClientResultsSetPagination
from app.tenancies.services import SoftDeleteModelCheck
from app.tenancies.tests.organization.base import *


class OrganizationUserTest(OrganizationBaseTest):

    def test_create_client_organization(self):
        organization = self.create_organization(name="CBPO-MANAGE", user=self.user)
        self.create_client_organization(organization=organization, name="TEST-CLIENT-1")
        self.verify_grant_access_user_organization_sucess(user=self.user, organization=organization,
                                                          role=RoleService.role_owner())
        #
        user1 = self.init_user(email='testdemo1@test.com', password='1234567890')
        self.invitation_organization_accept(organization=organization, user_invitation=user1,
                                            user_create=self.user, role_name='admin')

        self.verify_grant_access_user_organization_sucess(user=user1, organization=organization,
                                                          role=RoleService.role_admin())

        #
        user2 = self.init_user(email='testdemo2@test.com', password='1234567890')
        self.invitation_organization_accept(organization=organization, user_invitation=user2,
                                            user_create=self.user, role_name='staff')

        self.verify_grant_access_user_organization_normal(user=user2, organization=organization,
                                                          role=RoleService.role_staff())

    def test_organization_list_client_grant_access_to_user(self):
        Setting.objects.filter(name="default").update(number_ws_limit=250)
        page_size = OrganizationClientResultsSetPagination.page_size
        self.assertEqual(page_size, 250)
        #
        organization = self.create_organization(name="CBPO-MANAGE", user=self.user)
        for i in range(0, page_size):
            self.create_client_organization(organization=organization, name="TEST-CLIENT-{}".format(i))
        #
        user_test = self.init_user(email="testuser@mail.com")
        url = reverse('organization-list-client-grant-to-user',
                      kwargs={'pk': str(organization.pk), 'user_id': str(user_test.id)})
        rs = self.client.get(path=url, format='json')
        print(rs)
        self.assertEqual(rs.status_code, 400)
        # invite user to organization
        self.invitation_organization_accept(organization=organization, user_invitation=user_test, user_create=self.user,
                                            role_name="client")
        url = reverse('organization-list-client-grant-to-user',
                      kwargs={'pk': str(organization.pk), 'user_id': str(user_test.id)})
        rs = self.client.get(path=url, format='json')
        print(rs)
        self.assertEqual(rs.status_code, status.HTTP_200_OK)
        content = json.loads(rs.content.decode('utf-8'))
        # page size default limit
        self.assertEqual(len(content["results"]), page_size)

    def test_action_organization(self):
        self.create_organization(name="CBPO Organization", user=self.user)
        #
        organization = Organization.objects.get(name="CBPO Organization")
        url = reverse('retrieve-update-destroy-organization', kwargs={'pk': str(organization.pk)})
        rs = self.client.get(path=url, format='json')
        self.assertEqual(rs.status_code, status.HTTP_200_OK)
        rs = self.client.put(path=url, data={'name': 'Test Change'}, format='json')
        self.assertEqual(rs.status_code, status.HTTP_200_OK)

        #
        user1 = self.init_user(email='test@test.com', password='123456')
        self.client.force_authenticate(user=user1)

        rs = self.client.get(path=url, format='json')
        self.assertEqual(rs.status_code, status.HTTP_403_FORBIDDEN)
        rs = self.client.put(path=url, data={'name': 'Test Change 1'}, format='json')
        self.assertEqual(rs.status_code, status.HTTP_403_FORBIDDEN)
        rs = self.client.delete(path=url)
        self.assertEqual(rs.status_code, status.HTTP_403_FORBIDDEN)
        #
        self.client.force_authenticate(user=self.user)
        rs = self.client.delete(path=url)
        self.assertEqual(rs.status_code, status.HTTP_204_NO_CONTENT)

    def test_action_client(self):
        self.create_organization(name="CBPO TEST CREATE CLIENT", user=self.user)
        organization = Organization.objects.get(name="CBPO TEST CREATE CLIENT")
        client = self.create_client_organization(name="test create client", organization=organization)
        #
        self.verify_manage_client_organization(organization=organization, client=client, user=self.user)
        #
        url = reverse('update-delete-organization-client',
                      kwargs={'pk': str(organization.pk), 'client_id': str(client.pk)})
        data = {
            'name': 'Test Update client'
        }
        rs = self.client.put(path=url, data=data, format='json')
        self.assertEqual(rs.status_code, status.HTTP_200_OK)
        client.refresh_from_db()
        self.assertEqual(client.name == data.get('name'), True)
        #
        user1 = self.init_user(email='test@test.com', password='123456')
        self.client.force_authenticate(user=user1)
        rs = self.client.put(path=url, data=data, format='json')
        # Accept invitation
        self.assertEqual(rs.status_code, status.HTTP_403_FORBIDDEN)

    def test_organization_invitation_user(self):
        self.create_organization(name="CBPO TEST CREATE CLIENT", user=self.user)
        organization = Organization.objects.get(name="CBPO TEST CREATE CLIENT")
        # test approve client by staff user create
        user1 = self.init_user(email='test@test.com', password='123456')
        self.invitation_organization_accept(organization=organization, user_create=self.user, user_invitation=user1)
        # Denied invitation
        user2 = self.init_user(email='test1@test.com', password='123456')
        self.invitation_organization_denied(organization=organization, user_create=self.user, user_invitation=user2)

    def _create_client_organization(self, organization: Organization = None, name: str = None):
        url = reverse('list-create-organization-client', kwargs={'pk': str(organization.pk)})
        data = {
            'name': name
        }
        return self.client.post(url, data=data, format='json')

    def test_action_create_client_duplicate(self):
        self.create_organization(name="CBPO TEST CREATE CLIENT ABC", user=self.user)
        organization = Organization.objects.get(name="CBPO TEST CREATE CLIENT ABC")
        # CASE 1: Create client successfully
        rs = self._create_client_organization(name="Client1", organization=organization)
        self.assertEqual(rs.status_code, status.HTTP_201_CREATED)
        content = json.loads(rs.content.decode('utf-8'))
        client_id1 = content['id']
        print(content)
        # CASE 2: Create client conflict
        rs = self._create_client_organization(name="Client1", organization=organization)
        self.assertEqual(rs.status_code, status.HTTP_409_CONFLICT)
        content = json.loads(rs.content.decode('utf-8'))
        print(content)
        # CASE 3: User staff suggestion
        user1 = self.init_user(email='testabc@test.com', password='123456')
        self.invitation_organization_accept(organization=organization, user_create=self.user, user_invitation=user1,
                                            role_name="staff")
        #
        rs = self._create_client_organization(name="Client1", organization=organization)
        self.assertEqual(rs.status_code, status.HTTP_409_CONFLICT)
        content = json.loads(rs.content.decode('utf-8'))
        print(content)
        #
        rs = self._create_client_organization(name="Client2", organization=organization)
        self.assertEqual(rs.status_code, status.HTTP_201_CREATED)
        content = json.loads(rs.content.decode('utf-8'))
        print(content)
        # CASE 4: Update name client 2 to client 1 raise duplicate
        self.client.force_authenticate(user=self.user)
        url = reverse('update-delete-organization-client',
                      kwargs={'pk': str(organization.pk), 'client_id': str(client_id1)})
        data = {
            'name': "Client2"
        }
        rs = self.client.put(url, data=data, format='json')
        self.assertEqual(rs.status_code, status.HTTP_409_CONFLICT)
        content = json.loads(rs.content.decode('utf-8'))
        print(content)
        rs = self.client.patch(url, data=data, format='json')
        self.assertEqual(rs.status_code, status.HTTP_409_CONFLICT)
        content = json.loads(rs.content.decode('utf-8'))
        print(content)
        # CASE 4: Update new name
        data = {
            'name': "Client3"
        }
        rs = self.client.put(url, data=data, format='json')
        self.assertEqual(rs.status_code, status.HTTP_200_OK)
        content = json.loads(rs.content.decode('utf-8'))
        print(content)
        rs = self.client.patch(url, data=data, format='json')
        self.assertEqual(rs.status_code, status.HTTP_200_OK)
        content = json.loads(rs.content.decode('utf-8'))
        print(content)

        # CASE 5 : Create client same name with record soft delete of Organization
        #       Expect : change name record soft delete to name = name + '-' + now(), create new ones
        rs = self._create_client_organization(name="Client4", organization=organization)
        self.assertEqual(rs.status_code, status.HTTP_201_CREATED)
        content = json.loads(rs.content.decode('utf-8'))
        client_id4 = content['id']
        print(content)
        #
        self.client.force_authenticate(user=self.user)
        url_delete = reverse(viewname='update-delete-organization-client',
                             kwargs={'pk': str(organization.pk), 'client_id': str(client_id4)})
        rs = self.client.delete(path=url_delete, data=None, format='json')
        self.assertEqual(rs.status_code, status.HTTP_204_NO_CONTENT)
        client_delete = SoftDeleteModelCheck.get_soft_delete_model(model=Client, name='Client4')
        self.assertNotEqual(client_delete, None, msg='Client soft delete is not None')
        self.assertEqual(str(client_delete.pk), client_id4)
        # create same name client
        rs = self._create_client_organization(name="Client4", organization=organization)
        self.assertEqual(rs.status_code, status.HTTP_201_CREATED)
        filter = {
            'name__icontains': "Client4",
            'organization': organization
        }
        clients_same_name = Client.all_objects.filter(**filter)
        self.assertEqual(clients_same_name.count(), 2)
        for item in clients_same_name:
            print("List client same name :  {}".format(item.name))

    def test_account_manager_client_organization(self):
        self.create_organization(name="CBPO TEST CREATE CLIENT ABC", user=self.user)
        organization = Organization.objects.get(name="CBPO TEST CREATE CLIENT ABC")
        rs = self._create_client_organization(name="ClientTestAccountManager", organization=organization)
        self.assertEqual(rs.status_code, status.HTTP_201_CREATED)
        content = json.loads(rs.content.decode('utf-8'))
        client_id = content['id']
        # get info client object

        client = Client.objects.get(pk=client_id)
        account_manager = content['account_manager']
        #
        self.assertEqual(account_manager, None)

        # update manager account 'test@hdwebsoft.co' != list domain email
        payload = {
            'name': 'Test',
            'account_manager': 'test@hdwebsoft.co'
        }
        url = reverse('client-information', kwargs={'pk': client_id})
        rs = self.client.put(path=url, data=payload, format='json')
        content = json.loads(rs.content.decode('utf-8'))
        account_manager = content['account_manager']
        #
        self.assertEqual(account_manager, None)
        spa = content['special_project_manager']
        self.assertEqual(spa, None)

        # update manager account 'test@hdwebsoft.com'
        self.user.email = 'xxxxxxx@hdwebsoft.com'
        self.user.save()
        payload = {
            'name': 'Test',
            'account_manager': 'test@hdwebsoft.com',
            'special_project_manager': 'special@hdwebsoft.com'
        }
        url = reverse('client-information', kwargs={'pk': client_id})
        rs = self.client.put(path=url, data=payload, format='json')
        content = json.loads(rs.content.decode('utf-8'))
        account_manager = content['account_manager']
        #
        self.assertEqual(account_manager, 'test@hdwebsoft.com')
        spa = content['special_project_manager']
        self.assertEqual(spa, 'special@hdwebsoft.com')

        # update manager account 'test@outdoorequipped.com'
        self.user.save()
        payload = {
            'name': 'Test',
            'account_manager': 'test@outdoorequipped.com',
            'special_project_manager': 'special@outdoorequipped.com'
        }
        url = reverse('client-information', kwargs={'pk': client_id})
        rs = self.client.put(path=url, data=payload, format='json')
        content = json.loads(rs.content.decode('utf-8'))
        account_manager = content['account_manager']
        self.assertEqual(account_manager, 'test@outdoorequipped.com')
        spa = content['special_project_manager']
        self.assertEqual(spa, 'special@outdoorequipped.com')

        # Update account 'test@channelprecision.com'
        self.user.save()
        payload = {
            'name': 'Test',
            'account_manager': 'test@channelprecision.com',
            'special_project_manager': 'special@channelprecision.com',
        }
        url = reverse('client-information', kwargs={'pk': client_id})
        rs = self.client.put(path=url, data=payload, format='json')
        content = json.loads(rs.content.decode('utf-8'))
        account_manager = content['account_manager']
        #
        self.assertEqual(account_manager, 'test@channelprecision.com')
        spa = content['special_project_manager']
        self.assertEqual(spa, 'special@channelprecision.com')

        # check user not same list email domain
        self.user.email = 'xxxxxxx@demo.com'
        self.user.save()
        payload = {
            'name': 'Test'
        }
        url = reverse('client-information', kwargs={'pk': client_id})
        rs = self.client.put(path=url, data=payload, format='json')
        content = json.loads(rs.content.decode('utf-8'))
        account_manager = content['account_manager']
        self.assertEqual(account_manager, None)
        spa = content['special_project_manager']
        self.assertEqual(spa, None)
        client.refresh_from_db()
        self.assertEqual(client.account_manager, 'test@channelprecision.com')
        self.assertEqual(client.special_project_manager, 'special@channelprecision.com')

        # check user not same list email domain
        self.user.email = 'xxxxxxx@demo.com'
        self.user.save()
        payload = {
            'name': 'Test',
            'account_manager': '',
        }
        url = reverse('client-information', kwargs={'pk': client_id})
        rs = self.client.put(path=url, data=payload, format='json')
        content = json.loads(rs.content.decode('utf-8'))
        account_manager = content['account_manager']
        self.assertEqual(account_manager, None)
        spa = content['special_project_manager']
        self.assertEqual(spa, None)
        client.refresh_from_db()
        self.assertEqual(client.account_manager, 'test@channelprecision.com')
        self.assertEqual(client.special_project_manager, 'special@channelprecision.com')

        # check user not same list email domain
        self.user.email = 'xxxxxxx@demo.com'
        self.user.save()
        payload = {
            'name': 'Test',
            'account_manager': None,
        }
        url = reverse('client-information', kwargs={'pk': client_id})
        rs = self.client.put(path=url, data=payload, format='json')
        content = json.loads(rs.content.decode('utf-8'))
        account_manager = content['account_manager']
        self.assertEqual(account_manager, None)
        spa = content['special_project_manager']
        self.assertEqual(spa, None)
        client.refresh_from_db()
        self.assertEqual(client.account_manager, 'test@channelprecision.com')
        self.assertEqual(client.special_project_manager, 'special@channelprecision.com')

        #
        url = reverse('client-information', kwargs={'pk': client_id})
        rs = self.client.get(path=url, format='json')
        content = json.loads(rs.content.decode('utf-8'))
        account_manager = content['account_manager']
        #
        self.assertEqual(account_manager, None)
        spa = content['special_project_manager']
        self.assertEqual(spa, None)
        client.refresh_from_db()
        self.assertEqual(client.account_manager, 'test@channelprecision.com')
        self.assertEqual(client.special_project_manager, 'special@channelprecision.com')

    def test_force_invite_member(self):
        """
        force invitation
        @return:
        """
        data = {
            'email': 'fake_email@gmail.com',
            'password': 'emcuangayhomqua',
            'web_base_url': 'http://localhost',
        }
        self.create_organization(name="CBPO TEST CREATE CLIENT", user=self.user)
        organization = Organization.objects.get(name="CBPO TEST CREATE CLIENT")
        self.force_invitation = reverse('force-organization-invitation-users', kwargs={'pk': str(organization.id)})
        # self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.post(self.force_invitation, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user_org = OrganizationUser.objects.get(user__email="fake_email@gmail.com")
        self.assertEqual(user_org.status, 'MEMBER')
        self.assertEqual(EmailAddress.objects.get(email='fake_email@gmail.com').verified, True)
