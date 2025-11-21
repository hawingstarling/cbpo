import uuid

from allauth.account.models import EmailAddress
from django.urls import reverse
from itsdangerous import URLSafeTimedSerializer
from rest_framework import status
from rest_framework.test import APITestCase

from app.tenancies.models import UserOTP
from app.tenancies.tests.base import *
from config.settings.common import SECRET_KEY


class PasswordRecoveryTest(APITestCase):
    fixtures = fixtures

    def setUp(self):
        init_app_context()
        self.user, self.token = init_user()
        self.url_reset_password = reverse('password-reset')
        self.url_reset_password_confirm = reverse('rest_password_reset_confirm')
        self.url_reset_password_identity = reverse('password-reset-identity')

    def test_password_recovery_1(self):
        """
        require reset password
        - allow any
        - has no email field
        :return:
        - HTTP 400
        """
        response = self.client.post(self.url_reset_password, None, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, 'require email field')

    def test_password_recovery_2(self):
        """
        require reset password
        - allow any
        - email field
        - email does not exist in the system
        :return:
        - HTTP 406
        """
        data = {'email': 'fake_email@gmail.com'}
        response = self.client.post(self.url_reset_password, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE, 'not exist')

    def test_password_recovery_3(self):
        """
        require reset password
        - allow any
        - email field
        - email is valid
        :return:
        - HTTP 200 mail with code is sent
        """
        data = {'email': DATA.get('email')}
        response = self.client.post(self.url_reset_password, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, 'code is sent')

    def test_password_recovery_4(self):
        """
        verify user by code, token
        - allow any
        - no code, token
        :return:
        - HTTP 400
        """
        response = self.client.post(self.url_reset_password_identity, None, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, 'require email field')

    def test_password_recovery_5(self):
        """
        verify user by code, token
        - allow any
        - token is invalid
        :return:
        - HTTP 400
        """
        s = URLSafeTimedSerializer(SECRET_KEY)
        token = s.dumps({'user_id': str(uuid.uuid4())})
        data = s.loads(token, max_age=10000)  # `max_age` replaces `expires_in`
        response = self.client.post(self.url_reset_password_identity, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, 'token is invalid')

    def test_password_recovery_6(self):
        """
        verify user by code, token
        - allow any
        - token is valid
        - code is used before
        :return:
        - HTTP 400
        """
        code = UserOTPService.get_or_create_code(self.user)
        user_otp = UserOTP.objects.filter(user=self.user).first()
        user_otp.reset_after_verified()
        token = UserOTPService.get_token(self.user)
        data = {'code': code, 'token': token}
        response = self.client.post(self.url_reset_password_identity, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE, 'token not found')

    def test_password_recovery_6b(self):
        """
        verify user by code, token
        - allow any
        - token is valid
        - code is not match
        :return:
        - HTTP 400
        """
        UserOTPService.get_or_create_code(self.user)
        token = UserOTPService.get_token(self.user)
        data = {'code': int(123456), 'token': token}
        response = self.client.post(self.url_reset_password_identity, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE, 'code is not match')

    def test_password_recovery_7(self):
        """
        verify user by code, token
        - token is valid
        - code is invalid
        :return:
        - HTTP 200
        """
        code = UserOTPService.get_or_create_code(self.user)
        token = UserOTPService.get_token(self.user)
        data = {'code': code, 'token': token}
        response = self.client.post(self.url_reset_password_identity, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, 'token is valid')

    def test_password_recovery_8(self):
        """
        confirm reset password ( new password )
        - has no input fields
        :return:
        - HTTP 400
        """
        response = self.client.post(self.url_reset_password_confirm, None, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, 'required input')

    def test_password_recovery_10(self):
        """
        confirm reset password ( new password )
        - input field password
        - token is invalid
        :return:
        - HTTP 400
        """
        s = URLSafeTimedSerializer(SECRET_KEY)
        token = s.dumps({'user_id': str(uuid.uuid4())})
        data = {
            'token': token,
            'password': 'newpassword'
        }
        response = self.client.post(self.url_reset_password_confirm, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE, 'invalid token')

    def test_password_recovery_12(self):
        """
        confirm reset password ( new password )
        - input fields
        - token is valid
        :return:
        - HTTP 200 reset password successfully
        """
        email_address = EmailAddress.objects.create(user=self.user, email=self.user.email)
        email_address.save()
        UserOTPService.get_or_create_code(self.user)
        token = UserOTPService.get_token(self.user)
        data = {
            'token': token,
            'password': 'newpassword'
        }
        response = self.client.post(self.url_reset_password_confirm, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, 'reset password successfully.')
