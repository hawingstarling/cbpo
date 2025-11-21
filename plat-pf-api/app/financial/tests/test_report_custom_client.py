import json
from django.urls import reverse
from django.utils import timezone
from rest_framework.status import HTTP_201_CREATED
from app.financial.models import SaleItem
from app.financial.tests.base import BaseAPITest
from config.settings.common import ROOT_DIR, BASE_URL

APPS_DIR = ROOT_DIR.path('app')

fixtures = [
    APPS_DIR + "financial/tests/fixtures/brand.json",
    APPS_DIR + "financial/tests/fixtures/fulfillmentchannel.json",
    APPS_DIR + "financial/tests/fixtures/channel.json",
    APPS_DIR + "financial/tests/fixtures/sale_status.json",
    APPS_DIR + "financial/tests/fixtures/profit_status.json",
    APPS_DIR + "financial/tests/fixtures/sale.json",
    APPS_DIR + "financial/tests/fixtures/sale_charge_and_cost.json",
    APPS_DIR + "financial/tests/fixtures/sale_item.json",
]


class ClientCustomReportAPITest(BaseAPITest):
    fixtures = BaseAPITest.fixtures + fixtures

    def setUp(self):
        super().setUp()
        # create table manage data sale items
        self.create_flatten_manage_sale_items()
        #
        self.first_record = SaleItem.objects.tenant_db_for(self.client_id).order_by('created').first()
        #
        self.sale_item_ids = [str(self.first_record.pk)]

    def test_create_custom_report(self):
        url = reverse('client-user-custom-reports-list-create',
                      kwargs={
                          'client_id': self.client_id,
                          'user_id': self.user_id
                      })
        headers = {
            'HTTP_AUTHORIZATION': 'Bearer {}'.format(self.jwt_token)
        }
        name_report = f'custom-report-test-{timezone.now().timestamp()}'
        data = {
            'name': name_report,
            'item_ids': self.sale_item_ids,
            'ds_query': {},
            'bulk_operations': [
                {
                    "column": "title",
                    "action": "change_to",
                    "value": "XXXX"
                }
            ]
        }
        rs = self.client.post(path=url, data=data, format='json', **headers)
        print(rs)
        self.assertEqual(rs.status_code, HTTP_201_CREATED)
        content = json.loads(rs.content.decode('utf-8'))
        print(content)
        self.assertTrue('id' in content, msg='key not found')
        time_now = timezone.now()
        d, m, y = time_now.strftime('%d'), time_now.strftime('%m'), time_now.year
        self.assertEqual(
            f"{BASE_URL}/media/pf/lib_imports/reports/{self.client_id}/{y}/{m}/{d}/{name_report}" in content[
                'download_url'], True)
