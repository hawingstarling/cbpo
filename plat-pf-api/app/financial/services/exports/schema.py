import logging
import os
import pandas as pd
from django.db import connections
from typing import Union, List
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db.models import QuerySet
from django.utils import timezone
from pandas import DataFrame
from plat_import_lib_api.services.utils.utils import get_bucket_google_storage
from app.database.helper import get_connection_workspace
from config.settings.common import BASE_URL, MEDIA_URL
from plat_import_lib_api.static_variable.config import plat_import_setting

logger = logging.getLogger(__name__)

CSV = "csv"
EXCEL = "excel"
EXCEL_XLSX = 'xlsx'
EXCEL_XLS = 'xls'


class ExportSchema:
    def __init__(self, client_id: str, columns: dict, queryset: Union[QuerySet, None, str], category: str, **kwargs):
        self.client_id = str(client_id)
        self.db_using = get_connection_workspace(self.client_id)
        self.columns = columns
        self.queryset = queryset
        self.category = category
        self.kwargs = kwargs
        self.time_now = timezone.now()
        self._file_path = self.get_file_path_kwargs()

    @staticmethod
    def get_options_global_pandas(k):
        return pd.get_option(k)

    @staticmethod
    def set_options_global_pandas(k, v):
        pd.set_option(k, v)

    @property
    def data_extension(self):
        return self.kwargs.get('data_extension', [])

    @property
    def storage_env(self):
        return self.kwargs.get('storage_env', 'google')

    @property
    def df_mode(self):
        return self.kwargs.get('df_mode', 'w')

    @property
    def index(self):
        return self.kwargs.get('index', True)

    @property
    def header(self):
        return self.kwargs.get('header', True)

    @property
    def report_name(self):
        return self.kwargs.get('report_name', self.category)

    @property
    def read_sql(self):
        return self.kwargs.get('read_sql', False)

    def get_file_path_kwargs(self):
        return self.kwargs.get('file_path', None)

    @property
    def file_path(self):
        return self._file_path

    @file_path.setter
    def file_path(self, val):
        self._file_path = val

    @property
    def file_type(self):
        return self.kwargs.get("file_type", CSV)

    @property
    def file_extension(self):
        return self.kwargs.get("file_extension", CSV)

    @property
    def writer_engine(self):
        return self.kwargs.get("writer_engine", "openpyxl")

    def get_file_path(self):
        if self.file_path is not None:
            return self.file_path
        y, m, d = self.time_now.year, self.time_now.strftime('%m'), self.time_now.strftime('%d')
        file_path = f"{plat_import_setting.storage_folder}/reports/{self.client_id}/{y}/{m}/{d}/" \
                    f"{self.report_name}-{m}-{d}-{y}-{int(self.time_now.timestamp())}.{self.file_extension}"
        file_path = os.path.join(settings.MEDIA_ROOT, file_path)
        file_path = default_storage.save(file_path, ContentFile(''))
        return file_path

    def prefetch_data(self):
        if self.read_sql:
            return self.queryset
        if self.data_extension:
            return self.data_extension
        data = self.queryset.values(*self.columns)
        return data

    def processing(self):
        data = self.prefetch_data()
        file_path = self.processing_data_frame(data)
        return self.up_to_service(file_path)

    def _load_data_frame(self, data: any):
        if self.read_sql:
            conn = connections[self.db_using]
            df = pd.read_sql(sql=data, con=conn)
        else:
            df = DataFrame(list(data[:10000]))
        if self.index:
            df.index.name = 'Order'
            df.index += 1  # makes index number beginning at 1 instead of 0
        df.rename(columns=self.columns, inplace=True)
        return df

    def processing_data_frame(self, data: Union[List[List[dict]], str], sheet_name: str = "Sheet1"):
        try:
            df = self._load_data_frame(data)
            # df.style.set_properties(subset=["brand__name"], **{"width": 300})
            file_path = self.get_file_path()
            if self.file_type == CSV:
                df.to_csv(file_path, mode=self.df_mode, header=self.header, index=self.index)
            elif self.file_type == EXCEL:
                if self.writer_engine == "openpyxl":
                    optional = dict()
                    if self.df_mode == "a":
                        optional.update(dict(if_sheet_exists="overlay"))
                    with pd.ExcelWriter(
                            file_path,
                            engine="openpyxl",
                            mode=self.df_mode,
                            **optional
                    ) as writer:
                        df.to_excel(writer, sheet_name=sheet_name, startrow=writer.sheets[sheet_name].max_row,
                                    header=self.header, index=self.index)
                else:
                    with pd.ExcelWriter(
                            file_path,
                            engine="xlsxwriter"
                    ) as writer:
                        df.to_excel(writer, sheet_name=sheet_name, header=self.header, index=self.index)
            return file_path
        except Exception as ex:
            logger.error(f"{self.__class__.__name__}: {ex}")
            raise SystemError(ex)

    def up_to_service(self, file_path: str):
        try:
            if self.storage_env == 'local':
                file_url = f"{BASE_URL}{MEDIA_URL}{file_path.split(MEDIA_URL)[1]}"
            else:
                path = file_path.split(MEDIA_URL)[1]
                bucket = get_bucket_google_storage()
                blob = bucket.blob(path)
                blob.upload_from_filename(file_path)
                blob.make_public()
                file_url = blob.public_url
                os.remove(file_path)
            return file_url
        except Exception as ex:
            logger.error(f"{self.__class__.__name__}: {ex}")
            raise SystemError(ex)
