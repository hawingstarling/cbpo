import logging
from abc import ABC
from plat_import_lib_api.static_variable.raw_data_import import RAW_DELETED_TYPE, RAW_IGNORED_TYPE

from app.financial.import_template.base_custom_module import BaseCustomModule
from app.financial.models import TopClientASINs as TopClientASINsModel
from app.financial.permissions.base import JwtTokenPermission
from app.financial.services.activity import ActivityService
from app.financial.sub_serializers.top_asins_serializer import TopASINsImportSerializer
from app.financial.variable.activity_variable import IMPORT_TOP_ASINS_DATA_KEY, IMPORT_DELETE_TOP_ASINS_DATA_KEY

logger = logging.getLogger(__name__)


class TopASINs(BaseCustomModule, ABC):
    __NAME__ = 'TopASINs'
    __MODEL__ = TopClientASINsModel
    __LABEL__ = 'TopASINs'
    __SERIALIZER_CLASS__ = TopASINsImportSerializer
    __PERMISSION_CLASS__ = [JwtTokenPermission]
    __TEMPLATE_VERSION__ = '1.1'
    __TEMPLATE_NUMBER_RECORD__ = 3
    __ACTION__ = IMPORT_TOP_ASINS_DATA_KEY

    @property
    def data_sample(self):
        channel = ['amazon.com']
        parent_asin = ["HYTDCV94ND", "89GCDFRESN", "HFDESCMKHI"]
        child_asin = ["IVOSDK9C2P", "5DQVP9DQ1D", "GVQAQ5VFVO"]
        segment = ["Active", "Outdoor", "Style"]
        return {
            'channel': channel,
            'parent_asin': parent_asin,
            'child_asin': child_asin,
            'segment': segment
        }

    def process(self, lib_import_id: str, **kwargs) -> any:
        super().process(lib_import_id, **kwargs)
        ActivityService(client_id=self.client_id, user_id=self.user_id).create_activity_by_action(
            action=self.__ACTION__, client_id=self.client_id, module=self.__LABEL__)

    def filter_instance(self, lib_import_id: str, validated_data, **kwargs):
        client_id = kwargs['client_id']
        return {
            'client_id': client_id,
            'channel': validated_data['channel'],
            'parent_asin': validated_data['parent_asin'],
            'child_asin': validated_data['child_asin']
        }

    def keys_raw_map_config(self, lib_import_id: str, validated_data, **kwargs):
        return {
            'key_map': ['channel', 'parent_asin', 'child_asin']
        }


class TopASINsDelete(TopASINs):
    __NAME__ = 'TopASINsDelete'
    __MODEL__ = TopClientASINsModel
    __LABEL__ = 'TopASINsDelete'
    __ACTION__ = IMPORT_DELETE_TOP_ASINS_DATA_KEY
    __VERIFY_RAW_DELETE__ = True

    def bulk_process(self, lib_import_id: str, bulk_insert: list, bulk_update: list, **kwargs):
        """
        process insert or update data per chunk list data step process
        """
        self.load_queue_environment(**kwargs)
        # handler pre bulk process
        self.handler_bulk_process(lib_import_id, bulk_insert, bulk_update, **kwargs)
        ids_deleted = [obj.pk for obj in bulk_update]
        self.model_objects.filter(pk__in=ids_deleted).delete()

    def handler_verify_raw_process_ignore(self, raw_instance, instance_model_target, created: bool):
        try:
            assert self.instance_model_origin is None and created is True, "Raw is not accept ignore"
            raw_instance.type = RAW_IGNORED_TYPE
        except Exception as ex:
            print(f"[{self.__class__.__name__}][handler_verify_raw_process_ignore] {ex}")

    def handler_verify_raw_process_delete(self, raw_instance, instance_model_target, created: bool):
        try:
            # compare data row instance origin & target => set type ignore for raw data temp
            assert self.instance_model_origin is not None and not created, "Raw is not accept delete"
            raw_instance.type = RAW_DELETED_TYPE
        except Exception as ex:
            print(f"[{self.__class__.__name__}][handler_verify_raw_process_delete] {ex}")
