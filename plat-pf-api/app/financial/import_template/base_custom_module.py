import json
from abc import ABC
import logging
from django.db.utils import DEFAULT_DB_ALIAS
from plat_import_lib_api.services.files.utils import generate_url_sample, generate_file_sample

from app.financial.models import ClientPortal, User
from plat_import_lib_api.services.modules.base import BaseModule
from app.core.context import AppContext
from app.database.helper import get_connection_workspace

logger = logging.getLogger(__name__)


class BaseCustomModule(BaseModule, ABC):
    __VERIFY_RAW_IGNORE__ = True
    __MODULE_TEMPLATE_NAME__ = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.client_id = None
        self.user_id = None
        self.jwt_token = None
        self.client_db = DEFAULT_DB_ALIAS

    @property
    def template(self):
        module = self.__MODULE_TEMPLATE_NAME__
        if module is None:
            module = self.__NAME__
        url, exist = generate_url_sample(module, self.__TEMPLATE_VERSION__)
        if not exist:
            generate_file_sample(
                module,
                self.target_cols,
                self.__TEMPLATE_VERSION__,
                self.__TEMPLATE_NUMBER_RECORD__,
                self.data_sample)

        return url

    def validate_request_api_view(self, request, *args, **kwargs):
        pass

    @classmethod
    def setup_metadata_username(self, meta, context_serializer, **kwargs):
        try:
            meta_payload = json.loads(context_serializer.get('request').data['meta'])
            username = User.objects.tenant_db_for(meta_payload['client_id']).get(pk=meta['user_id']).username
            meta.update({'username': username})
        except Exception as ex:
            pass

    def setup_metadata(self, meta, context_serializer, **kwargs):
        context = AppContext.instance()
        kwargs.update({'user_id': str(context.user_id), 'jwt_token': str(context.jwt_token)})
        meta = super().setup_metadata(meta, context_serializer, **kwargs)
        self.load_queue_environment(**kwargs)
        #
        self.setup_metadata_username(meta, context_serializer, **kwargs)
        return meta

    def load_queue_environment(self, **kwargs):
        try:
            client_id = kwargs['client_id']
            user_id = kwargs['user_id']
            jwt_token = kwargs['jwt_token']
            self.client_id = client_id
            self.user_id = user_id
            self.jwt_token = jwt_token
            self.client_db = get_connection_workspace(self.client_id)
            #
            context = AppContext.instance()
            context.user_id = self.user_id
            context.client_id = self.client_id
            context.jwt_token = self.jwt_token
        except Exception as ex:
            pass

    def validate(self, lib_import_id: str, map_config_request: list, **kwargs) -> any:
        self.load_queue_environment(**kwargs)
        super().validate(lib_import_id, map_config_request, **kwargs)

    def process(self, lib_import_id: str, **kwargs) -> any:
        self.load_queue_environment(**kwargs)
        super().process(lib_import_id, **kwargs)

    def handler_validated_data(self, lib_import_id: str, validated_data: dict, **kwargs):
        self.load_queue_environment(**kwargs)
        self.client_id = kwargs['client_id']
        validated_data['client_id'] = self.client_id
        validated_data['client'] = ClientPortal.objects.tenant_db_for(self.client_id).get(pk=self.client_id)
        return validated_data

    def make_instance(self, lib_import_id: str, validated_data: dict, **kwargs):
        self.load_queue_environment(**kwargs)
        return super().make_instance(lib_import_id, validated_data, **kwargs)

    def bulk_process(self, lib_import_id: str, bulk_insert: list, bulk_update: list, **kwargs):
        self.load_queue_environment(**kwargs)
        super().bulk_process(lib_import_id, bulk_insert, bulk_update, **kwargs)

    @property
    def model_objects(self):
        model_objects = super().model_objects
        return model_objects.tenant_db_for(self.client_id)
