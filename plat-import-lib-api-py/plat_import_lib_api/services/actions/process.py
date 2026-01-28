import json
import logging
import time
from django.utils import timezone
from .base import LibBaseAction
from ...models import RawDataTemporary, PROCESSED
from ...static_variable.action import PROCESS_ACTION
from ...static_variable.config import plat_import_setting
from ...static_variable.raw_data_import import RAW_UPDATED_TYPE

logger = logging.getLogger(__name__)


class LibProcessAction(LibBaseAction):
    JOB_ACTION = PROCESS_ACTION

    def __init__(self, lib_import_id: str, **kwargs):
        super().__init__(lib_import_id=lib_import_id, **kwargs)

        self.data_import_file = json.loads(self.lib_import.json_data_last_cache)

        self.serializer = self.lib_module.serializer_class

        self.start_time = time.time()

        # bulk process

        self.bulk_config = {}

        self.init_bulk_config()

    def init_bulk_config(self):
        self.bulk_config = {
            'insert': [],
            'update': []
        }

    def process_bulk(self):
        inserts = self.bulk_config['insert']
        updates = self.bulk_config['update']
        self.lib_module.bulk_process(self.lib_import_id, inserts, updates, **self.kwargs)
        self.init_bulk_config()

    def process(self):
        #
        self.update_to_lib_import()
        #
        for instance in self.raws_process_action_queryset:
            # logger.info(f"process raw : {instance.index}")
            self._handler_process_row(instance=instance)
            self.number_process += 1
            self.raws_instances.append(instance)
            if len(self.raws_instances) % plat_import_setting.bulk_process_size == 0:
                self.process_bulk()
                self.update_to_lib_import()
        #
        if len(self.raws_instances) > 0:
            self.process_bulk()
            self.update_to_lib_import()

    def _handler_process_row(self, instance: RawDataTemporary):
        data_request = instance.data_map_config
        raw = instance.data
        #
        validated_data = self.validate_data_request(data_request, raw, instance)
        validated_data = self.lib_module.handler_validated_data(self.lib_import_id, validated_data, **self.kwargs)
        model_instance, created = self.lib_module.make_instance(self.lib_import_id, validated_data, **self.kwargs)
        #
        self._set_status_process_row(instance, model_instance, created)
        self.add_obj_to_bulk(model_instance, created)

    def _set_status_process_row(self, instance, model_instance, created):
        if not created:
            instance.type = RAW_UPDATED_TYPE
        # Handle IGNORED
        if self.lib_module.__VERIFY_RAW_IGNORE__:
            self.lib_module.handler_verify_raw_process_ignore(instance, model_instance, created)
        # Handle DELETED
        if self.lib_module.__VERIFY_RAW_DELETE__:
            self.lib_module.handler_verify_raw_process_delete(instance, model_instance, created)

    def add_obj_to_bulk(self, obj: any, created: bool):
        if created:
            self.bulk_config['insert'].append(obj)
        else:
            self.bulk_config['update'].append(obj)

    def validate_data_request(self, data_request: dict, raw: dict = {}, instance: RawDataTemporary = None, **kwargs):
        if not instance:
            raise NotImplementedError
        validated_data, errors = super().validate_data_request(data_request, **kwargs)
        if len(errors) > 0:
            _error_update = []
            for key in errors:
                msg = self.lib_module.handler_message_error_column_validate(self.lib_import_id, key,
                                                                            data_request.get(key), errors[key],
                                                                            **self.kwargs)
                item = {
                    'code': key,
                    'message': msg
                }
                _error_update.append(item)
            instance.is_complete = False
            instance.processing_errors = _error_update
        else:
            instance.is_complete = True
            instance.processing_errors = []
        instance.status = PROCESSED
        instance.modified = timezone.now()
        #
        return validated_data
