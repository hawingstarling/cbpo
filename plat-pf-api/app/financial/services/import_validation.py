import copy
import itertools
import json

from plat_import_lib_api.models import DataImportTemporary
from plat_import_lib_api.services.utils.temp_data import DataTempService

from app.core.context import AppContext

GROUP_CHANNEL = 'CHANNEL'
GROUP_CHANNEL_ITEM = 'CHANNEL_ITEM'


class ImportValidationBase(object):
    total_field = None
    item_field = None
    message_default = None
    group_type = GROUP_CHANNEL

    def __init__(self, data_import, map_cols, info_import, **kwargs):
        self.client_id = AppContext.instance().client_id
        self.data_import = data_import
        self.map_cols = map_cols
        self.info_import = info_import
        self.kwargs = kwargs

    def primary_key_group(self, k):
        args = {
            GROUP_CHANNEL: ['channel_sale_id', 'channel'],
            GROUP_CHANNEL_ITEM: ['channel_sale_id', 'channel', 'sku']
        }
        keys = args.get(self.group_type, [])
        primary = self.get_primary_key(k, keys)
        return primary

    def get_primary_key(self, k, keys):
        empty = not any(k.get(self.map_cols[key], None) is None for key in keys)
        if not empty:
            return None
        data_keys = [str(k.get(self.map_cols[key])) for key in keys]
        return '_'.join(data_keys)

    def group_data_by_primary_key(self):
        group_key_data = {}
        for k, g in itertools.groupby(self.data_import, lambda k: self.primary_key_group(k)):
            if k:
                groups_data = group_key_data.get(k, [])
                groups_data += list(g)
                group_key_data[k] = groups_data
        return group_key_data

    def validate(self):
        raise NotImplementedError

    def get_message(self, msg: str = None):
        if not msg:
            msg = self.message_default
        return msg

    def map_data_import_validation(self, field, message_error, data_map):
        num_rows_map = [item['_meta']['number'] for item in data_map]
        summary = self.info_import['summary']
        for index, item in enumerate(self.data_import):
            meta = item['_meta']
            # if number of data import file exist in data map sale charged error
            if meta['number'] in num_rows_map:
                _index_record = meta['number']
                if _index_record in summary['total_success']['raws_index']:
                    summary['total_success']['raws_index'].remove(_index_record)
                    summary['total_success']['count'] -= 1
                if _index_record not in summary['total_errors']['raws_index']:
                    summary['total_errors']['raws_index'].append(_index_record)
                    summary['total_errors']['count'] += 1
                validation_errors = meta['validation_errors']
                if len(validation_errors) == 0:
                    meta['validation_errors'] = [{'code': field, 'message': [message_error]}]
                    meta['valid'] = False
                    self.data_import[index]['_meta'] = meta
                    continue
                normalize_validation_errors = {value['code']: {'index': idx, 'message': value['message']} for idx, value
                                               in enumerate(validation_errors) if value['code'] == field}
                sale_charged_info = normalize_validation_errors.get(field, {})
                err_idx = sale_charged_info.get('index', None)
                message = sale_charged_info.get('message', [])
                message.append(message_error)
                if err_idx:
                    meta['validation_errors'][err_idx] = {'code': field, 'message': message}
                else:
                    meta['validation_errors'].append({'code': field, 'message': message})
                meta['valid'] = False

class FlagErrorRecordSaleItemChannel(ImportValidationBase):
    message_default = 'One sale item of "{}" is invalid'

    def validate(self):
        group_data_by_primary_key = self.group_data_by_primary_key()
        for key in group_data_by_primary_key.keys():
            group_data = group_data_by_primary_key[key]
            has_record_invalid = self.has_record_invalid(group_data=group_data)
            if has_record_invalid and len(group_data) > 1:
                msg = copy.deepcopy(self.message_default)
                channel_info = key.split('_')[0]
                msg = msg.format(channel_info)
                self.map_data_import_validation(self.total_field, self.get_message(msg), group_data)

    def has_record_invalid(self, group_data):
        invalid_exist = any(not row['_meta']['valid'] for row in group_data)  # exist record invalid
        valid_exist = any(row['_meta']['valid'] for row in group_data)  # exist record valid
        if invalid_exist and valid_exist:
            return True
        return False


class DuplicateSaleItemValidation(ImportValidationBase):
    message_default = 'Record {} duplicate'
    group_type = GROUP_CHANNEL_ITEM

    def validate(self):
        group_data_by_primary_key = self.group_data_by_primary_key()
        for key in group_data_by_primary_key.keys():
            group_data = group_data_by_primary_key[key]
            if len(group_data) > 1:
                number_records = self.get_number_record(group_data)
                mgs = copy.deepcopy(self.message_default)
                if len(number_records) == 1:
                    joined = '{} is'.format(number_records[0])
                else:
                    head_part = number_records[:len(number_records) - 1]
                    tail_part = number_records[len(number_records) - 1]
                    joined = '{} and {} are'.format(', '.join(head_part), tail_part)
                mgs = mgs.format(joined)
                self.map_data_import_validation(self.total_field, self.get_message(mgs), group_data)

    def get_number_record(self, group_data):
        return [str(item['_meta']['number']) for item in group_data]


class ImportValidationManage:
    data_import = None
    info_import = None
    map_cols = {}

    def __init__(self, import_id, **kwargs):
        self.import_id = import_id
        self.kwargs = kwargs
        self.get_attr()

    def get_attr(self):
        import_file = DataImportTemporary.objects.get(pk=self.import_id)
        # data temp
        self.data_import = json.loads(import_file.json_data_last_cache)
        # info file import
        self.info_import = import_file.info_import_file
        map_cols_to_module = self.info_import.get('map_cols_to_module', [])
        self.map_cols = {item['target_col']: item['upload_col'] for item in map_cols_to_module}

    @property
    def list_validations(self):
        return [
            DuplicateSaleItemValidation,
            FlagErrorRecordSaleItemChannel
        ]

    def exec(self):
        for obj in self.list_validations:
            obj(data_import=self.data_import, map_cols=self.map_cols, info_import=self.info_import,
                **self.kwargs).validate()

        # update import temp
        self.update_temp_import()

    def update_temp_import(self):
        # update data validate to db
        data_update = {
            'json_data_last_cache': json.dumps(self.data_import),
            'info_import_file': self.info_import
        }
        DataTempService.update_import(self.import_id, **data_update)
