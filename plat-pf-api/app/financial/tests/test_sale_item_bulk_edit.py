import json
from datetime import datetime
from decimal import Decimal

from django.forms import model_to_dict
from django.urls import reverse
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_200_OK, HTTP_204_NO_CONTENT
from app.financial.jobs.data_flatten import flat_sale_items_bulks_sync_task
from app.financial.models import SaleItem, SaleStatus, ProfitStatus, Sale, Variant, Brand, \
    FulfillmentChannel
from app.financial.sub_serializers.sale_item_bulk_edit_serializer import ClientSaleItemBulkEditSerializer
from app.financial.tests.base import BaseAPITest
from app.financial.variable.bulk_edit_action_variable import APPEND, PREPEND, CHANGE_TO, ADD, SUBTRACT, MULTIPLY_BY, \
    DIVIDE_BY, PERCENT_INCREASE, PERCENT_DECREASE, UNDO_PERCENT_INCREASE, UNDO_PERCENT_DECREASE
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


def make_bulk_edit_operation(column: str, action: str, value):
    return dict(column=column, action=action, value=value)


def calculate_edited_value(original, action, value):
    return ClientSaleItemBulkEditSerializer.bulk_edit_calculate(original, action, value)


class SaleItemBulkEditAPITest(BaseAPITest):
    fixtures = BaseAPITest.fixtures + fixtures

    def setUp(self):
        super().setUp()

        if SaleItem.objects.tenant_db_for(self.client_id).count() == 0:
            self.db_table_client(new_table=True)

        # create table manage data sale items
        self.create_flatten_manage_sale_items()
        #
        self.sale_item_ids = [str(item.pk) for item in SaleItem.objects.tenant_db_for(self.client_id).all()]

        #
        self.first_record = self.sale_item_ids[0]

    def bulk_edit_sale_items(self, updates: list, status_code: int = HTTP_200_OK, error_validation: dict = {}):
        url = reverse('create-sale-items-bulk-edit', kwargs={'client_id': self.client_id})
        headers = {
            'HTTP_AUTHORIZATION': 'Bearer {}'.format(self.jwt_token),
            'format': 'json'
        }
        data = {
            'ids': self.sale_item_ids,
            'updates': updates
        }
        print("url request : {}".format(url))
        print("data update : {}".format(data))

        # Original sale items
        original_sale_items = SaleItem.objects.tenant_db_for(self.client_id).filter(id__in=self.sale_item_ids)
        original_sale_items = list(original_sale_items)
        # Original sales
        sale_ids = set(item.sale_id for item in original_sale_items)
        original_sales = Sale.objects.tenant_db_for(self.client_id).filter(id__in=sale_ids)
        original_sales = list(original_sales)

        rs = self.client.post(path=url, data=data, **headers)
        print(rs)
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
            # validate sale_item update
            self.validate_bulk_edit_sale_item(original_sale_items, updates)
            # validate sale update
            self.validate_bulk_edit_sale(original_sales, updates)
            # validate reset sale data
            self.validate_reset_sale_data()

    def validate_bulk_edit_sale_item(self, original_sale_items, updates):
        for original_sale_item in original_sale_items:
            sale_item = SaleItem.objects.tenant_db_for(self.client_id).get(pk=original_sale_item.pk)
            instance_data = model_to_dict(sale_item)
            for update in updates:
                field = update['column']
                if not hasattr(original_sale_item, field):
                    continue
                original_value = getattr(original_sale_item, field)
                action = update['action']
                value = update['value']
                expected_value = calculate_edited_value(original_value, action, value)
                print(f"Validate bulk-edit SaleItem<{original_sale_item.pk}>: '{field}' {action} '{value}'")
                if field == 'brand':
                    self.validate_brand(expect=expected_value, sale_item=sale_item)
                    continue
                if field == 'sale_status':
                    self.validate_sale_status(expect=expected_value, sale_item=sale_item)
                    continue
                if field == 'profit_status':
                    self.validate_profit_status(expect=expected_value, sale_item=sale_item)
                    continue
                if field == 'sale_date':
                    expected_value = datetime.strptime(expected_value, '%Y-%m-%dT%H:%M:%S.%fZ')
                if field == 'ship_date':
                    expected_value = datetime.strptime(expected_value, '%Y-%m-%dT%H:%M:%S.%fZ')
                if field == 'style_variant':
                    self.validate_style_variant(expect=expected_value, sale_item=sale_item)
                    continue
                if field == 'size_variant':
                    self.validate_size_variant(expect=expected_value, sale_item=sale_item)
                    continue
                if field in ['customer_name', 'recipient_name', 'state', 'city', 'country', 'postal_code']:
                    # this is field of sale level , it's validated in function validate_sale_update
                    continue
                if field == 'fulfillment_type':
                    self.validate_fulfillment_type(expected_value, sale_item)
                    continue
                if field == 'quantity' and not expected_value:
                    continue
                if field in ['channel_listing_fee', 'other_channel_fees']:
                    # field update by trans data event and live feed job
                    continue
                if instance_data['shipping_cost_accuracy'] == 100:
                    continue
                if isinstance(expected_value, Decimal):
                    expected_value = round(expected_value, 2)
                    self.assertEqual(expected_value, instance_data[field])
                    continue
                self.assertEqual(expected_value, instance_data[field])

    def validate_bulk_edit_sale(self, original_sales, updates):
        for original_sale in original_sales:
            sale = Sale.objects.tenant_db_for(self.client_id).get(pk=original_sale.pk)
            for update in updates:
                field = update['column']
                if not hasattr(original_sale, field):
                    continue
                original_value = getattr(original_sale, field)
                action = update['action']
                value = update['value']
                expect = calculate_edited_value(original_value, action, value)

                if field == 'customer_name':
                    self.assertEqual(expect, sale.customer_name)

                if field == 'recipient_name':
                    self.assertEqual(expect, sale.recipient_name)

                if field == 'state':
                    self.assertEqual(expect, sale.state)

                if field == 'city':
                    self.assertEqual(expect, sale.city)

                if field == 'country':
                    self.assertEqual(expect, sale.country)

                if field == 'postal_code':
                    self.assertEqual(expect, sale.postal_code)

    def validate_reset_sale_data(self):
        sale_ids = SaleItem.objects.tenant_db_for(self.client_id).filter(pk__in=self.sale_item_ids).values_list(
            'sale_id', flat=True).distinct('sale')
        sales = Sale.objects.tenant_db_for(self.client_id).filter(pk__in=sale_ids)
        for sale in sales:
            # sale status
            item_sale_status = sale.saleitem_set.tenant_db_for(self.client_id).all().order_by(
                'sale_status__order').first()
            self.assertEqual(sale.sale_status, item_sale_status.sale_status)
            # sale profit
            item_profit_status = sale.saleitem_set.tenant_db_for(self.client_id).all().order_by(
                'profit_status__order').first()
            self.assertEqual(sale.profit_status, item_profit_status.profit_status)
            # sale date
            item_sale_date = sale.saleitem_set.tenant_db_for(self.client_id).all().order_by('sale_date').first()
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

    def validate_fulfillment_type(self, expect: str = None, sale_item: SaleItem = None):
        obj = FulfillmentChannel.objects.tenant_db_for(self.client_id).get(name=expect)
        self.assertEqual(obj.pk, sale_item.fulfillment_type.pk)

    def validate_size_variant(self, expect: str = None, sale_item: SaleItem = None):
        obj = Variant.objects.tenant_db_for(self.client_id).get(value=expect, type=VARIANT_SIZE_TYPE)
        self.assertEqual(obj.pk, sale_item.size.pk)

    def validate_style_variant(self, expect: str = None, sale_item: SaleItem = None):
        obj = Variant.objects.tenant_db_for(self.client_id).get(value=expect, type=VARIANT_STYLE_TYPE)
        self.assertEqual(obj.pk, sale_item.style.pk)

    def validate_sale_status(self, expect: str = None, sale_item: SaleItem = None):
        obj = SaleStatus.objects.tenant_db_for(self.client_id).get(value=expect)
        self.assertEqual(obj.pk, sale_item.sale_status.pk)

    def validate_brand(self, expect: str = None, sale_item: SaleItem = None):
        if expect:
            expect = Brand.objects.tenant_db_for(self.client_id).get(name=expect, client_id=self.client_id)
        self.assertEqual(expect, sale_item.brand)

    def validate_profit_status(self, expect: str = None, sale_item: SaleItem = None):
        obj = ProfitStatus.objects.tenant_db_for(self.client_id).get(value=expect)
        self.assertEqual(obj.pk, sale_item.profit_status.pk)

    def test_calculation(self):
        test_cases = (
            # Text field actions
            ('test_string', CHANGE_TO, 'new_string', 'new_string'),
            ('test_string', APPEND, '_suffix', 'test_string_suffix'),
            ('test_string', PREPEND, 'prefix_', 'prefix_test_string'),
            # Numeric field actions
            (3012, CHANGE_TO, 2103, 2103),
            (3012, ADD, 88, 3100),
            (3100, SUBTRACT, 88, 3012),
            (3012, MULTIPLY_BY, 5, 15060),
            (15060, DIVIDE_BY, 5, 3012),
            (3012, PERCENT_INCREASE, 20, 3614.4),
            (3614.4, UNDO_PERCENT_INCREASE, 20, 3012),
            (3012, PERCENT_DECREASE, 20, 2409.6),
            (2409.6, UNDO_PERCENT_DECREASE, 20, 3012),
        )
        for (original_value, action, action_value, expected_value) in test_cases:
            result = calculate_edited_value(original_value, action, action_value)
            if isinstance(result, Decimal):
                result = float(result)
            self.assertEqual(result, expected_value)

    def test_bulk_edit_common_action(self):
        updates = [
            make_bulk_edit_operation('brand', CHANGE_TO, 'Nike'),
            make_bulk_edit_operation('customer_name', CHANGE_TO, 'Jack Sparrow'),
            make_bulk_edit_operation('recipient_name', CHANGE_TO, 'Jack Sparrow LJ'),
            make_bulk_edit_operation('tracking_fedex_id', CHANGE_TO, '1234512345678'),
            make_bulk_edit_operation('sale_status', CHANGE_TO, 'Completed'),
            make_bulk_edit_operation('profit_status', CHANGE_TO, 'Final'),
            make_bulk_edit_operation('fulfillment_type', CHANGE_TO, 'MFN'),
            make_bulk_edit_operation('ship_date', CHANGE_TO, '2020-12-30T12:30:12.301Z'),
            make_bulk_edit_operation('sale_date', CHANGE_TO, '2020-12-29T12:29:12.291Z'),
            make_bulk_edit_operation('product_number', CHANGE_TO, 'Navy123'),
            make_bulk_edit_operation('product_type', CHANGE_TO, 'Winter'),
            make_bulk_edit_operation('parent_asin', CHANGE_TO, '123-YYY-BBB'),
        ]
        self.bulk_edit_sale_items(updates=updates)

    def test_bulk_edit_text_fields(self):
        updates = [
            make_bulk_edit_operation('title', APPEND, '_suffix'),
            make_bulk_edit_operation('notes', PREPEND, 'prefix_'),
            make_bulk_edit_operation('sale_date', CHANGE_TO, '2020-12-29T12:29:12.291Z'),
        ]
        self.bulk_edit_sale_items(updates=updates)

    def test_bulk_edit_numeric_fields(self):
        updates = [
            make_bulk_edit_operation('sale_charged', ADD, 10),
            make_bulk_edit_operation('shipping_charged', SUBTRACT, 5.5),
            make_bulk_edit_operation('cog', MULTIPLY_BY, 2),
            make_bulk_edit_operation('actual_shipping_cost', DIVIDE_BY, 5),
            make_bulk_edit_operation('estimated_shipping_cost', DIVIDE_BY, 5),
            make_bulk_edit_operation('tax_cost', PERCENT_INCREASE, 50),
            make_bulk_edit_operation('tax_charged', PERCENT_DECREASE, 25),
            make_bulk_edit_operation('channel_listing_fee', UNDO_PERCENT_INCREASE, 10),
            make_bulk_edit_operation('other_channel_fees', UNDO_PERCENT_DECREASE, 15),
            make_bulk_edit_operation('channel_tax_withheld', CHANGE_TO, 3),
            make_bulk_edit_operation('channel_tax_withheld_accuracy', CHANGE_TO, 95),
            make_bulk_edit_operation('fulfillment_type_accuracy', CHANGE_TO, 90),
            make_bulk_edit_operation('sale_status', CHANGE_TO, 'Pending')
        ]
        self.bulk_edit_sale_items(updates=updates)
