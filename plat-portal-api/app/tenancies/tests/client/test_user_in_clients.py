from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from app.tenancies.services import UserClientService, ClientModuleService
from app.tenancies.tests.base import *


class UserClientBelongTest(APITestCase):
    fixtures = fixtures

    def setUp(self):
        init_app_context()
        self.url = reverse('clients-user-belong')
        self.user, self.token = init_user()

    def test_user_belong_1(self):
        """
        list all clients that user belongs to
        - no auth token
        :return:
        - HTTP 401
        """
        response = self.client.get(self.url, None, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_belong_2(self):
        """
        list all clients that user belongs to
        - auth token
        :return:
        - HTTP 200
        """
        data = {'name': 'client name',
                'logo': 'logo link'}
        client = ClientService.create_client(name=data['name'],
                                             logo=data['logo'],
                                             owner=self.user)
        client.save()
        role = RoleService.role_admin()
        UserClientService.create_user_client(client, self.user, role)
        ClientModuleService.create_client_module(client)

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.get(self.url, None, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.content, None)
