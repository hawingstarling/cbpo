import logging
from django.apps import AppConfig

logger = logging.getLogger(__name__)


class DataImportConfig(AppConfig):
    name = 'plat_import_lib_api'

    def ready(self):
        from .services.utils.scheduler import create_periodic_tasks_import_lib
        create_periodic_tasks_import_lib()
