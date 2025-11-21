import logging
from app.financial.import_template.custom_report import SaleItemCustomReport
from app.financial.models import TopClientASINs
from app.financial.services.sale_item_bulk.custom_report_type.base import BaseCustomReportModuleService
from app.financial.services.top_asins.utils import get_query_set_filter_top_asins
from app.financial.sub_serializers.sale_item_bulk_edit_serializer import ClientSaleItemBulkEditSerializer

logger = logging.getLogger(__name__)


class TopASINsCustomReportModuleService(BaseCustomReportModuleService):
    module = SaleItemCustomReport
    serializer_class = ClientSaleItemBulkEditSerializer
    model = TopClientASINs

    def get_columns_export(self):
        columns = {
            'channel': 'Channel',
            'parent_asin': 'Parent ASIN',
            'child_asin': 'Child ASIN',
            'segment': 'Segment',
        }
        self.columns_as_type = {
            'channel': 'string',
            'parent_asin': 'string',
            'child_asin': 'string',
            'segment': 'string'
        }
        return columns

    def get_total_ids(self):
        channel_id = self.update_operations.get('channel_id', {}).get('value', None)
        keyword = self.update_operations.get('keyword', {}).get('value', None)
        all_data = self.update_operations.get('all', {}).get('value', None)
        if all_data:
            queryset = get_query_set_filter_top_asins(client_id=self.client_id, sort_field='created',
                                                      sort_direction='desc')
        else:
            queryset = get_query_set_filter_top_asins(client_id=self.client_id, ids=self.ids, channel_id=channel_id,
                                                      sort_field='created', sort_direction='desc', keyword=keyword)
        meta_data = list(queryset.values_list('parent_asin', flat=True)[:10])
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

    def _process_data_item(self, instance: TopClientASINs, validated_data, export_data, **kwargs):
        try:
            channel = instance.channel.name if instance.channel is not None else None
            data = {
                'channel': channel,
                'parent_asin': instance.parent_asin,
                'child_asin': instance.child_asin,
                'segment': instance.segment
            }
            export_data.append(data)
        except Exception as ex:
            logger.error(f"[{self.__class__.__name__}][_process_data_item][{instance.pk}] {ex}")
