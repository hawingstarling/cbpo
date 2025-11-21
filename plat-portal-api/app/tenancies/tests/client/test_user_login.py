import json

from allauth.account.models import EmailAddress
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from app.tenancies.tests.base import *


class UserTestLogin(APITestCase):
    fixtures = fixtures

    def setUp(self):
        init_app_context()
        self.user, self.token = init_user()
        self.data_login = {
            'email': self.user.email,
            'password': 'test123'
        }
        self.url = reverse('rest_login')

    def test_login_1(self):
        """
        user login
        - allow any
        - has no input
        :return:
        - HTTP 400
        """
        response = self.client.post(self.url, None, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, 'fields are required.')

    def test_login_2(self):
        """
        user login
        - allow any
        - valid input fields
        :return:
        - HTTP 200
        - token
        """
        email_address = EmailAddress.objects.create(user=self.user, email=self.user.email)
        email_address.verified = True
        email_address.save()
        response = self.client.post(self.url, self.data_login, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # TODO: feature/PS-906
        # token = json.loads(response.content).get('token')
        token = json.loads(response.content).get('key')
        self.assertNotEqual(token, None, msg='token is not None')
        self.assertNotEqual(token, '', msg='token is not empty')

    def test_login_3(self):
        """
        user login
        - allow any
        - invalid input fields
        :return:
        - HTTP 400
        """
        data_login = {'email': 'faker@gmail.com', 'password': 'fakepassword'}
        response = self.client.post(self.url, data_login, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, 'not enough credentials')

    def test_login_4(self):
        """
        user login
        - allow any
        - valid input fields
        - email is not verified
        :return:
        - HTTP 406
        """
        email_address = EmailAddress.objects.create(user=self.user, email=self.user.email)
        email_address.save()
        response = self.client.post(self.url, self.data_login, format='json')
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)
