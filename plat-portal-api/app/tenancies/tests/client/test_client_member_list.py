import uuid

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from app.tenancies.services import UserClientService, ClientModuleService
from app.tenancies.tests.base import *


class ClientMemberListTest(APITestCase):
    fixtures = fixtures

    def setUp(self):
        init_app_context()
        self.user, self.token = init_user()
        self.client_obj = init_client(user=self.user)
        role = RoleService.role_admin()
        UserClientService.create_user_client(self.client_obj, self.user, role)
        ClientModuleService.create_client_module(self.client_obj)

        member_1 = UserService.create_user(email='member1@gmail.com',
                                           password='password')
        member_2 = UserService.create_user(email='member2@gmail.com',
                                           password='password')
        role_staff = RoleService.role_staff()
        UserClientService.create_user_client(self.client_obj, member_1, role_staff)
        UserClientService.create_user_client(self.client_obj, member_2, role_staff)

    def test_client_member_1(self):
        """
        list al member in the client
        - no auth token
        :return:
        HTTP 401
        """
        url = reverse('client-member-list', kwargs={'client_id': self.client_obj.id})
        response = self.client.get(url, None, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_client_member_2(self):
        """
        list all member in the client
        - auth token
        - client_id is invalid
        :return:
        HTTP 400
        """
        client_id = uuid.uuid4()
        url = reverse('client-member-list', kwargs={'client_id': client_id})
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.get(url, None, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_client_member_3(self):
        """
        list all member in the client
        - auth token
        - client_id is valid
        - pair of auth token and client_id is not appropriate, auth token has no permission as admin or manager
        :return:
        HTTP 403
        """
        url = reverse('client-member-list', kwargs={'client_id': self.client_obj.id})
        member = UserService.create_user(email='member@gmail.com',
                                         password='password')
        token = UserService.create_token(user=member)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        response = self.client.get(url, None, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_client_member_4(self):
        """
        list all member in the client
        - auth token
        - client_id is valid
        - auth token has permission with client_id as admin or manager
        :return:
        HTTP 200
        """
        url = reverse('client-member-list', kwargs={'client_id': self.client_obj.id})
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.get(url, None, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
