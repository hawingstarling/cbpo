import io
import json
from datetime import datetime
from decimal import Decimal
from unittest.mock import patch

from django.http import HttpResponse
from rest_framework import status

from app.financial.models import Sale, SaleItem
from app.financial.services.sale_item_mapping.builder import MappingSaleItemBuilder
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
    APPS_DIR + "financial/tests/fixtures/sale.json",
    APPS_DIR + "financial/tests/fixtures/sale_charge_and_cost.json",
    APPS_DIR + "financial/tests/fixtures/brand_setting.json",
    APPS_DIR + "job/tests/fixtures/job_config.json",
]


class MappingSaleItemFromDcTest(BaseAPITest):
    """
    map sale items from DC. Options:
    - all
    - 12h recent only
    """
    fixtures = fixtures

    @classmethod
    def fake_dc_response(cls):
        content = {
            "items": [
                {
                    "brand": "Adidas",
                    "aws_brand": "Adidas",
                    "domain": "amazon.com",
                    "upc": "1kmj56789",
                    "sku": "DRN-1480_BLACK_ZZ",
                    "cost": 10
                },
                {
                    "brand": "NorthFace",
                    "aws_brand": "North Face",
                    "domain": "amazon.com",
                    "upc": "1kmj56000",
                    "sku": "DRN-1466_DENIM_ZZ",
                    "cost": 12
                }
            ]
        }
        content = io.BytesIO(json.dumps(content).encode("utf-8"))
        return HttpResponse(content=content, status=status.HTTP_200_OK)

    def start_patcher(self):
        super().start_patcher()
        self.patcher_dc_response = patch('app.core.services.dc_service.DCManager.get_upc',
                                         return_value=self.fake_dc_response()).start()

    def stop_patcher(self):
        super().stop_patcher()
        self.patcher_dc_response.stop()

    def test_mapping_from_dc(self):
        # Prerequisite
        sale_date_time = datetime(2015, 12, 12)

        self.truncate_data()

        sale = Sale.objects.tenant_db_for(self.client_id).create(channel_sale_id="111-222-3234",
                                                                 profit_status_id='9d41389c-ea0b-42a3-99bc-73be4f11ada8',
                                                                 sale_status_id='a4d57188-aa29-4f16-9288-5365ebe2e4a7',
                                                                 client_id=self.client_id,
                                                                 channel_id="4c3c7cdc-4297-4ff5-aa35-aa388c1f4e14",
                                                                 date=sale_date_time)
        sale_item_1 = SaleItem.objects.tenant_db_for(self.client_id).create(sale=sale,
                                                                            fulfillment_type_id="5b7bc589-14ce-41cb-8911-2925f504bb8d",
                                                                            client_id=self.client_id,
                                                                            sku='DRN-1480_BLACK_ZZ',
                                                                            sale_date=sale_date_time,
                                                                            quantity=5, shipping_cost_accuracy=0,
                                                                            dirty=True)
        sale_item_2 = SaleItem.objects.tenant_db_for(self.client_id).create(sale=sale,
                                                                            brand_id="02edd561-1084-4f55-bd5c-9222d008df4e",
                                                                            # adidas
                                                                            # MFN
                                                                            fulfillment_type_id="a8502437-d298-449a-bd7d-e60034d49daf",
                                                                            client_id=self.client_id,
                                                                            sku='DRN-1466_DENIM_ZZ',
                                                                            sale_date=sale_date_time,
                                                                            quantity=3, shipping_cost_accuracy=0,
                                                                            dirty=True)
        sale_item_3 = SaleItem.objects.tenant_db_for(self.client_id).create(sale=sale,
                                                                            brand_id="40e9d228-9785-4cf0-a6c2-d90fe813b32e",
                                                                            # NIke
                                                                            # MFN
                                                                            fulfillment_type_id="a8502437-d298-449a-bd7d-e60034d49daf",
                                                                            client_id=self.client_id,
                                                                            sku='DRN-1466_UUUIM_ZZ',
                                                                            sale_date=sale_date_time,
                                                                            quantity=4, shipping_cost_accuracy=0,
                                                                            dirty=True)
        sale_item_4 = SaleItem.objects.tenant_db_for(self.client_id).create(sale=sale,
                                                                            brand_id="818ad366-f624-4b2c-b0d3-64cc942d17ce",
                                                                            # North Face
                                                                            # MFN
                                                                            fulfillment_type_id="a8502437-d298-449a-bd7d-e60034d49daf",
                                                                            client_id=self.client_id,
                                                                            sku='DRN-0466_UUUIM_ZZ',
                                                                            sale_date=sale_date_time,
                                                                            quantity=4, shipping_cost_accuracy=0,
                                                                            dirty=True)
        self.create_flatten_manage_sale_items()

        builder_mapping_sale_item = MappingSaleItemBuilder.instance()
        builder_mapping_sale_item \
            .tenant_db_for_only(self.client_id) \
            .with_override_mode(False) \
            .with_chunk_size_query_set_sale_item(1000)
        builder_mapping_sale_item.with_common_mapping_fields(['upc', 'unit_cog', 'cog', 'brand', 'channel_brand'])
        handler_dc = builder_mapping_sale_item.build_mapping_from_live_feed_dc()
        handler_dc.exec()

        sale_item_1 = SaleItem.objects.tenant_db_for(self.client_id).get(id=sale_item_1.id)
        print(sale_item_1.brand.name)
        self.assertEqual(str(sale_item_1.brand_id), '02edd561-1084-4f55-bd5c-9222d008df4e',
                         'brand mapping error')
        self.assertEqual(sale_item_1.channel_brand, 'Adidas',
                         'channel brand mapping error')
        self.assertEqual(sale_item_1.segment, 'Outdoor',
                         'segment mapping error')
        self.assertEqual(sale_item_1.inbound_freight_cost, Decimal('15'),
                         'est unit inbound freight cost mapping error')
        self.assertEqual(sale_item_1.outbound_freight_cost, Decimal('-5'),
                         'est unit outbound freight cost mapping error')
        self.assertEqual(sale_item_1.user_provided_cost, Decimal('15'),
                         'add user provided cost mapping error')
        self.assertEqual(sale_item_1.upc, '1kmj56789',
                         'upc mapping error')
        self.assertEqual(sale_item_1.quantity, 5, 'quantity error')
        self.assertEqual(sale_item_1.unit_cog, Decimal(format(10.00, '.2f')),
                         'cog mapping error')
        self.assertEqual(sale_item_1.cog, Decimal(format(50.00, '.2f')),
                         'cog mapping error')

    def test_mapping_from_dc_12h_recent(self):
        # Prerequisite
        sale_date_time = datetime(2015, 12, 12)

        self.truncate_data()

        sale = Sale.objects.tenant_db_for(self.client_id).create(channel_sale_id="111-222-3234",
                                                                 profit_status_id='9d41389c-ea0b-42a3-99bc-73be4f11ada8',
                                                                 sale_status_id='a4d57188-aa29-4f16-9288-5365ebe2e4a7',
                                                                 client_id=self.client_id,
                                                                 channel_id="4c3c7cdc-4297-4ff5-aa35-aa388c1f4e14",
                                                                 date=sale_date_time)
        sale_item_1 = SaleItem.objects.tenant_db_for(self.client_id).create(sale=sale,
                                                                            brand_id="02edd561-1084-4f55-bd5c-9222d008df4e",
                                                                            # adidas
                                                                            # FBA
                                                                            fulfillment_type_id="5b7bc589-14ce-41cb-8911-2925f504bb8d",
                                                                            client_id=self.client_id,
                                                                            sku='DRN-1480_BLACK_ZZ',
                                                                            sale_date=sale_date_time,
                                                                            quantity=5, shipping_cost_accuracy=0,
                                                                            dirty=True)
        sale_item_2 = SaleItem.objects.tenant_db_for(self.client_id).create(sale=sale,
                                                                            fulfillment_type_id="a8502437-d298-449a-bd7d-e60034d49daf",
                                                                            client_id=self.client_id,
                                                                            sku='DRN-1466_DENIM_ZZ',
                                                                            sale_date=sale_date_time,
                                                                            quantity=3, shipping_cost_accuracy=0,
                                                                            dirty=True)
        sale_item_3 = SaleItem.objects.tenant_db_for(self.client_id).create(sale=sale,
                                                                            brand_id="40e9d228-9785-4cf0-a6c2-d90fe813b32e",
                                                                            # NIke
                                                                            # MFN
                                                                            fulfillment_type_id="a8502437-d298-449a-bd7d-e60034d49daf",
                                                                            client_id=self.client_id,
                                                                            sku='DRN-1466_UUUIM_ZZ',
                                                                            sale_date=sale_date_time,
                                                                            quantity=4, shipping_cost_accuracy=0,
                                                                            dirty=True)
        sale_item_4 = SaleItem.objects.tenant_db_for(self.client_id).create(sale=sale,
                                                                            brand_id="818ad366-f624-4b2c-b0d3-64cc942d17ce",
                                                                            # North Face
                                                                            # MFN
                                                                            fulfillment_type_id="a8502437-d298-449a-bd7d-e60034d49daf",
                                                                            client_id=self.client_id,
                                                                            sku='DRN-0466_UUUIM_ZZ',
                                                                            sale_date=sale_date_time,
                                                                            quantity=4, shipping_cost_accuracy=0,
                                                                            dirty=True)
        self.create_flatten_manage_sale_items()

        builder_mapping_sale_item = MappingSaleItemBuilder.instance()
        builder_mapping_sale_item \
            .tenant_db_for_only(self.client_id) \
            .with_override_mode(False) \
            .with_chunk_size_query_set_sale_item(1000)
        builder_mapping_sale_item.with_common_mapping_fields(['upc', 'unit_cog', 'cog', 'brand', 'channel_brand'])
        handler_dc = builder_mapping_sale_item.build_mapping_from_live_feed_12h_recent_dc()
        handler_dc.exec()

        sale_item_2 = SaleItem.objects.tenant_db_for(self.client_id).get(id=sale_item_2.id)
        self.assertEqual(str(sale_item_2.brand_id), '818ad366-f624-4b2c-b0d3-64cc942d17ce',
                         'brand mapping error')
        self.assertEqual(sale_item_2.channel_brand, 'North Face',
                         'channel brand mapping error')
        self.assertEqual(sale_item_2.upc, '1kmj56000',
                         'upc mapping error')
        self.assertEqual(sale_item_2.quantity, 3, 'quantity error')
        self.assertEqual(sale_item_2.unit_cog, Decimal(format(12.00, '.2f')),
                         'cog mapping error')

        self.assertEqual(sale_item_2.cog, Decimal(format(36.00, '.2f')),
                         'cog mapping error')
