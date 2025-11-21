import json

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from app.tenancies.models import Client, ClientModule, UserClient
from app.tenancies.tests.base import *


class CreateClientTest(APITestCase):
    fixtures = fixtures

    def setUp(self):
        init_app_context()
        self.user, self.token = init_user()
        self.url = reverse("client-register")

    def test_create_client_1(self):
        """
        create client
        - invalid token authentication
        :return:
        - HTTP 401
        """
        response = self.client.post(self.url, None, format="json")
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED, "invalid token"
        )

    def test_create_client_2(self):
        """
        create client
        - valid token
        - has no input fields
        :return:
        - HTTP 400
        """
        self.user.can_create_client = True
        self.user.save()
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        response = self.client.post(self.url, None, format="json")
        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST, "fields required"
        )

    def test_create_client_2b(self):
        """
        create client
        - valid token
        - user has no permission to create new client
        :return:
        - HTTP 403
        """
        data = {"name": "name", "logo": "logo"}
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(
            response.status_code, status.HTTP_403_FORBIDDEN, "permission required"
        )

    def test_create_client_3(self):
        """
        create client
        - valid token
        - input fields
        - has permission
        :return:
        - HTTP 201 one client is added
        - client modules are added
        - member is added to the client as admin
        - member permissions are added (enable for all permission - admin)
        """
        data = {"name": "name", "logo": "logo"}
        self.user.can_create_client = True
        self.user.save()
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        count_before = Client.objects.all().count()
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, "created")
        count_after = Client.objects.all().count()
        self.assertEqual(count_after - count_before, 1, "one more id added")
        client_id = json.loads(response.content).get("id")
        client_modules = ClientModule.objects.filter(client_id=client_id).all()
        self.assertNotEqual(client_modules, None, "modules are added for the client")
        user_client = UserClient.objects.filter(
            client_id=client_id, user=self.user
        ).first()
        self.assertNotEqual(user_client, None, "member is added to the client")
