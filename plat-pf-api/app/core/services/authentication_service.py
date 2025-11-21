from calendar import timegm
from datetime import datetime, timedelta

from django.conf import settings
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.backends import TokenBackend
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.state import token_backend

from app.core.exceptions import JwtTokenRequiredException
from app.financial.models import User

APP_REQUEST_AUDIENCE = "precise_financial"


class AuthenticationService:

    def __init__(self):
        pass

    @staticmethod
    def get_jwt_request(request: any = None):
        jwt_auth = JWTAuthentication()
        header = jwt_auth.get_header(request)
        if header is None:
            return None

        raw_token = jwt_auth.get_raw_token(header)
        if raw_token is None:
            return None

        jwt_token = jwt_auth.get_validated_token(raw_token)
        if not jwt_token:
            raise JwtTokenRequiredException()
        jwt_token = jwt_token.token.decode('utf-8')
        return jwt_token

    @staticmethod
    def generate_jwt_token_signature(client_id: str, user_id: str = None):
        # create payload
        user = User.objects.tenant_db_for(client_id).get(user_id=user_id)
        payload = {
            "user_id": str(user.pk),
            "username": user.email,
            "exp": datetime.utcnow() + timedelta(days=2),
            "email": user.email,
            "fname": user.first_name,
            "lname": user.last_name,
            "orig_iat": timegm(datetime.utcnow().utctimetuple()),
            "app": APP_REQUEST_AUDIENCE
        }
        return token_backend.encode(payload)

    @staticmethod
    def generate_jwt_token_internal_signature():
        token_backend_audience = TokenBackend(
            api_settings.ALGORITHM,
            api_settings.SIGNING_KEY,
            api_settings.VERIFYING_KEY,
            settings.JWT_AUDIENCE,
            api_settings.ISSUER,
            api_settings.JWK_URL,
            api_settings.LEEWAY,
            api_settings.JSON_ENCODER,
        )
        # create payload
        payload = {
            "exp": datetime.utcnow() + timedelta(minutes=5),  # set 5 minutes
            "orig_iat": timegm(datetime.utcnow().utctimetuple()),
            "app": APP_REQUEST_AUDIENCE
        }
        return token_backend_audience.encode(payload)

    @staticmethod
    def verify_jwt_token_signature(jwt_token: str = None, verify: bool = False):
        """
        This is method verify token jwt with time short expired
        :param jwt_token: 
        :param verify: 
        :return: 
        """""
        return token_backend.decode(jwt_token, verify=verify)

    @staticmethod
    def get_user_id_jwt_token(jwt_token: str = None):
        try:
            payload = AuthenticationService.verify_jwt_token_signature(jwt_token=jwt_token)
            return payload['user_id']
        except Exception as ex:
            return None

    @staticmethod
    def get_email_jwt_token(jwt_token: str = None):
        try:
            payload = AuthenticationService.verify_jwt_token_signature(jwt_token=jwt_token)
            return payload['email']
        except Exception as ex:
            return None
