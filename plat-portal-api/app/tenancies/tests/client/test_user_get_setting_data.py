import uuid

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from app.permission.services.compose_permission_service import ComposePermissionService
from app.tenancies.custom_payload_jwt import custom_token_handler
from app.tenancies.services import UserClientService, ClientModuleService
from app.tenancies.tests.base import *


class GetSettingDataTest(APITestCase):
    fixtures = fixtures

    def setUp(self):
        init_app_context()
        self.user, self.token = init_user()
        self.client_obj = init_client(user=self.user)
        role = RoleService.role_admin()
        self.user_client = UserClientService.create_user_client(self.client_obj, self.user, role)
        ClientModuleService.create_client_module(self.client_obj)
        token = custom_token_handler(self.user, self.client_obj, self.user_client)
        self.token = str(token)

    def test_get_setting_data_1(self):
        """
        using JWT Token to get member's setting data
        - no auth token
        :return:
        - HTTP 401
        """
        self.url = reverse('settings', kwargs={'client_id': uuid.uuid4(),
                                               'user_id': uuid.uuid4()})
        response = self.client.get(self.url, None, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_setting_data_2(self):
        """
         using JWT Token to get member's setting data
        - auth token
        - invalid client id
        :return:
        - HTTP 400
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(self.token))
        self.url = reverse('settings', kwargs={'client_id': uuid.uuid4(),
                                               'user_id': uuid.uuid4()})
        response = self.client.get(self.url, None, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_setting_data_3(self):
        """
         using JWT Token to get member's setting data
        - auth token
        - client id
        - invalid user_client_id
        :return:
        - HTTP 400
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(self.token))
        self.url = reverse('settings', kwargs={'client_id': self.client_obj.id,
                                               'user_id': uuid.uuid4()})
        response = self.client.get(self.url, None, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_setting_data_4(self):
        """
         using JWT Token to get member's setting data
        - auth token
        - client id
        - user_client_id
        :return:
        - HTTP 200
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(self.token))
        self.url = reverse('settings', kwargs={'client_id': self.client_obj.id,
                                               'user_id': self.user.user_id})
        self.user_client.status = 'MEMBER'
        self.user_client.save()
        ComposePermissionService.sync_permission_of_user_client_org([self.user_client.id])
        response = self.client.get(self.url, None, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
