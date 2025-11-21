import json
from django.urls import reverse
from rest_framework import status
from app.financial.models import SaleItem, FulfillmentChannel
from app.financial.tests.base import BaseAPITest
from app.financial.variable.shipping_cost_source import AMZ_POSTAGE_BILLING_SOURCE_KEY
from config.settings.common import ROOT_DIR

APPS_DIR = ROOT_DIR.path('app')

fixtures = [
    APPS_DIR + "financial/tests/fixtures/organization.json",
    APPS_DIR + "financial/tests/fixtures/clientportal.json",
    APPS_DIR + "financial/tests/fixtures/brand.json",
    APPS_DIR + "financial/tests/fixtures/fulfillmentchannel.json",
    APPS_DIR + "financial/tests/fixtures/variant.json",
    APPS_DIR + "job/tests/fixtures/job_config.json"
]


class ClientBrandAPITest(BaseAPITest):
    fixtures = fixtures

    def test_get_list_brand(self):
        url = reverse('client-list-brands', kwargs={'client_id': self.client_id})
        #
        headers = {
            'HTTP_AUTHORIZATION': 'Bearer {}'.format(self.jwt_token)
        }
        rs = self.client.get(path=url, format='json', **headers)
        self.assertEqual(rs.status_code, status.HTTP_200_OK)
        content = json.loads(rs.content.decode('utf-8'))
        print(content)
        self.assertEqual(content['count'], 5)
        self.assertEqual(len(content['results']), 5)

    def test_get_list_brand_search(self):
        search = "Alt"
        url = reverse('client-list-brands', kwargs={'client_id': self.client_id}) + "?search={}".format(search)
        headers = {
            'HTTP_AUTHORIZATION': 'Bearer {}'.format(self.jwt_token)
        }
        rs = self.client.get(path=url, format='json', **headers)
        self.assertEqual(rs.status_code, status.HTTP_200_OK)
        content = json.loads(rs.content.decode('utf-8'))
        print(content)
        self.assertEqual(content['count'], 1)
        self.assertEqual(len(content['results']), 1)
        item = content['results'][0]
        self.assertEqual(item['name'], "Altra")


class ClientFulfillTypeAPITest(BaseAPITest):
    fixtures = fixtures

    def test_get_list_fulfillment_types(self):
        url = reverse('client-list-fulfillment-types', kwargs={'client_id': self.client_id})
        headers = {
            'HTTP_AUTHORIZATION': 'Bearer {}'.format(self.jwt_token)
        }
        rs = self.client.get(path=url, format='json', **headers)
        self.assertEqual(rs.status_code, status.HTTP_200_OK)
        content = json.loads(rs.content.decode('utf-8'))
        print(content)
        self.assertEqual(content['count'], 5)
        self.assertEqual(len(content['results']), 5)

    def test_get_list_fulfillment_types_search(self):
        search = "MFN-Prime"
        url = reverse('client-list-fulfillment-types', kwargs={'client_id': self.client_id}) + "?search={}".format(
            search)
        headers = {
            'HTTP_AUTHORIZATION': 'Bearer {}'.format(self.jwt_token)
        }
        rs = self.client.get(path=url, format='json', **headers)
        self.assertEqual(rs.status_code, status.HTTP_200_OK)
        content = json.loads(rs.content.decode('utf-8'))
        print(content)
        self.assertEqual(content['count'], 1)
        self.assertEqual(len(content['results']), 1)
        item = content['results'][0]
        self.assertEqual(item['name'], "MFN-Prime")


class ClientVariantAPITest(BaseAPITest):
    fixtures = fixtures

    def test_get_list_size(self):
        url = reverse('sale-items-variations', kwargs={'client_id': self.client_id, 'type': 'Size'})
        headers = {
            'HTTP_AUTHORIZATION': 'Bearer {}'.format(self.jwt_token)
        }
        rs = self.client.get(path=url, format='json', **headers)
        self.assertEqual(rs.status_code, status.HTTP_200_OK)
        content = json.loads(rs.content.decode('utf-8'))
        print(content)
        self.assertEqual(content['count'], 2)
        self.assertEqual(len(content['results']), 2)

    def test_get_list_style(self):
        url = reverse('sale-items-variations', kwargs={'client_id': self.client_id, 'type': 'Style'})
        headers = {
            'HTTP_AUTHORIZATION': 'Bearer {}'.format(self.jwt_token)
        }
        rs = self.client.get(path=url, format='json', **headers)
        self.assertEqual(rs.status_code, status.HTTP_200_OK)
        content = json.loads(rs.content.decode('utf-8'))
        print(content)
        self.assertEqual(content['count'], 2)
        self.assertEqual(len(content['results']), 2)

    def test_get_list_size_search(self):
        search = "10"
        url = reverse('sale-items-variations',
                      kwargs={'client_id': self.client_id, 'type': 'Size'}) + "?search={}".format(search)
        headers = {
            'HTTP_AUTHORIZATION': 'Bearer {}'.format(self.jwt_token)
        }
        rs = self.client.get(path=url, format='json', **headers)
        self.assertEqual(rs.status_code, status.HTTP_200_OK)
        content = json.loads(rs.content.decode('utf-8'))
        print(content)
        self.assertEqual(content['count'], 1)
        self.assertEqual(len(content['results']), 1)
        item = content['results'][0]
        self.assertEqual(item['name'], search)

    def test_get_list_style_search(self):
        search = "Summer"
        url = reverse('sale-items-variations',
                      kwargs={'client_id': self.client_id, 'type': 'Style'}) + "?search={}".format(search)
        headers = {
            'HTTP_AUTHORIZATION': 'Bearer {}'.format(self.jwt_token)
        }
        rs = self.client.get(path=url, format='json', **headers)
        self.assertEqual(rs.status_code, status.HTTP_200_OK)
        content = json.loads(rs.content.decode('utf-8'))
        print(content)
        self.assertEqual(content['count'], 1)
        self.assertEqual(len(content['results']), 1)
        item = content['results'][0]
        self.assertEqual(item['name'], search)


class ClientSaleItemTransaction(BaseAPITest):
    fixtures = fixtures + [
        APPS_DIR + "financial/tests/fixtures/channel.json",
        APPS_DIR + "financial/tests/fixtures/sale_status.json",
        APPS_DIR + "financial/tests/fixtures/profit_status.json",
        APPS_DIR + "financial/tests/fixtures/sale.json",
        APPS_DIR + "financial/tests/fixtures/sale_charge_and_cost.json",
        APPS_DIR + "financial/tests/fixtures/sale_item.json",
        APPS_DIR + "financial/tests/fixtures/generic_transaction.json",
        APPS_DIR + "financial/tests/fixtures/plat_import_setting.json",
    ]

    def setUp(self):
        super().setUp()
        if SaleItem.objects.tenant_db_for(self.client_id).count() == 0:
            self.db_table_client(new_table=True)

    def test_get_list_trans_event_sale_items(self):

        sale_item = SaleItem.objects.tenant_db_for(self.client_id).get(pk='439e87be-d8c5-4617-a991-369d657cc0bd')
        sale_item.shipping_cost_source = AMZ_POSTAGE_BILLING_SOURCE_KEY
        sale_item.save()

        sale = sale_item.sale

        url = reverse('client-list-transaction-event-sale-item',
                      kwargs={'client_id': self.client_id, 'sale_item_id': '439e87be-d8c5-4617-a991-369d657cc0bd'})
        headers = {
            'HTTP_AUTHORIZATION': 'Bearer {}'.format(self.jwt_token)
        }
        rs = self.client.get(path=url, format='json', **headers)
        self.assertEqual(rs.status_code, status.HTTP_200_OK)
        content = json.loads(rs.content.decode('utf-8'))
        print(content)
        self.assertEqual(content['count'], 10)
        self.assertEqual(len(content['results']), 10)

        # sale item transaction of channel listing fee
        url1 = url + '?column=channel_listing_fee'
        print(url1)
        rs = self.client.get(path=url1, format='json', **headers)
        self.assertEqual(rs.status_code, status.HTTP_200_OK)
        content = json.loads(rs.content.decode('utf-8'))
        print(content)
        self.assertEqual(content['count'], 2)
        self.assertEqual(len(content['results']), 2)

        # sale item transaction of other_channel_fees
        url2 = url + '?column=other_channel_fees'
        print(url2)
        rs = self.client.get(path=url2, format='json', **headers)
        self.assertEqual(rs.status_code, status.HTTP_200_OK)
        content = json.loads(rs.content.decode('utf-8'))
        print(content)
        self.assertEqual(content['count'], 1)
        self.assertEqual(len(content['results']), 1)

        for item in content['results']:
            count = sale.saleitem_set.tenant_db_for(sale.client_id).count()
            self.assertEqual(count, 3)
            if item['type'] == 'ReturnPostageBilling_Postage':
                self.assertEqual(item['item_amount'], -3.1)
                self.assertEqual(item['amount'], -9.29)
            if item['type'] == 'ReturnPostageBilling_FuelSurcharge':
                self.assertEqual(item['item_amount'], -0.22)
                self.assertEqual(item['amount'], -0.65)

        # sale item transaction of tax_charged
        url3 = url + '?column=tax_charged'
        print(url3)
        rs = self.client.get(path=url3, format='json', **headers)
        self.assertEqual(rs.status_code, status.HTTP_200_OK)
        content = json.loads(rs.content.decode('utf-8'))
        print(content)
        self.assertEqual(content['count'], 3)
        self.assertEqual(len(content['results']), 3)

        # shipping_cost with fulfillment_type = FBA
        url4 = url + '?column=shipping_cost'
        print(url4)
        rs = self.client.get(path=url4, format='json', **headers)
        self.assertEqual(rs.status_code, status.HTTP_200_OK)
        content = json.loads(rs.content.decode('utf-8'))
        print(content)
        self.assertEqual(content['count'], 1)
        self.assertEqual(len(content['results']), 1)

        # shipping_cost with fulfillment_type = MFN, sale is_prime = True
        fulfillment_type = FulfillmentChannel.objects.tenant_db_for(self.client_id).get(name='MFN')
        sale_item.fulfillment_type = fulfillment_type
        sale_item.save()

        sale.is_prime = True
        sale.save()

        url5 = url + '?column=shipping_cost'
        print(url5)
        rs = self.client.get(path=url5, format='json', **headers)
        self.assertEqual(rs.status_code, status.HTTP_200_OK)
        content = json.loads(rs.content.decode('utf-8'))
        print(content)
        self.assertEqual(content['count'], 1)
        self.assertEqual(len(content['results']), 1)
        for item in content['results']:
            if item['type'] == 'PostageBilling_Postage':
                _item_count = sale.saleitem_set.tenant_db_for(sale.client_id) \
                    .filter(fulfillment_type=fulfillment_type).count()
                self.assertEqual(_item_count, 1)
                self.assertEqual(item['item_amount'], -8.14)

        url6 = url + '?reimbursement_costs'
        print(url6)
        rs = self.client.get(path=url6, format='json', **headers)
        self.assertEqual(rs.status_code, status.HTTP_200_OK)
        content = json.loads(rs.content.decode('utf-8'))
        print(content)
        self.assertEqual(content['count'], 10)
        self.assertEqual(len(content['results']), 10)
