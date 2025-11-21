import os
import pandas as pd
import logging
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.utils import timezone
from plat_import_lib_api.static_variable.config import plat_import_setting
from xlsxwriter import Workbook

from app.financial.services.exports.grand_summary_schema import GrandSummaryExportSchema
from app.financial.services.exports.schema import CSV, EXCEL

logger = logging.getLogger(__name__)


class SPClientReportAggregateBase:
    __FILE_NAME_TEMPLATE__ = None
    __FOLDER_CATEGORY__ = "custom_report"
    __FOLDER_STORAGE_FILE__ = "sp-api-reports"
    __FILE_TYPE__ = CSV
    __FILE_EXTENSION__ = CSV
    __WRITER_ENGINE__ = "openpyxl"
    __DF_MODE__ = "a"
    __APPEND_HEADER_FILE__ = False
    __APPEND_INDEX_FILE__ = False
    __FILE_READ_SQL__ = False

    def __init__(self, client_id: str, object_id: str, *args, **kwargs):
        self._client_id = client_id
        self._object_id = object_id
        self._object = self._get_object()
        self._columns = {}
        self._columns_as_type = {}
        self._time_now = timezone.now()
        self._file_path = None
        self._export_schema = None
        self.args = args
        self.kwargs = kwargs

    def _init_export_schema(self):
        self._export_schema = GrandSummaryExportSchema(
            client_id=self._client_id,
            columns=self._columns,
            queryset=None,
            category=self.__FOLDER_CATEGORY__,
            df_mode=self.__DF_MODE__,
            header=self.__APPEND_HEADER_FILE__,
            read_sql=self.__FILE_READ_SQL__,
            file_path=self._file_path, file_type=self.__FILE_TYPE__,
            file_extension=self.__FILE_EXTENSION__,
            index=self.__APPEND_INDEX_FILE__,
            storage_env=plat_import_setting.storage_location,
            writer_engine=self.__WRITER_ENGINE__
        )

    def _get_object(self):
        raise NotImplementedError

    def _get_columns_export(self):
        raise NotImplementedError

    @property
    def file_name_report(self):
        return self.__FILE_NAME_TEMPLATE__

    def _generate_file_storage(self):
        if self._file_path is not None:
            return self._file_path
        d, m, y = self._time_now.strftime("%d"), self._time_now.strftime("%m"), self._time_now.year
        timestamp = int(self._time_now.timestamp())
        file_path = f"{plat_import_setting.storage_folder}/{self.__FOLDER_STORAGE_FILE__}/" \
                    f"{self._client_id}/{y}/{m}/{d}/{self.file_name_report}-{timestamp}.{self.__FILE_EXTENSION__}"
        file_path = os.path.join(settings.MEDIA_ROOT, file_path)
        file_path = default_storage.save(file_path, ContentFile(""))
        return file_path

    def _init_header_file_report(self, file_path: str):
        data = {k: [v] for k, v in self._columns.items()}
        df = pd.DataFrame(data=data)
        if self.__FILE_TYPE__ == CSV:
            df.to_csv(file_path, header=False, index=False)
        elif self.__FILE_TYPE__ == EXCEL:
            workbook = Workbook(file_path)
            worksheet = workbook.add_worksheet(name="Sheet1")
            i = 0
            for k, v in self._columns.items():
                worksheet.set_column(i, i, 20)
                worksheet.write(0, i, v)
                i += 1
            workbook.close()

    def _init_file_report(self):
        logger.debug(f"[{self.__class__.__name__}][{self._client_id}][_init_file_report]"
                     f"[{self.__FILE_TYPE__}][{self.__FILE_EXTENSION__}] begin generating ...")
        file_path = self._generate_file_storage()
        logger.debug(f"[{self.__class__.__name__}][{self._client_id}][_init_file_report]"
                     f"[{self.__FILE_TYPE__}][{self.__FILE_EXTENSION__}] Init row header {file_path} ...")
        if not self.__APPEND_HEADER_FILE__:
            self._init_header_file_report(file_path)
        self._file_path = file_path

    def validate(self):
        assert self.__FILE_NAME_TEMPLATE__ is not None
        self._get_columns_export()
        self._init_file_report()
        self._init_export_schema()

    def normalize_data(self, *args, **kwargs):
        raise NotImplementedError

    def process(self):
        raise NotImplementedError

    def complete(self):
        pass
