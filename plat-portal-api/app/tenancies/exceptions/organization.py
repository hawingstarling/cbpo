from app.core.exceptions import GenericException
from rest_framework import status


class AccessClientException(GenericException):
    code = 2001
    verbose = True

    def __init__(self, message: str = "You have role admin to all client."):
        status_code = status.HTTP_403_FORBIDDEN
        super().__init__(message=message, status_code=status_code)


class UniqueClientOrganizationException(GenericException):
    code = 2002
    verbose = True

    def __init__(self,
                 message: str = "That workspace name is not available, please choose another name or ask administrator to have access."):
        status_code = status.HTTP_409_CONFLICT
        super().__init__(message=message, status_code=status_code)
