from abc import ABC
from app.financial.import_template.base_custom_module import BaseCustomModule
from app.financial.models import HighChartMapping
from app.financial.permissions.base import JwtTokenPermission
from app.financial.sub_serializers.high_chart_mapping_serializer import HighChartMappingSerializer


class HighChartMappingModule(BaseCustomModule, ABC):
    __NAME__ = 'HighChartMappingModule'
    __MODEL__ = HighChartMapping
    __LABEL__ = 'High Chart Mappings'
    __SERIALIZER_CLASS__ = HighChartMappingSerializer
    __PERMISSION_CLASS__ = [JwtTokenPermission]
