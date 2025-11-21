from abc import ABC
from app.financial.import_template.base_custom_module import BaseCustomModule
from app.financial.models import SaleItem as SaleItemModel
from app.financial.permissions.base import JwtTokenPermission
from app.financial.sub_serializers.client_serializer import ClientSaleItemSerializer


class SaleItemBulkSync(BaseCustomModule, ABC):
    __NAME__ = 'SaleItemBulkSync'
    __MODEL__ = SaleItemModel
    __LABEL__ = 'Sales Bulk Sync'
    __TEMPLATE_URL__ = None
    __SERIALIZER_CLASS__ = ClientSaleItemSerializer
    __PERMISSION_CLASS__ = [JwtTokenPermission]
