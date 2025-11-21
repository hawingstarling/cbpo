from datetime import datetime, timezone
from typing import List
from urllib.parse import urljoin

import requests
from django.conf import settings
from django.db.models import F, ExpressionWrapper, fields

from app.app_setting.models import LWACredentialClientSetting
from app.core.logger import logger
from app.tenancies.services import EmailService


def query_lwa_setting_being_expired() -> List[LWACredentialClientSetting]:
    """
    query lwa settings are being expired
    """
    rs = LWACredentialClientSetting.objects.annotate(
        notify_date=ExpressionWrapper(
            F("date_expired") - F("days_scheduled_notification"),
            output_field=fields.DateTimeField(),
        )
    ).filter(notify_date__lte=datetime.now(tz=timezone.utc))
    return rs


def notify_a_lwa_setting(lwa_setting: LWACredentialClientSetting):
    logger.info(f"send_lwa_setting_to_services app_id: {lwa_setting.app_id}")
    url = urljoin(
        base=settings.BASE_URL,
        url=f"/admin/app_setting/lwacredentialclientsetting/{lwa_setting.id}/change/",
    )
    EmailService.send_notify_lwa_setting(
        app_lwa_id=lwa_setting.app_id,
        app_lwa_name=lwa_setting.app_name,
        date_expired=lwa_setting.date_expired.strftime("%Y-%m-%d %H:%M:%S"),
        url_django_admin=url,
        emails=list(lwa_setting.emails),
    )


def send_lwa_setting_to_service(
    lwa_setting: LWACredentialClientSetting,
    service_url: str,
    connect_timeout=None,
    read_timeout=None,
):
    logger.info(f"send_lwa_setting_to_services url: {service_url}")
    headers = {"authorization": settings.INTERNAL_TOKEN}
    data = {
        "app_id": lwa_setting.app_id,
        "lwa_client_id": lwa_setting.lwa_client_id,
        "lwa_client_secret": lwa_setting.plain_text_lwa_secret_key,
        "date_expired": lwa_setting.date_expired.strftime("%Y-%m-%d %H:%M:%S"),
    }
    response = requests.post(
        url=service_url,
        data=data,
        headers=headers,
        timeout=(connect_timeout, read_timeout),
    )
    return response
