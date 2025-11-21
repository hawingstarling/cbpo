import ftplib
import logging

from django.conf import settings
import os

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.utils import timezone

from app.edi.configs.source import SOURCE_EXTENSION_CONFIG

logger = logging.getLogger(__name__)


class FTPConnect:
    def __init__(self):
        self._ftp_host = settings.FTP_FEDEX_HOST
        self._ftp_user = settings.FTP_FEDEX_USER
        self._ftp_passwd = settings.FTP_FEDEX_PASSWD
        self._ftp_port = settings.FTP_FEDEX_PORT
        self._ftp_debug_level = settings.FTP_FEDEX_DEBUG_LEVEL

        self.date_now = timezone.now()

        self.folder = os.path.join("edi", str(self.date_now.year), str(self.date_now.month), str(self.date_now.day))

        self.file_sources = {}

    @property
    def ftp_host(self):
        return self._ftp_host

    @ftp_host.setter
    def ftp_host(self, value):
        self._ftp_host = value

    @property
    def ftp_user(self):
        return self._ftp_user

    @ftp_user.setter
    def ftp_user(self, value):
        self._ftp_user = value

    @property
    def ftp_passwd(self):
        return self._ftp_passwd

    @ftp_passwd.setter
    def ftp_passwd(self, value):
        self._ftp_passwd = value

    @property
    def ftp_port(self):
        return self._ftp_port

    @ftp_port.setter
    def ftp_port(self, value):
        self._ftp_port = value

    @property
    def ftp_debug_level(self):
        return self._ftp_debug_level

    @ftp_debug_level.setter
    def ftp_debug_level(self, value):
        self._ftp_debug_level = value

    def make_connect(self):
        ftp = None
        try:
            # connect to the FTP server
            ftp = ftplib.FTP()
            ftp.set_debuglevel(self.ftp_debug_level)
            #
            ftp.connect(host=self.ftp_host, port=self.ftp_port)
            # force UTF-8 encoding
            ftp.encoding = "utf-8"
            ftp.login(self.ftp_user, self.ftp_passwd)
        except Exception as ex:
            logger.error(f"[{self.__class__.__name__}]: {ex}")
        return ftp

    def add_file_sources(self, path_storage, extension):
        source = SOURCE_EXTENSION_CONFIG[extension]
        try:
            self.file_sources[source].append(path_storage)
        except Exception as ex:
            self.file_sources.update({source: [path_storage]})

    def download_files_edi(self, directory: str):
        #
        ftp_connect = self.make_connect()
        if ftp_connect is None:
            return self.file_sources
        #
        ftp_connect.cwd(directory)

        # ftp_connect.retrlines('LIST')
        # local file name you want to upload
        files = ftp_connect.nlst()
        #
        for file in files:
            filename, file_extension = os.path.splitext(file)
            if not file_extension:
                file_extension = '.csv'
            if file_extension not in ['.txt', '.csv']:
                continue
            try:
                # storage file
                path_storage = os.path.join(self.folder, f"{filename}{file_extension}")
                #
                self.add_file_sources(path_storage, file_extension)
                #
                path_storage = os.path.join(settings.MEDIA_ROOT, path_storage)
                # use FTP's STOR command to upload the file
                path_storage = default_storage.generate_filename(path_storage)
                if default_storage.exists(path_storage):
                    # default_storage.delete(path_storage)
                    continue
                path_storage = default_storage.save(path_storage, ContentFile(b''))
                with open(path_storage, "wb") as file_storage:
                    ftp_connect.retrbinary(f"RETR {file}", file_storage.write)
            except Exception as ex:
                logger.error(f"[{self.__class__.__name__}] {ex}")
        # close connect
        ftp_connect.quit()
        return self.file_sources

    def move_files_edi(self, directory_origin: str, directory_target: str, file_names: [str]):
        #
        ftp_connect = self.make_connect()
        # default make connect ftp in folder root
        #
        if ftp_connect is None:
            return
        for file_name in file_names:
            try:
                try:
                    ftp_connect.rename(f"{directory_origin}/{file_name}",
                                       f"{directory_target}/{file_name}")  # move file
                except ftplib.all_errors as ex:
                    file_name, extension = os.path.splitext(file_name)
                    ftp_connect.rename(f"{directory_origin}/{file_name}",
                                       f"{directory_target}/{file_name}")  # move file
            except Exception as ex:
                logger.error(f"[{self.__class__.__name__}] {ex}")
        ftp_connect.quit()
