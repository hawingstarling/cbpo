import json
import random

from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.state import token_backend

from app.tenancies.config_app_and_module import APP_NAME_BUILD_PROFILE
from app.tenancies.tests.base import *
from app.tenancies.tests.organization.base import OrganizationBaseTest


class AppProfileConfig(OrganizationBaseTest):
    password = "1234567890"
    app_profile = APP_NAME_BUILD_PROFILE
    number_test = 100

    def setUp(self) -> None:
        self.user = self.init_user(email="owner@test.com", password=self.password)
        self.organization = self.create_organization(name="TBD", user=self.user)
        self.ws = self.create_client_organization(name="WS TBD", organization=self.organization)
        self.init_list_users()

    def init_list_users(self):
        """
        Init list users with number for test app profile send difference per user
        :param number:
        :return:
        """
        for item in range(1, self.number_test, 1):
            email = "test{}@test.com".format(item)
            print("email init uset : {}".format(email))
            user = self.init_user(email=email, password=self.password)
            self.invitation_organization_accept(user_create=self.user, user_invitation=user,
                                                organization=self.organization, role_name="admin")

    def verify_config(self, token: str = None, user: User = None):
        """
        Verify :
            1. Using token authen with Bearer
            2. Compare MODULE between get from app name config static variable VS API client module get from jwt token
            3. Test multi request in the moment time
        :param token:
        :return:
        """
        # 1. Using token authen with Bearer
        payloads = token_backend.decode(token, verify=False)
        app_name = payloads.get('app', None)
        print("App name : {}".format(app_name))
        self.assertNotEqual(app_name, None, msg="App name must not None")
        # 2. Compare MODULE between get from app name config static variable VS API client module get from jwt token
        modules_app = AppService.get_modules_app(app_name=app_name)
        print("App module profile app: {}".format(modules_app))
        header = {
            'HTTP_AUTHORIZATION': 'Bearer {}'.format(token)
        }
        client = ClientService.get_queryset_client().order_by('-created').first()
        url = reverse(viewname="user-permission", kwargs={'client_id': str(client.pk), 'user_id': str(user.pk)})
        rs = self.client.get(path=url, data=None, **header)
        self.assertEqual(rs.status_code, status.HTTP_200_OK)
        content = json.loads(rs.content.decode('utf-8'))
        print('List client module permission response : {}'.format(content))
        modules_result = []
        for item in content:
            modules_result.append(item['module'])
            self.assertNotEqual(item['permissions'], [], msg='Permission is not Empty')
        self.assertEqual(list(set(modules_result) - set(modules_app)), [])

    def test_app_login_single(self):
        for item in range(1, self.number_test, 1):
            email = "test{}@test.com".format(item)
            data = {
                'email': email,
                'password': self.password,
                'app': random.choice(self.app_profile)
            }
            url = reverse(viewname="login-app-token")
            rs = self.client.post(path=url, data=data, format='json')
            content = json.loads(rs.content.decode('utf-8'))
            print("email : {} with content : {}".format("test{}@test.com".format(item), content))
            self.assertEqual(rs.status_code, status.HTTP_200_OK)
            token = content['token']
            user = User.objects.get(email=email)
            self.verify_config(token=token, user=user)
