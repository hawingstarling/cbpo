import json
import os
import pathlib
from unittest.mock import patch
from django.urls import reverse
from rest_framework import status
from decimal import Decimal
from app.financial.jobs.data_flatten import flat_sale_items_bulks_sync_task
from app.financial.models import Sale, Channel, SaleItem
from app.financial.tests.base import BaseAPITest
from config.settings.common import ROOT_DIR

APPS_DIR = ROOT_DIR.path('app')

fixtures = [
    APPS_DIR + "financial/tests/fixtures/organization.json",
    APPS_DIR + "financial/tests/fixtures/clientportal.json",
    APPS_DIR + "financial/tests/fixtures/client_settings.json",
    APPS_DIR + "financial/tests/fixtures/brand.json",
    APPS_DIR + "financial/tests/fixtures/fulfillmentchannel.json",
    APPS_DIR + "financial/tests/fixtures/channel.json",
    APPS_DIR + "financial/tests/fixtures/sale_status.json",
    APPS_DIR + "financial/tests/fixtures/profit_status.json",
    APPS_DIR + "financial/tests/fixtures/plat_import_setting.json",
    APPS_DIR + "job/tests/fixtures/job_config.json",
]

client_id = '1dd0bded-e981-4d2f-9bef-2874016661e7'


def trigger_sync_sale_items(client_id):
    flat_sale_items_bulks_sync_task(client_id=client_id)


class SaleItemImportAPITest(BaseAPITest):
    fixtures = fixtures
    NUM_RECORD = 0

    def setUp(self):
        super().setUp()
        self.create_flatten_manage_sale_items()
        #
        self.sale_item_ids = []
        # file name
        self.file_name = 'data.xlsx'

        self.sale_ids = []

    def upload_import(self):
        url = reverse('upload-data-import-to-module', kwargs={'module': 'SaleItem'})
        headers = {
            'HTTP_AUTHORIZATION': 'Bearer {}'.format(self.jwt_token)
        }
        path_folder = pathlib.Path(__file__).parent.absolute()
        path_file = os.path.join(path_folder, 'fixtures', 'upload_sale_item', self.file_name)
        print(path_file)
        file = open(path_file, 'rb')
        data = {
            'file': file,
            'meta': '{"client_id": "' + self.client_id + '"}'
        }
        rs = self.client.post(path=url,
                              data=data,
                              format='multipart',
                              **headers)
        file.close()
        return rs

    def test_upload_sale_item_module(self):
        rs = self.upload_import()
        print(rs)
        self.assertEqual(rs.status_code, status.HTTP_201_CREATED)
        content = json.loads(rs.content.decode('utf-8'))
        print(content)
        self.assertIsNotNone(content, msg='Content is not None')
        print("process : {}".format(content.get('progress')))
        self.assertEqual(content["progress"], 100)
        self.assertEqual(content["status"], "uploaded")

    def items_import(self, import_id):
        url = reverse('items-data-import-of-module', kwargs={'module': 'SaleItem', 'import_id': import_id})
        headers = {
            'HTTP_AUTHORIZATION': 'Bearer {}'.format(self.jwt_token)
        }
        rs = self.client.get(path=url, format='json', **headers)
        return rs

    def test_get_items_sale_items_module(self):
        self.NUM_RECORD = 10
        rs = self.upload_import()
        content = json.loads(rs.content.decode('utf-8'))
        print(content)
        import_id = content["id"]
        rs = self.items_import(import_id)
        print(rs)
        self.assertEqual(rs.status_code, status.HTTP_200_OK)
        content = json.loads(rs.content.decode('utf-8'))
        print(content)
        self.assertEqual(content['total'], self.NUM_RECORD, msg="count record not correct")
        self.assertEqual(len(content['items']), self.NUM_RECORD, msg="count items record not correct")

    def validate_import(self, import_id, data):
        url = reverse('validate-data-import-of-module', kwargs={'module': 'SaleItem', 'import_id': import_id})
        headers = {
            'HTTP_AUTHORIZATION': 'Bearer {}'.format(self.jwt_token)
        }
        rs = self.client.put(path=url, data=data, format='json', **headers)
        return rs

    def validate_sale_item(self):
        rs = self.upload_import()
        content = json.loads(rs.content.decode('utf-8'))
        print(content)
        import_id = content["id"]
        map_config = content['column_mapping']
        data = {
            "column_mapping": map_config
        }
        rs = self.validate_import(import_id, data)
        print(rs)
        self.assertEqual(rs.status_code, status.HTTP_200_OK)
        content = json.loads(rs.content.decode('utf-8'))
        print(content)
        self.assertEqual(content["progress"], 100)
        self.assertEqual(content["status"], "validated")
        #
        return self.items_import(import_id)

    def test_validate_sale_item_module(self):
        print("validate file name : {}".format(self.file_name))
        number_row_pass = [1, 2, 3]
        number_row_fail = [4, 5, 6, 7, 8, 9]
        self.NUM_RECORD = 10
        rs = self.validate_sale_item()
        print(rs)
        self.assertEqual(rs.status_code, status.HTTP_200_OK)
        content = json.loads(rs.content.decode('utf-8'))
        print(content)
        self.assertEqual(content['total'], self.NUM_RECORD, msg="count record not correct")
        self.assertEqual(len(content['items']), self.NUM_RECORD, msg="count items record not correct")
        for item in content['items']:
            print("channel id : {}".format(item['channel_sale_id']))
            print("channel name : {}".format(item['channel']))
            print("validation errors : {}".format(item['_meta']['validation_errors']))
            if item['_meta']['number'] in number_row_pass:
                self.assertEqual(item['_meta']['valid'], True, msg="item valid not correct")
            if item['_meta']['number'] in number_row_fail:
                self.assertEqual(item['_meta']['valid'], False, msg="item valid not correct")

    def process_import(self, import_id):
        url = reverse('client-process-import-module',
                      kwargs={'module': 'SaleItem', 'import_id': import_id, 'client_id': self.client_id})
        headers = {
            'HTTP_AUTHORIZATION': 'Bearer {}'.format(self.jwt_token)
        }
        rs = self.client.put(path=url, data={}, format='json', **headers)
        return rs

    def get_items_import(self, import_id):
        #
        rs = self.items_import(import_id)
        print(rs)
        self.assertEqual(rs.status_code, status.HTTP_200_OK)
        content = json.loads(rs.content.decode('utf-8'))
        print(content)
        self.assertEqual(content['total'], self.NUM_RECORD, msg="count record not correct")
        self.assertEqual(len(content['items']), self.NUM_RECORD, msg="count items record not correct")
        return content['items']

    def validate_process_import(self, flatten_sync, number_row_pass: list = [], number_row_fail: list = []):
        """
        validate import process
            + flatten_sync : patch for mock function implement celery unittest
            + number row pass
            + number row fail
        :param flatten_sync:
        :param number_row_pass:
        :param number_row_fail:
        :return:
        """
        rs = self.upload_import()
        content = json.loads(rs.content.decode('utf-8'))
        print(content)
        import_id = content["id"]
        map_config = content['column_mapping']
        data = {
            "column_mapping": map_config
        }
        rs = self.validate_import(import_id, data)
        print(rs)
        content = json.loads(rs.content.decode('utf-8'))
        print(content)
        self.assertEqual(content["progress"], 100)
        self.assertEqual(content["status"], "validated")
        # process import
        rs = self.process_import(import_id)
        print(rs)
        self.assertEqual(rs.status_code, status.HTTP_200_OK)
        content = json.loads(rs.content.decode('utf-8'))
        self.assertEqual(content['progress'], 100)
        self.assertEqual(content['status'], 'processed')
        #
        flatten_sync.return_value = trigger_sync_sale_items(client_id=self.client_id)
        #
        rs = self.items_import(import_id)
        print(rs)
        self.assertEqual(rs.status_code, status.HTTP_200_OK)
        content = json.loads(rs.content.decode('utf-8'))
        print(content)
        self.assertEqual(content['total'], self.NUM_RECORD, msg="count record not correct")
        self.assertEqual(len(content['items']), self.NUM_RECORD, msg="count items record not correct")
        for item in content['items']:
            if item['_meta']['number'] in number_row_pass:
                print("complete validation error", item['_meta']['processing_errors'])
                self.assertEqual(item['_meta']['complete'], True, msg="item complete status not correct")
            if item['_meta']['number'] in number_row_fail:
                self.assertEqual(item['_meta']['complete'], False, msg="item complete status not correct")
        # check data sale item in table
        items_import = self.get_items_import(import_id)
        # sales
        self.sale_ids = []
        for item in items_import:
            if item['_meta']['number'] in number_row_pass:
                # check row file insert to table
                channel_sale_id = item['channel_sale_id']
                channel = item['channel']
                channel = Channel.objects.tenant_db_for(self.client_id).get(name=channel)
                sale = Sale.objects.tenant_db_for(self.client_id).get(channel_sale_id=channel_sale_id, channel=channel)
                self.sale_ids.append(str(sale.id))
                self.assertEqual(sale.saleitem_set.tenant_db_for(self.client_id).count() > 0, True,
                                 msg="sale item records not exist")
                # compare row import have sync to ds
                sale_item = sale.saleitem_set.tenant_db_for(sale.client_id).first()
                self.sale_item_ids = [str(sale_item.pk)]
                rs = self.get_result_flatten_data()
                self.assertEqual(len(rs), 1)
                self.compare_sale_item_update_ds(rs)
                self.verify_log_entry(1, 0)
        # validate sale data
        self.validate_data_sale_import(self.sale_ids)

    def __validate_calculate_cog_and_unit_cog(self, client_id):
        sale = Sale.objects.tenant_db_for(self.client_id).get(channel_sale_id='112-9454136-2630625',
                                                              client_id=client_id)
        sale_item = sale.saleitem_set.tenant_db_for(sale.client_id).get(sku='AT-ALW1933G-220-8.5D')
        self.assertEqual(sale_item.quantity, 2)
        self.assertEqual(sale_item.cog, Decimal('66.5'))
        self.assertEqual(sale_item.unit_cog, Decimal('33.25'))

    def validate_data_sale_import(self, sale_ids):
        print("-- verify data sale import reset --")
        sale_ids = list(set(sale_ids))
        sales = Sale.objects.tenant_db_for(self.client_id).filter(pk__in=sale_ids)
        for sale in sales.iterator():
            print("sale id : {}".format(sale.pk))
            query_set = SaleItem.objects.tenant_db_for(self.client_id).filter(sale=sale)
            item_sale_status_min = query_set.order_by('sale_status__order').first()
            self.assertEqual(item_sale_status_min.sale_status, sale.sale_status)
            # profit status
            item_sale_profit_min = query_set.order_by('profit_status__order').first()
            self.assertEqual(item_sale_profit_min.profit_status, sale.profit_status)
            # sale date
            sale_item_min = query_set.order_by('sale_date').first()
            self.assertEqual(sale_item_min.sale_date, sale.date)

    def test_import_sale_item_excel(self):
        self.file_name = 'data.xlsx'
        # import for workspace default
        number_row_pass = [1, 2, 3]
        number_row_fail = [4, 5, 6, 7, 8, 9]
        self.NUM_RECORD = 10
        with patch('app.financial.jobs.data_flatten.flat_sale_items_bulks_sync_task.delay') as flatten_sync:
            self.validate_process_import(flatten_sync, number_row_pass, number_row_fail)
            # validate calculate cog ang unit cog
            self.__validate_calculate_cog_and_unit_cog(self.client_id)

        sale_ids = list(set(self.sale_ids))
        sales = Sale.objects.tenant_db_for(self.client_id).filter(pk__in=sale_ids)
        for sale in sales:
            # customer name
            self.assertEqual(sale.customer_name, 'Test')
            self.assertEqual(sale.recipient_name, 'AAAAA')
            # line address
            self.assertEqual(sale.address_line_1, 'hello test line 1')
            self.assertEqual(sale.address_line_2, 'hello test line 2')
            self.assertEqual(sale.address_line_3, 'hello test line 3')

    def test_import_sale_item_csv(self):
        self.file_name = 'data.csv'
        # import for workspace default
        number_row_pass = [1, 2, 3]
        number_row_fail = [4, 5, 6]
        self.NUM_RECORD = 6
        self.file_name = 'data.csv'
        with patch('app.financial.jobs.data_flatten.flat_sale_items_bulks_sync_task.delay') as flatten_sync:
            self.validate_process_import(flatten_sync, number_row_pass, number_row_fail)

    def test_import_sale_item_2_item_separated_into_2_file(self):
        self.file_name = 'data.xlsx'
        # import for workspace default
        number_row_pass = [1, 2, 3]
        number_row_fail = [4, 5, 6, 7, 8, 9]
        self.NUM_RECORD = 10
        with patch('app.financial.jobs.data_flatten.flat_sale_items_bulks_sync_task.delay') as flatten_sync:
            self.validate_process_import(flatten_sync, number_row_pass, number_row_fail)

    def test_validate_error_import(self):
        self.file_name = 'data.xlsx'
        self.NUM_RECORD = 10
        print("validate file name : {}".format(self.file_name))
        number_row_pass = [1, 2, 3]
        number_row_fail = [4, 5, 6, 7, 8, 9, 10]
        rs = self.validate_sale_item()
        print(rs)
        self.assertEqual(rs.status_code, status.HTTP_200_OK)
        content = json.loads(rs.content.decode('utf-8'))
        print(content)
        self.assertEqual(content['total'], self.NUM_RECORD, msg="count record not correct")
        self.assertEqual(len(content['items']), self.NUM_RECORD, msg="count items record not correct")
        for item in content['items']:
            print("channel id : {}".format(item['channel_sale_id']))
            print("channel name : {}".format(item['channel']))
            validation_errors = item['_meta']['validation_errors']
            print("validation errors : {}".format(validation_errors))
            if item['_meta']['number'] in number_row_pass:
                self.assertEqual(item['_meta']['valid'], True, msg="item valid not correct")
            if item['_meta']['number'] in number_row_fail:
                self.assertEqual(item['_meta']['valid'], False, msg="item valid not correct")
                # test data record duplicate
                if item['_meta']['number'] in [4, 5]:
                    messages = [error['message'][0] for error in validation_errors if
                                error['message'][0] == 'Record 4 and 5 are duplicate (channel_sale_id, channel, sku)']
                    self.assertEqual(len(messages) > 0, True)
                if item['_meta']['number'] in [6, 7]:
                    messages = [error['message'][0] for error in validation_errors if
                                error['message'][0] == 'Record 6 and 7 are duplicate (channel_sale_id, channel, sku)']
                    self.assertEqual(len(messages) > 0, True)
                # test exist record channel invalid
                if item['_meta']['number'] in [9]:
                    messages = [error['message'][0] for error in validation_errors if
                                error['message'][0] == 'One item of "113-4728285-9171434" is invalid']
                    self.assertEqual(len(messages) > 0, True)
                # test ASIN , UPC/EAN, Sale Status , Profit Status is in valid
                if item['_meta']['number'] in [10]:
                    messages = {error['message'][0] for error in validation_errors}
                    self.assertEqual('ASIN is invalid' in messages, True)
                    self.assertEqual('UPC/EAN is invalid' in messages, True)
                    self.assertEqual('Sale Status is invalid' in messages, True)
                    self.assertEqual('Profit Status is invalid' in messages, True)
                    self.assertEqual('Channel Sale ID cannot be null' in messages, True)
                    self.assertEqual('Channel name "shopify" does not exist' in messages, True)
                    self.assertEqual('"SamSung" brand does not exist' in messages, True)
                    self.assertEqual('SKU cannot be null' in messages, True)
