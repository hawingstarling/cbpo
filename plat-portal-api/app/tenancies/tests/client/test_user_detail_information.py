from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from app.tenancies.tests.base import *


class PersonalProfileTest(APITestCase):
    fixtures = fixtures

    def setUp(self):
        init_app_context()
        self.url = reverse('rest_user_details')
        self.user, self.token = init_user()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

    def test_method_get(self):
        """
        method GET personal profile
        - authentication token is valid
        :return:
        - HTTP 200
        """
        response = self.client.get(self.url, None, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.content, None, 'expect: content is not None')

    def test_method_patch(self):
        """
        method PATCH personal profile
        - authentication token is valid
        - change personal information
        :return:
        - HTTP 200
        """
        data = {'first_name': 'sdfdsfds', 'last_name': 'dsfdsfds'}
        response = self.client.patch(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.content, None, 'expect: content is not none')
