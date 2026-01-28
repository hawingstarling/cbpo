import os, logging
from plat_import_lib_api.services.files.csv import CSVImportObject
from plat_import_lib_api.services.files.excel import ExcelImportObject
from plat_import_lib_api.services.files.txt import TXTImportObject
from ..utils.exceptions import InvalidFormatException
from ...models import DataImportTemporary

logger = logging.getLogger('django')


class ReaderFileManage(object):

    def __init__(self, lib_import_id: str):
        self.lib_import_id = lib_import_id
        self.lib_import = DataImportTemporary.objects.get(pk=self.lib_import_id)
        self.service = self.load_service()

    def load_service(self):
        file = self.lib_import.temp_file_path
        filename, file_extension = os.path.splitext(file)
        if not file_extension:
            raise InvalidFormatException(message="File not found file_extension")
        args = {
            '.csv': CSVImportObject,
            '.xlsx': ExcelImportObject,
            '.xls': ExcelImportObject,
            '.txt': TXTImportObject,
        }

        instance = args.get(file_extension)
        if not instance:
            raise InvalidFormatException(message="File not supported")

        return instance(lib_import_id=self.lib_import_id)

    def processing(self):
        self.service.process()
