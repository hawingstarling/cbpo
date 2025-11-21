from allauth.account.models import EmailAddress
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from app.tenancies.tests.base import *


class ResendCodeForUserActivationTest(APITestCase):
    fixtures = fixtures

    def setUp(self):
        init_app_context()
        self.url = reverse('resend-activation')
        self.user, self.token = init_user()
        self.email_address = EmailAddress.objects.create(user=self.user, email=self.user.email)

    def test_resend_1(self):
        """
        resend code for activation
        - no auth token
        :return:
        - HTTP 401
        """
        response = self.client.get(self.url, None, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_resend_2(self):
        """
        resend code fore activation
        - auth token
        - user is activated
        :return:
        - HTTP 409
        """
        self.email_address.verified = True  # make user being verified
        self.email_address.save()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.get(self.url, None, format='json')
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_resend_3(self):
        """
        resend code fore activation
        - auth token
        - user is not activated
        :return:
        - HTTP 200 activated
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.get(self.url, None, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
