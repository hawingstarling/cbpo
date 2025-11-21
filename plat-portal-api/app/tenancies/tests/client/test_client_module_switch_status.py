import uuid

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from app.tenancies.services import UserClientService, ClientModuleService
from app.tenancies.tests.base import *


class ClientModulesSwitchingStatusTest(APITestCase):
    fixtures = fixtures

    def setUp(self):
        init_app_context()
        self.user, self.token = init_user()
        self.client_obj = init_client(user=self.user, role_organization=RoleService.role_admin())
        role = RoleService.role_admin()
        UserClientService.create_user_client(self.client_obj, self.user, role)
        ClientModuleService.create_client_module(self.client_obj)
        self.url = reverse('client-module-switching', kwargs={'client_id': self.client_obj.id,
                                                              'module': 'MAP'})

    def test_client_module_switch_1(self):
        """
        switching the status of modules
        - no auth token
        :return:
        - HTTP 401
        """
        response = self.client.put(self.url, None, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_client_module_switch_2(self):
        """
        switching the status of modules
        - auth token
        - token has no permission
        :return:
        - HTTP 403
        """
        # second user for getting token as staff member in the client, has no permission to modify the information
        user_second = UserService.create_user(email='second@gmail.com',
                                              password='password123')
        second_token = UserService.create_token(user_second)
        role = RoleService.role_staff()
        UserClientService.create_user_client(self.client_obj, user_second, role)

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + second_token.key)
        response = self.client.put(self.url, None, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_client_module_switch_3(self):
        """
        switching the status of modules
        - auth token
        - token is as admin or manager
        :return:
        - HTTP 200 switch module status
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.put(self.url, None, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_client_module_switch_4(self):
        """
        switching the status of modules
        - auth token
        - token is as admin or manager
        - invalid module parameter module
        :return:
        - HTTP 400
        """
        self.url = reverse('client-module-switching', kwargs={'client_id': self.client_obj.id,
                                                              'module': 'abc'})
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.put(self.url, None, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_client_module_switch_5(self):
        """
        switching the status of modules
        - auth token
        - token is as admin or manager
        - invalid module parameter client id
        :return:
        - HTTP 406
        """
        self.url = reverse('client-module-switching', kwargs={'client_id': uuid.uuid4(),
                                                              'module': 'MAP'})
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.put(self.url, None, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
