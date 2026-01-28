import copy
import logging
import maya
from django.db.models import Count, CharField, Case, When, IntegerField
from django.db.models.functions import Cast
from django.utils import timezone
from plat_import_lib_api.models import RawDataTemporary, VALIDATED
from .base import LibBaseAction
from ..utils.exceptions import InvalidParamException
from ...static_variable.action import VALIDATE_ACTION
from ..utils.utils import round_up_currency
from ...static_variable.config import plat_import_setting

logger = logging.getLogger(__name__)


class LibValidateAction(LibBaseAction):
    JOB_ACTION = VALIDATE_ACTION

    def __init__(self, lib_import_id: str, map_config_request: list, **kwargs):
        super().__init__(lib_import_id=lib_import_id, **kwargs)

        self.map_config_request = map_config_request
        self.map_config_dict = {}
        self.map_config_diff = {}
        self.validate_map_config_request()

    def validate_map_config_request(self):
        try:
            assert self.map_config_request is not None, f"Map config request not in config"
            target_cols_keys = [item['name'] for item in self.lib_module.target_cols]
            upload_col_keys = [item['name'] for item in self.info_import_file.get('cols_file')]
            for item in self.map_config_request:
                if not item['upload_col']:
                    continue
                assert item[
                           'target_col'] in target_cols_keys, f"'{item['target_col']}' target col request not in config"
                assert item['upload_col'] in upload_col_keys, f"'{item['upload_col']}' target col request not in config"
        except Exception as ex:
            raise InvalidParamException(message=ex, verbose=True)

    def merge_map_config_cols(self):
        map_config_request = {item['target_col']: item['upload_col'] for item in self.map_config_request}
        map_config = []
        for item in self.map_config:
            _item = copy.deepcopy(item)
            try:
                _upload_request = map_config_request[_item['target_col']]
                if _upload_request != _item['upload_col']:
                    _item['upload_col'] = _upload_request
            except Exception as ex:
                pass
            map_config.append(_item)

        self.map_config = map_config
        self.map_config_dict = {item['target_col']: item['upload_col'] for item in self.map_config}
        self.map_config_diff = {item['upload_col']: item['target_col'] for item in self.map_config if
                                item['target_col'] != item['upload_col']}
        self._has_update_map_config()

    def process(self):
        # merge map config request to map config exist
        self.merge_map_config_cols()
        #
        self.update_to_lib_import()
        #
        self._has_update_map_config()
        #
        for instance in self.raws_process_action_queryset:
            # logger.info(f"validate raw: {instance.index}")
            self.validate_raw_temp_to_rule(instance)
            self.number_process += 1
            self.raws_instances.append(instance)
            if len(self.raws_instances) % plat_import_setting.bulk_process_size == 0:
                self.update_to_lib_import()
        #
        if len(self.raws_instances) > 0:
            self.update_to_lib_import()

        self.process_key_map()
        self.process_parent_key_map()

    def process_key_map(self):
        try:
            queryset = RawDataTemporary.objects.filter(lib_import_id=self.lib_import_id, status=VALIDATED) \
                .filter(key_map__isnull=False).values('key_map') \
                .annotate(count=Count('key_map')).filter(count__gt=1).order_by('key_map')
            self.raws_instances = []
            for item in queryset:
                item_key_duplicate = RawDataTemporary.objects.filter(lib_import_id=self.lib_import_id,
                                                                     key_map=item['key_map']).order_by('index')
                number_records = list(item_key_duplicate.annotate(number=Cast('index', output_field=CharField()))
                                      .values_list('number', flat=True))
                head_part = number_records[:len(number_records) - 1]
                tail_part = number_records[len(number_records) - 1]
                joined = f"{', '.join(head_part)} and {tail_part} are"
                mgs = f"Record {joined} duplicate"
                for dup_instance in item_key_duplicate:
                    keys_raw_map = self.lib_module.keys_raw_map_config(self.lib_import_id, dup_instance.data_map_config)
                    duplicate_key_labels: list = self.get_dupicate_key_labels(keys_raw_map)

                    message = mgs
                    if duplicate_key_labels:
                        duplicate_key_labels = ', '.join(duplicate_key_labels)
                        message = f"{mgs} ({duplicate_key_labels})"
                    _error = {'code': None, 'message': [message]}
                    dup_instance.validation_errors.append(_error)
                    dup_instance.is_valid = False
                    dup_instance.modified = timezone.now()
                    self.raws_instances.append(dup_instance)
                if len(self.raws_instances) % plat_import_setting.bulk_process_size == 0:
                    self.update_raws_process()
            if len(self.raws_instances) > 0:
                self.update_raws_process()
        except Exception as ex:
            pass

    def process_parent_key_map(self):
        try:
            queryset = RawDataTemporary.objects.filter(lib_import_id=self.lib_import_id, status=VALIDATED) \
                .filter(parent_key_map__isnull=False).values('parent_key_map') \
                .annotate(count=Count('parent_key_map')).filter(count__gt=1).order_by('parent_key_map')
            self.raws_instances = []
            for item in queryset:
                item_group_key = RawDataTemporary.objects \
                    .filter(lib_import_id=self.lib_import_id, parent_key_map=item['parent_key_map'])
                agg_dump_error = item_group_key.aggregate(
                    count_valid=Count(Case(When(is_valid=True, then=1), output_field=IntegerField())),
                    count_invalid=Count(Case(When(is_valid=False, then=1), output_field=IntegerField()))
                )

                if agg_dump_error['count_invalid'] == 0 or agg_dump_error['count_valid'] == 0:
                    continue
                for dump_error_instance in item_group_key.filter(is_valid=True).order_by('index'):
                    present_key = dump_error_instance.parent_key_map.split('__$__')[0]
                    mgs = f'One item of "{present_key}" is invalid'
                    _error = {'code': None, 'message': [mgs]}
                    dump_error_instance.validation_errors.append(_error)
                    dump_error_instance.is_valid = False
                    dump_error_instance.modified = timezone.now()
                    self.raws_instances.append(dump_error_instance)
                if len(self.raws_instances) % plat_import_setting.bulk_process_size == 0:
                    self.update_raws_process()
            if len(self.raws_instances) > 0:
                self.update_raws_process()
        except Exception as ex:
            pass

    def validate_raw_temp_to_rule(self, instance: RawDataTemporary):
        data_request = {}
        raw = instance.data
        # serializer
        target_cols = self.lib_module.target_cols

        for item in target_cols:
            _upload_col_name = self.map_config_dict.get(item['name'], None)
            if not _upload_col_name:
                continue
            _upload_col_val = raw.get(_upload_col_name, None)
            if _upload_col_val and item['type'] in ['float', 'number']:
                try:
                    if type(_upload_col_val) is str:
                        _upload_col_val = _upload_col_val.replace(',', '')
                    # round up with next cent
                    _upload_col_val = float(_upload_col_val)
                    _upload_col_val = round_up_currency(_upload_col_val)
                    raw[_upload_col_name] = str(_upload_col_val)
                except Exception as ex:
                    logger.error(f"[{self.__class__.__name__}][round_up_currency] ex")
                    pass
            if _upload_col_val and item['type'] == 'datetime':
                try:
                    date_time_parsed = maya.parse(_upload_col_val)
                    _upload_col_val = date_time_parsed.datetime().strftime('%Y-%m-%dT%H:%M:%S.%f%z')
                    raw[_upload_col_name] = date_time_parsed.strftime(plat_import_setting.date_time_format)
                except Exception as ex:
                    pass
            data_request[item['name']] = _upload_col_val
        self.validate_data_request(data_request, raw, instance)

    def validate_data_request(self, data_request: dict, raw: dict = {}, instance: RawDataTemporary = None, **kwargs):
        if not instance:
            raise NotImplementedError
        data_validation, errors = super().validate_data_request(data_request=data_request, **kwargs)

        _errors = []

        self.lib_module.handler_validate_row(lib_import_id=self.lib_import_id, validated_data=data_validation,
                                             row=raw, map_config=self.map_config, errors=errors,
                                             data_request=data_request, **self.kwargs)

        for key in errors:
            msg = self.lib_module.handler_message_error_column_validate(self.lib_import_id, key,
                                                                        data_request.get(key), errors[key],
                                                                        **self.kwargs)
            item = {
                'code': key,
                'message': msg
            }
            _errors.append(item)

        if len(_errors) > 0:
            instance.is_valid = False
            instance.validation_errors = _errors
        else:
            instance.is_valid = True
            instance.validation_errors = []
        #
        self._get_key_raw_map(data_request, instance, **kwargs)
        for key, val in self.map_config_diff.items():
            data_request.update({key: data_request.get(val, None)})
        instance.data = raw
        instance.data_map_config = data_request
        instance.map_config = self.map_config
        instance.status = VALIDATED
        instance.processing_errors = []
        instance.modified = timezone.now()

    def _get_key_raw_map(self, data_request, instance, **kwargs):
        keys_raw_map = self.lib_module.keys_raw_map_config(self.lib_import_id, data_request, **kwargs)
        if len(keys_raw_map.get('key_map', [])) > 0:
            try:
                instance.key_map = "__$__".join([data_request[key] for key in keys_raw_map['key_map']])
            except Exception as ex:
                pass
        if len(keys_raw_map.get('parent_key_map', [])) > 0:
            try:
                instance.parent_key_map = "__$__".join([data_request[key] for key in keys_raw_map['parent_key_map']])
            except Exception as ex:
                pass

    def get_dupicate_key_labels(self, keys_raw_map):
        key_map: list = keys_raw_map.get('key_map', [])
        labels = [self.map_config_dict.get(item) for item in key_map]
        return labels
