import logging
from abc import ABC
from datetime import datetime
from app.core.services.authentication_service import AuthenticationService
from plat_import_lib_api.models import DataImportTemporary, STATUS_CHOICE
from app.financial.sub_serializers.sale_item_import_serializer import ClientSaleItemsImportSerializer
from app.financial.variable.profit_status_static_variable import PROFIT_STATUS
from app.financial.variable.sale_status_static_variable import SALE_STATUS
from .base_custom_module import BaseCustomModule
from ..jobs.imports import create_activity_import_sale_data
from ..models import Brand, SaleItem as SaleItemModel
from ..permissions.base import JwtTokenPermission
from ..services.import_validation import ImportValidationManage
from ..services.imports import ImportDataModuleService
from app.financial.services.utils.common import round_currency
from ..variable.shipping_cost_source import SHIP_CARRIER_FEDEX, SHIP_CARRIER_UPS, SHIP_CARRIER_USPS

logger = logging.getLogger(__name__)


class SaleItem(BaseCustomModule, ABC):
    __NAME__ = 'SaleItem'
    __MODEL__ = SaleItemModel
    __LABEL__ = 'Sales'
    __SERIALIZER_CLASS__ = ClientSaleItemsImportSerializer
    __PERMISSION_CLASS__ = [JwtTokenPermission]

    __TEMPLATE_VERSION__ = '3.6'  # version of file template in google cloud storage
    __TEMPLATE_NUMBER_RECORD__ = 3

    @property
    def data_sample(self):
        channel_sale_id = ['RYY-021-QZ88', 'KKQ-801-XU00', 'LFU-902-TW04']
        channel = ['amazon.com']
        country = ['USA']
        customer_name = ['Jess']
        recipient_name = ['Jessica']
        address_line_1 = ['590 TREETOP LN']
        address_line_2 = ['1130 BROADWAY ST']
        address_line_3 = ['1991 HIGH DR']
        state = ['California', 'Arizona', 'New York']
        city = ['Los Angeles', 'Phoenix', 'New York City']
        postal_code = ['4647-48841', '5523-03764', '7318-90743']
        brand = Brand.objects.all().values_list('name', flat=True).distinct()
        upc = ['1267510478100', '988469606956', '472796568472']
        sku = ['NT_80-91155_5-E', 'TA_34-01004_1-Z', 'YD_89-53434_0-W']
        asin = ['GOKUJV4O9H', 'JJMMLATTXN', 'FNWR8KU1ET']
        fulfillment_type = ['FBA', 'MFN']
        sale_status = [item[0][0] for item in SALE_STATUS]
        profit_status = [item[0][0] for item in PROFIT_STATUS]
        cog = [10]
        unit_cog = [5]
        ship_date = [datetime(2021, 1, 7, 3, 15)]
        sale_date = [datetime(2021, 1, 7, 3, 15)]
        quantity = [2]
        shipping_cost_accuracy = [100]
        sale_charged_accuracy = [100]
        freight_cost_accuracy = [100]
        channel_listing_fee_accuracy = [100]
        channel_tax_withheld_accuracy = [100]
        tracking_fedex_id = ['1234567890']
        ship_carrier = [SHIP_CARRIER_USPS, SHIP_CARRIER_FEDEX, SHIP_CARRIER_UPS]
        label_cost = [1.0]
        return {
            'channel_sale_id': channel_sale_id,
            'channel': channel,
            'country': country,
            'customer_name': customer_name,
            'recipient_name': recipient_name,
            'address_line_1': address_line_1,
            'address_line_2': address_line_2,
            'address_line_3': address_line_3,
            'state': state,
            'city': city,
            'postal_code': postal_code,
            'brand': brand,
            'upc': upc,
            'sku': sku,
            'asin': asin,
            'fulfillment_type': fulfillment_type,
            'sale_status': sale_status,
            'profit_status': profit_status,
            'cog': cog,
            'unit_cog': unit_cog,
            'ship_date': ship_date,
            'sale_date': sale_date,
            'quantity': quantity,
            'shipping_cost_accuracy': shipping_cost_accuracy,
            'sale_charged_accuracy': sale_charged_accuracy,
            'channel_listing_fee_accuracy': channel_listing_fee_accuracy,
            'inbound_freight_cost_accuracy': freight_cost_accuracy,
            'outbound_freight_cost_accuracy': freight_cost_accuracy,
            'channel_tax_withheld_accuracy': channel_tax_withheld_accuracy,
            'tracking_fedex_id': tracking_fedex_id,
            'ship_carrier': ship_carrier,
            'label_cost': label_cost
        }

    def handler_validate_row(self, lib_import_id: str, validated_data: dict, row: dict, map_config: list, errors: dict,
                             data_request: dict, **kwargs):

        # Calculate between column cog and unit cog
        self.__process_validate_cog_and_unit_cog(validated_data=validated_data, row=row, map_config=map_config,
                                                 errors=errors, data_request=data_request, **kwargs)

    def __handler_get_data_request_cog_and_unit_cog(self, data_request: dict):
        # Calculate between column cog and unit cog
        quantity = data_request.get('quantity', None)
        cog = data_request.get('cog', None)
        unit_cog = data_request.get('unit_cog', None)

        if quantity is None:
            quantity = 1
        return cog, unit_cog, quantity

    def __process_validate_cog_and_unit_cog(self, validated_data: dict, row: dict, map_config: list, errors: dict,
                                            data_request: dict, **kwargs):
        # Calculate between column cog and unit cog
        if not validated_data:
            cog, unit_cog, quantity = self.__handler_get_data_request_cog_and_unit_cog(data_request)
        else:
            cog, unit_cog, quantity = self.__handler_get_data_request_cog_and_unit_cog(validated_data)

        if not cog and not unit_cog:
            return

        # check total amount is valid
        if cog and unit_cog:
            self.__check_sum_cog(cog, unit_cog, quantity, map_config, errors, **kwargs)
        else:
            # calculate cog or unit cog 
            self.__calculate_cog_or_unit_cog(cog, unit_cog, quantity, row, map_config, data_request, **kwargs)

    def __check_sum_cog(self, cog: float, unit_cog: float, quantity: int, map_config: list, errors: dict, **kwargs):
        try:
            cog = float(cog)
            quantity = int(quantity)
            unit_cog = float(unit_cog)

            _validate = cog == quantity * unit_cog

            # round next cent
            if not _validate:
                exist_cog_msg = False

                for key in errors:
                    if key == 'cog':
                        errors[key].append('COG is invalid')
                        exist_cog_msg = True

                if not exist_cog_msg:
                    errors.update({'cog': ['COG is invalid']})

            # logger.info(f'[{self.__class__.__name__}][handler_row_validate][{column_update}] amount = {amount} ; map_config : {map_config}')
        except Exception as ex:
            logger.error(f'[{self.__class__.__name__}][handler_row_validate][check_sum_cog] : {ex}')

    def __calculate_cog_or_unit_cog(self, cog: float, unit_cog: float, quantity: int, row: dict, map_config: list,
                                    data_request: dict, **kwargs):
        try:
            if cog:
                column_update = 'unit_cog'
                cog = float(cog)
                quantity = int(quantity)
                amount = cog / quantity
            else:
                column_update = 'cog'
                unit_cog = float(unit_cog)
                quantity = int(quantity)
                amount = unit_cog * quantity

            # round next cent
            amount = round_currency(amount)

            # add column calculate for map config show data
            for item in map_config:
                if item['target_col'] == column_update:
                    if not item['upload_col']:
                        item['upload_col'] = column_update
                    row.update({item['upload_col']: amount})
            #
            data_request.update({column_update: amount})
            # logger.info(f'[{self.__class__.__name__}][handler_row_validate][{column_update}] amount = {amount} ; map_config : {map_config}')
        except Exception as ex:
            logger.error(f'[{self.__class__.__name__}][handler_row_validate][calculate_cog_or_unit_cog] : {ex}')

    def validate(self, lib_import_id: str, map_config_request: list, **kwargs) -> any:
        self.load_queue_environment(**kwargs)
        super().validate(lib_import_id, map_config_request, **kwargs)
        # validate total import
        validation_manage = ImportValidationManage(import_id=lib_import_id)
        validation_manage.exec()

    def process(self, lib_import_id: str, **kwargs) -> any:
        self.load_queue_environment(**kwargs)

        import_data_module_obj = ImportDataModuleService(jwt_token=self.jwt_token, import_file_id=lib_import_id,
                                                         user_id=self.user_id, client_id=self.client_id, mode='merge')
        import_data_module_obj.process_file_import()
        #
        # add celery task for make file import to gcloud and update status temp file
        lib_import = DataImportTemporary.objects.get(id=lib_import_id)
        if lib_import.status == STATUS_CHOICE[5][0] and lib_import.progress == 100:
            create_activity_import_sale_data(client_id=self.client_id, user_id=self.user_id)

    @property
    def regex_pattern_map_config(self):
        return {
            'channel': ['^Channel$'],
            'cog': ['^COG$', '(COG|Total Items Cost)'],
            'shipping_charged': ['^Shipping Charged$', '(Shipping Charged|Additional Shipping Charged)'],
            'product_number': [
                '^Style Number$',
                '(Style No.|Material No.|Style Number|Product|Product Number|Product ID)'
            ],
            'product_type': ['^Style Category$', '(Product Type|Product Category)'],
        }

    def validate_request_api_view(self, request, *args, **kwargs):
        pass

    def handler_response_detail(self, response_data, **kwargs):
        try:
            del response_data['meta']['jwt_token']
        except Exception as ex:
            logger.error(ex)
        return response_data

    def keys_raw_map_config(self, lib_import_id: str, validated_data, **kwargs):
        return {
            'key_map': ['channel_sale_id', 'channel', 'sku'],
            'parent_key_map': ['channel_sale_id', 'channel'],
        }

    def setup_metadata(self, meta, context_serializer, **kwargs):
        _meta = super(SaleItem, self).setup_metadata(meta, context_serializer, **kwargs)
        _jwt_token = _meta.get("jwt_token")
        if _jwt_token:
            payload = AuthenticationService.verify_jwt_token_signature(_jwt_token, verify=False)
            _meta.update({"username": payload.get("username", None)})
        return _meta
