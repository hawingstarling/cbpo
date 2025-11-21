from datetime import datetime
from decimal import Decimal

from app.financial.models import Sale, SaleItem, Item
from app.financial.services.sale_item_mapping.builder import MappingSaleItemBuilder
from app.financial.tests.base import BaseAPITest
from app.financial.variable.sale_item import COG_TYPE_CALCULATED_KEY
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
    APPS_DIR + "financial/tests/fixtures/variant.json",
    APPS_DIR + "financial/tests/fixtures/item.json",
    APPS_DIR + "financial/tests/fixtures/itemcog.json",
    APPS_DIR + "job/tests/fixtures/job_config.json",
]


class MappingSaleItemCogTest(BaseAPITest):
    """
    test mapping sale item COG module
    """
    fixtures = fixtures

    def test_mapping_sale_item_cog(self):
        """
        mapping sale item COG
        input is sale item ids

        override option: True
        calculate for all values from Sale Item COG
        """
        # Prerequisite
        sale_date_time = datetime(2015, 12, 12)

        self.truncate_data()

        sale = Sale.objects.tenant_db_for(self.client_id).create(
            channel_sale_id="111-222-3234",
            profit_status_id='9d41389c-ea0b-42a3-99bc-73be4f11ada8',
            sale_status_id='a4d57188-aa29-4f16-9288-5365ebe2e4a7',
            client_id=self.client_id,
            channel_id="4c3c7cdc-4297-4ff5-aa35-aa388c1f4e14",
            date=sale_date_time)
        sale_item_1 = SaleItem.objects.tenant_db_for(self.client_id).create(
            sale=sale,
            brand_id="02edd561-1084-4f55-bd5c-9222d008df4e",
            # adidas
            # FBA
            fulfillment_type_id="5b7bc589-14ce-41cb-8911-2925f504bb8d",
            client_id=self.client_id,
            sku='VQ_54-21135_0-B',
            cog=Decimal('12.34'),
            sale_date=sale_date_time,
            quantity=5, shipping_cost_accuracy=0,
            dirty=True)
        sale_item_2 = SaleItem.objects.tenant_db_for(self.client_id).create(
            sale=sale,
            brand_id="02edd561-1084-4f55-bd5c-9222d008df4e",
            # adidas
            # MFN
            fulfillment_type_id="a8502437-d298-449a-bd7d-e60034d49daf",
            client_id=self.client_id,
            sku='DRN-1466_DENIM_ZZ',
            sale_date=sale_date_time,
            quantity=3, shipping_cost_accuracy=0,
            dirty=True)
        sale_item_3 = SaleItem.objects.tenant_db_for(self.client_id).create(
            sale=sale,
            brand_id="40e9d228-9785-4cf0-a6c2-d90fe813b32e",
            # NIke
            # MFN
            fulfillment_type_id="a8502437-d298-449a-bd7d-e60034d49daf",
            client_id=self.client_id,
            sku='DRN-1466_UUUIM_ZZ',
            sale_date=sale_date_time,
            quantity=4, shipping_cost_accuracy=0,
            dirty=True)
        sale_item_4 = SaleItem.objects.tenant_db_for(self.client_id).create(
            sale=sale,
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

        sale_item_1_before = SaleItem.objects.tenant_db_for(self.client_id).get(id=sale_item_1.pk)
        self.assertEqual(sale_item_1_before.cog, Decimal('12.34'))
        # mapping for sale item
        ins = MappingSaleItemBuilder.instance() \
            .tenant_db_for_only(self.client_id) \
            .with_selected_sale_item_ids([str(sale_item_1.id)]) \
            .with_override_mode(True) \
            .with_chunk_size_query_set_sale_item(5000) \
            .build_mapping_cog_from_item()
        ins.exec()
        sale_item_1_after = SaleItem.objects.tenant_db_for(self.client_id).get(id=sale_item_1.pk)
        self.assertEqual(sale_item_1_after.cog, Decimal('30.66') * sale_item_1.quantity)  # from item cog fixture

    def test_mapping_sale_item_cog_override(self):
        """
        override option: False
        calculate for null or zero value COG from Sale Item
        """
        sale_date_time = datetime(2015, 12, 12)
        self.truncate_data()

        sale = Sale.objects.tenant_db_for(self.client_id).create(
            channel_sale_id="111-222-3230",
            profit_status_id='9d41389c-ea0b-42a3-99bc-73be4f11ada8',
            sale_status_id='a4d57188-aa29-4f16-9288-5365ebe2e4a7',
            client_id=self.client_id,
            channel_id="4c3c7cdc-4297-4ff5-aa35-aa388c1f4e14",
            date=sale_date_time)
        sale_item_1 = SaleItem.objects.tenant_db_for(self.client_id).create(
            sale=sale,
            brand_id="02edd561-1084-4f55-bd5c-9222d008df4e",
            # adidas
            # FBA
            fulfillment_type_id="5b7bc589-14ce-41cb-8911-2925f504bb8d",
            client_id=self.client_id,
            sku='VQ_54-21135_0-B',
            sale_date=sale_date_time,
            cog=Decimal('11.11'),
            quantity=5, shipping_cost_accuracy=0,
            dirty=True)

        self.create_flatten_manage_sale_items()

        sale_item_1_before = SaleItem.objects.tenant_db_for(self.client_id).get(id=sale_item_1.pk)
        self.assertEqual(sale_item_1_before.cog, Decimal('11.11'))
        # mapping for sale item
        ins = MappingSaleItemBuilder.instance() \
            .tenant_db_for_only(self.client_id) \
            .with_selected_sale_item_ids([str(sale_item_1.id)]) \
            .with_override_mode(False) \
            .with_chunk_size_query_set_sale_item(5000) \
            .build_mapping_cog_from_item()
        ins.exec()

        sale_item_1_after = SaleItem.objects.tenant_db_for(self.client_id).get(id=sale_item_1.pk)
        self.assertEqual(sale_item_1_after.cog, Decimal('11.11'))

    def test_mapping_sale_item_cog_12h_recent(self):
        """
        mapping sale item COG
        processes for sale item which are modified in recent 12 hours
        """
        # Prerequisite
        sale_date_time = datetime(2015, 12, 12)
        self.truncate_data()
        sale = Sale.objects.tenant_db_for(self.client_id).create(
            channel_sale_id="111-222-3235",
            profit_status_id='9d41389c-ea0b-42a3-99bc-73be4f11ada8',
            sale_status_id='a4d57188-aa29-4f16-9288-5365ebe2e4a7',
            client_id=self.client_id,
            channel_id="4c3c7cdc-4297-4ff5-aa35-aa388c1f4e14",
            date=sale_date_time,
        )
        sale_item = SaleItem.objects.tenant_db_for(self.client_id).create(
            sale=sale,
            brand_id="818ad366-f624-4b2c-b0d3-64cc942d17ce",
            # North Face
            # MFN
            fulfillment_type_id="a8502437-d298-449a-bd7d-e60034d49daf",
            client_id=self.client_id,
            sku='VQ_54-21135_0-B',
            sale_date=sale_date_time,
            quantity=4, shipping_cost_accuracy=0, type_cog=COG_TYPE_CALCULATED_KEY,
            dirty=True)

        self.create_flatten_manage_sale_items()

        self.assertEqual(sale_item.cog, None)
        # mapping for sale item
        ins = MappingSaleItemBuilder.instance() \
            .tenant_db_for_only(self.client_id) \
            .with_chunk_size_query_set_sale_item(5000) \
            .build_mapping_cog_from_item_12h_recent_only()
        ins.exec()
        sale_item_after = SaleItem.objects.tenant_db_for(self.client_id).get(id=sale_item.pk)
        # created_or_modified_time is less than current time
        self.assertEqual(sale_item_after.cog, Decimal('30.66') * sale_item.quantity)  # from item cog fixture

    def test_mapping_sale_item_from_base_item(self):
        """
        mapping sale item COG
        input is Item base
        """
        # Prerequisite
        sale_date_time = datetime(2015, 12, 12)
        self.truncate_data()
        sale = Sale.objects.tenant_db_for(self.client_id).create(
            channel_sale_id="111-222-3236",
            profit_status_id='9d41389c-ea0b-42a3-99bc-73be4f11ada8',
            sale_status_id='a4d57188-aa29-4f16-9288-5365ebe2e4a7',
            client_id=self.client_id,
            channel_id="4c3c7cdc-4297-4ff5-aa35-aa388c1f4e14",
            date=sale_date_time,
        )
        sale_item = SaleItem.objects.tenant_db_for(self.client_id).create(
            sale=sale,
            brand_id="818ad366-f624-4b2c-b0d3-64cc942d17ce",
            # North Face
            # MFN
            fulfillment_type_id="a8502437-d298-449a-bd7d-e60034d49daf",
            client_id=self.client_id,
            sku='VQ_54-21135_0-B',
            sale_date=sale_date_time,
            quantity=4, shipping_cost_accuracy=0, type_cog=COG_TYPE_CALCULATED_KEY,
            dirty=True)

        self.create_flatten_manage_sale_items()

        item = Item.objects.tenant_db_for(self.client_id).get(id='d7e93d88-ea0e-41f8-a909-f9a5e415234a')  # fixture

        self.assertEqual(sale_item.cog, None)
        # mapping for sale item
        ins = MappingSaleItemBuilder.instance() \
            .tenant_db_for_only(self.client_id) \
            .build_mapping_cog_from_item_based(item=item)
        ins.exec()
        sale_item_after = SaleItem.objects.tenant_db_for(self.client_id).get(id=sale_item.pk)
        # created_or_modified_time is less than current time
        self.assertEqual(sale_item_after.cog, Decimal('30.66') * sale_item.quantity)  # from item cog fixture

    def test_mapping_sale_item_common(self):
        pass

    def test_mapping_sale_item_common_12h_recent(self):
        pass
