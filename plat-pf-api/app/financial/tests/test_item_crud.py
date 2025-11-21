from rest_framework import status
from rest_framework.reverse import reverse

from app.financial.models import Brand, FulfillmentChannel, Item, Variant, ItemCog, Channel
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
    APPS_DIR + "financial/tests/fixtures/variant.json",
    APPS_DIR + "job/tests/fixtures/job_config.json",
]


class ItemTest(BaseAPITest):
    # TODO: permission from PS
    """
    - test post create item
    - test get list item
    - test update put item
    - test update patch item
    - test delete item
    - test bulk action put item
    - test bulk action delete item
    - test post create item cog
    - test get list item cog
    - test update put item cog
    - test update patch item cog
    - test delete item cog
    """

    fixtures = fixtures

    def test_post_item(self):
        data = {
            "sku": "string",
            "upc": "string",
            "asin": "string",
            "title": "string",
            "description": "string",
            "est_shipping_cost": 0,
            "est_drop_ship_cost": 0,
            "brand": "Nike",
            "size": "10",
            "style": "Summer",
            "fulfillment_type": "FBA",
            "channel": "amazon.com"
        }
        # Test
        url = reverse("list-create-item-view", kwargs={'client_id': self.client_id})
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.jwt_token}')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, 'post create item error')

    def test_get_list_items(self):
        # Prerequisite
        data = {
            "sku": "string",
            "upc": "string",
            "asin": "string",
            "title": "string",
            "description": "string",
            "est_shipping_cost": 0,
            "est_drop_ship_cost": 0,
            "brand": Brand.objects.tenant_db_for(self.client_id).get(name='Nike', client_id=self.client_id),
            "size": Variant.objects.tenant_db_for(self.client_id).get(type='Size', value='20'),
            "style": Variant.objects.tenant_db_for(self.client_id).get(type='Style', value='Summer'),
            "fulfillment_type": FulfillmentChannel.objects.tenant_db_for(self.client_id).get(name='FBA'),
            "channel": Channel.objects.tenant_db_for(self.client_id).get(name='amazon.com'),
            "client_id": self.client_id
        }
        Item.objects.tenant_db_for(self.client_id).create(**data)
        # Test
        url = reverse('list-create-item-view', kwargs={'client_id': self.client_id})
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.jwt_token}')
        response = self.client.get(url, None, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, 'get list items error')

    def test_get_item(self):
        # Prerequisite
        data = {
            "sku": "string",
            "upc": "string",
            "asin": "string",
            "title": "string",
            "description": "string",
            "est_shipping_cost": 0,
            "est_drop_ship_cost": 0,
            "brand": Brand.objects.tenant_db_for(self.client_id).get(name='Nike', client_id=self.client_id),
            "size": Variant.objects.tenant_db_for(self.client_id).get(type='Size', value="20"),
            "style": Variant.objects.tenant_db_for(self.client_id).get(type='Style', value='Summer'),
            "fulfillment_type": FulfillmentChannel.objects.tenant_db_for(self.client_id).get(name='FBA'),
            "channel": Channel.objects.tenant_db_for(self.client_id).get(name='amazon.com'),
            "client_id": self.client_id
        }
        item = Item.objects.tenant_db_for(self.client_id).create(**data)
        # Test
        url = reverse('update-delete-item-view', kwargs={'client_id': self.client_id, 'pk': item.pk})
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.jwt_token}')
        response = self.client.get(url, None, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, 'get item error')

    def test_put_item(self):
        # Prerequisite
        data = {
            "sku": "string",
            "upc": "string",
            "asin": "string",
            "title": "string",
            "description": "string",
            "est_shipping_cost": 0,
            "est_drop_ship_cost": 0,
            "brand": Brand.objects.tenant_db_for(self.client_id).get(name='Nike', client_id=self.client_id),
            "size": Variant.objects.tenant_db_for(self.client_id).get(type='Size', value="20"),
            "style": Variant.objects.tenant_db_for(self.client_id).get(type='Style', value='Summer'),
            "fulfillment_type": FulfillmentChannel.objects.tenant_db_for(self.client_id).get(name='FBA'),
            "channel": Channel.objects.tenant_db_for(self.client_id).get(name='amazon.com'),
            "client_id": self.client_id
        }
        item = Item.objects.tenant_db_for(self.client_id).create(**data)
        data_update = {
            "sku": "string",
            "upc": "string_update",
            "asin": "string_update",
            "title": "string_update",
            "description": "string",
            "est_shipping_cost": 0,
            "est_drop_ship_cost": 0,
            "brand": "Nike",
            "channel": "amazon.com",
            "size": "Size",
            "style": "Style",
            "fulfillment_type": "FBA",
            "client_id": self.client_id
        }
        # Test
        url = reverse('update-delete-item-view', kwargs={'client_id': self.client_id, 'pk': item.pk})
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.jwt_token}')
        response = self.client.put(url, data_update, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, 'put item error')

    def test_patch_item(self):
        # Prerequisite
        data = {
            "sku": "string",
            "upc": "string",
            "asin": "string",
            "title": "string",
            "description": "string",
            "est_shipping_cost": 0,
            "est_drop_ship_cost": 0,
            "brand": Brand.objects.tenant_db_for(self.client_id).get(name='Nike', client_id=self.client_id),
            "size": Variant.objects.tenant_db_for(self.client_id).get(type='Size', value="20"),
            "style": Variant.objects.tenant_db_for(self.client_id).get(type='Style', value='Summer'),
            "fulfillment_type": FulfillmentChannel.objects.tenant_db_for(self.client_id).get(name='FBA'),
            "channel": Channel.objects.tenant_db_for(self.client_id).get(name='amazon.com'),
            "client_id": self.client_id
        }
        item = Item.objects.tenant_db_for(self.client_id).create(**data)
        data_update = {
            "upc": "string_update",
            "asin": "string_update",
            "title": "string_update",
        }
        # Test
        url = reverse('update-delete-item-view', kwargs={'client_id': self.client_id, 'pk': item.pk})
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.jwt_token}')
        response = self.client.patch(url, data_update, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, 'patch item error')

    def test_delete_item(self):
        # Prerequisite
        data = {
            "sku": "string",
            "upc": "string",
            "asin": "string",
            "title": "string",
            "description": "string",
            "est_shipping_cost": 0,
            "est_drop_ship_cost": 0,
            "brand": Brand.objects.tenant_db_for(self.client_id).get(name='Nike', client_id=self.client_id),
            "size": Variant.objects.tenant_db_for(self.client_id).get(type='Size', value="20"),
            "style": Variant.objects.tenant_db_for(self.client_id).get(type='Style', value='Summer'),
            "fulfillment_type": FulfillmentChannel.objects.tenant_db_for(self.client_id).get(name='FBA'),
            "channel": Channel.objects.tenant_db_for(self.client_id).get(name='amazon.com'),
            "client_id": self.client_id
        }
        item = Item.objects.tenant_db_for(self.client_id).create(**data)
        # Test
        url = reverse('update-delete-item-view', kwargs={'client_id': self.client_id, 'pk': item.pk})
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.jwt_token}')
        response = self.client.delete(url, None, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT, 'patch item error')

    def test_post_create_item_cog(self):
        # Prerequisite
        data = {
            "sku": "string",
            "upc": "string",
            "asin": "string",
            "title": "string",
            "description": "string",
            "est_shipping_cost": 0,
            "est_drop_ship_cost": 0,
            "brand": Brand.objects.tenant_db_for(self.client_id).get(name='Nike', client_id=self.client_id),
            "size": Variant.objects.tenant_db_for(self.client_id).get(type='Size', value="20"),
            "style": Variant.objects.tenant_db_for(self.client_id).get(type='Style', value='Summer'),
            "fulfillment_type": FulfillmentChannel.objects.tenant_db_for(self.client_id).get(name='FBA'),
            "channel": Channel.objects.tenant_db_for(self.client_id).get(name='amazon.com'),
            "client_id": self.client_id
        }
        item = Item.objects.tenant_db_for(self.client_id).create(**data)
        # Test
        data_cog = {
            "cog": 10,
            "effect_start_date": "2020-10-21T03:46:14.070Z",
            "effect_end_date": "2020-10-21T03:46:14.070Z"
        }
        url = reverse("list-create-item-cog", kwargs={"client_id": self.client_id, "item_id": item.pk})
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.jwt_token}')
        response = self.client.post(url, data_cog, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, 'post item cog error')

    def test_get_list_item_cogs(self):
        # Prerequisite
        data = {
            "sku": "string",
            "upc": "string",
            "asin": "string",
            "title": "string",
            "description": "string",
            "est_shipping_cost": 0,
            "est_drop_ship_cost": 0,
            "brand": Brand.objects.tenant_db_for(self.client_id).get(name='Nike', client_id=self.client_id),
            "size": Variant.objects.tenant_db_for(self.client_id).get(type='Size', value="20"),
            "style": Variant.objects.tenant_db_for(self.client_id).get(type='Style', value='Summer'),
            "fulfillment_type": FulfillmentChannel.objects.tenant_db_for(self.client_id).get(name='FBA'),
            "channel": Channel.objects.tenant_db_for(self.client_id).get(name='amazon.com'),
            "client_id": self.client_id
        }
        item = Item.objects.tenant_db_for(self.client_id).create(**data)
        item_cog_1 = {
            "cog": 10,
            "effect_start_date": "2020-10-21T03:46:14.070Z",
            "effect_end_date": "2020-10-21T03:46:14.070Z"
        }
        item_cog_2 = {
            "cog": 10,
            "effect_start_date": "2020-10-21T03:46:14.070Z",
            "effect_end_date": "2020-10-21T03:46:14.070Z"
        }
        ItemCog.objects.tenant_db_for(self.client_id).bulk_create(
            [ItemCog(item=item, **item_cog_1), ItemCog(item=item, **item_cog_2)])
        # Test
        url = reverse("list-create-item-cog", kwargs={"client_id": self.client_id, "item_id": item.pk})
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.jwt_token}')
        response = self.client.get(url, None, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, 'get list item cog error')

    def test_get_item_cog(self):
        data = {
            "sku": "string",
            "upc": "string",
            "asin": "string",
            "title": "string",
            "description": "string",
            "est_shipping_cost": 0,
            "est_drop_ship_cost": 0,
            "brand": Brand.objects.tenant_db_for(self.client_id).get(name='Nike', client_id=self.client_id),
            "size": Variant.objects.tenant_db_for(self.client_id).get(type='Size', value="20"),
            "style": Variant.objects.tenant_db_for(self.client_id).get(type='Style', value='Summer'),
            "fulfillment_type": FulfillmentChannel.objects.tenant_db_for(self.client_id).get(name='FBA'),
            "channel": Channel.objects.tenant_db_for(self.client_id).get(name='amazon.com'),
            "client_id": self.client_id
        }
        item = Item.objects.tenant_db_for(self.client_id).create(**data)
        item_cog = {
            "cog": 10,
            "effect_start_date": "2020-10-21T03:46:14.070Z",
            "effect_end_date": "2020-10-21T03:46:14.070Z"
        }
        item_cog = ItemCog.objects.tenant_db_for(self.client_id).create(item=item, **item_cog)
        # Test
        url = reverse("update-delete-item-cog",
                      kwargs={"client_id": self.client_id, "item_id": item.pk, "pk": item_cog.pk})
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.jwt_token}')
        response = self.client.get(url, None, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, 'get item cog error')

    def test_put_item_cog(self):
        data = {
            "sku": "string",
            "upc": "string",
            "asin": "string",
            "title": "string",
            "description": "string",
            "est_shipping_cost": 0,
            "est_drop_ship_cost": 0,
            "brand": Brand.objects.tenant_db_for(self.client_id).get(name='Nike', client_id=self.client_id),
            "size": Variant.objects.tenant_db_for(self.client_id).get(type='Size', value="20"),
            "style": Variant.objects.tenant_db_for(self.client_id).get(type='Style', value='Summer'),
            "fulfillment_type": FulfillmentChannel.objects.tenant_db_for(self.client_id).get(name='FBA'),
            "channel": Channel.objects.tenant_db_for(self.client_id).get(name='amazon.com'),
            "client_id": self.client_id
        }
        item = Item.objects.tenant_db_for(self.client_id).create(**data)
        item_cog = {
            "cog": 10,
            "effect_start_date": "2020-10-21T03:46:14.070Z",
            "effect_end_date": "2020-10-21T03:46:14.070Z"
        }
        item_cog = ItemCog.objects.tenant_db_for(self.client_id).create(item=item, **item_cog)
        # Test
        data_update = {
            "cog": 3,
            "effect_start_date": "2020-10-21T03:46:14.070Z",
            "effect_end_date": "2020-10-21T03:46:14.070Z"
        }
        url = reverse("update-delete-item-cog",
                      kwargs={"client_id": self.client_id, "item_id": item.pk, "pk": item_cog.pk})
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.jwt_token}')
        response = self.client.put(url, data_update, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, 'put item cog error')

    def test_patch_item_cog(self):
        data = {
            "sku": "string",
            "upc": "string",
            "asin": "string",
            "title": "string",
            "description": "string",
            "est_shipping_cost": 0,
            "est_drop_ship_cost": 0,
            "brand": Brand.objects.tenant_db_for(self.client_id).get(name='Nike', client_id=self.client_id),
            "size": Variant.objects.tenant_db_for(self.client_id).get(type='Size', value="20"),
            "style": Variant.objects.tenant_db_for(self.client_id).get(type='Style', value='Summer'),
            "fulfillment_type": FulfillmentChannel.objects.tenant_db_for(self.client_id).get(name='FBA'),
            "channel": Channel.objects.tenant_db_for(self.client_id).get(name='amazon.com'),
            "client_id": self.client_id
        }
        item = Item.objects.tenant_db_for(self.client_id).create(**data)
        item_cog = {
            "cog": 10,
            "effect_start_date": "2020-10-21T03:46:14.070Z",
            "effect_end_date": "2020-10-21T03:46:14.070Z"
        }
        item_cog = ItemCog.objects.tenant_db_for(self.client_id).create(item=item, **item_cog)
        # Test
        data_update = {
            "cog": 3,
            "effect_end_date": "2020-10-21T03:46:14.070Z"
        }
        url = reverse("update-delete-item-cog",
                      kwargs={"client_id": self.client_id, "item_id": item.pk, "pk": item_cog.pk})
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.jwt_token}')
        response = self.client.patch(url, data_update, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, 'patch item cog error')

    def test_put_bulk_item(self):
        # Prerequisite
        brand = Brand.objects.tenant_db_for(self.client_id).get(name='Nike', client_id=self.client_id)
        channel = Channel.objects.tenant_db_for(self.client_id).get(name='amazon.com')
        size = Variant.objects.tenant_db_for(self.client_id).get(type='Size', value="20")
        style = Variant.objects.tenant_db_for(self.client_id).get(type='Style', value='Summer')
        fulfillment = FulfillmentChannel.objects.tenant_db_for(self.client_id).get(name='FBA')

        data_common = {
            "upc": "string",
            "asin": "string",
            "title": "string",
            "description": "string",
            "est_shipping_cost": 0,
            "est_drop_ship_cost": 0,
            "brand": brand,
            "channel": channel,
            "size": size,
            "style": style,
            "fulfillment_type": fulfillment,
            "client_id": self.client_id
        }

        item_1 = Item.objects.tenant_db_for(self.client_id).create(sku="sku_1", **data_common)
        item_2 = Item.objects.tenant_db_for(self.client_id).create(sku="sku_2", **data_common)
        # Test
        data_update = {
            "title": "string",
            "description": "string",
            "est_shipping_cost": 1,
            "est_drop_ship_cost": 1,
            "brand": "Nike",
            "channel": "amazon.com",
            "size": "Size",
            "style": "Style",
            "fulfillment_type": "FBA"
        }
        url = reverse("item-bulk-action-view", kwargs={"client_id": self.client_id})
        url = url + f'?item_ids={str(item_1.id)},{str(item_2.id)}'
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.jwt_token}')
        response = self.client.put(url, data_update, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, 'put bulk item error')

    def test_delete_bulk_item(self):
        # Prerequisite
        brand = Brand.objects.tenant_db_for(self.client_id).get(name='Nike', client_id=self.client_id)
        channel = Channel.objects.tenant_db_for(self.client_id).get(name='amazon.com')
        size = Variant.objects.tenant_db_for(self.client_id).get(type='Size', value='20')
        style = Variant.objects.tenant_db_for(self.client_id).get(type='Style', value='Summer')
        fulfillment = FulfillmentChannel.objects.tenant_db_for(self.client_id).get(name='FBA')

        data_common = {
            "upc": "string",
            "asin": "string",
            "title": "string",
            "description": "string",
            "est_shipping_cost": 0,
            "est_drop_ship_cost": 0,
            "brand": brand,
            "channel": channel,
            "size": size,
            "style": style,
            "fulfillment_type": fulfillment,
            "client_id": self.client_id
        }
        item_1 = Item.objects.tenant_db_for(self.client_id).create(sku="sku_1", **data_common)
        item_2 = Item.objects.tenant_db_for(self.client_id).create(sku="sku_2", **data_common)
        # Test
        url = reverse("item-bulk-action-view", kwargs={"client_id": self.client_id})
        url = url + f'?item_ids={str(item_1.id)},{str(item_2.id)}'
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.jwt_token}')
        response = self.client.delete(url, None, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT, 'delete bulk item error')
