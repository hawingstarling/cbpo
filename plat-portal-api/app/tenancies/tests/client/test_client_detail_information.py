from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from app.tenancies.services import UserClientService
from app.tenancies.tests.base import *


class ClientInformationTest(APITestCase):
    fixtures = fixtures

    def setUp(self):
        init_app_context()
        self.user, self.token = init_user()
        self.client_obj = init_client(user=self.user)
        role = RoleService.role_admin()
        UserClientService.create_user_client(self.client_obj, self.user, role)
        self.url = reverse('client-information', kwargs={'pk': self.client_obj.id})

    def test_client_information_1(self):
        """
        managing client information method GET
        managing client information method GET
        - no auth token
        :return:
        - HTTP 401
        """
        response = self.client.get(self.url, None, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_client_information_2(self):
        """
        managing client information method GET
        - auth token
        :return:
        - HTTP 200
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.get(self.url, None, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_client_information_3(self):
        """
        managing client information method PUT / PATCH
        - auth token
        - user has no permission to modify the client information
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
        response = self.client.patch(self.url, None, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotEqual(response.content, None, 'expect not None')

    def test_client_information_4(self):
        """
        managing client information method PUT / PATCH
        - auth token
        - user has permission to modify the client information ( admin, manager )
        :return:
        - HTTP 200
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.patch(self.url, None, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.content, None, 'expect not None')
