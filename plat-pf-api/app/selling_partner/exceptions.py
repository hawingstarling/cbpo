from rest_framework import status
from app.core.exceptions import GenericException


class ReportUniqueException(GenericException):
    code = 3000
    summary = 'Invalid request'

    def __init__(self, message=None, verbose=False):
        status_code = status.HTTP_400_BAD_REQUEST
        if not message:
            message = "Report is unique."
        self.verbose = verbose
        super().__init__(message=message, status_code=status_code)


class SPAPIReportException(GenericException):
    code = 3001
    summary = 'Permission SPAPI'

    def __init__(self, message=None, verbose=False):
        status_code = status.HTTP_400_BAD_REQUEST
        if not message:
            message = "Permission to disallow sending requests with report type."
        self.verbose = verbose
        super().__init__(message=message, status_code=status_code)
