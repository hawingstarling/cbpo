from allauth.account.models import EmailAddress
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from app.tenancies.tests.base import *


class UserRegistrationTest(APITestCase):
    fixtures = fixtures

    def setUp(self):
        init_app_context()
        self.url = reverse('user-register')
        self.user, self.token = init_user()

    def test_register_1(self):
        """
        user register
        - allow any
        - has no input
        :return:
        - HTTP 400
        """
        response = self.client.post(self.url, None, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, 'fields are required.')

    def test_register_2(self):
        """
        user register
        - allow any
        - user name | email is used , not verified
        :return:
        - HTTP 200
        """
        data = DATA

        # email_address = EmailAddress.objects.create(user=self.user)
        # email_address.save()

        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, 'username | email is used.')

    def test_register_2b(self):
        """
        user register
        - allow any
        - user name | email is used , verified
        :return:
        - HTTP 400
        """
        data = DATA

        email_address = EmailAddress.objects.create(user=self.user)
        email_address.verified = True
        email_address.save()

        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, 'username | email is used.')

    def test_register_3(self):
        """
        user register
        - allow any
        - valid fields required
        :return:
        - HTTP 201
        - user object
        """
        data = {
            'username': 'testcreate',
            'email': 'test_create@gmail.com',
            'password1': 'hasdsadsadss',
            'password2': 'hasdsadsadss'
        }
        count_before = User.objects.count()
        response = self.client.post(self.url, data, format='json')
        count_after = User.objects.count()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(count_after - count_before == 1, msg='one more is added!')
        self.assertNotEqual(response.content, None, 'expect not None')

    def test_register_4(self):
        """
        user register
        - allow any
        - valid fields required
        - optional first_name and last_name
        :return:
        - HTTP 201
        - user object
        """
        data = {
            'username': 'testcreate',
            'email': 'test_create@gmail.com',
            'password1': 'hasdsadsadss',
            'password2': 'hasdsadsadss',
            'first_name': 'FirstName',
            'last_name': 'LastName'
        }
        count_before = User.objects.count()
        response = self.client.post(self.url, data, format='json')
        count_after = User.objects.count()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(count_after - count_before == 1, msg='one more is added!')
        self.assertNotEqual(response.content, None, 'expect not None'),

    def test_register_5(self):
        """
        user register
        - allow any
        - valid fields required
        - optional first_name and last_name
        -  without username
        :return:
        - HTTP 201
        - user object
        """
        data = {
            'email': 'test_create@gmail.com',
            'password1': 'hasdsadsadss',
            'password2': 'hasdsadsadss',
            'first_name': 'FirstName',
            'last_name': 'LastName'
        }
        count_before = User.objects.count()
        response = self.client.post(self.url, data, format='json')
        count_after = User.objects.count()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(count_after - count_before == 1, msg='one more is added!')
        self.assertNotEqual(response.content, None, 'expect not None')
