from rest_framework.exceptions import APIException
from rest_framework import status


class GenericException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST

    code = 1000
    summary = 'Error'
    verbose = False

    def __init__(self, message=None, status_code=400):
        if not message:
            message = 'We hit a snag. Please check your internet connection and try'
        if status:
            self.status_code = status_code
        super().__init__(message)

    def serialize(self):
        return {
            'code': self.code,
            'message': self.detail,
            'summary': self.summary
        }


class ObjectNotFoundException(GenericException):
    code = 1001

    def __init__(self, message=None, object_id=None, verbose=False):
        if not message:
            message = 'Object not found: [%s] ' % object_id
        self.verbose = verbose
        super().__init__(message)


class MissingRequiredFieldException(GenericException):
    code = 1002

    def __init__(self, message=None, field_name=None):
        if not message:
            message = 'Missing required field: [%s] ' % field_name
        super().__init__(message)


class InvalidParameterException(GenericException):
    code = 1005

    def __init__(self, message=None):
        super().__init__(message=message)


class InvalidUploadFormException(GenericException):
    code = 1006

    def __init__(self, message=None):
        super().__init__(message=message)


class NameExistsException(GenericException):
    code = 1007
    verbose = True

    def __init__(self, message=None):
        super().__init__(message=message)


class MemberExistsException(GenericException):
    code = 1009
    verbose = True

    def __init__(self, message: str = None):
        status_code = status.HTTP_409_CONFLICT
        if not message:
            message = 'This user is already in the organization.'
        super().__init__(message=message, status_code=status_code)


class EmailDoesNotExistException(GenericException):
    code = 1010

    def __init__(self):
        status_code = status.HTTP_406_NOT_ACCEPTABLE
        message = 'This email does not exist in the system.'
        super().__init__(message=message, status_code=status_code)


class TokenHasNotBeenCreatedException(GenericException):
    code = 1011

    def __init__(self):
        status_code = status.HTTP_404_NOT_FOUND
        message = 'Your token has not been created.'
        super().__init__(message=message, status_code=status_code)


class InvalidTokenException(GenericException):
    code = 1012

    def __init__(self, message: str = 'The token is invalid.', verbose: bool = False):
        status_code = status.HTTP_406_NOT_ACCEPTABLE
        self.verbose = verbose
        super().__init__(message=message, status_code=status_code)


class InvalidCodeException(GenericException):
    code = 1013

    def __init__(self):
        status_code = status.HTTP_406_NOT_ACCEPTABLE
        message = 'The code is invalid.'
        super().__init__(message=message, status_code=status_code)


class CodeUsedException(GenericException):
    code = 1014

    def __init__(self):
        status_code = status.HTTP_406_NOT_ACCEPTABLE
        message = 'The code is used before.'
        super().__init__(message=message, status_code=status_code)


class EmailIsUsedException(GenericException):
    code = 1015

    def __init__(self):
        status_code = status.HTTP_409_CONFLICT
        message = 'The email is used.'
        super().__init__(message=message, status_code=status_code)


class UserIsActivatedException(GenericException):
    code = 1016

    def __init__(self):
        status_code = status.HTTP_409_CONFLICT
        message = 'User is activated.'
        super().__init__(message=message, status_code=status_code)


class StatusConflictException(GenericException):
    code = 1017

    def __init__(self):
        status_code = status.HTTP_409_CONFLICT
        message = 'Status is conflict.'
        super().__init__(message=message, status_code=status_code)


class InvalidFormatException(GenericException):
    code = 1019

    def __init__(self, message: str = None, verbose: bool = False):
        status_code = status.HTTP_406_NOT_ACCEPTABLE
        self.verbose = verbose
        super().__init__(message=message, status_code=status_code)


class RegisteredWithoutVerificationException(GenericException):
    code = 1020
    summary = 'Registered Without Verification'
    verbose = True

    def __init__(self):
        status_code = status.HTTP_409_CONFLICT
        message = "Your chosen email is already registered without verification. Please use forgot password feature " \
                  "to change your password and verify your email."
        super().__init__(message=message, status_code=status_code)


class LoginWithoutVerificationException(GenericException):
    code = 1021
    summary = 'Loign from account not verified.'
    verbose = True

    def __init__(self):
        status_code = status.HTTP_406_NOT_ACCEPTABLE
        message = "Your email has not been verified. Please use forgot password feature to change your password and verify your email"
        super().__init__(message=message, status_code=status_code)


class InvalidShareCustomException(GenericException):
    code = 1022

    def __init__(self, message):
        status_code = status.HTTP_406_NOT_ACCEPTABLE
        super().__init__(message=message, status_code=status_code)


class JwtTokenRequiredException(GenericException):
    code = 1023
    summary = 'JWT Token Required'

    def __init__(self):
        status_code = status.HTTP_404_NOT_FOUND
        message = 'JWT Token is required.'
        super().__init__(message=message, status_code=status_code)


class CustomViewUniqueException(GenericException):
    code = 1024
    summary = 'Name Request Duplicate'

    def __init__(self, viewname: str = None):
        status_code = status.HTTP_400_BAD_REQUEST
        message = f"'{viewname}' is not available. Please choose another name."
        super().__init__(message=message, status_code=status_code)


class ServicesErrorException(GenericException):

    def __init__(self, message='Services error'):
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        super().__init__(message=message, status_code=status_code)


class SqlExecutionException(GenericException):

    def __init__(self, message: str = 'Sql Execution Error'):
        status_code = status.HTTP_400_BAD_REQUEST
        super().__init__(message=message, status_code=status_code)


class ClientUserException(GenericException):
    code = 1025
    summary = 'Workspace user settings'

    def __init__(self, message=None, verbose=False):
        status_code = status.HTTP_400_BAD_REQUEST
        if not message:
            message = "User has not found in Workspace"
        self.verbose = verbose
        super().__init__(message=message, status_code=status_code)


class AnalysisDataException(GenericException):
    code = 1026
    summary = 'Analysis data permissions'

    def __init__(self, message=None, verbose=False):
        status_code = status.HTTP_403_FORBIDDEN
        if not message:
            message = "User has not permissions access data analysis"
        self.verbose = verbose
        super().__init__(message=message, status_code=status_code)


class PSServiceException(GenericException):
    code = 1027
    summary = 'portal_service_errors'

    def __init__(self, status_code: int = status.HTTP_400_BAD_REQUEST, message=None, verbose=False):
        if not message:
            message = "PS service error when call service"
        self.verbose = verbose
        super().__init__(message=message, status_code=status_code)


class NotWorkspaceDSException(GenericException):
    code = 1029
    summary = 'not_workspace_proxy_ds'

    def __init__(self, message=None, verbose=False):
        status_code = status.HTTP_400_BAD_REQUEST
        if not message:
            message = "Workspace Identity 'X-Ps-Client-Id' were not provided in request headers."
        self.verbose = verbose
        super().__init__(message=message, status_code=status_code)


class ACServiceError(GenericException):
    code = 1030
    summary = 'ac_service_errors'

    def __init__(self, status_code: int = status.HTTP_400_BAD_REQUEST, message=None, verbose=False):
        if not message:
            message = "AC service error when call service."
        self.verbose = verbose
        super().__init__(message=message, status_code=status_code)


class InternalTokenRequiredException(GenericException):
    code = 1031
    summary = 'Internal Token Required'

    def __init__(self):
        status_code = status.HTTP_404_NOT_FOUND
        message = 'Internal Token is required.'
        super().__init__(message=message, status_code=status_code)


class FedExException(GenericException):
    code = 1032
    summary = 'FedEx shipment permissions'

    def __init__(self, message=None, verbose=False):
        status_code = status.HTTP_403_FORBIDDEN
        if not message:
            message = "User doesn't have permissions to access FedEx shipment"
        self.verbose = verbose
        super().__init__(message=message, status_code=status_code)


class OrganizationSyncException(GenericException):
    code = 1033
    summary = 'Invalid Organization'

    def __init__(self, message=None, verbose=False):
        status_code = status.HTTP_400_BAD_REQUEST
        if not message:
            message = "Invalid param request"
        self.verbose = verbose
        super().__init__(message=message, status_code=status_code)


class WhileListException(GenericException):
    code = 1034
    summary = 'Invalid IP Addr'

    def __init__(self, message=None, verbose=False):
        status_code = status.HTTP_401_UNAUTHORIZED
        if not message:
            message = "Your Ip Addr not accept, Please contact with administrator!"
        self.verbose = verbose
        super().__init__(message=message, status_code=status_code)


class InternalTokenInvalidException(GenericException):
    code = 1035
    summary = 'Internal Token Invalid'

    def __init__(self, message=None, verbose=False):
        status_code = status.HTTP_403_FORBIDDEN
        if not message:
            message = 'Internal Token invalid.'
        self.verbose = verbose
        super().__init__(message=message, status_code=status_code)
