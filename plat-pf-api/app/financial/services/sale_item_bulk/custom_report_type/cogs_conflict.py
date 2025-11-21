import logging

from app.extensiv.models import COGSConflict
from app.financial.import_template.custom_report import SaleItemCustomReport
from app.financial.services.sale_item_bulk.custom_report_type.base import BaseCustomReportModuleService
from app.extensiv.utils import get_query_set_filter_cogs_conflict
from app.financial.sub_serializers.sale_item_bulk_edit_serializer import ClientSaleItemBulkEditSerializer

logger = logging.getLogger(__name__)


class COGSConflictCustomReportModuleService(BaseCustomReportModuleService):
    module = SaleItemCustomReport
    serializer_class = ClientSaleItemBulkEditSerializer
    model = COGSConflict

    def get_columns_export(self):
        columns = {
            'sku': 'SKU',
            'sale_ids': 'Sale IDs',
            'extensiv_cog': 'Extensiv COG',
            'dc_cog': 'Data Central COG',
            'pf_cog': 'PF COG',
            'used_cog': 'Used COG',
            'status': 'Status',
            'note': 'Notes',
        }
        self.columns_as_type = {
            'sku': 'string',
            'sale_ids': 'string',
            'extensiv_cog': 'string',
            'dc_cog': 'string',
            'pf_cog': 'string',
            'used_cog': 'string',
            'status': 'string',
            'note': 'string'
        }
        return columns

    def get_total_ids(self):
        channel = self.update_operations.get(
            'channel', {}).get('value', None)
        keyword = self.update_operations.get('keyword', {}).get('value', None)
        used_cog = self.update_operations.get(
            'used_cog', {}).get('value', None)
        status = self.update_operations.get('status', {}).get('value', None)
        all_data = self.update_operations.get('all', {}).get('value', None)
        if all_data:
            queryset = get_query_set_filter_cogs_conflict(client_id=self.client_id, sort_field='created',
                                                          sort_direction='desc')
        else:
            queryset = get_query_set_filter_cogs_conflict(client_id=self.client_id, ids=self.ids, channel=channel,
                                                          used_cog=used_cog, status=status,
                                                          sort_field='created', sort_direction='desc', keyword=keyword)
        meta_data = list(queryset.values_list('sku', flat=True)[:10])
        self._update_meta_custom_report(meta_data)
        total_ids = queryset.values_list('id', flat=True)

        return list(total_ids)

    def _get_instances(self, ids, **kwargs):
        self.instance_ids = ids
        return self.model.objects.tenant_db_for(self.client_id) \
            .filter(id__in=self.instance_ids, client__id=self.client_id).order_by('-created')

    def _validate_update_data(self, instance, **kwargs):
        return self.serializer_class(), [], {}

    def _validate_data_context(self, instance, raw_ins):
        return True, {}

    def _process_data_item(self, instance: COGSConflict, validated_data, export_data, **kwargs):
        try:
            # channel = getattr(instance, "channel").name if hasattr(instance, "channel") else None
            data = {
                'sku': instance.sku,
                'sale_ids': instance.sale_ids[0],
                'extensiv_cog': instance.extensiv_cog,
                'dc_cog': instance.dc_cog,
                'pf_cog': instance.pf_cog,
                'used_cog': instance.used_cog,
                'status': instance.status,
                'note': instance.note,
            }
            export_data.append(data)
        except Exception as ex:
            logger.error(
                f"[{self.__class__.__name__}][_process_data_item][{instance.pk}] {ex}")
