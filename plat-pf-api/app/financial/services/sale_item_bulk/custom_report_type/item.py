import logging
import maya
from app.financial.import_template.custom_report import SaleItemCustomReport
from app.financial.models import Item
from app.financial.services.item.utils import get_query_set_filter_items
from app.financial.services.sale_item_bulk.custom_report_type.base import BaseCustomReportModuleService
from app.financial.sub_serializers.sale_item_bulk_edit_serializer import ClientSaleItemBulkEditSerializer

logger = logging.getLogger(__name__)


class ItemCustomReportModuleService(BaseCustomReportModuleService):
    module = SaleItemCustomReport
    serializer_class = ClientSaleItemBulkEditSerializer
    model = Item

    def __init__(self, bulk_id: str = None, jwt_token: str = None, user_id: str = None, client_id: str = None):
        super().__init__(bulk_id=bulk_id, jwt_token=jwt_token,
                         user_id=user_id, client_id=client_id)

    def get_columns_export(self):
        columns = {
            'sku': 'SKU',
            'upc': 'UPC',
            'asin': 'ASIN',
            'cog': 'COG',
            'title': 'Title',
            'fulfillment_type': 'Fulfillment Type',
            'brand': 'Brand',
            'channel': 'Channel',
            'size': 'Size',
            'style': 'Style',
            'est_shipping_cost': 'Estimated Shipping Cost',
            'est_drop_ship_cost': 'Estimated Dropship Cost',
            'effect_start_date': 'Effective Start Date',
            'effect_end_date': 'Effective End Date',
            'description': 'Description',
            'product_number': 'Product Number',
            'product_type': 'Product Type',
            'parent_asin': 'Parent ASIN'
        }
        self.columns_as_type = {
            'sku': 'string',
            'upc': 'string',
            'asin': 'string',
            'cog': 'number',
            'title': 'string',
            'fulfillment_type': 'string',
            'brand': 'string',
            'channel': 'string',
            'size': 'string',
            'style': 'string',
            'est_shipping_cost': 'number',
            'est_drop_ship_cost': 'number',
            'effect_start_date': 'datetime',
            'effect_end_date': 'datetime',
            'description': 'string',
            'product_number': 'string',
            'product_type': 'string',
            'parent_asin': 'string'
        }
        return columns

    def get_total_ids(self):
        channel_id = self.update_operations.get('channel_id', {}).get('value', None)
        brand_id = self.update_operations.get('brand_id', {}).get('value', None)
        keyword = self.update_operations.get('keyword', {}).get('value', None)
        queryset = get_query_set_filter_items(client_id=self.client_id, ids=self.ids, channel_id=channel_id,
                                              brand_id=brand_id, sort_field='created', sort_direction='desc',
                                              keyword=keyword)
        meta_data = list(queryset.values_list('sku', flat=True)[:10])
        self._update_meta_custom_report(meta_data)
        total_ids = queryset.values_list('id', flat=True)

        return list(total_ids)

    def _get_instances(self, ids, **kwargs):
        self.instance_ids = ids
        return self.model.objects.tenant_db_for(self.client_id) \
            .filter(id__in=self.instance_ids, client__id=self.client_id).order_by('created')

    def _validate_update_data(self, instance, **kwargs):
        return self.serializer_class(), [], {}

    def _validate_data_context(self, instance, raw_ins):
        return True, {}

    def _process_data_item(self, instance: Item, validated_data, export_data, **kwargs):
        channel = instance.channel.name if instance.channel is not None else None
        brand = instance.brand.name if instance.brand is not None else None
        ff = instance.fulfillment_type.name if instance.fulfillment_type is not None else None
        size = instance.size.value if instance.size is not None else None
        style = instance.style.value if instance.style is not None else None
        #
        item_cogs = instance.itemcog_set.tenant_db_for(self.client_id).order_by('created')
        for item_cog in item_cogs:
            try:
                data_values = {
                    'sku': instance.sku,
                    'upc': instance.upc,
                    'asin': instance.asin,
                    'cog': item_cog.cog,
                    'title': instance.title,
                    'fulfillment_type': ff,
                    'brand': brand,
                    'channel': channel,
                    'size': size,
                    'style': style,
                    'est_shipping_cost': instance.est_shipping_cost,
                    'est_drop_ship_cost': instance.est_drop_ship_cost,
                    'effect_start_date': item_cog.effect_start_date,
                    'effect_end_date': item_cog.effect_end_date,
                    'description': instance.description,
                    'product_number': instance.product_number,
                    'product_type': instance.product_type,
                    'parent_asin': instance.parent_asin
                }
                data = {}
                for key in self.custom_report_columns_mapping:
                    _type = self.columns_as_type.get(key, "string")
                    val = data_values.get(key)
                    if _type in ["datetime"] and val:
                        val = maya.parse(val).datetime().astimezone(self.timezone).strftime("%m/%d/%Y %H:%M:%S")
                    data.update({key: val})
                export_data.append(data)
            except Exception as ex:
                logger.error(f"[{self.__class__.__name__}][_process_data_item][{instance.pk}] {ex}")
