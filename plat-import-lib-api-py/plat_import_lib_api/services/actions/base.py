import json
import logging
import hashlib
from django.db.models import Q
from django.utils import timezone
from ..objects.lib_import import LibImportObject
from ...models import DataImportTemporary, VALIDATING, VALIDATED, PROCESSING, PROCESSED, RawDataTemporary
from ..utils.utils import divide_chunks
from ...static_variable.action import UPLOAD_ACTION, VALIDATE_ACTION, PROCESS_ACTION
from ...static_variable.config import plat_import_setting

logger = logging.getLogger(__name__)


class LibBaseAction(LibImportObject):
    JOB_ACTION = None

    def __init__(self, lib_import_id: str, **kwargs):
        super().__init__(lib_import_id=lib_import_id, **kwargs)

        # config for process
        self.progress = 0  # percent process action
        #
        self.raws_process_action_queryset = self._get_raws_process_action_queryset()
        #
        self.raws_instances = []
        #
        self.number_process = self._get_last_number_process()

        self.hash_map_config = hashlib.md5(json.dumps(self.map_config).encode('utf-8')).hexdigest()
        #
        self.total_rows_action = self._get_total_rows_action()
        #
        self.fields_raw_instance_accept = [i.name for i in RawDataTemporary._meta.fields if
                                           i.name not in ['pk', 'id']]

    def validate(self):
        if not self.JOB_ACTION:
            raise NotImplementedError

    def process(self):
        raise NotImplementedError

    @property
    def status_action(self):
        if self.JOB_ACTION == UPLOAD_ACTION:
            if self.progress < 100:
                return VALIDATING
            return VALIDATED
        if self.JOB_ACTION == VALIDATE_ACTION:
            if self.progress < 100:
                return VALIDATING
            return VALIDATED

        if self.JOB_ACTION == PROCESS_ACTION:
            if self.progress < 100:
                return PROCESSING
            return PROCESSED

    def validate_total_type(self, total_type):
        assert total_type in ['total_errors', 'total_success', 'total_complete'], "Total type add summary not correct"

    @property
    def chunks_raws_file(self):
        return list(divide_chunks(self.data_import_file, plat_import_setting.bulk_process_size))

    def _has_update_map_config(self):
        __change_hash = hashlib.md5(json.dumps(self.map_config).encode('utf-8')).hexdigest()

        if __change_hash != self.hash_map_config:
            self.hash_map_config = __change_hash
            self.info_import_file.update({'map_cols_to_module': self.map_config})

    def update_raws_process(self):
        try:
            assert len(self.raws_instances) > 0, "Raws update is not empty"
            RawDataTemporary.objects.bulk_update(objs=self.raws_instances, fields=self.fields_raw_instance_accept)
            self.raws_instances = []
        except Exception as ex:
            logger.error(f"[{self.lib_import_id}][update_raws_process] {ex}")

    def update_to_lib_import(self, **kwargs):
        if len(self.raws_instances) == 0:
            return
        #
        logger.info("total process file : {}".format(self.number_process))
        #
        self.update_raws_process()
        #
        if self.total_rows_action == 0:
            self.progress = 100
        else:
            self.progress = round((self.number_process / self.total_rows_action * 100), 2)
        #
        self._has_update_map_config()
        #
        data = {
            'status': self.status_action,
            'progress': self.progress,
            'total_process': self.number_process,
            'info_import_file': self.info_import_file
        }
        data = {**data, **kwargs}
        logger.info(f"status : {data['status']}, progress : {data['progress']}")
        DataImportTemporary.objects.filter(pk=self.lib_import_id).update(**data)

    def validate_data_request(self, data_request: dict, **kwargs):
        self.kwargs.update(kwargs)
        context = {'kwargs': self.kwargs}
        logger.debug(f"context to serializer {self.serializer.__name__} : {context}")
        serializer = self.serializer(data=data_request, context=context)
        serializer.is_valid()
        errors = serializer.errors
        validated_data = serializer.validated_data
        return validated_data, errors

    def _get_total_rows_action(self):
        try:
            queryset = RawDataTemporary.objects.filter(lib_import_id=self.lib_import_id)
            if self.JOB_ACTION == PROCESS_ACTION:
                queryset = queryset.filter(is_valid=True)
            total = queryset.count()
        except Exception as ex:
            total = 0
        return total

    def _completed_raws_is_not_valid(self):
        if self.JOB_ACTION == PROCESS_ACTION:
            queryset = RawDataTemporary.objects.filter(status=PROCESSING, is_valid=False)
            if queryset.count() > 0:
                queryset.update(status=PROCESSED, is_complete=False, modified=timezone.now())

    def _get_raws_process_action_queryset(self):
        try:
            self._completed_raws_is_not_valid()
            #
            args = {
                VALIDATE_ACTION: VALIDATING,
                PROCESS_ACTION: PROCESSING
            }
            queryset = RawDataTemporary.objects.filter(status=args[self.JOB_ACTION], lib_import_id=self.lib_import_id) \
                .order_by('index')
        except Exception as ex:
            queryset = None
        return queryset

    def _get_last_number_process(self):
        try:
            args = {
                VALIDATE_ACTION: Q(status=VALIDATED),
                PROCESS_ACTION: Q(status=PROCESSED, is_complete=True)
            }
            cond = args[self.JOB_ACTION] & Q(lib_import_id=self.lib_import_id)
            number = RawDataTemporary.objects.filter(cond).count()
        except Exception as ex:
            number = 0
        return number
