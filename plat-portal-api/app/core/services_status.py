import asyncio
import json
from datetime import datetime

import sendgrid
from allauth.socialaccount.models import SocialApp
from django.conf import settings
from django.core.cache import cache
from google.cloud import storage

from app.core.firebase import fire_base_set_key_value


def _check_hourly(_datetime):
    return f"{_datetime.date()}-{_datetime.hour}"


HOUR = _check_hourly(datetime.utcnow())


async def check_sendgrid() -> dict:
    is_enabled = False
    is_healthy = False
    message = "ERROR"

    if settings.EMAIL_HOST == "smtp.sendgrid.net":
        is_enabled = True
        _hour = _check_hourly(datetime.utcnow())
        if _hour == HOUR:
            is_healthy = True
            message = "OK"
        else:
            try:
                sg = sendgrid.SendGridAPIClient(api_key=settings.EMAIL_HOST_PASSWORD)
                data = {
                    "personalizations": [
                        {
                            "to": [{"email": "test@example.com"}],
                            "subject": "Sending with SendGrid is Fun",
                        }
                    ],
                    "from": {"email": settings.DJANGO_DEFAULT_FROM_EMAIL},
                    "content": [
                        {
                            "type": "text/plain",
                            "value": "and easy to do anywhere, even with Python",
                        }
                    ],
                }
                _ = sg.client.mail.send.post(request_body=data)
                is_healthy = True
                message = "OK"

            except Exception as err:
                message = f"{err}"
                is_healthy = False

    return {"is_enabled": is_enabled, "is_healthy": is_healthy, "message": message}


async def check_redis():
    is_enabled = True
    try:
        cache.set("foo", "bar")
        is_healthy = True
        message = "OK"
    except Exception as err:
        is_healthy = False
        message = f"{err}"
    return {
        "is_enabled": is_enabled,
        "is_healthy": is_healthy,
        "message": message,
    }


async def check_firebase_real_time_database():
    is_enabled = False
    is_healthy = False
    message = "ERROR"

    if settings.USER_CLIENT_FIRE_BASE_ENABLED:
        is_enabled = True
        try:
            fire_base_set_key_value("foo", "bar")
            is_healthy = True
            message = "OK"
        except Exception as err:
            is_healthy = False
            message = f"{err}"

    return {
        "is_enabled": is_enabled,
        "is_healthy": is_healthy,
        "message": message,
    }


async def check_gg_cloud_storage():
    is_enabled = False
    is_healthy = False
    message = "ERROR"

    if settings.GOOGLE_CLOUD_STORAGE_BUCKET_ACCESS_KEY:
        is_enabled = True
        try:

            client = storage.Client.from_service_account_json(
                settings.GOOGLE_CLOUD_STORAGE_BUCKET_ACCESS_KEY
            )
            bucket = client.get_bucket(settings.GOOGLE_CLOUD_STORAGE_BUCKET_NAME)
            is_healthy = bucket.exists()
            message = "OK"
        except Exception as err:
            is_healthy = False
            message = f"{err}"
    return {
        "is_enabled": is_enabled,
        "is_healthy": is_healthy,
        "message": message,
    }


async def check_google_oauth2():
    is_enabled = False
    is_healthy = False
    message = "ERROR"

    if settings.CREDENTIAL_GOOGLE_AUTH_PATH:
        is_enabled = True
        try:
            # compare app config and credential
            google_app = SocialApp.objects.get(provider="google")
            with open(settings.CREDENTIAL_GOOGLE_AUTH_PATH) as f:
                google_auth = json.load(f)
                web_config = google_auth.get("web")
                if google_app.client_id == web_config.get(
                    "client_id", ""
                ) and google_app.secret == web_config.get("client_secret", ""):
                    is_healthy = True
                    message = "OK"
        except SocialApp.DoesNotExist:
            is_healthy = False
            message = "Not config social app for google login"
        except Exception as err:
            is_healthy = False
            message = f"{err}"

    return {
        "is_enabled": is_enabled,
        "is_healthy": is_healthy,
        "message": message,
    }


async def checking_status():
    # asynchronous
    # avoid blocking IO from multiple cloud services
    (
        _sendgrid,
        redis,
        firebase_realtime_db,
        gg_cloud_storage,
        google_oauth2,
    ) = await asyncio.gather(
        *[
            check_redis(),
            check_sendgrid(),
            check_firebase_real_time_database(),
            check_gg_cloud_storage(),
            check_google_oauth2(),
        ]
    )

    # temp = await asyncio.gather(check_google_oauth2())

    return {
        "sendgrid": _sendgrid,
        "redis": redis,
        "firebase_realtime_db": firebase_realtime_db,
        "gg_cloud_storage": gg_cloud_storage,
        "google_oauth2": google_oauth2,
    }
