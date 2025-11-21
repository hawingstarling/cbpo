from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from app.tenancies.custom_payload_jwt import custom_token_handler
from app.tenancies.services import UserClientService
from app.tenancies.tests.base import *


class RefreshJwtTest(APITestCase):
    fixtures = fixtures

    def setUp(self):
        init_app_context()
        self.user, self.token = init_user()
        self.client_obj = init_client(user=self.user)
        role = RoleService.role_admin()
        self.user_client = UserClientService.create_user_client(
            self.client_obj, self.user, role
        )
        self.url = reverse("jwt-refresh")

    def test_refresh_jwt_1(self):
        """
        refresh jwt
        - token
        :return:
        - HTTP 200
        """
        token = custom_token_handler(
            self.user, self.client_obj, self.user_client
        )
        token = str(token)
        data = {"token": token}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_refresh_jwt_2(self):
        """
        refresh jwt
        - no token
        :return:
        - HTTP 400
        """
        response = self.client.post(self.url, None, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
