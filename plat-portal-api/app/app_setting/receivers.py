import sys

from django.db.models.signals import post_save
from django.dispatch import receiver

from app.app_setting.models import LWACredentialClientSetting
from app.app_setting.tasks import task_run_send_lwa_credential_setting_to_service

django_command = sys.argv[1]


@receiver(post_save, sender=LWACredentialClientSetting)
def signal_user(**kwargs):
    if django_command == "test":
        return
    instance = kwargs.get("instance")
    url_callbacks = instance.url_callbacks
    for url in url_callbacks:
        task_run_send_lwa_credential_setting_to_service.apply_async(
            kwargs={
                "app_id": instance.app_id,
                "service_url": url,
            }
        )
