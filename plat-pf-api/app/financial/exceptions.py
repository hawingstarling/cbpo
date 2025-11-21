from rest_framework import status

from app.core.exceptions import GenericException


class SaleItemPayloadsException(GenericException):
    code = 2001
    summary = 'Invalid request'

    def __init__(self, message=None, verbose=False):
        status_code = status.HTTP_400_BAD_REQUEST
        if not message:
            message = "Invalid param request"
        self.verbose = verbose
        super().__init__(message=message, status_code=status_code)


class CustomObjNotFoundException(GenericException):
    code = 2002
    summary = 'Invalid share model'

    def __init__(self, message=None, verbose=False):
        status_code = status.HTTP_400_BAD_REQUEST
        if not message:
            message = "Invalid param request"
        self.verbose = verbose
        super().__init__(message=message, status_code=status_code)


class ShareCustomException(GenericException):
    code = 2003
    summary = 'Invalid share custom error'

    def __init__(self, message=None, verbose=False):
        status_code = status.HTTP_400_BAD_REQUEST
        if not message:
            message = "Invalid param request"
        self.verbose = verbose
        super().__init__(message=message, status_code=status_code)


class UserPermissionsException(GenericException):
    code = 2004
    summary = 'Invalid user permissions'

    def __init__(self, message=None, verbose=False):
        status_code = status.HTTP_400_BAD_REQUEST
        if not message:
            message = "Invalid param request"
        self.verbose = verbose
        super().__init__(message=message, status_code=status_code)


class ClientPortalSyncException(GenericException):
    code = 2005
    summary = 'Invalid client portal'

    def __init__(self, message=None, verbose=False):
        status_code = status.HTTP_400_BAD_REQUEST
        if not message:
            message = "Invalid param request"
        self.verbose = verbose
        super().__init__(message=message, status_code=status_code)


class InvalidBrandSettingException(GenericException):
    code = 2005
    summary = 'Invalid brand setting'

    def __init__(self, message=None):
        if not message:
            message = "Invalid brand setting"
        super().__init__(message=message, status_code=status.HTTP_400_BAD_REQUEST)


class InvalidDatasourceStatusException(GenericException):
    code = 2006
    summary = 'Invalid data source status'

    def __init__(self, message=None):
        if not message:
            message = "Invalid data source status"
        super().__init__(message=message, status_code=status.HTTP_400_BAD_REQUEST)


class RevertBulkSyncException(GenericException):
    code = 2007
    summary = 'Revert bulk sync invalid'

    def __init__(self, message=None):
        if not message:
            message = "Revert bulk sync invalid"
        super().__init__(message=message, status_code=status.HTTP_400_BAD_REQUEST)


class InvalidBrandException(GenericException):
    code = 2008
    summary = 'Invalid Brand Action'

    def __init__(self, message=None):
        if not message:
            message = "Invalid brand action"
        super().__init__(message=message, status_code=status.HTTP_400_BAD_REQUEST)


class InvalidClientACException(GenericException):
    code = 2009
    summary = 'Invalid Client AC Service'

    def __init__(self, message=None, verbose=False):
        if not message:
            message = "Invalid client register AC service"
        self.verbose = verbose
        super().__init__(message=message, status_code=status.HTTP_400_BAD_REQUEST)


class DivisionMaxLimitException(GenericException):
    code = 2010
    summary = 'Divisions Max Limit'

    def __init__(self, message=None, verbose=False):
        if not message:
            message = "Division max limit is reached"
        self.verbose = verbose
        super().__init__(message=message, status_code=status.HTTP_400_BAD_REQUEST)