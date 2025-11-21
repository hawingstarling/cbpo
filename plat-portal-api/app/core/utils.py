import logging
from datetime import datetime
from os import urandom
from pytz import utc
from rest_framework.response import Response
from .exceptions import *
from .context import AppContext

logger = logging.getLogger('plat.portal')


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


def get_app_name_profile():
    return AppContext.instance().app_name_profile


def get_all_module_enum_profile():
    return AppContext.instance().all_module_enum


def get_modules_app_profile():
    return AppContext.instance().modules_app


def get_module_permissions_app_profile():
    return AppContext.instance().module_permissions_app


def get_permissions_app_profile():
    return AppContext.instance().permissions_app
