import logging
import operator
from functools import reduce
from django.db.models import Q
from ..objects.lib_import import LibImportObject
from django.http import FileResponse
import mimetypes
import os
from wsgiref.util import FileWrapper
from ...models import RawDataTemporary, PROCESSED
from ...static_variable.raw_data_import import RAW_CREATED_TYPE, RAW_UPDATED_TYPE, RAW_IGNORED_TYPE

logger = logging.getLogger(__name__)


class ResponseDataService(LibImportObject):

    def __init__(self, lib_import_id: str, **kwargs):
        super().__init__(lib_import_id=lib_import_id, **kwargs)

        self.map_cols_obj = {_item['target_col']: _item['upload_col'] for _item in self.map_config}

    def validate(self):
        pass

    def process(self):
        pass

    @property
    def data_import(self):
        data = {
            'id': str(self.lib_import.pk),
            'name': self.lib_module.name,
            'label': self.lib_module.label,
            'meta': self.lib_import.meta,
            'status': self.lib_import.status,
            'progress': self.lib_import.progress,
            'columns': self.lib_module.target_cols,
            'summary': RawDataTemporary.summary(self.lib_import_id),
            'upload_columns': self.info_import_file.get('cols_file', []),
            'column_mapping': self.map_config,
            'created': self.lib_import.created,
            'updated': self.lib_import.modified,
            'validation_started': self.lib_import.validation_started,
            'validation_completed': self.lib_import.validation_completed,
            'process_started': self.lib_import.process_started,
            'process_completed': self.lib_import.process_completed
        }
        data = self.lib_module.handler_response_detail(data, **self.kwargs)
        return data

    def queryset_filter_raws_data_temporary(self, filters: dict = {}, order_by: str=None):
        cond = Q(lib_import_id=self.lib_import_id)
        #
        _type = filters.get('type', None)
        _key = filters.get('key', None)

        if _type:
            if _type == 'invalid':
                cond &= Q(is_valid=False)
            elif _type == 'valid':
                cond &= Q(is_valid=True)
            elif _type == 'processed':
                cond &= Q(status=PROCESSED, is_complete=True)
            elif _type == 'error':
                cond &= Q(status=PROCESSED, is_valid=True, is_complete=False)
            elif _type == 'created':
                cond &= Q(status=PROCESSED, is_complete=True, type=RAW_CREATED_TYPE)
            elif _type == 'updated':
                cond &= Q(status=PROCESSED, is_complete=True, type=RAW_UPDATED_TYPE)
            elif _type == 'ignored':
                cond &= Q(status=PROCESSED, is_complete=True, type=RAW_IGNORED_TYPE)
            else:
                pass

        queryset = RawDataTemporary.objects.filter(cond)
        #
        if _key:
            cols_file = self.lib_import.info_import_file['cols_file']
            cols_search_key = [{f"data__{item['name']}": _key} for item in cols_file]
            queryset = queryset.filter(reduce(operator.or_, (Q(**x) for x in cols_search_key)))
        if order_by:
            queryset = queryset.order_by(order_by)
        return queryset

    def get_raws_data_export(self, filters):
        raws_data = []
        _type = filters.get('type', None)
        queryset = self.queryset_filter_raws_data_temporary(filters ,'index')
        for instance in queryset.iterator():
            raws_data.append(instance.normalize_raw_response(_type))
        return raws_data

    def download_file(self, file_path: str = None):
        file_path = os.path.join(file_path)
        file_handle = FileWrapper(open(file_path))
        mime_type, _ = mimetypes.guess_type(file_path)[0]
        response = FileResponse(file_handle, content_type=mime_type)
        response['Content-Disposition'] = 'attachment; filename="%s"' % 'test.csv'
        return response
