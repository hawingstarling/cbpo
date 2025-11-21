from abc import ABC
from app.financial.import_template.base_custom_module import BaseCustomModule
from app.financial.models import SaleItem as SaleItemModel
from app.financial.permissions.base import JwtTokenPermission
from app.financial.sub_serializers.sale_item_import_serializer import ClientSaleItemsImportSerializer


class SaleItemBulkEdit(BaseCustomModule, ABC):
    __NAME__ = 'SaleItemBulkEdit'
    __MODEL__ = SaleItemModel
    __LABEL__ = 'Sales Bulk Edit'
    __SERIALIZER_CLASS__ = ClientSaleItemsImportSerializer
    __PERMISSION_CLASS__ = [JwtTokenPermission]
