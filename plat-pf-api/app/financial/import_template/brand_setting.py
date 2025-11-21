import logging
from app.financial.import_template.base_custom_module import BaseCustomModule
from app.financial.models import Brand, BrandSetting
from app.financial.permissions.base import JwtTokenPermission
from app.financial.sub_serializers.brand_setting_serializers import BrandSettingImportSerializer
from app.financial.variable.brand_setting import MFN_DROP_SHIP, MFN_RAPID_ACCESS, MFN_STANDARD, PO_DROPSHIP_METHOD_LIST

logger = logging.getLogger(__name__)


class BrandSettingModule(BaseCustomModule):
    __NAME__ = 'BrandSettingModule'
    __MODEL__ = BrandSetting
    __LABEL__ = 'Brand Settings'
    __SERIALIZER_CLASS__ = BrandSettingImportSerializer
    __PERMISSION_CLASS__ = [JwtTokenPermission]
    __TEMPLATE_VERSION__ = '1.4'

    @property
    def data_sample(self):
        channel = ['amazon.com', 'amazon.ca', 'shopify.com']
        brand_name = Brand.objects.all().values_list('name', flat=True).distinct()
        mfn_formula = [MFN_DROP_SHIP, MFN_RAPID_ACCESS, MFN_STANDARD, '']
        segment = ['Outdoor', 'Active']
        return {
            'channel': channel,
            'brand': brand_name,
            'mfn_formula': mfn_formula,
            'segment': segment,
            'po_dropship_method': PO_DROPSHIP_METHOD_LIST,
            'add_user_provided_method': PO_DROPSHIP_METHOD_LIST,
        }

    def handler_validated_data(self, lib_import_id: str, validated_data: dict, **kwargs):
        validated_data = super().handler_validated_data(lib_import_id, validated_data, **kwargs)
        return validated_data

    def filter_instance(self, lib_import_id: str, validated_data, **kwargs):
        return {
            'client_id': validated_data['client_id'],
            'brand': validated_data['brand'],
            'channel': validated_data['channel']
        }

    def keys_raw_map_config(self, lib_import_id: str, validated_data, **kwargs):
        return {
            'key_map': ['brand', 'channel']
        }
