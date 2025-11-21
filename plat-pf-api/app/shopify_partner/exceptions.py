from rest_framework import status

from app.core.exceptions import GenericException


class ConfigShopifyPartnerException(GenericException):
    code = 'not_shopify_partner_config'

    def __init__(self, message=None):
        if not message:
            message = 'not_shopify_partner_config'
        super().__init__(message, status_code=status.HTTP_503_SERVICE_UNAVAILABLE)


class NotFoundShopifyPartnerOauthClientRegister(GenericException):
    code = 'shopify_partner_not_connected'

    def __init__(self, message=None):
        if not message:
            message = 'shopify_partner_not_connected'
        super().__init__(message, status_code=status.HTTP_404_NOT_FOUND)
