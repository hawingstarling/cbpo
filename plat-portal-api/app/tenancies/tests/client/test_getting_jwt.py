from allauth.account.models import EmailAddress
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from app.tenancies.services import UserClientService
from app.tenancies.tests.base import *


class GettingJwtTest(APITestCase):
    fixtures = fixtures

    def setUp(self):
        init_app_context()
        self.user, self.token = init_user(
            email="test_login_app@test.com", password="1234567890"
        )
        self.client_obj = init_client(user=self.user)
        role = RoleService.role_admin()
        self.user_client = UserClientService.create_user_client(
            self.client_obj, self.user, role
        )

    def test_login_app_get_jwt(self):
        """
        get jwt for user_client
        - auth token
        - client_id
        - user_client_id
        :return:
        - HTTP 200
        """
        data = {
            "email": "test_login_app@test.com",
            "password": "1234567890",
            "app": "mwrw",
        }
        url = reverse("login-app-token")
        user = User.objects.get(email="test_login_app@test.com")
        EmailAddress.objects.create(user=user)
        UserService.activation(user=user)
        response = self.client.post(url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.content, None, "expect: content is not None")
