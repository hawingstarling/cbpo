from rest_framework import status
from rest_framework.exceptions import APIException


class ValueAPIException(APIException):
    status_code = status.HTTP_200_OK
