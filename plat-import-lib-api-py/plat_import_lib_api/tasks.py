import datetime
import logging
from django.db.models import Q
from django.utils import timezone
from .models import DataImportTemporary, PROCESSED, REVOKED, REVERTED, REPORTED, VALIDATING, PROCESSING, \
    RawDataTemporary, UPLOADING
from .services.common.healthy import HealthyModule
from plat_import_lib_api.services.controllers.controller import ImportController
from celery import current_app
from .static_variable.action import VALIDATE_ACTION, PROCESS_ACTION, UPLOAD_ACTION
from .static_variable.config import plat_import_setting

logger = logging.getLogger(__name__)


@current_app.task(bind=True)
def lib_import_process_action_task(self, lib_import_id: str, action: str, map_config_request: list = []):
    assert lib_import_id is not None, "Import temp id is not None"
    logger.info(f"[{self.request.id}][{lib_import_id}][{action}][lib_import_process_action_task] "
                f"Begin lib_import_process_action_task")
    controller = ImportController(lib_import_id=lib_import_id, action=action, map_config_request=map_config_request)
    controller.process()


@current_app.task(bind=True)
def reopen_lib_import_process_action(self):
    logger.info(f"[Scheduler][{self.request.id}][reopen_lib_import_process_action] beginning ...")
    time_reopen = timezone.now() - datetime.timedelta(minutes=int(plat_import_setting.healthy_check_minute / 2))
    cond = Q(progress__lt=100, status__in=[UPLOADING, VALIDATING, PROCESSING], modified__lt=time_reopen)
    module_reopen_exclude = plat_import_setting.module_reopen_exclude
    if len(module_reopen_exclude) > 0:
        cond &= ~Q(module__in=module_reopen_exclude)
    queryset = DataImportTemporary.objects.filter(cond).order_by('created')
    for item in queryset.iterator():
        #
        try:
            #
            last_raws_change = RawDataTemporary.objects.filter(lib_import_id=item.pk).order_by('-modified').first()
            if last_raws_change.modified >= time_reopen:
                continue
        except Exception as ex:
            logger.error(f"[reopen_lib_import_process_action] error:  {ex}")
        #
        logger.info(f"[reopen_lib_import_process_action] reopen for {item.pk}")
        #
        if item.status == UPLOADING:
            action = UPLOAD_ACTION
        elif item.status == VALIDATING:
            action = VALIDATE_ACTION
        else:
            action = PROCESS_ACTION
        map_config_request = item.info_import_file.get('map_cols_to_module', {})
        lib_import_process_action_task.apply_async(kwargs=dict(lib_import_id=str(item.pk), action=action,
                                                               map_config_request=map_config_request))


@current_app.task(bind=True)
def auto_check_health_module(self):
    logger.info(f"[Scheduler][{self.request.id}][auto_check_health_module] beginning ...")
    modules = DataImportTemporary.objects.values_list('module', flat=True).distinct('module')
    #
    for module in modules:
        try:
            logger.info(f"[auto_check_health_module] check health module {module}")
            healthy = HealthyModule(module)
            healthy.validate()
            healthy.process()
            healthy.complete()
        except Exception as ex:
            logger.error(f"[auto_check_health_module] check health module {ex}")


@current_app.task(bind=True)
def auto_clean_import_temp_completed(self):
    logger.info(f"[Scheduler][{self.request.id}][auto_clean_import_temp_completed] beginning ...")
    last_number_days = timezone.now() - datetime.timedelta(days=plat_import_setting.auto_clean_day)
    DataImportTemporary.objects.filter(status__in=[PROCESSED, REVOKED, REVERTED, REPORTED],
                                       created__lt=last_number_days).delete()


@current_app.task(bind=True)
def auto_clean_import_temp_old_of_date(self):
    logger.info(f"[Scheduler][{self.request.id}][auto_clean_import_temp_old_of_date] beginning ...")
    last_number_days = timezone.now() - datetime.timedelta(days=180)
    DataImportTemporary.objects.filter(created__lt=last_number_days).delete()