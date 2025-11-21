from celery.schedules import crontab
from celery import current_app


@current_app.task(bind=True)
def test_periodic_task(self):
    print(f"[Scheduler][{self.request.id}] Periodic Task is running ....")


current_app.conf.beat_schedule = {
    # Core
    "app.core.tasks.test_periodic_task": {
        "task": "app.core.tasks.test_periodic_task",
        "schedule": crontab(hour="0", minute="0"),
    },
    # App Setting
    "app.app_setting.tasks.periodic_task_notify_expired_lwa_credential_setting": {
        "task": "app.app_setting.tasks.periodic_task_notify_expired_lwa_credential_setting",
        "schedule": crontab(hour="0", minute="0"),
    },
    "app.app_setting.tasks.periodic_task_reopen_urls_callback_fail": {
        "task": "app.app_setting.tasks.periodic_task_reopen_urls_callback_fail",
        "schedule": crontab(hour="8", minute="0"),
    },
    # Payments
    # "app.payments.tasks.notify_low_balance": {
    #     "task": "app.payments.tasks.notify_low_balance",
    #     "schedule": crontab(hour="0", minute="0")
    # },
}
