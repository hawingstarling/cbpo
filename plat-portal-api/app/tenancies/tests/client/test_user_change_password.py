from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from app.tenancies.tests.base import *


class ChangePasswordTest(APITestCase):
    fixtures = fixtures

    def setUp(self):
        init_app_context()
        self.url = reverse('rest_password_change')
        self.user, self.token = init_user()

    def test_change_password_1(self):
        """
        change password
        - authentication token is invalid
        :return:
        - HTTP 401
        """
        response = self.client.post(self.url, None, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED, 'invalid token')

    def test_change_password_2(self):
        """
        change password
        - authentication token is valid
        - no input fields
        :return:
        - HTTP 400
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.post(self.url, None, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, 'input required')

    def test_change_password_3(self):
        """
        change password
        - authentication token is valid
        - input fields
        - old password field is invalid
        :return:
        - HTTP 400
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        data = {
            'old_password': 'fakepassword',
            'new_password1': 'newpassword',
            'new_password2': 'newpassword'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_password_4(self):
        """
        change password
        - authentication token is valid
        - input fields
        - old password is valid
        :return:
        - HTTP 200 password is changed
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        data = {
            'old_password': DATA.get('password'),
            'new_password1': 'newpassword123123',
            'new_password2': 'newpassword123123'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, 'password is changed')
        pass_before = self.user.password
        pass_after = User.objects.get(pk=self.user.user_id).password
        self.assertNotEqual(pass_before, pass_after, 'expect not equal')
