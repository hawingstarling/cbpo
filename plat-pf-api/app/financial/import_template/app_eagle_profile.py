import logging
from abc import ABC
from app.financial.import_template.base_custom_module import BaseCustomModule
from app.financial.models import AppEagleProfile
from app.financial.permissions.base import JwtTokenPermission
from app.financial.services.activity import ActivityService
from app.financial.sub_serializers.app_eagle_profile_serializer import AppEagleProfileImportSerializer

logger = logging.getLogger(__name__)


class AppEagleProfileModule(BaseCustomModule, ABC):
    __NAME__ = 'AppEagleProfileModule'
    __MODEL__ = AppEagleProfile
    __LABEL__ = 'Repricing'
    __SERIALIZER_CLASS__ = AppEagleProfileImportSerializer
    __PERMISSION_CLASS__ = [JwtTokenPermission]
    __TEMPLATE_VERSION__ = '1.1'
    __TEMPLATE_NUMBER_RECORD__ = 3

    @property
    def data_sample(self):
        profile_ids = ['10000', '20000', '30000']
        profile_names = ['Danner MAP With 20% Min Profit', 'NEW SUPPLIER PROFILE ID', 'Scully NO MAP- Min 15% Profit']

        return {
            'profile_id': profile_ids,
            'profile_name': profile_names
        }

    def process(self, lib_import_id: str, **kwargs) -> any:
        super().process(lib_import_id, **kwargs)
        ActivityService(client_id=self.client_id, user_id=self.user_id).create_activity_import_app_eagle_profile()
