from allauth.account.models import EmailAddress
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from app.tenancies.tests.base import *


class ChangeEmailTest(APITestCase):
    fixtures = fixtures

    def setUp(self):
        init_app_context()
        self.url_change = reverse('change-email')
        self.url_verify = reverse('verify-changing-email')
        self.user, self.token = init_user()

    def test_change_email_1(self):
        """
        changing email
        - authen token is invalid
        :return:
        - HTTP 401
        """
        response = self.client.post(self.url_change, None, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED, 'invalid token')

    def test_change_email_2(self):
        """
        changing email
        - auth token is valid
        - no input field
        :return:
        - HTTP 400
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.post(self.url_change, None, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, 'require input')

    def test_change_email_3(self):
        """
        changing email
        - auth token is valid
        - input field
        - input field email : is used by another
        :return:
        - HTTP 409
        """
        data = {'new_email': DATA.get('email')}
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.post(self.url_change, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT, 'code is sent')

    def test_change_email_4(self):
        """
        changing email
        - auth token is valid
        - input field
        - input field email : is valid
        :return:
        - HTTP 200
        """
        data = {'new_email': 'newemail@gmail.com'}
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.post(self.url_change, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, 'email with code is sent.')

    def test_change_email_5(self):
        """
        verify changing email
        - auth token is valid
        - input field (new email, code)
        - code is invalid
        :return:
        - HTTP 406
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        UserOTPService.get_or_create_code(self.user)

        data = {'email': 'new_test@gmail.com',
                'code': '123456'}
        response = self.client.put(self.url_verify, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE, 'code is invalid.')

    def test_change_email_6(self):
        """
        verify changing email
        - auth token is valid
        - input field (new email, code)
        - code is used before
        :return:
        - HTTP 406
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        code = UserOTPService.get_or_create_code(self.user)
        UserOTPService.reset_after_verified(self.user)

        data = {'email': 'new_test@gmail.com',
                'code': code}
        response = self.client.put(self.url_verify, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE, 'code is used.')

    def test_change_email_7(self):
        """
        verify changing email
        - auth token is valid
        - input field (new email, code)
        - code is valid
        :return:
        - HTTP 200
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        code = UserOTPService.get_or_create_code(self.user)

        email_address = EmailAddress.objects.create(user=self.user, email=self.user.email)
        email_address.save()

        data = {'email': 'new_test@gmail.com',
                'code': code}
        response = self.client.put(self.url_verify, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, 'email is changed successfully.')
