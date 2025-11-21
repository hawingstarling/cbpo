import copy
import logging
import maya
from app.financial.import_template.custom_report import SaleItemCustomReport
from app.financial.models import SaleItem
from app.financial.services.sale_item_bulk.custom_report_type.base import BaseCustomReportModuleService
from app.financial.sub_serializers.client_sale_item_log import SaleItemLogSerializer, ClientSaleLogSerializer
from app.financial.sub_serializers.sale_item_bulk_edit_serializer import ClientSaleItemBulkEditSerializer

logger = logging.getLogger(__name__)


class SaleItemCustomReportModuleService(BaseCustomReportModuleService):
    module = SaleItemCustomReport
    serializer_class = ClientSaleItemBulkEditSerializer
    model = SaleItem

    def __init__(self, bulk_id: str = None, jwt_token: str = None, user_id: str = None, client_id: str = None):
        super().__init__(bulk_id=bulk_id, jwt_token=jwt_token, user_id=user_id, client_id=client_id)

    def get_columns_export(self):
        column_request = self.bulk.meta.get('custom_report_columns')
        column_module = self.module().columns
        if column_request:
            columns = {}
            for item in column_request:
                if item['name'].startswith('item_'):
                    item['name'] = item['name'].replace('item_', '')
                if item['name'] == 'channel_id':
                    item['name'] = 'channel_sale_id'
                if item['name'] == 'channel_name':
                    item['name'] = 'channel'
                columns.update({item['name']: item['alias']})
        else:
            columns = {item['name']: item['label'] for item in column_module}
        self.columns_as_type = {item['name']: item['type'] for item in column_module if
                                item['name'] in list(columns.keys())}
        return columns

    def _process_data_item(self, instance, validated_data, export_data, **kwargs):
        #
        sale_item_calculated = copy.deepcopy(instance)
        sale_calculated = copy.deepcopy(instance.sale)
        for attr, value in validated_data.items():
            if attr.endswith("_variant"):
                attr = attr.replace("_variant", "")
            if attr in self.fields_sale_item_accept:
                setattr(sale_item_calculated, attr, value)
            else:
                setattr(sale_calculated, attr, value)
        sale_item_values = SaleItemLogSerializer(sale_item_calculated).log_data
        total_cost = sale_item_calculated.total_cost
        total_charged = sale_item_calculated.total_charged
        profit = sale_item_calculated.profit
        margin = sale_item_calculated.margin
        sale_values = ClientSaleLogSerializer(sale_calculated).log_data
        data_values = {**sale_values, **sale_item_values, 'total_cost': total_cost,
                       'total_charged': total_charged, 'profit': profit, 'margin': margin}
        data = {}
        for key in self.custom_report_columns_mapping:
            _type = self.columns_as_type.get(key, "string")
            val = data_values.get(key)
            if _type in ["datetime"] and val:
                val = maya.parse(val).datetime().astimezone(self.timezone).strftime("%m/%d/%Y %H:%M:%S")
            data.update({key: val})
        export_data.append(data)
