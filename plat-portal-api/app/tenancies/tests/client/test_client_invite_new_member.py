import uuid

from allauth.account.models import EmailAddress
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from app.tenancies.models import UserClient
from app.tenancies.services import UserClientService, ClientModuleService
from app.tenancies.tests.base import *


class ClientInvitationTest(APITestCase):
    fixtures = fixtures

    def setUp(self):
        init_app_context()
        self.user, self.token = init_user()
        self.client_obj = init_client(user=self.user)
        role = RoleService.role_admin()
        UserClientService.create_user_client(self.client_obj, self.user, role)
        ClientModuleService.create_client_module(self.client_obj)

    def test_client_invitation_1(self):
        """
        invite new member by email address
        - no auth token
        :return:
        HTTP 401
        """
        self.url_invitation = reverse(
            "client-inviting-member", kwargs={"client_id": self.client_obj.id}
        )
        response = self.client.post(self.url_invitation, None, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_client_invitation_2(self):
        """
        invite new member by email address
        - auth token
        - client_id is invalid
        :return:
        HTTP 400
        """
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        client_id = uuid.uuid4()  # invalid client id
        self.url_invitation = reverse(
            "client-inviting-member", kwargs={"client_id": client_id}
        )
        response = self.client.post(self.url_invitation, None, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_client_invitation_3(self):
        """
        invite new member by email address
        - auth token
        - client_id is invalid
        - pair of auth token and client_id is not appropriate, auth token has no permission as admin or manager
        :return:
        HTTP 401
        """
        self.url_invitation = reverse(
            "client-inviting-member", kwargs={"client_id": self.client_obj.id}
        )
        user_second = UserService.create_user(
            email="second@gmail.com", password="password123"
        )
        second_token = UserService.create_token(user_second)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + second_token.key)
        response = self.client.post(self.url_invitation, None, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_client_invitation_4(self):
        """
        invite new member by email address
        - auth token
        - client_id is valid
        - auth token has permission with client_id
        - no email member input field
        :return:
        HTTP 400
        """
        self.url_invitation = reverse(
            "client-inviting-member", kwargs={"client_id": self.client_obj.id}
        )
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        response = self.client.post(self.url_invitation, None, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_client_invitation_5a(self):
        """
        invite new member by email address
        - auth token
        - client_id is valid
        - auth token has permission with client_id
        - email input
        - no activation_link_template
        :return:
        HTTP 400
        """
        data = {"email": "fake_email@gmail.com"}
        self.url_invitation = reverse(
            "client-inviting-member", kwargs={"client_id": self.client_obj.id}
        )
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        response = self.client.post(self.url_invitation, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_client_invitation_5b(self):
        """
        invite new member by email address
        - auth token
        - client_id is valid
        - auth token has permission with client_id
        - email input -> email does not exist -> create new user (no first_name and or last_name)
        :return:
        HTTP 200
        """
        data = {
            "email": "fake_email@gmail.com",
            "activation_link_template": "http://localhost.com/?token={token}",
        }
        self.url_invitation = reverse(
            "client-inviting-member", kwargs={"client_id": self.client_obj.id}
        )
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        response = self.client.post(self.url_invitation, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_client_invitation_5c(self):
        """
        invite new member by email address
        - auth token
        - client_id is valid
        - auth token has permission with client_id
        - email does not exist -> create new user with first_name and last_name
        :return:
        HTTP 200
        """
        data = {
            "email": "fake_email@gmail.com",
            "first_name": "firstname",
            "last_name": "lastname",
            "activation_link_template": "http://localhost.com/?token={token}",
        }
        self.url_invitation = reverse(
            "client-inviting-member", kwargs={"client_id": self.client_obj.id}
        )
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        response = self.client.post(self.url_invitation, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_client_invitation_5d(self):
        """
        invite new member by email address
        - auth token
        - client_id is valid
        - auth token has permission with client_id
        - email input
        - activation_link_template is invalid
        :return:
        HTTP 400
        """
        data = {
            "email": "fake_email@gmail.com",
            "first_name": "firstname",
            "last_name": "lastname",
            "activation_link_template": "sdfdsftoken={token}",
        }
        self.url_invitation = reverse(
            "client-inviting-member", kwargs={"client_id": self.client_obj.id}
        )
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        response = self.client.post(self.url_invitation, data, format="json")
        print(response)
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

    def test_client_invitation_5e(self):
        """
        invite new member by email address
        - auth token
        - client_id is valid
        - auth token has permission with client_id
        - email input
        - activation_link_template is invalid (format token is invalid)
        :return:
        HTTP 400
        """
        data = {
            "email": "fake_email@gmail.com",
            "first_name": "firstname",
            "last_name": "lastname",
            "activation_link_template": "http://localhost.com/?todken=sdsn}",
        }
        self.url_invitation = reverse(
            "client-inviting-member", kwargs={"client_id": self.client_obj.id}
        )
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        response = self.client.post(self.url_invitation, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

    # def test_client_invitation_6(self):
    #     """
    #     invite new member by email address
    #     - auth token
    #     - client_id is valid
    #     - auth token has permission with client_id
    #     - email is already in the client
    #     :return:
    #     HTTP 409
    #     """
    #     data = {'email': DATA.get('email')}
    #     self.url_invitation = reverse('client-inviting-member', kwargs={'client_id': self.client_obj.id})
    #     self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
    #     response = self.client.post(self.url_invitation, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_client_invitation_7(self):
        """
        invite new member by email address
        - auth token
        - client_id is valid
        - auth token has permission with client_id
        - email is valid
        - activation_link_template
        :return:
        HTTP 200
        """
        user_member = UserService.create_user(
            email="second@gmail.com", password="password123"
        )
        data = {
            "email": "second@gmail.com",
            "activation_link_template": "http://localhost.com/?token={token}",
        }
        self.url_invitation = reverse(
            "client-inviting-member", kwargs={"client_id": self.client_obj.id}
        )
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        response = self.client.post(self.url_invitation, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_client_invitation_8(self):
        """
        force invitation
        @return:
        """
        data = {
            "email": "fake_email@gmail.com",
            "password": "emcuangayhomqua",
            "web_base_url": "http://localhost",
        }
        self.url_invitation = reverse(
            "force-client-inviting-member", kwargs={"client_id": self.client_obj.id}
        )
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        response = self.client.post(self.url_invitation, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user_client = UserClient.objects.get(user__email="fake_email@gmail.com")
        self.assertEqual(user_client.status, "MEMBER")
        self.assertEqual(
            EmailAddress.objects.get(email="fake_email@gmail.com").verified, True
        )

    def test_acception_8(self):
        """
        member accepts the client invitation
        - token is valid
        - new member is added
        - required changing password
        :return:
        HTTP 200
        """
        user_member = UserService.create_user(
            email="second@gmail.com", password="password123"
        )
        email_address = EmailAddress.objects.create(user=user_member)
        email_address.save()
        token = ClientService.generate_token_invitation(user_member, self.client_obj)
        role = RoleService.role_staff()

        UserClientService.create_user_client(self.client_obj, user_member, role)
        self.url_acception = reverse("client-member-accepting", kwargs={"token": token})
        response = self.client.get(self.url_acception, None, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_acception_8b(self):
        """
        member accepts the client invitation
        - token is valid
        - new member is added
        :return:
        HTTP 200
        """
        user_member = UserService.create_user(
            email="second@gmail.com", password="password123"
        )
        email_address = EmailAddress.objects.create(user=user_member)
        email_address.save()
        UserService.create_token(user_member)
        token = ClientService.generate_token_invitation(user_member, self.client_obj)
        role = RoleService.role_staff()
        UserClientService.create_user_client(self.client_obj, user_member, role)
        self.url_acception = reverse("client-member-accepting", kwargs={"token": token})
        response = self.client.get(self.url_acception, None, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_acception_8c(self):
        """
        member accepts the client invitation
        - token is invalid
        -
        :return:
        HTTP 406
        """
        user_member = UserService.create_user(
            email="second@gmail.com", password="password123"
        )
        UserService.create_token(user_member)
        token = ClientService.generate_token_invitation(user_member, self.client_obj)
        self.url_acception = reverse("client-member-accepting", kwargs={"token": token})
        response = self.client.get(self.url_acception, None, format="json")
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

    def test_acception_8d(self):
        """
        member accepts the client invitation
        - token is valid
        - new member is added (user client is soft deleted before)
        :return:
        HTTP 200
        """
        user_member = UserService.create_user(
            email="second@gmail.com", password="password123"
        )
        email_address = EmailAddress.objects.create(user=user_member)
        email_address.save()
        UserService.create_token(user_member)
        token = ClientService.generate_token_invitation(user_member, self.client_obj)
        role = RoleService.role_staff()
        user_client = UserClientService.create_user_client(
            self.client_obj, user_member, role
        )
        self.url_acception = reverse("client-member-accepting", kwargs={"token": token})
        response = self.client.get(self.url_acception, None, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_client_invitation_9(self):
        """
        invite new member by email address
        - auth token
        - client_id is valid
        - auth token has permission with client_id
        - email is valid
        - member is invited again from soft deleted pending invitation before
        :return:
        HTTP 200
        """
        user_member = UserService.create_user(
            email="second@gmail.com", password="password123"
        )
        data = {
            "email": "second@gmail.com",
            "activation_link_template": "http://localhost.com/?token={token}",
        }
        role = RoleService.role_staff()
        member_client = UserClientService.create_user_client(
            self.client_obj, user_member, role
        )
        member_client.delete()
        self.url_invitation = reverse(
            "client-inviting-member", kwargs={"client_id": self.client_obj.id}
        )
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        response = self.client.post(self.url_invitation, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
