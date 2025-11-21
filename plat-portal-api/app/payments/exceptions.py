from rest_framework import status

from app.core.exceptions import GenericException


class __PaymentGenericException(GenericException):
    code = "payments"
    summary = "Payment App Error"


class NotHandleAppException(GenericException):
    summary = "Not implemented Error"

    def __init__(self, message="Not implemented for your app"):
        super(NotHandleAppException, self).__init__(
            message, status_code=status.HTTP_406_NOT_ACCEPTABLE
        )


class OrganizationSubscribedPlanException(__PaymentGenericException):
    def __init__(self, message="The organization has already subscribed a plan"):
        super().__init__(message=message, status_code=status.HTTP_400_BAD_REQUEST)


class OrganizationHasNotSubscribedAnyPlanException(__PaymentGenericException):
    def __init__(self, message="The organization has not subscribed any plans"):
        super(OrganizationHasNotSubscribedAnyPlanException, self).__init__(
            message=message, status_code=status.HTTP_400_BAD_REQUEST
        )


class HandleSubscriptionOnlyException(__PaymentGenericException):
    def __init__(
            self, message="Ignore transactions which are not relevant to subscription"
    ):
        super().__init__(message=message, status_code=status.HTTP_406_NOT_ACCEPTABLE)


class InvoiceItemException(__PaymentGenericException):
    summary = "Invoice Item Error!"

    def __init__(self, message=None, status_code=status.HTTP_400_BAD_REQUEST):
        if not message:
            message = self.summary
        super().__init__(message=message, status_code=status_code)


class IntegrityException(__PaymentGenericException):
    summary = "not enough balance"

    def __init__(self, message=None, status_code=status.HTTP_406_NOT_ACCEPTABLE):
        if not message:
            message = self.summary
        super().__init__(message=message, status_code=status_code)


class InvalidCouponException(__PaymentGenericException):
    code = 'invalid_coupon'
    summary = 'invalid promo code'

    def __init__(self, message=None, status_code=status.HTTP_406_NOT_ACCEPTABLE):
        if not message:
            message = self.summary
        super().__init__(message=message, status_code=status_code)


class DuplicatedCouponUsageException(__PaymentGenericException):
    code = 'duplicated_coupon_usage'
    summary = 'duplicated coupon usage'

    def __init__(self, message=None, status_code=status.HTTP_406_NOT_ACCEPTABLE):
        if not message:
            message = self.summary
        super().__init__(message=message, status_code=status_code)
