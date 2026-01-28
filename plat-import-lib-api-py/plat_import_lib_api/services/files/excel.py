import math, maya, logging, openpyxl, time
from plat_import_lib_api.services.files.base import FileImportInterface
from ..utils.exceptions import InvalidFormatException
from ...static_variable.config import plat_import_setting

logger = logging.getLogger('django')


class ExcelImportObject(FileImportInterface):
    def validate(self):
        super().validate()
        if not self.file_path.endswith('.xlsx') and not self.file_path.endswith('.xls'):
            raise InvalidFormatException(message="File not valid type EXCEL")
        pass

    def load_workbook(self):
        self.wb = openpyxl.load_workbook(filename=self.file_path)

    def get_header(self):
        worksheet = self.wb.worksheets[0]
        # init info
        cols_file = []
        columns_file = worksheet[1]  # get header
        for item in columns_file:
            cols_file.append(
                {
                    'label': str(item.value),
                    'name': str(item.value).replace(' ', '_').lower(),
                }
            )
        self.header = cols_file

    def get_total(self):
        self.total = self.wb.worksheets[0].max_row - 1  # exclude column header

    def process_row(self, raw, columns_file: list = []):
        _row_temp = {}
        for cell in raw:
            if isinstance(cell.value, float) and math.isnan(cell.value):
                cell.value = None
        empty = not any((cell.value for cell in raw))
        if empty:
            return _row_temp
        i = 0
        for cell in raw:
            name_header = self.header[i]['name']
            if cell.is_date:
                try:
                    _temp_cell = maya.parse(cell.value).datetime().strftime(plat_import_setting.date_time_format)
                except Exception as ex:
                    _temp_cell = None
                _row_temp[name_header] = _temp_cell
                i += 1
                continue
            _temp_cell = cell.value
            if isinstance(_temp_cell, float) and math.isnan(_temp_cell):
                _temp_cell = None
                _row_temp[self.header[i]['name']] = _temp_cell
                i += 1
                continue
            _row_temp[name_header] = _temp_cell
            i += 1
        return _row_temp

    def divide_chunks(self, l):
        n = plat_import_setting.bulk_process_size
        for i in range(0, len(l), n):
            yield l[i:i + n]

    def chunk_size(self, l):
        start_number = 2  # start read row
        list_chunk = list(self.divide_chunks(range(l)))
        for index, value in enumerate(list_chunk):
            list_chunk[index] = list(map(lambda x: x + start_number, value))
        return list_chunk

    def process(self):
        try:
            self.init_info_import_file()
            worksheet = self.wb.worksheets[0]
            # update info
            #
            # start upload
            segments = self.chunk_size(self.total)
            #
            self.start_time = time.time()
            #
            for segment in segments:
                logger.info(f"processing read segment length : {len(segment)}")
                for row in worksheet.iter_rows(min_row=segment[0], max_row=segment[-1]):
                    raw_instance = self.process_raw_file(row)
                    if not raw_instance:
                        continue
                    self.raws_instances.append(raw_instance)
                    self.num_row += 1
                # cal percent chunk uploader
                self.total_progress += len(segment)
                self.update_process_upload()
                #
                logger.info("complete processing segment length : {}".format(len(segment)))
        except Exception as ex:
            logger.error('[{}] ReadFile.read_data_file_excel: {}'.format(self.__class__.__name__, ex))
            raise ex
