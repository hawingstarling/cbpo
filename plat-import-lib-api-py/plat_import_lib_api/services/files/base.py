import hashlib
import json, logging, time, maya
from dateutil.parser import parse
from django.core.files.storage import default_storage
from plat_import_lib_api.services.files.utils import suggest_upload_column_to_target_column
from plat_import_lib_api.models import STATUS_CHOICE, DataImportTemporary, RawDataTemporary
from .storage import StorageFileManage, STORAGE_DOWNLOAD_ACTION
from ..objects.lib_import import LibImportObject
from ..utils.exceptions import InvalidFormatException
from ...static_variable.config import plat_import_setting

logger = logging.getLogger('django')


class FileImportInterface(LibImportObject):

    def __init__(self, lib_import_id: str, **kwargs):
        super().__init__(lib_import_id=lib_import_id, **kwargs)

        #
        self.header = []
        self.total_progress = 0
        self.total = 0
        self.num_row = 1
        self.start_time = None
        self.load_workbook()
        #
        self.map_upload_to_target_cols = {}
        #
        self.config_cols_key = {item['name']: item for item in self.lib_module.target_cols}
        #
        self.raws_import_temporary_queryset = RawDataTemporary.objects.filter(lib_import_id=self.lib_import_id)
        self.last_number_raw_processing = self._get_last_number_raw_processing()
        #
        self.raws_instances = []

    def process_row(self, *args, **kwargs):
        raise NotImplemented

    def validate(self):
        self.load_file_remote_service()
        # validate file is not None or file not exists
        path_storage = default_storage.generate_filename(self.file_path)
        if not default_storage.exists(path_storage):
            raise InvalidFormatException(message="File not exist in system for uploader")

    def load_file_remote_service(self):
        try:
            assert plat_import_setting.storage_location == 'google', "Storage location not service remote"
            path_storage = default_storage.generate_filename(self.file_path)
            if default_storage.exists(path_storage):
                return
            file_manager = StorageFileManage(file_path=self.file_url_cloud, module=self.lib_import.module,
                                             action=STORAGE_DOWNLOAD_ACTION)
            file_path = file_manager.process()
            self.update_import_file_uploader(temp_file_path=file_path)
            self.file_path = file_path
        except Exception as ex:
            logger.error(f"[{self.__class__.__name__}][load_file_remote_service] {ex}")
            pass

    def get_header(self):
        pass

    def get_total(self):
        pass

    def init_info_import_file(self):
        self.get_header()
        self.get_total()
        # default map by row index, will using regex pattern from config for map
        map_config = suggest_upload_column_to_target_column(self.lib_module.target_cols, self.header)
        self.info_import_file = {
            'cols_file': self.header,
            'map_cols_to_module': map_config
        }
        # update import uploader
        self.update_import_file_uploader(info_import_file=self.info_import_file)

    @staticmethod
    def _hash_content_data(raw_temp):
        return hashlib.md5(json.dumps(raw_temp).encode('utf-8')).hexdigest()

    def _init_raw_instance(self, raw_temp: dict):
        hash_data = self._hash_content_data(raw_temp)
        return RawDataTemporary(lib_import_id=self.lib_import_id, index=self.num_row, data=raw_temp,
                                hash_data=hash_data)

    def _get_last_number_raw_processing(self):
        try:
            number = self.raws_import_temporary_queryset.count()
        except Exception as ex:
            number = self.num_row
        return number

    def process_raw_file(self, raw, columns_file: list = []):
        if self.num_row < self.last_number_raw_processing:
            self.num_row += 1
            return None
        _row_temp = self.process_row(raw, columns_file)
        if not _row_temp:
            return None
        raw_instance = self._init_raw_instance(_row_temp)
        return raw_instance

    def create_raws_process(self):
        try:
            assert len(self.raws_instances) > 0, "Raws create is not empty"
            RawDataTemporary.objects.bulk_create(objs=self.raws_instances, ignore_conflicts=True)
            self.raws_instances = []
        except Exception as ex:
            logger.error(f"[{self.lib_import_id}][create_raws_process] {ex}")

    def update_process_upload(self):
        if self.num_row < self.last_number_raw_processing:
            return
        logger.info("total process file : {}".format(self.total_progress))
        #
        self.create_raws_process()
        #
        progress = int(self.total_progress / self.total * 100)
        status = STATUS_CHOICE[1][0] if progress == 100 else STATUS_CHOICE[0][0]
        #
        time_exc = str(time.time() - self.start_time) if progress == 100 else None
        #
        update = dict(status=status, progress=progress, total_process=self.total_progress, time_exc=time_exc)
        # update info uploader chunk to records db
        self.update_import_file_uploader(**update)

    def is_date(self, value):
        """
        Check value is datetime format
        :param value:
        :return:
        """
        try:
            if not isinstance(value, str):
                return False
            parse(value)
            maya.parse(value)
            return True
        except ValueError:
            return False

    def load_workbook(self):
        raise NotImplemented

    def get_info(self):
        raise NotImplemented

    def update_import_file_uploader(self, **kwargs):
        DataImportTemporary.objects.filter(pk=self.lib_import_id).update(**kwargs)
