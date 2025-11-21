import copy
import json
import logging
from unittest.mock import patch
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT
from rest_framework.test import APITestCase
from django.db import connections, DatabaseError
from app.core.exceptions import PSServiceException
from app.financial.jobs.data_flatten import flat_sale_items
from app.database.jobs.db_table_template import sync_db_table_template_workspace
from app.financial.models import SaleItem, DataFlattenTrack, Sale, SaleChargeAndCost, SaleItemFinancial, \
    CacheTransaction, GenericTransaction, LogClientEntry, Item, ItemCog, Activity, SKUVaultPrimeTrack, FedExShipment, \
    ShippingInvoice, ClientPortal, User
from app.database.helper import get_connection_workspace
from app.financial.tests.fixtures.jwt_token import JWT_TOKEN1, JWT_PAYLOADS_CONFIG
from app.financial.tests.fixtures.user_client import USER_AUTH_CONFIG, USER_CLIENT_CONFIG
from app.financial.variable.data_flatten_variable import FLATTEN_SALE_ITEM_KEY, DATA_FLATTEN_TYPE_ANALYSIS_LIST, \
    DATA_FLATTEN_TYPE_LIST, FLATTEN_SALE_ITEM_FINANCIAL_KEY
from app.financial.variable.job_status import SUCCESS
from config.settings.common import ROOT_DIR

logger = logging.getLogger(__name__)

APPS_DIR = ROOT_DIR.path('app')

fixtures = [
    APPS_DIR + "financial/tests/fixtures/organization.json",
    APPS_DIR + "financial/tests/fixtures/clientportal.json",
    APPS_DIR + "financial/tests/fixtures/user.json",
    APPS_DIR + "financial/tests/fixtures/plat_import_setting.json",
    APPS_DIR + "financial/tests/fixtures/financial_settings.json",
    APPS_DIR + "job/tests/fixtures/job_config.json",
]


@override_settings(
    USE_TZ=False,
    CELERY_EAGER_PROPAGATES_EXCEPTIONS=True,
    CELERY_TASK_ALWAYS_EAGER=True,
    BROKER_BACKEND="memory",
    URL_PORTAL_SERVICE="http://portal-api.qa.channelprecision.com",
    URL_DS_SERVICE="http://ds-api.qa.channelprecision.com",
    URL_AC_SERVICE="http://ac-api.qa.channelprecision.com",
    AC_API_KEY="7ev4daqef5b5xzzwmuds4es52g6xpaty66p9sj4c"
)
class BaseAPITest(APITestCase):
    fixtures = fixtures
    type_flatten = FLATTEN_SALE_ITEM_KEY

    def setUp(self):
        self.client_id = '1dd0bded-e981-4d2f-9bef-2874016661e7'
        self.user_id = 'ce0be581-49df-4288-8b72-e961dd30a105'
        self.client_db = get_connection_workspace(self.client_id)
        self.permissions_update = {}
        self.role_update = {}
        self.jwt_token = JWT_TOKEN1
        #
        self.start_patcher()

        self.db_table_client(new_table=True)
        #
        self.init_client_user()

    def init_client_user(self):
        try:
            client_setting_base = copy.deepcopy(USER_CLIENT_CONFIG.get(self.client_id, {}))
            client_info = client_setting_base['client_information']
            user_info = client_setting_base['user']
            del user_info['enabled']
            client = ClientPortal(**client_info)
            ClientPortal.objects.bulk_create([client], ignore_conflicts=True)
            user = User(**user_info)
            User.objects.bulk_create([user], ignore_conflicts=True)
        except Exception as ex:
            print(f"[{self.__class__.__name__}][init_client_user] {ex}")

    @classmethod
    def setUpClass(cls):
        #
        try:
            Sale.objects.tenant_db_for(None).count()
            SaleChargeAndCost.objects.tenant_db_for(None).count()
            SaleItem.objects.tenant_db_for(None).count()
            SaleItemFinancial.objects.tenant_db_for(None).count()
            GenericTransaction.objects.tenant_db_for(None).count()
            CacheTransaction.objects.tenant_db_for(None).count()
            LogClientEntry.objects.tenant_db_for(None).count()
            Item.objects.tenant_db_for(None).count()
            ItemCog.objects.tenant_db_for(None).count()
            Activity.objects.tenant_db_for(None).count()
            SKUVaultPrimeTrack.objects.tenant_db_for(None).count()
            ShippingInvoice.objects.tenant_db_for(None).count()
            FedExShipment.objects.tenant_db_for(None).count()
        except Exception as ex:
            pass
        super().setUpClass()

    @staticmethod
    def db_table_client(new_table: bool = False):
        #
        sync_db_table_template_workspace(client_id='1dd0bded-e981-4d2f-9bef-2874016661e7', new_table=new_table)

    def start_patcher(self):
        self.patcher_user_client = patch('app.core.services.portal_service.PortalService.get_client_setting_user_ps',
                                         return_value=self.fake_response_client_setting())
        self.patcher_user_auth = patch('app.core.services.portal_service.PortalService.get_user_info_auth',
                                       return_value=self.fake_auth_user())
        self.patcher_jwt_decode_handler = patch('jwt.decode',
                                                return_value=self.jwt_decode_handler())
        self.patcher_simple_jwt_verifying = patch('rest_framework_simplejwt.tokens.Token.verify',
                                                  self.fake_simple_jwt_verifying)
        self.mock_user_client = self.patcher_user_client.start()
        self.mock_user_auth = self.patcher_user_auth.start()
        self.mock_jwt_decode_handler = self.patcher_jwt_decode_handler.start()
        self.mock_simple_jwt_verifying = self.patcher_simple_jwt_verifying.start()

    def fake_simple_jwt_verifying(self):
        pass

    def tearDown(self):
        self.stop_patcher()

    def restart_patcher(self):
        self.stop_patcher()
        self.start_patcher()

    def stop_patcher_user_client(self):
        self.patcher_user_client.stop()

    def start_patcher_user_client(self):
        self.patcher_user_client = patch('app.core.services.portal_service.PortalService.get_client_setting_user_ps',
                                         return_value=self.fake_response_client_setting())
        self.mock_user_client = self.patcher_user_client.start()

    def stop_patcher(self):
        self.patcher_user_client.stop()
        self.patcher_user_auth.stop()
        self.patcher_jwt_decode_handler.stop()

    def jwt_decode_handler(self):
        return JWT_PAYLOADS_CONFIG.get(self.user_id, {})

    def fake_auth_user(self):
        return USER_AUTH_CONFIG.get(self.user_id, {})

    def dictfetchall(self, cursor):
        "Return all rows from a cursor as a dict"
        columns = [col[0] for col in cursor.description]
        return [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]

    def verify_log_entry(self, number, action):
        count_log_entries = LogClientEntry.objects.tenant_db_for(self.client_id).filter(
            object_pk__in=self.sale_item_ids,
            action=action)
        self.assertEqual(count_log_entries.count(), number)

    def truncate_data(self):
        try:
            if Sale.all_objects.tenant_db_for(self.client_id).count() > 0:
                sql = """
                    TRUNCATE financial_1dd0bded_e981_4d2f_9bef_2874016661e7_saleitem CASCADE;
                    TRUNCATE financial_1dd0bded_e981_4d2f_9bef_2874016661e7_sale CASCADE;
                """
                with connections[self.client_db].cursor() as cursor:
                    try:
                        cursor.execute(sql)
                    except Exception or DatabaseError as err:
                        print(err)
        except Exception as ex:
            pass

    def create_extension_tablefunc(self):
        # enable extension tablefunc for using crosstab in PSQL
        sql = """
            CREATE EXTENSION IF NOT EXISTS tablefunc;
        """
        res = []
        with connections[self.client_db].cursor() as cursor:
            try:
                cursor.execute(sql)
            except Exception or DatabaseError as err:
                print(err)

    def get_result_flatten_data(self):
        sale_item_ids = tuple(self.sale_item_ids) if len(self.sale_item_ids) > 1 else """('{}')""".format(
            self.sale_item_ids[0])
        table_name = "flatten_sale_items_{}".format(self.client_id.replace('-', '_'))
        cond = "{}.sale_item_id IN {}".format(table_name, sale_item_ids)
        sql = """SELECT * FROM {} WHERE {}""".format(table_name, cond)
        res = []
        with connections[self.client_db].cursor() as cursor:
            try:
                cursor.execute(sql)
                res = self.dictfetchall(cursor)
                print("result query from table flatten : {}".format(res))
            except Exception or DatabaseError as err:
                print(err)
                cursor.execute("ROLLBACK")
            return res

    def compare_sale_item_update_ds(self, rs: list = [], sale_item_ids: list = []):
        if not sale_item_ids:
            sale_item_ids = self.sale_item_ids
        for row in rs:
            sale_item_id = str(row['sale_item_id'])
            self.assertEqual(sale_item_id in sale_item_ids, True, msg='sale item id not in list update')
            #
            print("row data source : {}".format(row))
            sale_item = SaleItem.objects.tenant_db_for(self.client_id).get(pk=sale_item_id)
            self.compare_sale_item_vs_data_source(sale_item, row)

    def compare_sale_item_vs_data_source(self, sale_item: SaleItem = None, sale_item_datasource: dict = {}):
        assert sale_item is not None, "Sale Item is not None"
        assert sale_item_datasource, "Sale Item DS is not Empty"
        logger.debug(f"[{self.__class__.__name__}][{self.client_id}] order ds info : {sale_item_datasource}")
        self.assertEqual(sale_item.sale.id, sale_item_datasource['sale_id'])
        self.assertEqual(sale_item.sale.channel_sale_id, sale_item_datasource['channel_id'])
        self.assertEqual(sale_item.sale.channel.name, sale_item_datasource['channel_name'])
        self.assertEqual(sale_item.sale_date, sale_item_datasource['sale_date'])
        self.assertEqual(sale_item.id, sale_item_datasource['sale_item_id'])
        self.assertEqual(sale_item.asin, sale_item_datasource['asin'])
        self.assertEqual(sale_item.title, sale_item_datasource['title'])
        # compare brand
        brand = sale_item.brand.name if sale_item.brand else None
        self.assertEqual(brand, sale_item_datasource['brand'])
        #
        self.assertEqual(sale_item.upc, sale_item_datasource['upc'])
        self.assertEqual(sale_item.sku, sale_item_datasource['sku'])
        # compare size
        size = sale_item.size.value if sale_item.size else None
        self.assertEqual(size, sale_item_datasource['size'])
        # compared style
        style = sale_item.style.value if sale_item.style else None
        self.assertEqual(style, sale_item_datasource['style'])
        # compare fulfillment_type
        fulfillment_type = sale_item.fulfillment_type.name if sale_item.fulfillment_type else None
        self.assertEqual(fulfillment_type, sale_item_datasource['fulfillment_type'])
        # compare state
        self.assertEqual(sale_item.sale_charged, sale_item_datasource['item_sale_charged'])
        self.assertEqual(sale_item.shipping_charged, sale_item_datasource['item_shipping_charged'])
        self.assertEqual(sale_item.tax_charged, sale_item_datasource['item_tax_charged'])
        self.assertEqual(sale_item.cog, sale_item_datasource['cog'])
        print(f'unit cog :  {sale_item.unit_cog}')
        self.assertEqual(sale_item.unit_cog, sale_item_datasource['unit_cog'])
        #
        self.assertEqual(sale_item.shipping_cost, sale_item_datasource['item_shipping_cost'])
        self.assertEqual(sale_item.shipping_cost_accuracy, sale_item_datasource['shipping_cost_accuracy'])
        if sale_item.shipping_cost_accuracy is not None and sale_item.shipping_cost_accuracy == 100:
            self.assertEqual(sale_item_datasource['actual_shipping_cost'], sale_item_datasource['item_shipping_cost'])
        else:
            self.assertEqual(sale_item_datasource['estimated_shipping_cost'],
                             sale_item_datasource['item_shipping_cost'])
        #
        self.assertEqual(sale_item.ship_date, sale_item_datasource['item_ship_date'])
        self.assertEqual(sale_item.total_charged, sale_item_datasource['item_total_charged'])
        self.assertEqual(sale_item.total_cost, sale_item_datasource['item_total_cost'])
        self.assertEqual(sale_item.profit, sale_item_datasource['item_profit'])
        self.assertEqual(sale_item.margin, sale_item_datasource['item_margin'])
        self.assertEqual(sale_item.sale_status.value, sale_item_datasource['item_sale_status'])
        self.assertEqual(sale_item.profit_status.value, sale_item_datasource['item_profit_status'])
        #
        self.assertEqual(sale_item.channel_listing_fee, sale_item_datasource['item_channel_listing_fee'])
        self.assertEqual(sale_item.channel_listing_fee_accuracy, sale_item_datasource['channel_listing_fee_accuracy'])
        #
        self.assertEqual(sale_item.other_channel_fees, sale_item_datasource['item_other_channel_fees'])
        self.assertEqual(sale_item.notes, sale_item_datasource['notes'])
        print("Quantity sale item : {}".format(sale_item.quantity))
        self.assertEqual(sale_item.quantity, sale_item_datasource['quantity'])
        # info sale address
        self.assertEqual(sale_item.sale.state, sale_item_datasource['state'])
        self.assertEqual(sale_item.sale.city, sale_item_datasource['city'])
        self.assertEqual(sale_item.sale.country, sale_item_datasource['country'])
        self.assertEqual(sale_item.sale.postal_code, sale_item_datasource['postal_code'])
        self.assertEqual(sale_item.sale.customer_name, sale_item_datasource['customer_name'])
        self.assertEqual(sale_item.sale.recipient_name, sale_item_datasource['recipient_name'])

    def fake_response_client_setting(self):
        """
        permissions_update = {
            {key}: {status}
        }
        :param :
        :return:
        """
        client_setting_base = USER_CLIENT_CONFIG.get(self.client_id, {})
        if not client_setting_base:
            raise PSServiceException(status_code=status.HTTP_401_UNAUTHORIZED)
        client_setting = copy.deepcopy(client_setting_base)
        permissions = client_setting.get('permissions')
        role = client_setting.get('role')
        if self.role_update:
            role['key'] = self.role_update.get('key')
            role['name'] = self.role_update.get('name')
        for key in self.permissions_update.keys():
            for item in permissions:
                if item['permission'] == key:
                    item['enabled'] = self.permissions_update[key]
        return client_setting

    def create_flatten_manage_sale_items(self):
        for type_flatten in DATA_FLATTEN_TYPE_ANALYSIS_LIST:
            data_source_id = f"pf:{self.client_id}:{str.lower(type_flatten)}"
            DataFlattenTrack.objects.tenant_db_for(self.client_id).update_or_create(client_id=self.client_id,
                                                                                    type=type_flatten, live_feed=True,
                                                                                    status=SUCCESS,
                                                                                    data_source_id=data_source_id)

            # Generate ds
            if type_flatten == FLATTEN_SALE_ITEM_KEY:
                # DS Analysis
                flat_sale_items(self.client_id, type_flatten)

    def create_full_flatten_manage(self):
        for type_flatten in DATA_FLATTEN_TYPE_LIST:
            data_source_id = f"pf:{self.client_id}:{str.lower(type_flatten)}"
            DataFlattenTrack.objects.tenant_db_for(self.client_id).update_or_create(client_id=self.client_id,
                                                                                    type=type_flatten, live_feed=True,
                                                                                    status=SUCCESS,
                                                                                    data_source_id=data_source_id)

            # Generate ds
            if type_flatten == FLATTEN_SALE_ITEM_KEY:
                # DS Analysis
                flat_sale_items(self.client_id, type_flatten)

    def get_list_custom_type(self, custom_type: str = None, status_res: int = HTTP_200_OK, number_records: int = 0,
                             key_check: str = None):
        args_view = {
            'CustomFilter': 'client-user-custom-filter-list-create',
            'CustomColumn': 'client-user-custom-column-list-create',
            'CustomView': 'client-user-custom-view-list-create'
        }
        view_name = args_view.get(custom_type, None)
        print('view name {}'.format(view_name))
        url = reverse(view_name,
                      kwargs={
                          'client_id': self.client_id,
                          'user_id': self.user_id
                      })
        headers = {
            'HTTP_AUTHORIZATION': 'Bearer {}'.format(self.jwt_token)
        }
        rs = self.client.get(path=url, format='json', **headers)
        print(rs)
        self.assertEqual(rs.status_code, status_res)
        content = json.loads(rs.content.decode('utf-8'))
        print(content)
        self.assertEqual(content.get('count'), number_records)
        results = content.get('results')
        if key_check:
            self.assertTrue(content.get('count') > 0, msg='number row empty')
            first_item = results[0]
            self.assertTrue(key_check in first_item, msg='key not found')
        return content

    def get_custom_type(self, obj_id: str = None, custom_type: str = None, status_res: int = HTTP_200_OK,
                        key_checks: list = []):
        args_view = {
            'CustomFilter': 'client-user-custom-filter-update-retrieve-destroy',
            'CustomColumn': 'client-user-custom-column-update-retrieve-destroy',
            'CustomView': 'client-user-custom-view-update-retrieve-destroy'
        }
        view_name = args_view.get(custom_type, None)
        print('view name {}'.format(view_name))
        url = reverse(view_name,
                      kwargs={
                          'client_id': self.client_id,
                          'user_id': self.user_id,
                          'pk': obj_id
                      })
        headers = {
            'HTTP_AUTHORIZATION': 'Bearer {}'.format(self.jwt_token)
        }
        rs = self.client.get(path=url, format='json', **headers)
        print(rs)
        self.assertEqual(rs.status_code, status_res)
        content = json.loads(rs.content.decode('utf-8'))
        print(content)
        if key_checks and status_res == HTTP_200_OK:
            for key in key_checks:
                self.assertTrue(key in content, msg='key not found')
        return content

    def update_custom_type(self, obj_id: str = None, custom_type: str = None, status_res: int = HTTP_200_OK,
                           data: dict = {}):
        args_view = {
            'CustomFilter': 'client-user-custom-filter-update-retrieve-destroy',
            'CustomColumn': 'client-user-custom-column-update-retrieve-destroy',
            'CustomView': 'client-user-custom-view-update-retrieve-destroy'
        }
        view_name = args_view.get(custom_type, None)
        print('view name {}'.format(view_name))
        url = reverse(view_name,
                      kwargs={
                          'client_id': self.client_id,
                          'user_id': self.user_id,
                          'pk': obj_id
                      })
        headers = {
            'HTTP_AUTHORIZATION': 'Bearer {}'.format(self.jwt_token)
        }
        rs = self.client.put(path=url, data=data, format='json', **headers)
        print(rs)
        self.assertEqual(rs.status_code, status_res)
        content = json.loads(rs.content.decode('utf-8'))
        print(content)
        for key in data.keys():
            self.assertEqual(data[key], content[key])
        return content

    def create_custom_type(self, custom_type: str = None, status_res: int = HTTP_201_CREATED, key_check: str = None):
        args_view = {
            'CustomFilter': 'client-user-custom-filter-list-create',
            'CustomColumn': 'client-user-custom-column-list-create',
            'CustomView': 'client-user-custom-view-list-create',
            'CustomReport': 'client-user-custom-reports-list-create',
        }
        view_name = args_view.get(custom_type, None)
        print('view name {}'.format(view_name))
        url = reverse(view_name,
                      kwargs={
                          'client_id': self.client_id,
                          'user_id': self.user_id
                      })
        headers = {
            'HTTP_AUTHORIZATION': 'Bearer {}'.format(self.jwt_token)
        }
        data = {
            'name': 'test_{}'.format(custom_type),
            # 'ds_filter': {},
            'ds_column': {},
            'ds_config': {},
            'share_mode': 0
        }
        rs = self.client.post(path=url, data=data, format='json', **headers)
        print(rs)
        self.assertEqual(rs.status_code, status_res)
        content = json.loads(rs.content.decode('utf-8'))
        print(content)
        if key_check and status_res == HTTP_201_CREATED:
            self.assertTrue(key_check in content, msg='key not found')
        return content

    def delete_custom_type(self, obj_id: str = None, custom_type: str = None, status_res: int = HTTP_204_NO_CONTENT):
        args_view = {
            'CustomFilter': 'client-user-custom-filter-update-retrieve-destroy',
            'CustomColumn': 'client-user-custom-column-update-retrieve-destroy',
            'CustomView': 'client-user-custom-view-update-retrieve-destroy'
        }
        view_name = args_view.get(custom_type, None)
        print('view name {}'.format(view_name))
        url = reverse(view_name,
                      kwargs={
                          'client_id': self.client_id,
                          'user_id': self.user_id,
                          'pk': obj_id
                      })
        headers = {
            'HTTP_AUTHORIZATION': 'Bearer {}'.format(self.jwt_token)
        }
        rs = self.client.delete(path=url, format='json', **headers)
        print(rs)
        self.assertEqual(rs.status_code, status_res)

    def create_share_custom_type(self, obj_id: str = None, custom_type: str = None, status_res: int = HTTP_200_OK,
                                 data: dict = None):
        args_view = {
            'CustomFilter': 'client-user-custom-filter-list-create-share-mode',
            'CustomColumn': 'client-user-custom-column-list-create-share-mode',
            'CustomView': 'client-user-custom-view-list-create-share-mode'
        }
        view_name = args_view.get(custom_type, None)
        print('view name {}'.format(view_name))
        url = reverse(view_name,
                      kwargs={
                          'client_id': self.client_id,
                          'user_id': self.user_id,
                          'pk': obj_id
                      })
        headers = {
            'HTTP_AUTHORIZATION': 'Bearer {}'.format(self.jwt_token)
        }
        rs = self.client.post(path=url, data=data, format='json', **headers)
        print(rs)
        self.assertEqual(rs.status_code, status_res)

    def get_share_custom_type(self, obj_id: str = None, custom_type: str = None, status_res: int = HTTP_200_OK,
                              data: dict = {}):
        args_view = {
            'CustomFilter': 'client-user-custom-filter-list-create-share-mode',
            'CustomColumn': 'client-user-custom-column-list-create-share-mode',
            'CustomView': 'client-user-custom-view-list-create-share-mode'
        }
        view_name = args_view.get(custom_type, None)
        print('view name {}'.format(view_name))
        url = reverse(view_name,
                      kwargs={
                          'client_id': self.client_id,
                          'user_id': self.user_id,
                          'pk': obj_id
                      })
        headers = {
            'HTTP_AUTHORIZATION': 'Bearer {}'.format(self.jwt_token)
        }
        rs = self.client.get(path=url, format='json', **headers)
        print(rs)
        self.assertEqual(rs.status_code, status_res)
        content = json.loads(rs.content.decode('utf-8'))
        print(content)
        if data:
            result = content.get('results')
            shared_users = {item['user_email']: item['permission'] for item in data.get('shared_users')}
            self.assertTrue(result is not None, True)
            result = {item['user_email']: item['permission'] for item in result}
            for key in shared_users.keys():
                self.assertEqual(shared_users[key], result[key])
        return content
