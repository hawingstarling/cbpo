import uuid

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from app.tenancies.services import UserClientService, ClientModuleService
from app.tenancies.tests.base import *


class ClientModulesTest(APITestCase):
    fixtures = fixtures

    def setUp(self):
        init_app_context()
        self.user, self.token = init_user()
        self.client_obj = init_client(user=self.user)
        role = RoleService.role_admin()
        UserClientService.create_user_client(self.client_obj, self.user, role)
        ClientModuleService.create_client_module(self.client_obj)
        self.url = reverse('client-modules', kwargs={'client_id': self.client_obj.id})

    def test_client_modules_view_1(self):
        """
        view all modules of the client
        - no auth token
        :return:
        - HTTP 401
        """
        response = self.client.get(self.url, None, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_client_modules_view_2(self):
        """
        view all modules of the client
        - auth token
        - token has no permission
        :return:
        - HTTP 403
        """
        # second user for getting token as staff member in the client, has no permission to modify the information
        user_second = UserService.create_user(email='second@gmail.com',
                                              password='password123')
        second_token = UserService.create_token(user_second)
        # role = RoleService.role_staff()
        # UserClientService.create_user_client(self.client_obj, user_second, role)

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + second_token.key)
        response = self.client.get(self.url, None, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_client_modules_view_3(self):
        """
        view all modules of the client
        - auth token
        - token as admin or manager of the client
        :return:
        - HTTP 200
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.get(self.url, None, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.content, None)

    def test_client_modules_view_4(self):
        """
        view all modules of the client
        - auth token
        - token as admin or manager of the client
        - invalid client_id
        :return:
        - HTTP 406
        """
        self.url = reverse('client-modules', kwargs={'client_id': uuid.uuid4()})
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.get(self.url, None, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotEqual(response.content, None)
