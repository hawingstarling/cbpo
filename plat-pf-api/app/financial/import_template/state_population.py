from abc import ABC
from app.financial.import_template.base_custom_module import BaseCustomModule
from app.financial.models import StatePopulation
from app.financial.permissions.base import JwtTokenPermission
from app.financial.sub_serializers.state_population_serializer import StatePopulationSerializer


class StatePopulationModule(BaseCustomModule, ABC):
    __NAME__ = 'StatePopulationModule'
    __MODEL__ = StatePopulation
    __LABEL__ = 'State\'s Population'
    __SERIALIZER_CLASS__ = StatePopulationSerializer
    __PERMISSION_CLASS__ = [JwtTokenPermission]
