import sys
from datetime import timedelta
from django.conf import settings

# environ config django
from django.utils import timezone

ENVIRONMENT = settings.ENVIRONMENT
BASE_URL = settings.BASE_URL
MEDIA_URL = settings.MEDIA_URL
MEDIA_ROOT = settings.MEDIA_ROOT


class __PlatImportSetting:
    def __init__(self):
        self._setting = None
        self._setting_queryset = self.__get_setting_queryset()
        self._load_setting()
        #
        self._time_refresh = timezone.now()
        self._is_test_env = self._get_is_test_env()

    @staticmethod
    def _get_is_test_env():
        try:
            is_test = sys.argv[1] == "test"
        except Exception as ex:
            is_test = False
        return is_test

    def _load_setting(self):
        try:
            self._setting = self._setting_queryset.first()
        except Exception as ex:
            pass

    @property
    def setting(self):
        if self._get_is_test_env or self._time_refresh < (timezone.now() - timedelta(minutes=30)):
            self._load_setting()
            self._time_refresh = timezone.now()
        return self._setting

    @staticmethod
    def __get_setting_queryset():
        try:
            from plat_import_lib_api.models import Setting
            queryset = Setting.objects.order_by('-created')
        except Exception as ex:
            queryset = None
        return queryset

    @property
    def use_queue(self):
        try:
            return self.setting.use_queue
        except Exception as ex:
            return False

    @property
    def bulk_process_size(self):
        try:
            return self.setting.bulk_process_size
        except Exception as ex:
            return 2000

    @property
    def storage_location(self):
        try:
            return self.setting.storage_location
        except Exception as ex:
            return 'local'

    @property
    def storage_folder(self):
        try:
            return self.setting.storage_folder
        except Exception as ex:
            return 'plat/lib_imports'

    @property
    def round_up_currency(self):
        try:
            return float(self.setting.round_up_currency)
        except Exception as ex:
            return float(0.0)

    @property
    def google_cloud_storage_bucket_name(self):
        try:
            return self.setting.google_cloud_storage_bucket_name
        except Exception as ex:
            return None

    @property
    def google_cloud_storage_bucket_access_key(self):
        try:
            return self.setting.google_cloud_storage_bucket_access_key
        except Exception as ex:
            return None

    @property
    def date_time_format(self):
        try:
            return self.setting.date_time_format
        except Exception as ex:
            return '%Y-%m-%d %H:%M:%S'

    @property
    def module_template_location(self):
        try:
            return self.setting.module_template_location
        except Exception as ex:
            return 'plat_import_lib_api.modules.base'

    @property
    def healthy_check_minute(self):
        try:
            return self.setting.healthy_check_minute
        except Exception as ex:
            return 30

    @property
    def auto_clean_day(self):
        try:
            return self.setting.auto_clean_day
        except Exception as ex:
            return 30

    @property
    def module_reopen_exclude(self):
        try:
            return self.setting.module_reopen_exclude
        except Exception as ex:
            return []


plat_import_setting = __PlatImportSetting()
