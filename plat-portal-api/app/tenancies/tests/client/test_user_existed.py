from allauth.account.models import EmailAddress
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from app.tenancies.tests.base import *


class UserRegistrationTest(APITestCase):
    fixtures = fixtures

    def setUp(self):
        init_app_context()
        self.url = reverse('check-user-is-existed')
        self.user, self.token = init_user()

    def test_check_user_existed_1(self):
        """
        user check_user_existed
        - invalid token authentication
        :return:
        - HTTP 401
        """
        data = {
            'email': 'test@gmail.com',
        }
        response = self.client.get(self.url,  data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_check_user_existed_2(self):
        """
        user check_user_existed
        - valid token
        - user does not exist
        :return:
        - HTTP 404
        """
        data = {
            'email': 'user-does-not-exist@gmail.com',
        }
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.get(self.url,  data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_check_user_existed_3(self):
        """
        user check_user_existed
        - valid token
        - user already exists
        :return:
        - HTTP 200
        - is_existed: True
        """
        data = {
            'email': 'test@gmail.com',
        }
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.get(self.url,  data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
