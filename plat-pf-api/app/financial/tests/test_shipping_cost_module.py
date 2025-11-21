from datetime import datetime, timezone
from decimal import Decimal

from app.financial.models import BrandSetting, SaleItem, FedExShipment
from app.financial.services.shipping_cost.builder import ShippingCostBuilder
from app.financial.tests.base import BaseAPITest
from config.settings.common import ROOT_DIR

APPS_DIR = ROOT_DIR.path('app')

fixtures = [
    APPS_DIR + "financial/tests/fixtures/brand.json",
    APPS_DIR + "financial/tests/fixtures/fulfillmentchannel.json",
    APPS_DIR + "financial/tests/fixtures/channel.json",
    APPS_DIR + "financial/tests/fixtures/sale_status.json",
    APPS_DIR + "financial/tests/fixtures/profit_status.json",
    APPS_DIR + "financial/tests/fixtures/shipping_cost_module/brand_setting.json",
    APPS_DIR + "financial/tests/fixtures/shipping_cost_module/sale.json",
    APPS_DIR + "financial/tests/fixtures/shipping_cost_module/sale_item.json",
    APPS_DIR + "financial/tests/fixtures/shipping_cost_module/fedex_shipment.json",

]


class ShippingCostModuleTest(BaseAPITest):
    fixtures = BaseAPITest.fixtures + fixtures

    def setUp(self):
        super().setUp()

        if SaleItem.objects.tenant_db_for(self.client_id).count() == 0:

            self.db_table_client(new_table=True)

    def test_shipping_cost_from_brand_settings_all_sale_item(self):
        """
        all sale items
        """
        self.create_flatten_manage_sale_items()
        # Test

        sale_item_1_before = SaleItem.objects.tenant_db_for(self.client_id).get(sku='DRN-1480_BLACK_ZZ',
                                                                                 client_id=self.client_id)
        sale_item_2_before = SaleItem.objects.tenant_db_for(self.client_id).get(sku='DRN-1466_DENIM_ZZ',
                                                                                 client_id=self.client_id)
        sale_item_3_before = SaleItem.objects.tenant_db_for(self.client_id).get(sku='DRN-1466_UUUIM_ZZ',
                                                                                 client_id=self.client_id)
        sale_item_4_before = SaleItem.objects.tenant_db_for(self.client_id).get(sku='DRN-0466_UUUIM_ZZ',
                                                                                 client_id=self.client_id)

        ShippingCostBuilder.instance().tenant_db_for_only(self.client_id).build_from_brand_settings().update()

        sale_item_1_after = SaleItem.objects.tenant_db_for(self.client_id).get(sku='DRN-1480_BLACK_ZZ',
                                                                                client_id=self.client_id)
        sale_item_2_after = SaleItem.objects.tenant_db_for(self.client_id).get(sku='DRN-1466_DENIM_ZZ',
                                                                                client_id=self.client_id)
        sale_item_3_after = SaleItem.objects.tenant_db_for(self.client_id).get(sku='DRN-1466_UUUIM_ZZ',
                                                                                client_id=self.client_id)
        sale_item_4_after = SaleItem.objects.tenant_db_for(self.client_id).get(sku='DRN-0466_UUUIM_ZZ',
                                                                                client_id=self.client_id)

        brand_setting_adidas = BrandSetting.objects.tenant_db_for(self.client_id).get(brand_id="02edd561-1084-4f55-bd5c-9222d008df4e",
                                                        client_id=self.client_id)

        self.assertEqual(sale_item_1_after.shipping_cost,
                         Decimal(format(brand_setting_adidas.est_fba_fees * sale_item_1_before.quantity, '.2f')),
                         'shipping cost calculation error')
        self.assertEqual(sale_item_2_after.shipping_cost, Decimal(format(20.63, '.2f')),
                         'shipping cost calculation error')

        self.assertEqual(sale_item_3_after.shipping_cost, Decimal(format(46.65, '.2f')),
                         'shipping cost calculation error')

        '''
        brand setting has empty formula -> shipping cost is not calculated
        '''
        self.assertEqual(sale_item_4_before.shipping_cost, sale_item_4_after.shipping_cost,
                         'shipping cost calculation error')

    def test_shipping_cost_from_brand_settings_selected_sale_items(self):
        """
        selected sale items
        """
        self.create_flatten_manage_sale_items()
        # Test

        sale_item_1_before = SaleItem.objects.tenant_db_for(self.client_id).get(sku='DRN-1480_BLACK_ZZ',
                                                                                 client_id=self.client_id)
        sale_item_2_before = SaleItem.objects.tenant_db_for(self.client_id).get(sku='DRN-1466_DENIM_ZZ',
                                                                                 client_id=self.client_id)
        sale_item_3_before = SaleItem.objects.tenant_db_for(self.client_id).get(sku='DRN-1466_UUUIM_ZZ',
                                                                                 client_id=self.client_id)
        sale_item_4_before = SaleItem.objects.tenant_db_for(self.client_id).get(sku='DRN-0466_UUUIM_ZZ',
                                                                                 client_id=self.client_id)

        ShippingCostBuilder.instance() \
            .tenant_db_for_only(self.client_id) \
            .with_sale_item_ids([sale_item_1_before.id, sale_item_2_before.id,
                                 sale_item_3_before.id, sale_item_4_before.id]) \
            .build_from_brand_settings().update()

        sale_item_1_after = SaleItem.objects.tenant_db_for(self.client_id).get(sku='DRN-1480_BLACK_ZZ',
                                                                                client_id=self.client_id)
        sale_item_2_after = SaleItem.objects.tenant_db_for(self.client_id).get(sku='DRN-1466_DENIM_ZZ',
                                                                                client_id=self.client_id)
        sale_item_3_after = SaleItem.objects.tenant_db_for(self.client_id).get(sku='DRN-1466_UUUIM_ZZ',
                                                                                client_id=self.client_id)
        sale_item_4_after = SaleItem.objects.tenant_db_for(self.client_id).get(sku='DRN-0466_UUUIM_ZZ',
                                                                                client_id=self.client_id)

        brand_setting_adidas = BrandSetting.objects.tenant_db_for(self.client_id).get(brand_id="02edd561-1084-4f55-bd5c-9222d008df4e",
                                                        client_id=self.client_id)

        self.assertEqual(sale_item_1_after.shipping_cost,
                         Decimal(format(brand_setting_adidas.est_fba_fees * sale_item_1_before.quantity, '.2f')),
                         'shipping cost calculation error')
        self.assertEqual(sale_item_2_after.shipping_cost, Decimal(format(20.63, '.2f')),
                         'shipping cost calculation error')

        self.assertEqual(sale_item_3_after.shipping_cost, Decimal(format(46.65, '.2f')),
                         'shipping cost calculation error')

        '''
        brand setting has empty formula -> shipping cost is not calculated
        '''
        self.assertEqual(sale_item_4_before.shipping_cost, sale_item_4_after.shipping_cost,
                         'shipping cost calculation error')

    def test_shipping_cost_from_brand_settings_12h_recent_sale_item_modified(self):
        """
        sale item modified 12h recent only
        """
        # Update to get modified time for getting 12h recent changes
        SaleItem.objects.tenant_db_for(self.client_id).all().update(modified=datetime.now(tz=timezone.utc))

        self.create_flatten_manage_sale_items()
        # Test

        sale_item_1_before = SaleItem.objects.tenant_db_for(self.client_id).get(sku='DRN-1480_BLACK_ZZ',
                                                                                 client_id=self.client_id)

        ShippingCostBuilder.instance().tenant_db_for_only(
            self.client_id).build_from_brand_settings_12h_recent().update()

        brand_setting_adidas = BrandSetting.objects.tenant_db_for(self.client_id).get(brand_id="02edd561-1084-4f55-bd5c-9222d008df4e",
                                                        client_id=self.client_id)

        sale_item_1_after = SaleItem.objects.tenant_db_for(self.client_id).get(sku='DRN-1480_BLACK_ZZ',
                                                                                client_id=self.client_id)
        sale_item_2_after = SaleItem.objects.tenant_db_for(self.client_id).get(sku='DRN-1466_DENIM_ZZ',
                                                                                client_id=self.client_id)
        sale_item_3_after = SaleItem.objects.tenant_db_for(self.client_id).get(sku='DRN-1466_UUUIM_ZZ',
                                                                                client_id=self.client_id)
        sale_item_4_after = SaleItem.objects.tenant_db_for(self.client_id).get(sku='DRN-0466_UUUIM_ZZ',
                                                                                client_id=self.client_id)

        self.assertEqual(sale_item_1_after.shipping_cost,
                         Decimal(format(brand_setting_adidas.est_fba_fees * sale_item_1_after.quantity, '.2f')),
                         'shipping cost calculation error')
        self.assertEqual(sale_item_2_after.shipping_cost, Decimal(format(20.63, '.2f')),
                         'shipping cost calculation error')

        self.assertEqual(sale_item_3_after.shipping_cost, Decimal(format(46.65, '.2f')),
                         'shipping cost calculation error')

        '''
        brand setting has empty formula -> shipping cost is not calculated
        '''
        self.assertEqual(sale_item_4_after.shipping_cost, sale_item_1_before.shipping_cost,
                         'shipping cost calculation error')

    def test_shipping_cost_from_fedex_shipment_all_sale_item(self):
        """
        for all sale sale item
        :return:
        """
        self.create_flatten_manage_sale_items()
        ShippingCostBuilder.instance().tenant_db_for_only(self.client_id).build_from_fedex_shipment().update()

        res = FedExShipment.objects.tenant_db_for(self.client_id).all().first()
        matched_sales = res.matched_sales
        print(matched_sales)

    def test_shipping_cost_from_fedex_shipment_selected_sale_items(self):
        """
        for selected sale items
        :return:
        """

        sale_item_1_before = SaleItem.objects.tenant_db_for(self.client_id).get(sku='DRN-1480_BLACK_ZZ',
                                                                                 client_id=self.client_id)
        sale_item_2_before = SaleItem.objects.tenant_db_for(self.client_id).get(sku='DRN-1466_DENIM_ZZ',
                                                                                 client_id=self.client_id)
        sale_item_3_before = SaleItem.objects.tenant_db_for(self.client_id).get(sku='DRN-1466_UUUIM_ZZ',
                                                                                 client_id=self.client_id)
        sale_item_4_before = SaleItem.objects.tenant_db_for(self.client_id).get(sku='DRN-0466_UUUIM_ZZ',
                                                                                 client_id=self.client_id)

        self.create_flatten_manage_sale_items()
        ShippingCostBuilder.instance() \
            .tenant_db_for_only(self.client_id) \
            .with_sale_item_ids([sale_item_1_before.id, sale_item_2_before.id,
                                 sale_item_3_before.id, sale_item_4_before.id]) \
            .build_from_fedex_shipment().update()

        res = FedExShipment.objects.tenant_db_for(self.client_id).all().first()
        matched_sales = res.matched_sales
        print(matched_sales)

    def test_shipping_cost_from_fedex_shipment_12h_recent_sale_item_modified(self):
        """
        sale item modified 12h recent only
        :return:
        """
        # Update to get modified time for getting 12h recent changes
        SaleItem.objects.tenant_db_for(self.client_id).all().update(modified=datetime.now(tz=timezone.utc))
        self.create_flatten_manage_sale_items()

        ShippingCostBuilder.instance().tenant_db_for_only(
            self.client_id).build_from_fedex_shipment_for_sale_items_12h_recent().update()

        res = FedExShipment.objects.tenant_db_for(self.client_id).all().first()
        matched_sales = res.matched_sales
        print(matched_sales)

    def test_shipping_cost_from_fedex_shipment_passive_action(self):
        """
        for all pending or none fedex shipment
        :return:
        """
        self.create_flatten_manage_sale_items()

        ShippingCostBuilder.instance().tenant_db_for_only(
            self.client_id).build_from_fedex_shipment_for_sale_items_passive().update()

        res = FedExShipment.objects.tenant_db_for(self.client_id).all().first()
        print(res.matched_sales)
        print(res.matched_channel_sale_ids)
        print(res.matched_time)

    def test_drop_ship_fee_all_sale_items(self):
        """
        for all sale items
        :return:
        """
        self.create_flatten_manage_sale_items()
        res_before = [item.warehouse_processing_fee for item in
                      SaleItem.objects.tenant_db_for(self.client_id).all().order_by('created')]
        ShippingCostBuilder.instance().tenant_db_for_only(
            self.client_id).build_from_brand_settings_for_drop_ship_fee().update()
        res_after = [item.warehouse_processing_fee for item in
                     SaleItem.objects.tenant_db_for(self.client_id).all().order_by('created')]
        print(res_before)
        print(res_after)

    def test_drop_ship_fee_12h_recent_sale_item_modified(self):
        """
        sale item modified 12h recent only
        :return:
        """
        # Update to get modified time for getting 12h recent changes
        SaleItem.objects.tenant_db_for(self.client_id).all().update(modified=datetime.now(tz=timezone.utc))
        self.create_flatten_manage_sale_items()
        res_before = [item.warehouse_processing_fee for item in
                      SaleItem.objects.tenant_db_for(self.client_id).all().order_by('created')]
        ShippingCostBuilder.instance().tenant_db_for_only(
            self.client_id).build_from_brand_settings_for_drop_ship_fee_12h_recent().update()
        res_after = [item.warehouse_processing_fee for item in
                     SaleItem.objects.tenant_db_for(self.client_id).all().order_by('created')]
        print(res_before)
        print(res_after)

    def test_drop_ship_fee_selected_sale_items(self):
        """
        for selected sale items
        :return:
        """
        sale_item_1_before = SaleItem.objects.tenant_db_for(self.client_id).get(sku='DRN-1480_BLACK_ZZ',
                                                                                 client_id=self.client_id)
        sale_item_2_before = SaleItem.objects.tenant_db_for(self.client_id).get(sku='DRN-1466_DENIM_ZZ',
                                                                                 client_id=self.client_id)
        sale_item_3_before = SaleItem.objects.tenant_db_for(self.client_id).get(sku='DRN-1466_UUUIM_ZZ',
                                                                                 client_id=self.client_id)
        sale_item_4_before = SaleItem.objects.tenant_db_for(self.client_id).get(sku='DRN-0466_UUUIM_ZZ',
                                                                                 client_id=self.client_id)

        self.create_flatten_manage_sale_items()
        res_before = [item.warehouse_processing_fee for item in
                      SaleItem.objects.tenant_db_for(self.client_id).all().order_by('created')]
        ShippingCostBuilder.instance() \
            .tenant_db_for_only(self.client_id) \
            .with_sale_item_ids([sale_item_1_before.id, sale_item_2_before.id,
                                 sale_item_3_before.id, sale_item_4_before.id]) \
            .build_from_brand_settings_for_drop_ship_fee().update()

        res_after = [item.warehouse_processing_fee for item in
                     SaleItem.objects.tenant_db_for(self.client_id).all().order_by('created')]
        print(res_before)
        print(res_after)
