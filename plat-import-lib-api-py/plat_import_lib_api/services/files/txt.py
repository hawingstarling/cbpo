import logging
from plat_import_lib_api.services.files.base import FileImportInterface
from plat_import_lib_api.services.files.csv import CSVImportObject
from ..utils.exceptions import InvalidFormatException

logger = logging.getLogger('django')


class TXTImportObject(CSVImportObject):

    @property
    def sep(self):
        return '\t'

    def validate(self) -> None:
        FileImportInterface.validate(self)
        if not self.file_path.endswith('.txt'):
            raise InvalidFormatException(message="File not valid type Text (TSV)")
