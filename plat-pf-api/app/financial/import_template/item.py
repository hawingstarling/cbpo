import logging
from abc import ABC
from datetime import datetime

from app.financial.import_template.base_custom_module import BaseCustomModule
from app.financial.models import Brand, Item as ItemModel, ItemCog
from app.financial.observer.publisher import publisher, ITEM_ASPECT_EVENT
from app.financial.permissions.base import JwtTokenPermission
from app.financial.services.activity import ActivityService
from app.financial.sub_serializers.item_serializer import ItemImportSerializer

logger = logging.getLogger(__name__)


class ItemModule(BaseCustomModule, ABC):
    __NAME__ = 'ItemModule'
    __MODEL__ = ItemModel
    __LABEL__ = 'Items'
    __SERIALIZER_CLASS__ = ItemImportSerializer
    __PERMISSION_CLASS__ = [JwtTokenPermission]
    __TEMPLATE_VERSION__ = '1.1'
    __TEMPLATE_NUMBER_RECORD__ = 3

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        #
        self.items_cog_created = []

    @property
    def data_sample(self):
        sku = ["EY_46-09057_5-Q", "OB_60-41353_5-L", "VQ_54-21135_0-B"]
        upc = ["304071789001", "802249599370", "1704633174449"]
        asin = ["IVOSDK9C2P", "5DQVP9DQ1D", "GVQAQ5VFVO"]
        fulfillment_type = ["FBA", "RA"]
        brand = Brand.objects.all().values_list('name', flat=True).distinct()
        channel = ['amazon.com']
        size = ["XL", "M", "L"]
        style = ["Holiday", "Brown", "Winter"]
        effect_start_date = [datetime(2020, 8, 27), datetime(2020, 8, 26), datetime(2020, 8, 25)]
        effect_end_date = [datetime(2020, 8, 29), datetime(2020, 8, 28), datetime(2020, 8, 28)]
        return {
            'sku': sku,
            'upc': upc,
            'asin': asin,
            'fulfillment_type': fulfillment_type,
            'brand': brand,
            'channel': channel,
            'size': size,
            'style': style,
            'effect_start_date': effect_start_date,
            'effect_end_date': effect_end_date,
        }

    def process(self, lib_import_id: str, **kwargs) -> any:
        super().process(lib_import_id, **kwargs)
        ActivityService(client_id=self.client_id, user_id=self.user_id).create_activity_import_item_data()

    def filter_instance(self, lib_import_id: str, validated_data, **kwargs):
        client_id = kwargs['client_id']
        return {
            'client_id': client_id,
            'sku': validated_data['sku']
        }

    def keys_raw_map_config(self, lib_import_id: str, validated_data, **kwargs):
        return {
            'key_map': ['sku']
        }

    def make_instance(self, lib_import_id: str, validated_data: dict, **kwargs):
        obj, created = super().make_instance(lib_import_id, validated_data, **kwargs)
        #
        if not validated_data.get('cog'):
            return obj, created
        item_cod_data = dict(
            item=obj,
            cog=validated_data['cog'],
            effect_start_date=validated_data.get("effective_start_date", None),
            effect_end_date=validated_data.get("effective_end_date", None)
        )
        try:
            ItemCog.objects.tenant_db_for(self.client_id).get(**item_cod_data)
        except ItemCog.DoesNotExist:
            self.items_cog_created.append(ItemCog(**item_cod_data))
        except Exception as ex:
            pass
        return obj, created

    def bulk_process(self, lib_import_id: str, bulk_insert: list, bulk_update: list, **kwargs):
        super().bulk_process(lib_import_id, bulk_insert, bulk_update, **kwargs)
        #
        if len(self.items_cog_created) > 0:
            ItemCog.objects.tenant_db_for(self.client_id).bulk_create(self.items_cog_created, ignore_conflicts=True)
            self.items_cog_created = []

        # trigger here
        item_ids_update = [str(ele.id) for ele in bulk_update]
        item_ids_insert = [str(ele.id) for ele in bulk_insert]
        item_ids = item_ids_update + item_ids_insert
        if len(item_ids):
            publisher.notify(
                # post action on item changes
                # mapping sale item cog
                event_type=ITEM_ASPECT_EVENT,
                client_id=str(self.client_id),
                item_ids=item_ids
            )

    def handler_response_detail(self, response_data, **kwargs):
        try:
            del response_data['meta']['jwt_token']
        except Exception as ex:
            logger.error(ex)
        return response_data

    def handler_validated_data(self, lib_import_id: str, validated_data: dict, **kwargs):
        validated_data = super().handler_validated_data(lib_import_id, validated_data, **kwargs)
        try:
            est_shipping_cost = validated_data.get('estimated_shipping_cost')
            est_drop_ship_cost = validated_data.get('estimated_dropship_cost')
            validated_data.update({"est_shipping_cost": est_shipping_cost, "est_drop_ship_cost": est_drop_ship_cost})
        except Exception as ex:
            pass
        return validated_data

    @property
    def regex_pattern_map_config(self):
        return {
            'estimated_shipping_cost': ['estimated shipping cost', 'est. ship cost of one unit'],
            'estimated_dropship_cost': [f'(estimated drop shipping cost|estimated dropship cost)',
                                        'est. drop ship cost of one package'],
            'effective_start_date': ['effective start date'],
            'effective_end_date': ['effective end date'],
        }
