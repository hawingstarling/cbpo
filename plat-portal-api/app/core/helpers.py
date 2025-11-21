from rest_framework_simplejwt.state import token_backend
from allauth.account.models import EmailAddress


def get_app_name_profile(jwt_value):
    try:
        payloads = token_backend.decode(jwt_value, verify=True)
        app_name = payloads.get('app', None)
    except Exception as ex:
        app_name = None
    return app_name


def email_address_exists(email, exclude_user=None):
    email_addresses = EmailAddress.objects
    if exclude_user:
        email_addresses = email_addresses.exclude(user=exclude_user)
    ret = email_addresses.filter(email__iexact=email).exists()
    return ret
