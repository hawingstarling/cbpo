import pandas as pd, logging, time, math
from plat_import_lib_api.services.files.base import FileImportInterface
from ..utils.exceptions import InvalidFormatException
from ...static_variable.config import plat_import_setting

logger = logging.getLogger('django')


class CSVImportObject(FileImportInterface):

    def validate(self) -> None:
        super(CSVImportObject, self).validate()
        if not self.file_path.endswith('.csv'):
            raise InvalidFormatException(message="File not valid type EXCEL")

    def load_workbook(self):
        self.wb = pd.read_csv(self.file_path, sep=self.sep)

    @property
    def sep(self):
        return ','

    def get_header(self):
        # init info
        cols_file = []
        columns = list(self.wb.columns)  # get header
        for value in columns:
            cols_file.append(
                {
                    'label': str(value),
                    'name': str(value).replace(' ', '_').lower(),
                }
            )
        self.header = cols_file

    def get_total(self):
        self.total = len(self.wb.index)

    def fetch_upload_cols_with_target_cols(self):
        map_cols_to_module = self.info_import_file.get('map_cols_to_module')
        self.map_upload_to_target_cols = {item['upload_col']: item['target_col'] for item in map_cols_to_module}

    def replace_last_dot_zero(self, _temp_cell):
        if ' ' not in _temp_cell and _temp_cell[-2:] == '.0':
            _temp_cell = _temp_cell.replace('.0', '')
        return _temp_cell

    def process_row(self, raw, columns_file):
        _row_temp = {}
        for column in columns_file:
            if isinstance(raw[column], float) and math.isnan(raw[column]):
                raw[column] = None
        empty = not any(raw[column] for column in columns_file)
        if empty:
            return _row_temp
        # start index
        i = 0
        for column in columns_file:
            _col_header = self.header[i]['name']
            value = raw[column]
            if value is not None:
                value = self.replace_last_dot_zero(value)
            _row_temp[_col_header] = value
            i += 1
        return _row_temp

    def process(self):
        try:
            self.init_info_import_file()
            #
            self.fetch_upload_cols_with_target_cols()

            columns_file = list(self.wb.columns)
            # start upload
            self.start_time = time.time()
            for segment in pd.read_csv(self.file_path, sep=self.sep,
                                       chunksize=plat_import_setting.bulk_process_size, dtype=str):
                logger.info(f"processing read segment length : {len(segment)}")
                for index, raw in segment.iterrows():
                    raw_instance = self.process_raw_file(raw, columns_file)
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
            logger.error('ReadFile.read_data_file_csv: {}'.format(ex))
            raise InvalidFormatException(message=ex, verbose=True)
