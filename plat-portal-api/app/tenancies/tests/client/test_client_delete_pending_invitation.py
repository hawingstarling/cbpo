import uuid

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from app.tenancies.services import UserClientService
from app.tenancies.tests.base import *


class ClientDeletePendingInvitationTest(APITestCase):
    fixtures = fixtures

    def setUp(self):
        init_app_context()
        self.user, self.token = init_user()
        self.client_obj = init_client(user=self.user)
        role = RoleService.role_admin()
        UserClientService.create_user_client(self.client_obj, self.user, role)

    def test_delete_pending_1(self):
        """
        delete pending invitation
        - no auth token
        :return:
        - HTTP 401
        """
        url = reverse('client-delete-invitation', kwargs={'client_id': self.client_obj.id,
                                                          'user_id': uuid.uuid4()})
        response = self.client.delete(url, None, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_pending_2(self):
        """
        delete pending invitation
        - auth token
        - user has no permission
        :return:
        - HTTP 403
        """
        url = reverse('client-delete-invitation', kwargs={'client_id': self.client_obj.id,
                                                          'user_id': uuid.uuid4()})
        # second user for getting token as staff member in the client, has no permission to modify the information
        user_second = UserService.create_user(email='second@gmail.com',
                                              password='password123')
        second_token = UserService.create_token(user_second)
        role = RoleService.role_staff()
        UserClientService.create_user_client(self.client_obj, user_second, role)

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + second_token.key)
        response = self.client.delete(url, None, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotEqual(response.content, None, 'expect not None')

    def test_delete_pending_3(self):
        """
        delete pending invitation
        - auth token
        - user has permission ( admin, manager )

        :return:
        - HTTP 204
        """
        user_second = UserService.create_user(email='second@gmail.com',
                                              password='password123')
        UserService.create_token(user_second)
        role = RoleService.role_staff()
        UserClientService.create_user_client(self.client_obj, user_second, role)

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        url = reverse('client-delete-invitation', kwargs={'client_id': self.client_obj.id,
                                                          'user_id': user_second.user_id})
        response = self.client.delete(url, None, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertNotEqual(response.content, None, 'expect not None')

    def test_delete_pending_4(self):
        """
        delete pending invitation
        - auth token
        - user has permission ( admin, manager )
        - delete member who is not pending status

        :return:
        - HTTP 409
        """
        # second user for getting token as staff member in the client, has no permission to modify the information
        user_second = UserService.create_user(email='second@gmail.com',
                                              password='password123')
        role = RoleService.role_staff()
        user_client = UserClientService.create_user_client(self.client_obj, user_second, role)
        user_client.pending_to_member()

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        url = reverse('client-delete-invitation', kwargs={'client_id': self.client_obj.id,
                                                          'user_id': user_second.user_id})
        response = self.client.delete(url, None, format='json')
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertNotEqual(response.content, None, 'expect not None')

    def test_delete_pending_6(self):
        """
        delete pending invitation
        - auth token
        - client_id parameter is invalid
        :return:
        - HTTP 400
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        url = reverse('client-delete-invitation', kwargs={'client_id': uuid.uuid4(),
                                                          'user_id': uuid.uuid4()})
        response = self.client.delete(url, None, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_pending_7(self):
        """
        delete pending invitation
        - auth token
        - user_id parameter is invalid
        :return:
        - HTTP 400
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        url = reverse('client-delete-invitation', kwargs={'client_id': self.client_obj.id,
                                                          'user_id': uuid.uuid4()})
        response = self.client.delete(url, None, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
