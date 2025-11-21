from rest_framework.exceptions import APIException
from rest_framework import status


class GenericException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST

    code = 1000
    summary = "Error"
    verbose = False

    def __init__(self, message=None, status_code=400):
        if not message:
            message = "We hit a snag. Please check your internet connection and try"
        if status:
            self.status_code = status_code
        super().__init__(message)

    def serialize(self):
        return {"code": self.code, "message": self.detail, "summary": self.summary}


class RegisteredWithoutVerificationException(GenericException):
    code = 1020
    summary = "Registered Without Verification"
    verbose = True

    def __init__(self):
        status_code = status.HTTP_409_CONFLICT
        message = (
            "Your chosen email is already registered without verification. Please use forgot password feature "
            "to change your password and verify your email."
        )
        super().__init__(message=message, status_code=status_code)


class LoginWithoutVerificationException(GenericException):
    code = 1021
    summary = "Loign from account not verified."
    verbose = True

    def __init__(self):
        status_code = status.HTTP_406_NOT_ACCEPTABLE
        message = "Your email has not been verified. Please use forgot password feature to change your password and verify your email"
        super().__init__(message=message, status_code=status_code)


class ObjectNotFoundException(GenericException):
    code = 1001

    def __init__(self, message=None, object_id=None, verbose=False):
        if not message:
            message = "Object not found: [%s] " % object_id
        self.verbose = verbose
        super().__init__(message)


class MissingRequiredFieldException(GenericException):
    code = 1002

    def __init__(self, message=None, field_name=None):
        if not message:
            message = "Missing required field: [%s] " % field_name
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
            message = "This user is already in the organization."
        super().__init__(message=message, status_code=status_code)


class EmailDoesNotExistException(GenericException):
    code = 1010

    def __init__(self):
        status_code = status.HTTP_406_NOT_ACCEPTABLE
        message = "This email does not exist in the system."
        super().__init__(message=message, status_code=status_code)


class TokenHasNotBeenCreatedException(GenericException):
    code = 1011

    def __init__(self):
        status_code = status.HTTP_404_NOT_FOUND
        message = "Your token has not been created."
        super().__init__(message=message, status_code=status_code)


class InvalidTokenException(GenericException):
    code = 1012

    def __init__(self, message="The token is invalid."):
        status_code = status.HTTP_406_NOT_ACCEPTABLE
        super().__init__(message=message, status_code=status_code)


class InvalidCodeException(GenericException):
    code = 1013

    def __init__(self):
        status_code = status.HTTP_406_NOT_ACCEPTABLE
        message = "The code is invalid."
        super().__init__(message=message, status_code=status_code)


class CodeUsedException(GenericException):
    code = 1014

    def __init__(self):
        status_code = status.HTTP_406_NOT_ACCEPTABLE
        message = "The code is used before."
        super().__init__(message=message, status_code=status_code)


class EmailIsUsedException(GenericException):
    code = 1015

    def __init__(self):
        status_code = status.HTTP_409_CONFLICT
        message = "The email is used."
        super().__init__(message=message, status_code=status_code)


class UserIsActivatedException(GenericException):
    code = 1016

    def __init__(self):
        status_code = status.HTTP_409_CONFLICT
        message = "User is activated."
        super().__init__(message=message, status_code=status_code)


class StatusConflictException(GenericException):
    code = 1017

    def __init__(self):
        status_code = status.HTTP_409_CONFLICT
        message = "Status is conflict."
        super().__init__(message=message, status_code=status_code)


class InvalidFormatException(GenericException):
    code = 1019

    def __init__(self, mess):
        status_code = status.HTTP_406_NOT_ACCEPTABLE
        message = mess
        super().__init__(message=message, status_code=status_code)


class OwnerRoleUpdateException(GenericException):
    code = 1020

    def __init__(self):
        status_code = status.HTTP_406_NOT_ACCEPTABLE
        message = "The owner's role can not be changed."
        super().__init__(message=message, status_code=status_code)


class UserInvitationException(GenericException):
    code = 1021
    verbose = True

    def __init__(self):
        status_code = status.HTTP_406_NOT_ACCEPTABLE
        message = "User already have invitation."
        super().__init__(message=message, status_code=status_code)


class ServicesAuthenException(GenericException):
    def __init__(self):
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        message = "Not config services authentication."
        super().__init__(message=message, status_code=status_code)


class ServiceJWTException(GenericException):
    def __init__(self):
        status_code = status.HTTP_401_UNAUTHORIZED
        message = "requires JWT token for service"
        super().__init__(message=message, status_code=status_code)
