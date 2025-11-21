from rest_framework import status

from app.core.exceptions import GenericException


class UserClientMemberException(GenericException):
    summary = 'User does not belong to the client'
    verbose = True

    def __init__(self, message=None):
        status_code = status.HTTP_403_FORBIDDEN
        if not message:
            message = "User does not belong to the client"
        super().__init__(message=message, status_code=status_code)


class PermissionGroupLevelException(GenericException):
    summary = 'Permissions Groups Level'
    verbose = True

    def __init__(self, message_content: str = None, level: str = None):
        status_code = status.HTTP_400_BAD_REQUEST
        if level:
            self.summary = "Permissions Groups {} Level".format(level)
        message = "We don't action permissions groups {} level".format(level)
        if message_content:
            message = message_content
        super().__init__(message=message, status_code=status_code)


class CustomRoleLevelException(GenericException):
    summary = 'Custom Role Level'
    verbose = True

    def __init__(self, message_content: str = None, level: str = None):
        status_code = status.HTTP_400_BAD_REQUEST
        if level:
            self.summary = "Custom Role {} Level".format(level)
        message = "We don't action with custom role {} level".format(level)
        if message_content:
            message = message_content
        super().__init__(message=message, status_code=status_code)


class UserLevelCustomRolePermissionException(GenericException):
    summary = 'User Custom Role Permission Level'
    verbose = True

    def __init__(self, message_content: str = None, level: str = None):
        status_code = status.HTTP_400_BAD_REQUEST
        if level:
            self.summary = "User Custom Role Permission {} Level".format(level)
        message = "We don't action with user custom role permission {} level".format(level)
        if message_content:
            message = message_content
        super().__init__(message=message, status_code=status_code)


class AccessRuleException(GenericException):
    summary = 'Access Rule Exception'
    verbose = True

    def __init__(self, message=summary):
        status_code = status.HTTP_400_BAD_REQUEST
        super().__init__(message=message, status_code=status_code)


class PermissionOnChangesException(GenericException):
    summary = "Custom Role & Access Rule Exception"
    verbose = True

    def __init__(self, message=summary):
        status_code = status.HTTP_403_FORBIDDEN
        super().__init__(message=message, status_code=status_code)
