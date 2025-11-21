import hashlib
import json
import logging
import sys
from datetime import datetime
from os import urandom
from typing import Any

from django.db import DEFAULT_DB_ALIAS
from twilio.rest import Client
from django.conf import settings
from pytz import utc
from rest_framework.response import Response
from .exceptions import *
from ..selling_partner.models import AppSetting

logger = logging.getLogger(__name__)

next_cent = settings.PLAT_IMPORT_CURRENCY_NEXT_CENT if hasattr(settings, 'PLAT_IMPORT_CURRENCY_NEXT_CENT') else 0
TESTING = sys.argv[1] == "test"


def has_valid_value(value):
    if isinstance(value, str):
        return bool(value.strip())  # Non-empty string
    elif isinstance(value, list):
        return bool(value)  # Non-empty list
    return False  # Neither string nor list


def hashlib_content(data: Any, algorthm: str = 'md5'):
    method_action = getattr(hashlib, algorthm.lower())
    hash_content = method_action(json.dumps(data).encode('utf-8')).hexdigest()
    return hash_content


def round_currency(value):
    _round = round(value, 2)
    _temp = _round - value
    if _temp >= 0:
        value = _round
    else:
        value = round(_round + next_cent, 2)
    return value


def get_now():
    return datetime.now(tz=utc)


def response_error(ex, status_code=400):
    if not isinstance(ex, GenericException):
        ex = GenericException(message=str(ex), status_code=status_code)
    print(ex.detail)
    error_message = "Oops! We hit a snag. Please try again in a bit."
    if ex.verbose is True:
        error_message = str(ex)

    error_data = {'code': ex.code, 'message': error_message, 'summary': ex.summary}
    return Response(data=error_data, status=ex.status_code)


def generate_password(length=20):
    chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    re = []
    for c in urandom(length - 1):
        t = chars[int(c) % len(chars)]
        l = len(re)
        if l % 2 == 0:
            t = t.lower()

        if l == int(length / 2):
            re.append("@")

        re.append(t)

    return "".join(re)


def is_number(s):
    try:
        if s is None:
            return False
        float(str(s))  # for int, long and float
    except ValueError:
        return False
    return True


def get_nested_attr(obj: object, path: str, default=None):
    attributes = path.split('.')
    value = obj
    for attr in attributes:
        value = getattr(value, attr, None)
        if value is None:
            return default
    return value


def send_twilio_message(to_number, body):
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

    return client.messages.create(
        body=body,
        to=to_number,
        from_=settings.TWILIO_PHONE_NUMBER,
        provide_feedback=True
    )


def convert_result_from_request_api(rs):
    try:
        status_code = rs.status_code
        try:
            content = json.loads(rs.content.decode('utf-8'))
        except Exception as ex:
            content = {}
    except Exception as ex:
        logger.error(f"[convert_result_from_request_api] {ex}")
        status_code = status.HTTP_400_BAD_REQUEST
        content = {}
    return status_code, content


def check_current_is_test_env():
    try:
        is_test = sys.argv[1] == "test"
    except Exception as ex:
        is_test = False
    return is_test


def get_name_from_email(email):
    try:
        assert email is not None, f"[get_name_from_email] Email is not Nonetype"
        # Split the email at '@' and take the local part
        local_part = email.split('@')[0]

        # Replace dots or underscores with spaces and capitalize each word
        name_parts = local_part.replace('.', ' ').replace('_', ' ').title()

        return name_parts
    except Exception as ex:
        return None


def get_app_setting_latest(client_id: str):
    return AppSetting.objects.tenant_db_for(client_id).last()
