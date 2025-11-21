import random
import string
from datetime import datetime
from decimal import Decimal
import json
from unittest.mock import patch
from django.db.models import Q
from django.forms import model_to_dict
from django.urls import reverse
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_200_OK, HTTP_204_NO_CONTENT, HTTP_403_FORBIDDEN

from app.core.variable.permission import ROLE_STAFF
from app.financial.jobs.data_flatten import flat_sale_items_bulks_sync_task
from app.financial.models import SaleItem, SaleStatus, ProfitStatus, Sale, Variant, Brand, \
    FulfillmentChannel
from app.financial.tests.base import BaseAPITest
from app.financial.variable.variant_type_static_variable import VARIANT_SIZE_TYPE, VARIANT_STYLE_TYPE
from config.settings.common import ROOT_DIR

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


def trigger_sync_sale_items(client_id):
    flat_sale_items_bulks_sync_task(client_id=client_id)


class SaleItemUpdateAPITest(BaseAPITest):
    fixtures = BaseAPITest.fixtures + fixtures

    def setUp(self):
        super().setUp()
        # create table manage data sale items
        self.create_flatten_manage_sale_items()
        #
        self.first_record = SaleItem.objects.tenant_db_for(self.client_id).order_by('created').first()
        #
        self.sale_item_ids = [str(self.first_record.pk)]

    def make_suffix_sale_item_ids(self):
        sale_item_first_id = self.sale_item_ids[0]
        suffix_item_ids = "?sale_item_ids[]={}".format(sale_item_first_id)
        for sale_item_id in self.sale_item_ids:
            if sale_item_id == sale_item_first_id:
                continue
            suffix_item_ids += "&sale_item_ids[]={}".format(sale_item_id)
        return suffix_item_ids

    def request_sale_item_action(self, data: dict = {}, type_action: int = 1):
        args = {
            1: reverse('update-delete-client-single-sale-items',
                       kwargs={
                           'client_id': self.client_id,
                           'pk': str(self.first_record.pk)
                       }),
            2: reverse('update-delete-client-single-sale-items',
                       kwargs={
                           'client_id': self.client_id,
                           'pk': str(self.first_record.pk)
                       }),
            3: reverse('update-client-bulk-sale-items',
                       kwargs={
                           'client_id': self.client_id
                       }) + self.make_suffix_sale_item_ids(),
            4: reverse('delete-client-bulk-sale-items',
                       kwargs={
                           'client_id': self.client_id
                       }) + self.make_suffix_sale_item_ids()
        }
        url = args.get(type_action, None)
        print("url request : {}".format(url))

        headers = {
            'HTTP_AUTHORIZATION': 'Bearer {}'.format(self.jwt_token),
            'format': 'json'
        }
        rs = None
        if type_action in [1]:
            rs = self.client.put(path=url, data=data, **headers)
        if type_action in [2, 4]:
            rs = self.client.delete(path=url, **headers)
        if type_action in [3]:
            rs = self.client.patch(path=url, data=data, **headers)
        print(rs)
        return rs

    def update_sale_item(self, data: dict = {}, status_code: int = HTTP_200_OK, error_validation: dict = {},
                         type_action: int = 1):
        print("data update : {}".format(data))
        rs = self.request_sale_item_action(data=data, type_action=type_action)
        self.assertEqual(rs.status_code, status_code)
        if rs.status_code == HTTP_400_BAD_REQUEST:
            content = json.loads(rs.content.decode('utf-8'))
            print(content)
            for field in content.keys():
                target = content[field]
                expect = error_validation[field]
                if isinstance(target, list):
                    for error in target:
                        self.assertIn(error, expect, msg="Error message not correct")
                else:
                    self.assertEqual(target, expect, msg="Error message not correct")
        if rs.status_code == HTTP_200_OK:
            self.validate_sale_item_update(data=data)
            # validate sale update
            self.validate_sale_update(data=data)
            # validate reset sale data
            self.validate_reset_sale_data()

    def validate_sale_update(self, data):
        sale_ids = SaleItem.objects.tenant_db_for(self.client_id).filter(pk__in=self.sale_item_ids).values_list(
            'sale_id', flat=True).distinct('sale')
        sales = Sale.objects.tenant_db_for(self.client_id).filter(pk__in=sale_ids)
        for sale in sales:
            state = data.get('state')

            if state:
                self.assertEqual(state, sale.state)

            city = data.get('city')
            if city:
                self.assertEqual(city, sale.city)

            country = data.get('country')
            if country:
                self.assertEqual(country, sale.country)

            postal_code = data.get('postal_code')
            if postal_code:
                self.assertEqual(postal_code, sale.postal_code)

            customer_name = data.get('customer_name')
            if customer_name:
                self.assertEqual(customer_name, sale.customer_name)
            recipient_name = data.get('recipient_name')
            if recipient_name:
                self.assertEqual(recipient_name, sale.recipient_name)

    def validate_reset_sale_data(self):
        sale_ids = SaleItem.objects.tenant_db_for(self.client_id).filter(pk__in=self.sale_item_ids).values_list(
            'sale_id', flat=True).distinct('sale')
        sales = Sale.objects.tenant_db_for(self.client_id).filter(pk__in=sale_ids)
        for sale in sales:
            # sale status
            item_sale_status = sale.saleitem_set.tenant_db_for(sale.client_id).all().order_by(
                'sale_status__order').first()
            self.assertEqual(sale.sale_status, item_sale_status.sale_status)
            # sale profit
            item_profit_status = sale.saleitem_set.tenant_db_for(sale.client_id).all().order_by(
                'profit_status__order').first()
            self.assertEqual(sale.profit_status, item_profit_status.profit_status)
            # sale date
            item_sale_date = sale.saleitem_set.tenant_db_for(sale.client_id).all().order_by('sale_date').first()
            self.assertEqual(sale.date, item_sale_date.sale_date)

    def delete_sale_item(self, status_code: int = HTTP_200_OK, type_action: int = 2):
        rs = self.request_sale_item_action(type_action=type_action)
        self.assertEqual(rs.status_code, status_code)
        if rs.status_code == HTTP_204_NO_CONTENT:
            self.validate_sale_item_delete(obj_id=str(self.first_record.pk))
            # self.validate_log_entry()

    def validate_sale_item_delete(self, obj_id: str = None):
        item = SaleItem.objects.tenant_db_for(self.client_id).filter(pk=obj_id).first()
        self.assertEqual(item, None)

    def validate_sale_item_update(self, data: dict = {}):
        for sale_item_id in self.sale_item_ids:
            sale_item = SaleItem.objects.tenant_db_for(self.client_id).get(pk=sale_item_id)
            instance_data = model_to_dict(sale_item)
            for field in data.keys():
                value = data[field]
                print("validate field : {} value : {}".format(field, value))
                if field == 'brand':
                    self.validate_brand(value=value, sale_item=sale_item)
                    continue
                if field == 'sale_status':
                    self.validate_sale_status(value=value, sale_item=sale_item)
                    continue
                if field == 'profit_status':
                    self.validate_profit_status(value=value, sale_item=sale_item)
                    continue
                if field == 'sale_date':
                    value = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%fZ')
                if field == 'ship_date':
                    value = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%fZ')
                if field == 'style_variant':
                    self.validate_style_variant(value=value, sale_item=sale_item)
                    continue
                if field == 'size_variant':
                    self.validate_size_variant(value=value, sale_item=sale_item)
                    continue
                if field in ['customer_name', 'recipient_name', 'state', 'city', 'country', 'postal_code']:
                    # this is field of sale level , it's validated in function validate_sale_update
                    continue
                if field == 'fulfillment_type':
                    self.validate_fulfillment_type(value, sale_item)
                    continue
                if field == 'quantity' and not value:
                    continue

                if field in ['channel_listing_fee', 'other_channel_fees']:
                    # field update by trans data event and live feed job
                    continue
                if instance_data['shipping_cost_accuracy'] == 100:
                    continue
                self.assertEqual(value, instance_data[field])

    def validate_fulfillment_type(self, value: str = None, sale_item: SaleItem = None):
        obj = FulfillmentChannel.objects.tenant_db_for(self.client_id).get(name=value)
        self.assertEqual(obj.pk, sale_item.fulfillment_type.pk)

    def validate_size_variant(self, value: str = None, sale_item: SaleItem = None):
        obj = Variant.objects.tenant_db_for(self.client_id).get(value=value, type=VARIANT_SIZE_TYPE)
        self.assertEqual(obj.pk, sale_item.size.pk)

    def validate_style_variant(self, value: str = None, sale_item: SaleItem = None):
        obj = Variant.objects.tenant_db_for(self.client_id).get(value=value, type=VARIANT_STYLE_TYPE)
        self.assertEqual(obj.pk, sale_item.style.pk)

    def validate_sale_status(self, value: str = None, sale_item: SaleItem = None):
        obj = SaleStatus.objects.tenant_db_for(self.client_id).get(value=value)
        self.assertEqual(obj.pk, sale_item.sale_status.pk)

    def validate_brand(self, value: str = None, sale_item: SaleItem = None):
        if value:
            value = Brand.objects.tenant_db_for(self.client_id).get(name=value, client_id=self.client_id)
        self.assertEqual(value, sale_item.brand)

    def validate_profit_status(self, value: str = None, sale_item: SaleItem = None):
        obj = ProfitStatus.objects.tenant_db_for(self.client_id).get(value=value)
        self.assertEqual(obj.pk, sale_item.profit_status.pk)

    def test_update_sale_item1(self):
        # single
        data = {
            "profit_status": "Projected",
            "sale_status": "Pending",
            "asin": "string",
            "sale_charged": 0
        }
        errors_validation = {
            'asin': [
                'ASIN is invalid'
            ],
            'sale_charged': [
                'Sale Charged does not accept negative number'
            ],
            'sale_date': [
                'This field is required.'
            ]
        }
        self.update_sale_item(data=data, status_code=HTTP_400_BAD_REQUEST, error_validation=errors_validation)
        # bulk update
        second = SaleItem.objects.tenant_db_for(self.client_id).filter(~Q(pk__in=self.sale_item_ids)).first()
        self.sale_item_ids.append(str(second.pk))
        self.update_sale_item(data=data, status_code=HTTP_400_BAD_REQUEST, error_validation=errors_validation,
                              type_action=3)

    def test_update_sale_item2(self):
        data = {
            "profit_status": "fdsfsfsfsfsf",
            "sale_status": "dsfdsfsfsfdsf",
            "quantity": 101
        }
        errors_validation = {
            'profit_status': [
                '"fdsfsfsfsfsf" is not a valid choice.'
            ],
            'sale_status': [
                '"dsfdsfsfsfdsf" is not a valid choice.'
            ],
            'sale_date': [
                'This field is required.'
            ],
            'quantity': [
                'Quantity value is less than or equal to 100'
            ]
        }
        self.update_sale_item(data=data, status_code=HTTP_400_BAD_REQUEST, error_validation=errors_validation)
        # bulk update
        second = SaleItem.objects.tenant_db_for(self.client_id).filter(~Q(pk__in=self.sale_item_ids)).first()
        self.sale_item_ids.append(str(second.pk))
        self.update_sale_item(data=data, status_code=HTTP_400_BAD_REQUEST, error_validation=errors_validation,
                              type_action=3)

    def test_update_sale_item3(self):
        data = {
            "sale_charged": -1,
            "state": self.generate_string_length(length=50),
            "shipping_charged": -2,
            "tax_charged": -3,
            "cog": 'yewtryw',
            "actual_shipping_cost": -4,
            "estimated_shipping_cost": -4,
            "tax_cost": 0,
            "notes": "string",
            "channel_listing_fee": -7,
            "other_channel_fees": 0,
            "title": self.generate_string_length(length=300),
            "style_variant": self.generate_string_length(length=300),
            "size_variant": self.generate_string_length(length=300),
            "sale_date": "2020-01-01T04:03:32.370Z",
            "brand": "XXXXXXXXXXXXXXXX",
            "fulfillment_type": "ASDFG",
            "quantity": -4,
        }
        errors_validation = {
            'sale_charged': [
                'Sale Charged does not accept negative number'
            ],
            'shipping_charged': [
                'Shipping Charged does not accept negative number'
            ],
            'cog': [
                'A valid number is required.'
            ],
            'tax_charged': [
                'Tax Charged does not accept negative number'
            ],
            'actual_shipping_cost': [
                'Actual Shipping Cost does not accept negative number'
            ],
            'estimated_shipping_cost': [
                'Estimated Shipping Cost does not accept negative number'
            ],
            'channel_listing_fee': [
                'Channel Listing Fee does not accept negative number'
            ],
            'title': [
                'Title length is 255 maximum'
            ],
            'brand': [
                '"XXXXXXXXXXXXXXXX" brand does not exist'
            ],
            'state': [
                'State length is 45 maximum'
            ],
            'fulfillment_type': [
                'Fulfillment Type is invalid'
            ],
            'quantity': [
                'Quantity does not accept negative number'
            ],
            'size_variant': [
                'Size length is 200 maximum'
            ],
            'style_variant': [
                'Style length is 200 maximum'
            ],
        }
        self.update_sale_item(data=data, status_code=HTTP_400_BAD_REQUEST, error_validation=errors_validation)
        # bulk update
        second = SaleItem.objects.tenant_db_for(self.client_id).filter(~Q(pk__in=self.sale_item_ids)).first()
        self.sale_item_ids.append(str(second.pk))
        self.update_sale_item(data=data, status_code=HTTP_400_BAD_REQUEST, error_validation=errors_validation,
                              type_action=3)

    @patch('app.financial.jobs.data_flatten.flat_sale_items_bulks_sync_task.delay')
    def test_update_sale_item4(self, flatten_sale_items_update):
        print("sale status current : {}".format(self.first_record.sale_status.value))
        print("sale profit_status current : {}".format(self.first_record.profit_status.value))
        data = {
            "profit_status": "Final",
            "sale_status": "Other",
            "sale_date": "2020-01-01T04:03:32.370Z",
            "brand": None,
            "cog": 0,
            "quantity": None  # default set 1 in serializer
        }
        self.update_sale_item(data=data, status_code=HTTP_200_OK)
        self.verify_log_entry(1, 1)
        # trigger run celery job
        flatten_sale_items_update.return_value = trigger_sync_sale_items(self.client_id)

        # self.validate_log_entry()
        rs = self.get_result_flatten_data()
        self.assertEqual(len(rs), 1)
        self.compare_sale_item_update_ds(rs)

        # bulk update
        second = SaleItem.objects.tenant_db_for(self.client_id).filter(~Q(pk__in=self.sale_item_ids)).first()
        self.sale_item_ids.append(str(second.pk))
        self.update_sale_item(data=data, status_code=HTTP_200_OK, type_action=3)
        #
        flatten_sale_items_update.return_value = trigger_sync_sale_items(self.client_id)
        # self.validate_log_entry()
        rs = self.get_result_flatten_data()
        self.assertEqual(len(rs), 2)
        self.compare_sale_item_update_ds(rs)
        self.verify_log_entry(2, 1)

    def generate_string_length(self, characters=string.ascii_uppercase + string.digits, length=10):
        return ''.join(random.choice(characters) for _ in range(length))

    @patch('app.financial.jobs.data_flatten.flat_sale_items_bulks_sync_task.delay')
    def test_update_sale_item5(self, flatten_sale_items_update):
        data = {
            "brand": "The NorthFace",
            "customer_name": "Jack Sparrow",
            "recipient_name": "Jack Sparrow LJ",
            "state": self.generate_string_length(length=45),
            "sale_date": "2020-01-01T21:27:10.253Z",
            "profit_status": "Projected",
            "sale_status": "Pending",
            "size_variant": "50",
            "style_variant": "Young",
            "notes": "string",
            "upc": "1234567890123",
            "brand_sku": "23456782345678",
            "asin": "1234567890",
            "title": "Title for Test",
            "sale_charged": 600,
            "shipping_charged": 200,
            "channel_tax_withheld": 2,
            "cog": 200,
            "actual_shipping_cost": 200,
            "estimated_shipping_cost": 190,
            "tax_cost": 200,
            "tax_charged": 200,
            "ship_date": "2020-08-19T21:27:10.253Z",
            "channel_listing_fee": 200,
            "other_channel_fees": 200,
            "fulfillment_type": "MFN",
            "quantity": 5,
            "city": "North County",
            "country": "United States",
            "postal_code": "22222-3333",
            "tracking_fedex_id": "123456789012345",
            "product_number": "Navy123",
            "product_type": "Winter",
            "parent_asin": "123-YYY-BBB",
            "return_postage_billing": 105
        }
        self.update_sale_item(data=data, status_code=HTTP_200_OK)
        #
        flatten_sale_items_update.return_value = trigger_sync_sale_items(self.client_id)
        #
        rs = self.get_result_flatten_data()
        self.assertEqual(len(rs), 1)
        self.compare_sale_item_update_ds(rs)
        self.verify_log_entry(1, 1)

        # validate single edit unit cog calculate
        self.first_record.refresh_from_db()
        self.assertEqual(self.first_record.unit_cog, Decimal('40'))

        # bulk update
        second = SaleItem.objects.tenant_db_for(self.client_id).filter(~Q(pk__in=self.sale_item_ids)).first()
        self.sale_item_ids.append(str(second.pk))
        self.update_sale_item(data=data, status_code=HTTP_200_OK, type_action=3)
        #
        flatten_sale_items_update.return_value = trigger_sync_sale_items(self.client_id)
        rs = self.get_result_flatten_data()
        self.assertEqual(len(rs), 2)
        self.compare_sale_item_update_ds(rs)
        self.verify_log_entry(2, 1)

    def test_update_sale_item6(self):
        self.role_update = {
            'key': ROLE_STAFF,
            'name': ROLE_STAFF.lower().title()
        }
        self.permissions_update = {
            'SALE_SINGLE_EDIT': False
        }
        self.restart_patcher()
        error_validation = {
            'code': 1026,
            'message': 'You can not permission edit record',
            'summary': 'Analysis data permissions'
        }
        print("sale status current : {}".format(self.first_record.sale_status.value))
        print("sale profit_status current : {}".format(self.first_record.profit_status.value))
        data = {
            "profit_status": "Final",
            "sale_status": "Other",
            "sale_date": "2020-01-01T04:03:32.370Z"
        }
        self.update_sale_item(data=data, status_code=HTTP_403_FORBIDDEN, error_validation=error_validation)

    def test_update_sale_item7(self):
        self.role_update = {
            'key': ROLE_STAFF,
            'name': ROLE_STAFF.lower().title()
        }
        self.permissions_update = {
            'SALE_BULK_EDIT': False
        }
        self.restart_patcher()
        # bulk update
        second = SaleItem.objects.tenant_db_for(self.client_id).filter(~Q(pk__in=self.sale_item_ids)).first()
        self.sale_item_ids.append(str(second.pk))
        #
        error_validation = {
            'code': 1026,
            'message': 'You can not permission edit record',
            'summary': 'Analysis data permissions'
        }
        print("sale status current : {}".format(self.first_record.sale_status.value))
        print("sale profit_status current : {}".format(self.first_record.profit_status.value))
        data = {
            "profit_status": "Final",
            "sale_status": "Other",
            "sale_date": "2020-01-01T04:03:32.370Z"
        }
        self.update_sale_item(data=data, status_code=HTTP_403_FORBIDDEN, type_action=3,
                              error_validation=error_validation)

    @patch('app.financial.jobs.data_flatten.flat_sale_items_bulks_sync_task.delay')
    def test_update_sale_item8(self, flatten_sale_items_update):
        sale_item = SaleItem.objects.tenant_db_for(self.client_id).filter(sale_date__isnull=True).first()
        sale = sale_item.sale
        sale.date = None
        sale.save()
        self.first_record = sale_item
        self.sale_item_ids = [str(self.first_record.pk)]
        data = {
            "sale_date": "2020-01-01T21:27:10.253Z",
            "brand": None,
            "upc": "1234567890123"
        }
        self.update_sale_item(data=data, status_code=HTTP_200_OK)
        #
        flatten_sale_items_update.return_value = trigger_sync_sale_items(self.client_id)
        #
        rs = self.get_result_flatten_data()
        self.assertEqual(len(rs), 1)
        self.compare_sale_item_update_ds(rs)
        self.verify_log_entry(1, 1)

    def test_delete_sale_item1(self):
        self.permissions_update = {
            'SALE_SINGLE_DELETE': False
        }
        self.restart_patcher()
        self.delete_sale_item(status_code=HTTP_403_FORBIDDEN)

    def test_delete_sale_item2(self):
        self.permissions_update = {
            'SALE_BULK_DELETE': False
        }
        self.restart_patcher()
        # bulk update
        second = SaleItem.objects.tenant_db_for(self.client_id).filter(~Q(pk__in=self.sale_item_ids)).first()
        self.sale_item_ids.append(str(second.pk))
        self.delete_sale_item(status_code=HTTP_403_FORBIDDEN, type_action=4)

    def test_delete_sale_item3(self):
        with patch(
                'app.financial.jobs.data_flatten.flat_sale_items_bulks_sync_task.delay') as flatten_sale_items_update:
            print("sale status current : {}".format(self.first_record.sale_status.value))
            print("sale profit_status current : {}".format(self.first_record.profit_status.value))
            data = {
                "profit_status": "Final",
                "sale_status": "Other",
                "sale_date": "2020-01-01T04:03:32.370Z"
            }
            self.update_sale_item(data=data, status_code=HTTP_200_OK)
            #
            flatten_sale_items_update.return_value = trigger_sync_sale_items(self.client_id)
            rs = self.get_result_flatten_data()
            self.assertEqual(len(rs), 1)
            self.compare_sale_item_update_ds(rs)
            self.verify_log_entry(1, 1)
        with patch(
                'app.financial.jobs.data_flatten.flat_sale_items_bulks_sync_task.delay') as flatten_sale_items_update:
            self.delete_sale_item(status_code=HTTP_204_NO_CONTENT)
            flatten_sale_items_update.return_value = trigger_sync_sale_items(self.client_id)
            rs = self.get_result_flatten_data()
            self.assertEqual(len(rs), 0)

    def test_delete_sale_item4(self):
        second = SaleItem.objects.tenant_db_for(self.client_id).filter(~Q(pk__in=self.sale_item_ids)).first()
        self.sale_item_ids.append(str(second.pk))
        with patch(
                'app.financial.jobs.data_flatten.flat_sale_items_bulks_sync_task.delay') as flatten_sale_items_update:
            print("sale status current : {}".format(self.first_record.sale_status.value))
            print("sale profit_status current : {}".format(self.first_record.profit_status.value))
            data = {
                "profit_status": "Final",
                "sale_status": "Other",
                "sale_date": "2020-01-11T04:03:32.370Z"
            }
            self.update_sale_item(data=data, status_code=HTTP_200_OK, type_action=3)
            #
            flatten_sale_items_update.return_value = trigger_sync_sale_items(self.client_id)
            rs = self.get_result_flatten_data()
            self.assertEqual(len(rs), 2)
            self.compare_sale_item_update_ds(rs)
            self.verify_log_entry(2, 1)
        with patch(
                'app.financial.jobs.data_flatten.flat_sale_items_bulks_sync_task.delay') as flatten_sale_items_update:
            # bulk delete
            self.delete_sale_item(status_code=HTTP_204_NO_CONTENT, type_action=4)
            count = SaleItem.objects.tenant_db_for(self.client_id).filter(pk__in=self.sale_item_ids).count()
            self.assertEqual(count, 0)
            flatten_sale_items_update.return_value = trigger_sync_sale_items(self.client_id)
            rs = self.get_result_flatten_data()
            self.assertEqual(len(rs), 0)

    def test_update_field_accurate(self):
        # CASE 1 - shipping_cost_accuracy = 0 => accept change value
        self.first_record.shipping_cost_accuracy = 0
        self.first_record.sale_charged_accuracy = 0
        self.first_record.save()
        data = {
            "sale_date": "2020-01-01T21:27:10.253Z",
            "actual_shipping_cost": 100,
            "estimated_shipping_cost": 80,
            "sale_charged": 100,
        }
        self.update_sale_item(data=data, status_code=HTTP_200_OK)
        # shipping_cost_accuracy = 0 and accept update shipping_cost
        self.first_record.refresh_from_db()
        self.assertEqual(self.first_record.actual_shipping_cost, 100)
        self.assertEqual(self.first_record.actual_shipping_cost, self.first_record.shipping_cost)
        self.assertEqual(self.first_record.estimated_shipping_cost, 80)

        # CASE 2 - shipping_cost_accuracy = 100 => denied change value
        self.first_record.shipping_cost_accuracy = 100
        self.first_record.sale_charged_accuracy = 100
        self.first_record.save()
        data = {
            "sale_date": "2020-01-01T21:27:10.253Z",
            "actual_shipping_cost": 500,
            "estimated_shipping_cost": 90,
            "sale_charged": 500,
        }
        self.update_sale_item(data=data, status_code=HTTP_200_OK)
        #
        self.first_record.refresh_from_db()
        # shipping_cost_accuracy = 0 and not update shipping_cost
        self.assertEqual(self.first_record.actual_shipping_cost, 500)
        self.assertEqual(self.first_record.estimated_shipping_cost, 90)
        self.assertEqual(self.first_record.sale_charged, 100)

        # CASE 3 - accept change value [estimated_shipping_cost, sale_charged_accuracy, channel_listing_fee_accuracy]
        # to null
        data = {
            "sale_date": "2020-01-01T21:27:10.253Z",
            "sale_charged_accuracy": None,
            "estimated_shipping_cost": 90,
            "shipping_cost_accuracy": 0,
            "channel_listing_fee_accuracy": None
        }
        self.update_sale_item(data=data, status_code=HTTP_200_OK)
        #
        self.first_record.refresh_from_db()
        # shipping_cost_accuracy = 0 and not update shipping_cost
        self.assertEqual(self.first_record.sale_charged_accuracy, None)
        self.assertEqual(self.first_record.shipping_cost_accuracy, 100)
        self.assertEqual(self.first_record.actual_shipping_cost, 500)
        self.assertEqual(self.first_record.estimated_shipping_cost, 90)
        self.assertEqual(self.first_record.channel_listing_fee_accuracy, None)

        # CASE 4 - accept change value [shipping_cost_accuracy]
        # to null
        data = {
            "sale_date": "2020-01-01T21:27:10.253Z",
            "actual_shipping_cost": 100,
            "estimated_shipping_cost": 90,
            "shipping_cost_accuracy": 100,
        }
        self.update_sale_item(data=data, status_code=HTTP_200_OK)
        #
        self.first_record.refresh_from_db()
        # shipping_cost_accuracy = 0 and not update shipping_cost
        self.assertEqual(self.first_record.actual_shipping_cost, 100)
        self.assertEqual(self.first_record.shipping_cost_accuracy, 100)
        self.assertEqual(self.first_record.estimated_shipping_cost, 90)
