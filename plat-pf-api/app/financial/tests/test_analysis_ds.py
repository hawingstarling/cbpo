import json
from unittest.mock import patch
from django.utils.translation import ugettext as _
from rest_framework import status, exceptions
from rest_framework.reverse import reverse
from app.core.exceptions import PSServiceException
from app.core.variable.permission import ROLE_STAFF
from app.financial.models import SaleItem
from app.financial.services.data_flatten import DataFlatten
from app.financial.sql_generator.flat_sql_generator_container import SqlGeneratorContainer
from app.financial.tests.base import BaseAPITest
from app.financial.variable.data_flatten_variable import FLATTEN_SALE_ITEM_KEY
from app.financial.variable.job_status import SUCCESS
from config.settings.common import ROOT_DIR

APPS_DIR = ROOT_DIR.path('app')

fixtures = [
    APPS_DIR + "financial/tests/fixtures/organization.json",
    APPS_DIR + "financial/tests/fixtures/clientportal.json",
    APPS_DIR + "financial/tests/fixtures/channel.json",
    APPS_DIR + "job/tests/fixtures/job_config.json",
    APPS_DIR + "financial/tests/fixtures/division_manage.json",
    APPS_DIR + "financial/tests/fixtures/top_client_asins.json"
]


class ClientGenerateDataSourceAPITest(BaseAPITest):
    fixtures = fixtures
    type_flatten = FLATTEN_SALE_ITEM_KEY

    def setUp(self):
        super().setUp()

        if SaleItem.objects.tenant_db_for(self.client_id).count() == 0:
            self.db_table_client(new_table=True)

        # enable extension tablefunc for using crosstab in PSQL
        self.create_extension_tablefunc()

        # create table manage data sale items
        self.create_full_flatten_manage()

    def fake_get_or_create_data_source(self, external_id):
        return {
            'external_id': "pf:{}:sale_items".format(self.client_id)
        }

    def test_get_datasource(self):
        headers = {
            'HTTP_AUTHORIZATION': 'Bearer {}'.format(self.jwt_token),
            'HTTP_X_PS_CLIENT_ID': self.client_id
        }
        # CASE get data source
        url = reverse('flatten-sale-items-status', kwargs={'client_id': self.client_id})
        rs = self.client.get(url, **headers)
        self.assertEqual(rs.status_code, status.HTTP_200_OK)
        content = json.loads(rs.content)
        print(content)
        self.assertEqual(content['status'], SUCCESS)

        data_flatten = DataFlatten(client_id=self.client_id, type_flatten=self.type_flatten,
                                   sql_generator=SqlGeneratorContainer.flat_sale_items())
        exist = data_flatten.is_flatten_exists()
        self.assertEqual(exist, True)

    def test_get_datasource_with_flatten_not_exist(self):
        """
        Data source exist
        Flatten table not exist
        Auto check and generate flatten
        :return:
        """
        data_flatten = DataFlatten(client_id=self.client_id, type_flatten=self.type_flatten,
                                   sql_generator=SqlGeneratorContainer.flat_sale_items())
        data_flatten.drop_flatten_exists()

        headers = {
            'HTTP_AUTHORIZATION': 'Bearer {}'.format(self.jwt_token),
            'HTTP_X_PS_CLIENT_ID': self.client_id
        }
        # CASE get data source
        url = reverse('flatten-sale-items-status', kwargs={'client_id': self.client_id})
        rs = self.client.get(url, **headers)
        self.assertEqual(rs.status_code, status.HTTP_200_OK)
        content = json.loads(rs.content)
        print(content)
        self.assertEqual(content['status'], SUCCESS)

        data_flatten = DataFlatten(client_id=self.client_id, type_flatten=self.type_flatten,
                                   sql_generator=SqlGeneratorContainer.flat_sale_items())
        exist = data_flatten.is_flatten_exists()
        self.assertEqual(exist, True)

    @patch('app.financial.services.data_source.DataSource.get_or_create_data_source', fake_get_or_create_data_source)
    def test_generate_ds(self):
        self.client_id = '1dd0bded-e981-4d2f-9bef-2874016661e7'
        self.restart_patcher()
        headers = {
            'HTTP_AUTHORIZATION': 'Bearer {}'.format(self.jwt_token),
            'HTTP_X_PS_CLIENT_ID': self.client_id
        }
        # CASE generate data source
        url = reverse('flatten-sale-items', kwargs={'client_id': self.client_id})
        print(url)
        rs = self.client.post(url, **headers)

        content = json.loads(rs.content)
        print(content)

        self.assertEqual(rs.status_code, status.HTTP_200_OK)
        self.assertEqual(content['status'], 'SUCCESS')

        data_flatten = DataFlatten(client_id=self.client_id, type_flatten=self.type_flatten,
                                   sql_generator=SqlGeneratorContainer.flat_sale_items())
        exist = data_flatten.is_flatten_exists()
        self.assertEqual(exist, True)


def fake_simple_jwt_check_verifying(claim="exp", current_time=None):
    pass


def fake_build_condition_for_24_hours():
    return {
        "type": "AND",
        "conditions": [
            {
                "column": "channel_name",
                "value": "amazon.com",
                "operator": "$eq",
            },
            {
                "column": "sale_date",
                "value": "2020-01-01T05:00:00.000Z",
                "operator": "$gte",
            },
            {
                "column": "sale_date",
                "value": "2020-01-02T05:00:00.000Z",
                "operator": "$lte",
            }
        ]
    }


class ClientAnalysisProxyAPITest(BaseAPITest):
    body = {
        'query': {
            'distinct': False,
            'paging': {
                'limit': 20,
                'current': 1
            },
            'orders': [
                {'column': 'sale_date', 'direction': 'desc'}
            ],
            'group': {'columns': [], 'aggregations': []},
            'filter': {
                'type': 'AND',
                'conditions': [
                    {'column': 'sale_date', 'operator': '$gte', 'value': "DATE_LAST(30,'days')"},
                    {'column': 'sale_date', 'operator': '$lte', 'value': 'TODAY()'},
                    {'column': 'channel_name', 'operator': '$eq', 'value': 'amazon.com'},
                    {
                        'id': 'id-aece4ded-fd70-4c71-91a5-a2db37efe2b8', 'level': 0, 'type': 'AND',
                        'conditions': [
                            {
                                'id': 'id-62c586e8-c5e0-440f-b251-1b6e7b6e9de3', 'level': 1,
                                'column': 'channel_id', 'value': 'XXX-XXXX-TEST',
                                'operator': '$eq',
                                'parentId': 'id-aece4ded-fd70-4c71-91a5-a2db37efe2b8'
                            }
                        ],
                        'parentId': None
                    }
                ]
            },
            'timezone': 'America/Belize',
            'fields': [{'name': 'sale_id', 'alias': 'sale_id'}, {'name': 'channel_id', 'alias': 'channel_id'},
                       {'name': 'channel_name', 'alias': 'channel_name'}, {'name': 'sale_date', 'alias': 'sale_date'},
                       {'name': 'sale_item_id', 'alias': 'sale_item_id'}, {'name': 'asin', 'alias': 'asin'},
                       {'name': 'title', 'alias': 'title'}, {'name': 'brand', 'alias': 'brand'},
                       {'name': 'upc', 'alias': 'upc'}, {'name': 'sku', 'alias': 'sku'},
                       {'name': 'brand_sku', 'alias': 'brand_sku'}, {'name': 'size', 'alias': 'size'},
                       {'name': 'style', 'alias': 'style'}, {'name': 'item_sale_charged', 'alias': 'item_sale_charged'},
                       {'name': 'item_shipping_charged', 'alias': 'item_shipping_charged'},
                       {'name': 'item_tax_charged', 'alias': 'item_tax_charged'},
                       {'name': 'cog', 'alias': 'cog'},
                       {'name': 'item_shipping_cost', 'alias': 'item_shipping_cost'},
                       {'name': 'item_ship_date', 'alias': 'item_ship_date'},
                       {'name': 'item_total_charged', 'alias': 'item_total_charged'},
                       {'name': 'item_total_cost', 'alias': 'item_total_cost'},
                       {'name': 'item_profit', 'alias': 'item_profit'}, {'name': 'item_margin', 'alias': 'item_margin'},
                       {'name': 'item_sale_status', 'alias': 'item_sale_status'},
                       {'name': 'item_profit_status', 'alias': 'item_profit_status'},
                       {'name': 'item_channel_listing_fee', 'alias': 'item_channel_listing_fee'},
                       {'name': 'item_other_channel_fees', 'alias': 'item_other_channel_fees'},
                       {'name': 'notes', 'alias': 'notes'}, {'name': 'created', 'alias': 'created'},
                       {'name': 'modified', 'alias': 'modified'}]
        }
    }

    def setUp(self):
        super().setUp()
        self.url = reverse('proxy-pf-to-ds', kwargs={'path': 'v1/ds/pf:{}:sale_items/exec'.format(self.client_id)})

    def test_owner_admin_analysis_ds(self):
        print("url: {}".format(self.url))
        headers = {
            'HTTP_AUTHORIZATION': 'Bearer {}'.format(self.jwt_token),
            'HTTP_X_PS_CLIENT_ID': self.client_id
        }

        rs = self.client.post(path=self.url, data=self.body, format='json', **headers)
        request = rs.wsgi_request
        try:
            body = json.loads(request.body)
        except ValueError:
            body = None
        cond = body['query']['filter']['conditions']
        timezone = body['query']['timezone']
        print(cond, timezone)
        self.assertTrue(len(cond) == len(self.body['query']['filter']['conditions']), msg="2 conditions not equal")
        self.assertTrue(cond == self.body['query']['filter']['conditions'], msg="2 conditions not equal")
        self.assertTrue(timezone == self.body['query']['timezone'], msg="2 timezone not equal")

    @patch('app.core.proxy.ds.DSProxyView.build_condition_for_24_hours', fake_build_condition_for_24_hours())
    @patch('rest_framework_simplejwt.tokens.Token.verify', fake_simple_jwt_check_verifying)
    def test_staff_analysis_ds1(self):
        self.role_update = {
            'key': ROLE_STAFF,
            'name': 'Staff'
        }
        self.permissions_update = {
            'SALE_VIEW_ALL': False,
            'SALE_VIEW_24H': True
        }
        #
        self.restart_patcher()
        #
        print("url: {}".format(self.url))
        headers = {
            'HTTP_AUTHORIZATION': 'Bearer {}'.format(self.jwt_token),
            'HTTP_X_PS_CLIENT_ID': self.client_id
        }
        #
        rs = self.client.post(path=self.url, data=self.body, format='json', **headers)
        request = rs.wsgi_request
        try:
            body = json.loads(request.body)
        except ValueError:
            body = None
        print(f"request body = {body}")
        cond = body['query']['filter']['conditions'][1]['conditions']
        timezone = body['query']['timezone']
        print(cond, timezone)
        self.assertEqual(cond[0], {'column': 'channel_name', 'value': "amazon.com", 'operator': '$eq'})
        self.assertEqual(cond[1], {'column': 'sale_date', 'value': "2020-01-01T05:00:00.000Z", 'operator': '$gte'})
        self.assertEqual(cond[2], {'column': 'sale_date', 'value': "2020-01-02T05:00:00.000Z", 'operator': '$lte'})
        self.assertTrue(timezone == self.body['query']['timezone'], msg="2 timezone not equal")

    @patch('rest_framework_simplejwt.tokens.Token.verify', fake_simple_jwt_check_verifying)
    def test_staff_analysis_ds2(self):
        self.role_update = {
            'key': ROLE_STAFF,
            'name': 'Staff'
        }
        self.permissions_update = {
            'SALE_VIEW_ALL': False,
            'SALE_VIEW_24H': False
        }
        #
        self.restart_patcher()
        #
        print("url: {}".format(self.url))
        headers = {
            'HTTP_AUTHORIZATION': 'Bearer {}'.format(self.jwt_token),
            'HTTP_X_PS_CLIENT_ID': self.client_id
        }
        #
        rs = self.client.post(path=self.url, data=self.body, format='json', **headers)
        print(rs)
        self.assertEqual(rs.status_code, status.HTTP_403_FORBIDDEN)
        content = json.loads(rs.content.decode('utf-8'))
        print(content)
        self.assertEqual(content['code'], 1026)
        self.assertEqual(content['message'], "User has not permissions access data analysis")

    def test_not_authenticated(self):
        print("url: {}".format(self.url))
        headers = {
            'HTTP_X_PS_CLIENT_ID': self.client_id
        }
        rs = self.client.post(path=self.url, data=self.body, format='json', **headers)
        print(rs)
        self.assertEqual(rs.status_code, status.HTTP_401_UNAUTHORIZED)
        content = json.loads(rs.content.decode('utf-8'))
        self.assertEqual(content['detail'], 'Authentication credentials were not provided.')

    @patch('rest_framework_simplejwt.tokens.Token.verify', fake_simple_jwt_check_verifying)
    def test_not_workspace(self):
        print("url: {}".format(self.url))
        headers = {
            'HTTP_AUTHORIZATION': 'Bearer {}'.format(self.jwt_token)
        }
        rs = self.client.post(path=self.url, data=self.body, format='json', **headers)
        print(rs)
        self.assertEqual(rs.status_code, status.HTTP_400_BAD_REQUEST)
        content = json.loads(rs.content.decode('utf-8'))
        print(content)
        self.assertEqual(content['code'], 1029)
        self.assertEqual(content['message'],
                         "Workspace Identity 'X-Ps-Client-Id' were not provided in request headers.")

    def fake_jwt_token_expired(self, request=None):
        msg = _('Signature has expired.')
        raise exceptions.AuthenticationFailed(msg)

    def test_jwt_token_expired(self):
        print("url: {}".format(self.url))
        headers = {
            'HTTP_AUTHORIZATION': 'Bearer {}'.format(self.jwt_token),
            'HTTP_X_PS_CLIENT_ID': self.client_id
        }
        with patch('app.core.simple_authentication.JWTTokenHandlerAuthentication.authenticate',
                   self.fake_jwt_token_expired):
            rs = self.client.post(path=self.url, data=self.body, format='json', **headers)
            print(rs)
            self.assertEqual(rs.status_code, status.HTTP_401_UNAUTHORIZED)
            content = json.loads(rs.content.decode('utf-8'))
            self.assertEqual(content['detail'], 'Signature has expired.')

    def fake_jwt_error_decoding(self, request=None):
        msg = _('Error decoding signature.')
        raise exceptions.AuthenticationFailed(msg)

    def test_jwt_error_decoding(self):
        print("url: {}".format(self.url))
        headers = {
            'HTTP_AUTHORIZATION': 'Bearer {}'.format(self.jwt_token),
            'HTTP_X_PS_CLIENT_ID': self.client_id
        }
        with patch('app.core.simple_authentication.JWTTokenHandlerAuthentication.authenticate',
                   self.fake_jwt_error_decoding):
            rs = self.client.post(path=self.url, data=self.body, format='json', **headers)
            print(rs)
            self.assertEqual(rs.status_code, status.HTTP_401_UNAUTHORIZED)
            content = json.loads(rs.content.decode('utf-8'))
            self.assertEqual(content['detail'], 'Error decoding signature.')

    def fake_jwt_invalid_token_error(self, request=None):
        raise exceptions.AuthenticationFailed()

    def test_jwt_invalid_token_error(self):
        print("url: {}".format(self.url))
        headers = {
            'HTTP_AUTHORIZATION': 'Bearer {}'.format(self.jwt_token),
            'HTTP_X_PS_CLIENT_ID': self.client_id
        }
        with patch('app.core.simple_authentication.JWTTokenHandlerAuthentication.authenticate',
                   self.fake_jwt_invalid_token_error):
            rs = self.client.post(path=self.url, data=self.body, format='json', **headers)
            print(rs)
            self.assertEqual(rs.status_code, status.HTTP_401_UNAUTHORIZED)
            content = json.loads(rs.content.decode('utf-8'))
            self.assertEqual(content['detail'], 'Incorrect authentication credentials.')

    def fake_user_client_portal_error(self, request):
        # fake error
        raise PSServiceException(status_code=status.HTTP_401_UNAUTHORIZED)

    def test_bad_request_user_permission_error(self):
        print("url: {}".format(self.url))
        headers = {
            'HTTP_AUTHORIZATION': 'Bearer {}'.format(self.jwt_token),
            'HTTP_X_PS_CLIENT_ID': self.client_id
        }
        with patch('app.core.simple_authentication.JWTTokenHandlerAuthentication.authenticate',
                   self.fake_user_client_portal_error):
            rs = self.client.post(path=self.url, data=self.body, format='json', **headers)
            print(rs)
            self.assertEqual(rs.status_code, status.HTTP_401_UNAUTHORIZED)
            content = json.loads(rs.content.decode('utf-8'))
            print(content)
            self.assertEqual(content['code'], 1027)
            self.assertEqual(content['message'], 'PS service error when call service')
