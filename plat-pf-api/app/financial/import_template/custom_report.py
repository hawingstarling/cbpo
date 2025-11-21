from abc import ABC
from app.financial.import_template.base_custom_module import BaseCustomModule
from app.financial.models import SaleItem as SaleItemModel
from app.financial.permissions.base import JwtTokenPermission
from app.financial.sub_serializers.sale_item_import_serializer import ClientSaleItemsImportSerializer


class SaleItemCustomReport(BaseCustomModule, ABC):
    __NAME__ = 'SaleItemCustomReport'
    __MODEL__ = SaleItemModel
    __LABEL__ = 'Sales Custom Reports'
    __SERIALIZER_CLASS__ = ClientSaleItemsImportSerializer
    __PERMISSION_CLASS__ = [JwtTokenPermission]

    def validate_request_api_view(self, request, *args, **kwargs):
        pass
