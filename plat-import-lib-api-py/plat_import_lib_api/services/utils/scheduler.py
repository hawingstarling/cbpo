import logging
from django.db import DEFAULT_DB_ALIAS
from plat_import_lib_api.static_variable.config import plat_import_setting

logger = logging.getLogger(__name__)


def create_periodic_tasks_import_lib():
    try:
        from django_celery_beat.models import CrontabSchedule, PeriodicTask
        configs = {
            "plat_import_lib_api.tasks.reopen_lib_import_process_action": dict(
                enabled=True,
                crontab=dict(
                    minute=f"*/{int(plat_import_setting.healthy_check_minute / 2)}",
                    hour="*",
                    day_of_week="*",
                    day_of_month="*",
                    month_of_year="*"
                ),
                one_off=False
            ),
            "plat_import_lib_api.tasks.auto_check_health_module": dict(
                enabled=True,
                crontab=dict(
                    minute=f"*/{plat_import_setting.healthy_check_minute}",
                    hour="*",
                    day_of_week="*",
                    day_of_month="*",
                    month_of_year="*"
                ),
                one_off=False
            ),
            "plat_import_lib_api.tasks.auto_clean_import_temp_completed": dict(
                enabled=True,
                crontab=dict(
                    minute="0",
                    hour="0",
                    day_of_month="1",
                    day_of_week="*",
                    month_of_year="*"
                ),
                one_off=False
            )
        }
        tasks_config = list(configs.keys())
        qs = PeriodicTask.objects.db_manager(DEFAULT_DB_ALIAS).filter(task__in=tasks_config)
        if qs.count() == len(tasks_config):
            logger.debug(f"[create_periodic_tasks_import_lib] Tasks has created in Periodic Scheduler")
            return
        objs_created = []
        objs_updated = []
        for key, vals in configs.items():
            cron_tab, _ = CrontabSchedule.objects.db_manager(DEFAULT_DB_ALIAS) \
                .get_or_create(**vals["crontab"])
            try:
                obj = qs.get(task=key)
                if obj.crontab_id == cron_tab.id:
                    continue
                obj.crontab = cron_tab
                objs_updated.append(obj)
            except Exception as ex:
                logger.debug(f"[create_periodic_tasks_import_lib] {ex}")
                vals["crontab"] = cron_tab
                objs_created.append(PeriodicTask(name=key, task=key, **vals))
        PeriodicTask.objects.db_manager(DEFAULT_DB_ALIAS).bulk_create(objs_created, ignore_conflicts=True)
        PeriodicTask.objects.db_manager(DEFAULT_DB_ALIAS).bulk_update(objs_updated, fields=["crontab"])
    except Exception as ex:
        logger.error(f"[create_periodic_tasks_import_lib] {ex}")
