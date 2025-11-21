from rest_framework.views import exception_handler

from .utils import response_error

from .exceptions import GenericException
from app.core.logger import logger


def api_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    logger.exception(exc)
    response = exception_handler(exc, context)
    if not response:
        return response_error(exc)

    # Now add the HTTP status code to the response.
    if isinstance(exc, GenericException):
        response.data = exc.serialize()

    return response
