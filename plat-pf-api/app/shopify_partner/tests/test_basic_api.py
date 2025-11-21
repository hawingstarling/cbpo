import json
from unittest.mock import patch, MagicMock

from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from app.database.helper import get_connection_workspace
from app.financial.tests.fixtures.jwt_token import JWT_TOKEN1, JWT_PAYLOADS_CONFIG
from app.financial.tests.fixtures.user_client import USER_AUTH_CONFIG
from app.shopify_partner.models import OauthTokenRequest, ShopifyPartnerOauthClientRegister
from config.settings.common import ROOT_DIR

APPS_DIR = ROOT_DIR.path('app')


@override_settings(
    # CLIENT_ID_SHOPIFY_REVIEW='1dd0bded-e981-4d2f-9bef-2874016661e7',
    FERNET_KEY='9EPW4gpP3VSde2tY9toAZichYIsSwF2_8EgBk6k7jJo=',
)
class BasicApiTest(APITestCase):
    fixtures = [
        APPS_DIR + "financial/tests/fixtures/organization.json",
        APPS_DIR + "financial/tests/fixtures/clientportal.json",
        APPS_DIR + "financial/tests/fixtures/client_settings.json",
        APPS_DIR + "shopify_partner/tests/fixtures/setting.json"
    ]

    def setUp(self):
        self.client_id = '1dd0bded-e981-4d2f-9bef-2874016661e7'
        self.user_id = 'ce0be581-49df-4288-8b72-e961dd30a105'
        self.client_db = get_connection_workspace(self.client_id)
        self.permissions_update = {}
        self.role_update = {}
        self.jwt_token = JWT_TOKEN1

        self.start_patcher()
        # self.db_table_client(new_table=True)

    def start_patcher(self):
        ###
        self.patcher_user_auth = patch(
            'app.core.services.portal_service.PortalService.get_user_info_auth',
            return_value=USER_AUTH_CONFIG.get(self.user_id, {}))
        self.patcher_jwt_decode_handler = patch(
            'jwt.decode',
            return_value=JWT_PAYLOADS_CONFIG.get(self.user_id, {}))
        self.patcher_simple_jwt_verifying = patch('rest_framework_simplejwt.tokens.Token.verify',
                                                  self.fake_simple_jwt_verifying)

        ###
        self.patcher_user_auth.start()
        self.patcher_jwt_decode_handler.start()
        self.mock_simple_jwt_verifying = self.patcher_simple_jwt_verifying.start()

    def fake_simple_jwt_verifying(self):
        pass

    def stop_patcher(self):
        self.patcher_user_auth.stop()
        self.patcher_jwt_decode_handler.stop()

    def tearDown(self):
        self.stop_patcher()

    def test_get_sp_setting(self):
        url = reverse('sp-setting', kwargs={'client_id': self.client_id})
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.jwt_token}')
        rs = self.client.get(path=url, format='json')
        self.assertEqual(rs.status_code, status.HTTP_404_NOT_FOUND)

    def test_register_shop_url(self):
        url = reverse('register-shop-url', kwargs={'client_id': self.client_id})
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.jwt_token}')
        rs = self.client.post(path=url, data={
            "shop_url": "my-shop.myshopify.com",
            "client_id": self.client_id

        }, format='json')
        self.assertEqual(rs.status_code, status.HTTP_200_OK)

    def test_request_oauth_sp(self):
        url = reverse('client-sp-oauth-o2-token', kwargs={'client_id': self.client_id})
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.jwt_token}')
        rs = self.client.post(path=url, data={
            "shop_url": "my-shop.myshopify.com",
            "client_id": self.client_id

        }, format='json')
        self.assertEqual(rs.status_code, status.HTTP_200_OK)

    @patch('shopify.session.Session.validate_params', MagicMock(return_value=True))
    @patch('shopify.session.Session.request_token', MagicMock(return_value='fake_token_123'))
    @patch('app.shopify_partner.services.integrations.ac_register_or_revoke.ac_register', MagicMock(return_value=None))
    def test_full_flow_oauth_sp(self):
        url_request_oauth = reverse('client-sp-oauth-o2-token', kwargs={'client_id': self.client_id})
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.jwt_token}')
        rs_request_oauth = self.client.post(path=url_request_oauth, data={
            "shop_url": "my-shop.myshopify.com",
            "client_id": self.client_id

        }, format='json')
        content = json.loads(rs_request_oauth.content.decode('utf-8'))
        self.assertIsNotNone(content['auth_url'])
        oauth_ins = OauthTokenRequest.objects.get(client_id=self.client_id)
        url_callback = reverse("sp-oauth-callback") + "?shop={}&state={}".format(oauth_ins.shop_url, oauth_ins.state)

        self.client.get(path=url_callback, format='json')

        res = ShopifyPartnerOauthClientRegister.objects.tenant_db_for(self.client_id).get(client_id=self.client_id)
        self.assertEqual(res.enabled, True)
        # access token is encrypted to store in DB
        self.assertNotEqual(res.oauth_token_request.access_token, 'fake_token_123')
        self.assertEqual(res.oauth_token_request.get_decrypted_access_token, 'fake_token_123')


@override_settings(
    CLIENT_ID_SHOPIFY_REVIEW='1dd0bded-e981-4d2f-9bef-2874016661e7',
    FERNET_KEY='9EPW4gpP3VSde2tY9toAZichYIsSwF2_8EgBk6k7jJo=',
)
class ShopifyAppInstallForReviewProcessTest(APITestCase):
    fixtures = [
        APPS_DIR + "financial/tests/fixtures/organization.json",
        APPS_DIR + "financial/tests/fixtures/clientportal.json",
        APPS_DIR + "financial/tests/fixtures/client_settings.json",
        APPS_DIR + "shopify_partner/tests/fixtures/setting.json"
    ]

    def setUp(self):
        self.client_id = '1dd0bded-e981-4d2f-9bef-2874016661e7'
        self.user_id = 'ce0be581-49df-4288-8b72-e961dd30a105'
        self.client_db = get_connection_workspace(self.client_id)
        self.permissions_update = {}
        self.role_update = {}
        self.jwt_token = JWT_TOKEN1

        self.start_patcher()
        # self.db_table_client(new_table=True)

    def start_patcher(self):
        ###
        self.patcher_user_auth = patch(
            'app.core.services.portal_service.PortalService.get_user_info_auth',
            return_value=USER_AUTH_CONFIG.get(self.user_id, {}))
        self.patcher_jwt_decode_handler = patch(
            'AuthenticationService.verify_jwt_token_signature',
            return_value=JWT_PAYLOADS_CONFIG.get(self.user_id, {}))

        ###
        self.patcher_user_auth.start()
        self.patcher_jwt_decode_handler.start()

    def stop_patcher(self):
        self.patcher_user_auth.stop()
        self.patcher_jwt_decode_handler.stop()

    def tearDown(self):
        self.stop_patcher()
