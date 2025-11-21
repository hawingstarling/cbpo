from celery import current_app

from app.app_setting.models import (
    LWACredentialClientSetting,
    TrackingURLCallback,
)
from app.app_setting.services import (
    query_lwa_setting_being_expired,
    notify_a_lwa_setting,
    send_lwa_setting_to_service,
)
from app.core.logger import logger
from app.app_setting.config_static_variable import ERROR_STATUS_KEY, DONE_STATUS_KEY


@current_app.task(bind=True)
def task_run_send_lwa_credential_setting_to_service(self, app_id, service_url):
    logger.info(f"[{self.__class__.__name__}]")
    lwa_setting = LWACredentialClientSetting.objects.get(app_id=app_id)
    existing_tracking_instance = TrackingURLCallback.objects.filter(
        lwa_setting=lwa_setting, url=service_url
    ).first()

    if existing_tracking_instance:
        tracking_instance = existing_tracking_instance
    else:
        tracking_instance = TrackingURLCallback(
            lwa_setting=lwa_setting, url=service_url
        )

    try:
        response = send_lwa_setting_to_service(
            lwa_setting=lwa_setting, service_url=service_url
        )
        response.raise_for_status()
        tracking_instance.status = DONE_STATUS_KEY
    except Exception as error:
        tracking_instance.status = ERROR_STATUS_KEY
        tracking_instance.retry += 1
        tracking_instance.log = f"Fail to connect to {service_url}: {str(error)}"

    tracking_instance.save()
    return {"message": "success"}


@current_app.task(bind=True)
def task_run_notify_an_expired_lwa_credential_setting(self, app_id):
    logger.info(f"[{self.__class__.__name__}] app_id: {app_id}")
    lwa_setting = LWACredentialClientSetting.objects.get(app_id=app_id)
    notify_a_lwa_setting(lwa_setting)
    return {"message": "success"}


@current_app.task(bind=True)
def periodic_task_notify_expired_lwa_credential_setting(self):
    logger.info(f"[{self.__class__.__name__}]")
    qs = query_lwa_setting_being_expired()
    for ele in qs:
        task_run_notify_an_expired_lwa_credential_setting.apply_async(
            kwargs={"app_id": ele.app_id}
        )
    return {"message": f"notify {len(qs)} lwa settings"}


@current_app.task(bind=True)
def periodic_task_reopen_urls_callback_fail(self):
    logger.info(f"[{self.__class__.__name__}]")
    tracking_lwas = TrackingURLCallback.objects.select_related("lwa_setting").filter(
        status=ERROR_STATUS_KEY, retry__lt=3
    )
    for tracking_lwa in tracking_lwas:
        if tracking_lwa.url in tracking_lwa.lwa_setting.url_callbacks:
            try:
                response = send_lwa_setting_to_service(
                    lwa_setting=tracking_lwa.lwa_setting, service_url=tracking_lwa.url
                )
                response.raise_for_status()
                tracking_lwa.status = DONE_STATUS_KEY
            except Exception as error:
                tracking_lwa.status = ERROR_STATUS_KEY
                tracking_lwa.retry += 1
                tracking_lwa.log = (
                    f"Fail to connect to {tracking_lwa.url}: {str(error)}"
                )
            tracking_lwa.save()

    return {"message": "success"}
