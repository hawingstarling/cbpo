from allauth.account.models import EmailAddress
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from app.tenancies.tests.base import *


class UserRegisterActivationTest(APITestCase):
    fixtures = fixtures

    def setUp(self):
        init_app_context()
        self.url = reverse('user-activation')
        self.user, self.token = init_user()
        self.email_address = EmailAddress.objects.create(user=self.user, email=self.user.email)

    def test_activation_1(self):
        """
        user activation
        - no auth token
        :return:
        - HTTP 401
        """
        response = self.client.put(self.url, None, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_activation_2(self):
        """
        user activation
        - auth token
        - no input field code
        :return:
        - HTTP 400
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.put(self.url, None, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_activation_3(self):
        """
        user activation
        - auth token
        - input field code
        - code is invalid
        :return:
        - HTTP 406
        """
        UserOTPService.get_or_create_code(self.user)
        data = {'code': '111111'}
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.put(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

    def test_activation_4(self):
        """
        user activation
        - auth token
        - input field code
        - code is valid
        :return:
        - HTTP 200
        """
        code = UserOTPService.get_or_create_code(self.user)
        data = {'code': code}
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.put(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
