import json
import os
import pathlib

from django.forms import model_to_dict
from django.urls import reverse
from rest_framework import status

from app.financial.models import Item
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


class ItemImportAPITest(BaseAPITest):
    fixtures = fixtures
    NUM_RECORD = 0

    def setUp(self):
        super().setUp()
        self.create_flatten_manage_sale_items()
        #
        self.sale_item_ids = []
        # file name
        self.file_name = 'item.xlsx'

    def upload_import(self):
        url = reverse('upload-data-import-to-module', kwargs={'module': 'ItemModule'})
        headers = {
            'HTTP_AUTHORIZATION': 'Bearer {}'.format(self.jwt_token)
        }
        path_folder = pathlib.Path(__file__).parent.absolute()
        path_file = os.path.join(path_folder, 'fixtures', 'upload_item', self.file_name)
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
        url = reverse('items-data-import-of-module', kwargs={'module': 'ItemModule', 'import_id': import_id})
        headers = {
            'HTTP_AUTHORIZATION': 'Bearer {}'.format(self.jwt_token)
        }
        rs = self.client.get(path=url, format='json', **headers)
        return rs

    def test_get_items_sale_items_module(self):
        self.NUM_RECORD = 3
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
        url = reverse('validate-data-import-of-module', kwargs={'module': 'ItemModule', 'import_id': import_id})
        headers = {
            'HTTP_AUTHORIZATION': 'Bearer {}'.format(self.jwt_token)
        }
        rs = self.client.put(path=url, data=data, format='json', **headers)
        return rs

    def validate_item(self):
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

    def test_validate_item_module(self):
        print("validate file name : {}".format(self.file_name))
        number_row_pass = [1, 2, 3]
        self.NUM_RECORD = 3
        rs = self.validate_item()
        print(rs)
        self.assertEqual(rs.status_code, status.HTTP_200_OK)
        content = json.loads(rs.content.decode('utf-8'))
        print(content)
        self.assertEqual(content['total'], self.NUM_RECORD, msg="count record not correct")
        self.assertEqual(len(content['items']), self.NUM_RECORD, msg="count items record not correct")
        for item in content['items']:
            print("validation errors : {}".format(item['_meta']['validation_errors']))
            if item['_meta']['number'] in number_row_pass:
                self.assertEqual(item['_meta']['valid'], True, msg="item valid not correct")

    def process_import(self, import_id):
        url = reverse('client-process-import-module',
                      kwargs={'module': 'ItemModule', 'import_id': import_id, 'client_id': self.client_id})
        headers = {
            'HTTP_AUTHORIZATION': 'Bearer {}'.format(self.jwt_token)
        }
        rs = self.client.put(path=url, data={}, format='json', **headers)
        return rs

    def validate_process_import(self, number_row_pass: list = [], number_row_fail: list = []):
        """
        validate import process
            + number row pass
            + number row fail
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
        for item in items_import:
            if item['_meta']['number'] in number_row_pass:
                # check row file insert to table
                sku = item['sku']
                fulfillment_type = item['fulfillment_type']
                item_import = Item.objects.tenant_db_for(self.client_id).get(client_id=self.client_id, sku=sku)
                print("data import model : {}".format(model_to_dict(item_import)))
                self.assertEqual(item_import is not None, 1)
                self.assertEqual(item_import.fulfillment_type.name, fulfillment_type)

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

    def test_import_item_excel(self):
        # import for workspace default
        number_row_pass = [1, 2, 3]
        number_row_fail = []
        self.NUM_RECORD = 3
        self.validate_process_import(number_row_pass, number_row_fail)
