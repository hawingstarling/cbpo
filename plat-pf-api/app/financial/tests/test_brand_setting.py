import json
from datetime import datetime
from decimal import Decimal

from rest_framework import status
from rest_framework.reverse import reverse
from app.financial.models import Brand, BrandSetting, SaleItem, Sale
from app.financial.services.brand_settings.ship_cost_calculation_for_sale_item import BrandSettingUpdateSaleItem
from app.financial.sub_serializers.brand_setting_serializers import UpdateSaleSerializer
from app.financial.tests.base import BaseAPITest
from config.settings.common import ROOT_DIR
from app.financial.variable.shipping_cost_source import BRAND_SETTING_SOURCE_KEY

APPS_DIR = ROOT_DIR.path('app')

fixtures = [
    APPS_DIR + "financial/tests/fixtures/brand.json",
    APPS_DIR + "financial/tests/fixtures/fulfillmentchannel.json",
    APPS_DIR + "financial/tests/fixtures/channel.json",
    APPS_DIR + "financial/tests/fixtures/sale_status.json",
    APPS_DIR + "financial/tests/fixtures/profit_status.json",
    APPS_DIR + "financial/tests/fixtures/sale.json",
    APPS_DIR + "financial/tests/fixtures/sale_charge_and_cost.json",
]


class BrandSettingTest(BaseAPITest):
    """
    - test post create brand setting
    - test get list brand setting
    - test get brand setting
    - test put brand setting
    - test patch brand setting
    - test delete brabd setting
    - test count sale items from brand setting
    - test update sales
    """
    fixtures = BaseAPITest.fixtures + fixtures

    def test_post_brand_setting(self):
        # Test
        data = {
            "est_first_item_shipcost": 0,
            "est_add_item_shipcost": 0,
            "est_fba_fees": 0,
            "po_dropship_cost": 0,
            "mfn_formula": "Rapid Access",
            "auto_update_sales": True,
            "channel": "amazon.com",
            "brand": "Nike"
        }

        url = reverse("list-create-brand-settings", kwargs={'client_id': self.client_id})
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.jwt_token}')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, 'post create brand setting error')

    def test_get_list_brand_setting(self):
        # Prerequisite
        brand_feather = Brand.objects.tenant_db_for(self.client_id).create(name='Feather')
        data_common = {
            "est_first_item_shipcost": 0,
            "est_add_item_shipcost": 0,
            "est_fba_fees": 0,
            "po_dropship_cost": 0,
            "mfn_formula": "Rapid Access",
            "auto_update_sales": True,
            "channel_id": "4c3c7cdc-4297-4ff5-aa35-aa388c1f4e14",
            "client_id": self.client_id
        }
        _ = BrandSetting.objects.tenant_db_for(self.client_id).create(brand_id="40e9d228-9785-4cf0-a6c2-d90fe813b32e",
                                                                      **data_common)
        _ = BrandSetting.objects.tenant_db_for(self.client_id).create(brand=brand_feather, **data_common)
        # Test
        url = reverse("list-create-brand-settings", kwargs={'client_id': self.client_id})
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.jwt_token}')
        response = self.client.get(url, None, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, 'get list brand setting error')

    def test_get_brand_setting(self):
        # Test
        data = {
            "est_first_item_shipcost": 0,
            "est_add_item_shipcost": 0,
            "est_fba_fees": 0,
            "po_dropship_cost": 0,
            "mfn_formula": "Rapid Access",
            "auto_update_sales": True,
            "channel_id": "4c3c7cdc-4297-4ff5-aa35-aa388c1f4e14",
            "brand_id": "40e9d228-9785-4cf0-a6c2-d90fe813b32e",
            "client_id": self.client_id,
            "segment": "Active"
        }
        brand_setting = BrandSetting.objects.tenant_db_for(self.client_id).create(**data)
        # Test
        url = reverse("retrieve-update-delete-brand-setting",
                      kwargs={'client_id': self.client_id, "brand_setting_id": brand_setting.id})
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.jwt_token}')
        response = self.client.get(url, None, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, 'get brand setting error')

    def test_put_brand_setting(self):
        data = {
            "est_first_item_shipcost": 0,
            "est_add_item_shipcost": 0,
            "est_fba_fees": 0,
            "po_dropship_cost": 0,
            "mfn_formula": "Rapid Access",
            "auto_update_sales": True,
            "channel_id": "4c3c7cdc-4297-4ff5-aa35-aa388c1f4e14",
            "brand_id": "40e9d228-9785-4cf0-a6c2-d90fe813b32e",
            "client_id": self.client_id,
            "segment": "Active"
        }
        brand_setting = BrandSetting.objects.tenant_db_for(self.client_id).create(**data)
        # Test
        data_update = {
            "est_first_item_shipcost": 0,
            "est_add_item_shipcost": 0,
            "est_fba_fees": 0,
            "po_dropship_cost": 0,
            "mfn_formula": "Rapid Access",
            "auto_update_sales": False,
            "channel": "amazon.com",
            "brand": "Nike",
            "segment": "Outdoor"
        }
        url = reverse("retrieve-update-delete-brand-setting",
                      kwargs={'client_id': self.client_id, "brand_setting_id": brand_setting.id})
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.jwt_token}')
        response = self.client.put(url, data_update, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, 'put brand setting error')

    def test_patch_brand_setting(self):
        data = {
            "est_first_item_shipcost": 0,
            "est_add_item_shipcost": 0,
            "est_fba_fees": 0,
            "po_dropship_cost": 0,
            "mfn_formula": "Rapid Access",
            "auto_update_sales": True,
            "channel_id": "4c3c7cdc-4297-4ff5-aa35-aa388c1f4e14",
            "brand_id": "40e9d228-9785-4cf0-a6c2-d90fe813b32e",
            "client_id": self.client_id
        }
        brand_setting = BrandSetting.objects.tenant_db_for(self.client_id).create(**data)
        # Test
        data_update = {
            "est_first_item_shipcost": 0,
            "est_add_item_shipcost": 0,
            "est_fba_fees": 1
        }
        url = reverse("retrieve-update-delete-brand-setting",
                      kwargs={'client_id': self.client_id, "brand_setting_id": brand_setting.id})
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.jwt_token}')
        response = self.client.patch(url, data_update, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, 'patch brand setting error')

    def test_delete_brand_setting(self):
        # Test
        data = {
            "est_first_item_shipcost": 0,
            "est_add_item_shipcost": 0,
            "est_fba_fees": 0,
            "po_dropship_cost": 0,
            "mfn_formula": "Rapid Access",
            "auto_update_sales": True,
            "channel_id": "4c3c7cdc-4297-4ff5-aa35-aa388c1f4e14",
            "brand_id": "40e9d228-9785-4cf0-a6c2-d90fe813b32e",
            "client_id": self.client_id
        }
        brand_setting = BrandSetting.objects.tenant_db_for(self.client_id).create(**data)
        # Test
        url = reverse("retrieve-update-delete-brand-setting",
                      kwargs={'client_id': self.client_id, "brand_setting_id": brand_setting.id})
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.jwt_token}')
        response = self.client.delete(url, None, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT, 'delete brand setting error')

    def test_count_sale_item_by_brand_setting(self):
        # Prerequisite
        data_brand_adidas = {
            "est_first_item_shipcost": 10.00,
            "est_add_item_shipcost": 3.00,
            "est_fba_fees": 69.69,
            "po_dropship_cost": 12.34,
            "mfn_formula": "Rapid Access",
            "auto_update_sales": False,
            "channel_id": "4c3c7cdc-4297-4ff5-aa35-aa388c1f4e14",
            "brand_id": "02edd561-1084-4f55-bd5c-9222d008df4e",  # Adidas
            "client_id": self.client_id
        }
        data_brand_nike = {
            "est_first_item_shipcost": 33.33,
            "est_add_item_shipcost": 4.44,
            "est_fba_fees": 42.42,
            "po_dropship_cost": 42.56,
            "mfn_formula": "Dropship",
            "auto_update_sales": False,
            "channel_id": "4c3c7cdc-4297-4ff5-aa35-aa388c1f4e14",
            "brand_id": "40e9d228-9785-4cf0-a6c2-d90fe813b32e",  # Nike
            "client_id": self.client_id
        }
        brand_setting_adidas = BrandSetting.objects.tenant_db_for(self.client_id).create(**data_brand_adidas)
        _ = BrandSetting.objects.create(**data_brand_nike)
        sale_date_time = datetime(2015, 12, 12)

        self.truncate_data()

        sale = Sale.objects.tenant_db_for(self.client_id).create(channel_sale_id="111-222-3234",
                                                                 profit_status_id='9d41389c-ea0b-42a3-99bc-73be4f11ada8',
                                                                 sale_status_id='a4d57188-aa29-4f16-9288-5365ebe2e4a7',
                                                                 client_id=self.client_id,
                                                                 channel_id="4c3c7cdc-4297-4ff5-aa35-aa388c1f4e14",
                                                                 date=sale_date_time)
        _ = SaleItem.objects.tenant_db_for(self.client_id).create(sale=sale,
                                                                  brand_id="02edd561-1084-4f55-bd5c-9222d008df4e",
                                                                  # adidas
                                                                  # FBA
                                                                  fulfillment_type_id="5b7bc589-14ce-41cb-8911-2925f504bb8d",
                                                                  client_id=self.client_id,
                                                                  sku='DRN-1480_BLACK_ZZ',
                                                                  sale_date=sale_date_time,
                                                                  quantity=5, shipping_cost_accuracy=0, dirty=True)
        _ = SaleItem.objects.tenant_db_for(self.client_id).create(sale=sale,
                                                                  brand_id="02edd561-1084-4f55-bd5c-9222d008df4e",
                                                                  # adidas
                                                                  # MFN
                                                                  fulfillment_type_id="a8502437-d298-449a-bd7d-e60034d49daf",
                                                                  client_id=self.client_id,
                                                                  sku='DRN-1466_DENIM_ZZ',
                                                                  sale_date=sale_date_time,
                                                                  quantity=3, shipping_cost_accuracy=0, dirty=True)
        _ = SaleItem.objects.tenant_db_for(self.client_id).create(sale=sale,
                                                                  brand_id="40e9d228-9785-4cf0-a6c2-d90fe813b32e",
                                                                  # Nike
                                                                  # MFN
                                                                  fulfillment_type_id="a8502437-d298-449a-bd7d-e60034d49daf",
                                                                  client_id=self.client_id,
                                                                  sku='DRN-1466_UUUIM_ZZ',
                                                                  sale_date=sale_date_time,
                                                                  quantity=4, shipping_cost_accuracy=0, dirty=True)
        self.create_flatten_manage_sale_items()
        # Test
        data_req = {
            "sale_date_from": "2010-10-21T09:08:36.755Z",
            "sale_date_to": "3020-10-21T09:08:36.755Z",
            "recalculate": True
        }
        url = reverse("count-brand-setting-update-sales",
                      kwargs={'client_id': self.client_id, "brand_setting_id": brand_setting_adidas.id})
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.jwt_token}')
        response = self.client.post(url, data_req, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, 'count sale items from brand setting error')
        count_sale_items = json.loads(response.content).get('count-sales')
        self.assertEqual(count_sale_items, 2, 'count sale items from brand setting error')

    def test_update_sales(self):
        # Prerequisite
        data_brand_adidas = {
            "est_first_item_shipcost": 10.00,
            "est_add_item_shipcost": 3.00,
            "est_fba_fees": 69.69,
            "po_dropship_cost": 12.34,
            "mfn_formula": "Rapid Access",
            "auto_update_sales": False,
            "channel_id": "4c3c7cdc-4297-4ff5-aa35-aa388c1f4e14",
            "brand_id": "02edd561-1084-4f55-bd5c-9222d008df4e",  # Adidas
            "client_id": self.client_id,
            "segment": "Active"
        }
        data_brand_nike = {
            "est_first_item_shipcost": 33.33,
            "est_add_item_shipcost": 4.44,
            "est_fba_fees": 42.42,
            "po_dropship_cost": 42.56,
            "mfn_formula": "Dropship",
            "auto_update_sales": False,
            "channel_id": "4c3c7cdc-4297-4ff5-aa35-aa388c1f4e14",
            "brand_id": "40e9d228-9785-4cf0-a6c2-d90fe813b32e",  # Nike
            "client_id": self.client_id,
            "segment": "Outdoor"
        }
        data_brand_north_face = {
            "est_first_item_shipcost": 33.33,
            "est_add_item_shipcost": 4.44,
            "est_fba_fees": 42.42,
            "po_dropship_cost": 42.56,
            "mfn_formula": "",
            "auto_update_sales": False,
            "channel_id": "4c3c7cdc-4297-4ff5-aa35-aa388c1f4e14",
            "brand_id": "818ad366-f624-4b2c-b0d3-64cc942d17ce",  # North Face
            "client_id": self.client_id,
            "segment": "Lifestyle"
        }
        brand_setting_adidas = BrandSetting.objects.tenant_db_for(self.client_id).create(**data_brand_adidas)
        brand_setting_nike = BrandSetting.objects.tenant_db_for(self.client_id).create(**data_brand_nike)
        brand_setting_north_face = BrandSetting.objects.tenant_db_for(self.client_id).create(**data_brand_north_face)
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
        # Test
        serializer = UpdateSaleSerializer(data={
            "sale_date_from": "2005-10-21T11:07:10.748Z",
            "sale_date_to": "2020-10-21T11:07:10.748Z",
            "recalculate": True
        })
        serializer.is_valid(raise_exception=True)
        handler = BrandSettingUpdateSaleItem(client_id=self.client_id, brand_setting=brand_setting_adidas,
                                             chunk_size=5000,
                                             from_date=serializer.validated_data["sale_date_from"],
                                             to_date=serializer.validated_data["sale_date_to"],
                                             is_recalculate=serializer.validated_data["recalculate"])
        handler.update()
        sale_item_1 = SaleItem.objects.tenant_db_for(self.client_id).get(id=sale_item_1.id)
        self.assertEqual(sale_item_1.shipping_cost,
                         Decimal(format(brand_setting_adidas.est_fba_fees * sale_item_1.quantity, '.2f')),
                         'shipping cost calculation error')
        self.assertEqual(sale_item_1.shipping_cost_source, BRAND_SETTING_SOURCE_KEY)
        sale_item_2 = SaleItem.objects.tenant_db_for(self.client_id).get(id=sale_item_2.id)
        self.assertEqual(sale_item_2.shipping_cost, Decimal(format(20.63, '.2f')),
                         'shipping cost calculation error')
        self.assertEqual(sale_item_2.shipping_cost_source, BRAND_SETTING_SOURCE_KEY)
        handler = BrandSettingUpdateSaleItem(client_id=self.client_id, brand_setting=brand_setting_nike,
                                             chunk_size=5000,
                                             from_date=serializer.validated_data["sale_date_from"],
                                             to_date=serializer.validated_data["sale_date_to"],
                                             is_recalculate=serializer.validated_data["recalculate"])
        handler.update()
        sale_item_3 = SaleItem.objects.tenant_db_for(self.client_id).get(id=sale_item_3.id)
        self.assertEqual(sale_item_3.shipping_cost, Decimal(format(46.65, '.2f')),
                         'shipping cost calculation error')
        self.assertEqual(sale_item_3.shipping_cost_source, BRAND_SETTING_SOURCE_KEY)

        before_update = sale_item_4.shipping_cost
        handler = BrandSettingUpdateSaleItem(client_id=self.client_id, brand_setting=brand_setting_north_face,
                                             chunk_size=5000,
                                             from_date=serializer.validated_data["sale_date_from"],
                                             to_date=serializer.validated_data["sale_date_to"],
                                             is_recalculate=serializer.validated_data["recalculate"])
        handler.update()
        '''
        brand setting has empty formula -> shipping cost is not calculated
        '''
        sale_item_4 = SaleItem.objects.tenant_db_for(self.client_id).get(id=sale_item_4.id)
        self.assertEqual(sale_item_4.shipping_cost, before_update, 'shipping cost calculation error')
