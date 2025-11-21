import json
import time
from datetime import datetime, timedelta

from rest_framework import status
from rest_framework.reverse import reverse

from app.tenancies.config_app_and_module import APP_NAME_BUILD_PROFILE
from app.tenancies.custom_payload_jwt import custom_token_handler
from app.tenancies.tests.organization.base import OrganizationBaseTest


class TestTokenHandle(OrganizationBaseTest):
    password = "1234567890"
    app_profile = APP_NAME_BUILD_PROFILE

    def setUp(self) -> None:
        self.user = self.init_user(email="owner@test.com", password=self.password)
        self.organization = self.create_organization(name="TBD", user=self.user)
        self.ws = self.create_client_organization(name="WS TBD", organization=self.organization)
        self.init_list_users()

    def test_handle_raise_token_expired_for_refresh_token(self):
        self.client.force_authenticate(user=None)
        email = "owner@test.com"
        data = {
            'email': email,
            'password': self.password,
            'app': "mwrw"
        }
        url = reverse(viewname="login-app-token")
        rs = self.client.post(path=url, data=data, format='json')
        content = json.loads(rs.content.decode('utf-8'))
        print("email : {} with content : {}".format("test1@test.com", content))
        self.assertEqual(rs.status_code, status.HTTP_200_OK)
        token = content['token']
        # CASE 1 : using token and get data success
        header = {
            'HTTP_AUTHORIZATION': 'Bearer {}'.format(token)
        }
        url_permission = reverse(viewname="user-permission",
                                 kwargs={'client_id': str(self.ws.pk), 'user_id': str(self.user.pk)})
        rs = self.client.get(path=url_permission, data=None, **header)
        self.assertEqual(rs.status_code, status.HTTP_200_OK)
        content = json.loads(rs.content.decode('utf-8'))
        print('List client module permission response : {}'.format(content))
        # CASE 2: Raise token expired and refresh success
        token = custom_token_handler(user=self.user)
        token['exp'] = datetime.utcnow() + timedelta(seconds=10)
        token = str(token)
        for number in range(1, 3, 1):
            time.sleep(5)
            header = {
                'HTTP_AUTHORIZATION': 'Bearer {}'.format(token)
            }
            rs = self.client.get(path=url_permission, data=None, **header)
            if rs.status_code == status.HTTP_401_UNAUTHORIZED:
                # refresh token
                data = {
                    'token': token
                }
                url_refresh_token = reverse(viewname="app-jwt-refresh")
                rs = self.client.post(path=url_refresh_token, data=data, format='json')
                self.assertEqual(rs.status_code, status.HTTP_200_OK)
                content = json.loads(rs.content.decode('utf-8'))
                token_refresh = content['token']
                print('Token refresh : {}'.format(token))
                self.assertNotEqual(token, None, msg="Token refresh is not None")
                # Get permission again
                header = {
                    'HTTP_AUTHORIZATION': 'Bearer {}'.format(token_refresh)
                }
                rs = self.client.get(path=url_permission, data=None, **header)
                self.assertEqual(rs.status_code, status.HTTP_200_OK)
