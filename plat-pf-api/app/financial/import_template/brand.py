import logging
from app.financial.import_template.base_custom_module import BaseCustomModule
from app.financial.models import Brand
from app.financial.permissions.base import JwtTokenPermission
from app.financial.sub_serializers.brand_serializer import BrandImportSerializer
logger = logging.getLogger(__name__)


class BrandModule(BaseCustomModule):
    __NAME__ = 'BrandModule'
    __MODEL__ = Brand
    __LABEL__ = 'Brands'
    __SERIALIZER_CLASS__ = BrandImportSerializer
    __PERMISSION_CLASS__ = [JwtTokenPermission]
    __TEMPLATE_VERSION__ = '1.1'

    @property
    def data_sample(self):
        name = ['Adidas', 'The North Face', 'Asics']
        supplier_name = ['cbpo']
        is_obsolete = [False]
        acquired_date = ['2021-01-01 00:00:00']
        # edi = [None]
        return {
            'name': name,
            'supplier_name': supplier_name,
            'acquired_date': acquired_date,
            'is_obsolete': is_obsolete
        }

    def filter_instance(self, lib_import_id: str, validated_data, **kwargs):
        client_id = kwargs['client_id']
        return {
            'client_id': client_id,
            'name': validated_data['name']
        }

    def keys_raw_map_config(self, lib_import_id: str, validated_data, **kwargs):
        return {
            'key_map': ['name']
        }
