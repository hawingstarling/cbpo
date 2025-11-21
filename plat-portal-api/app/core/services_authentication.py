from abc import ABC
from typing import Tuple

import jwt
from Crypto.PublicKey import RSA
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from jwt import InvalidAudienceError
from rest_framework import exceptions
from rest_framework_simplejwt.authentication import JWTAuthentication

from app.core.exceptions import ServicesAuthenException, ServiceJWTException


class __CustomJWTServices(ABC, JWTAuthentication):
    SERVICE_PUBLIC_KEY_PATH = settings.PUBLIC_KEY_PATH  # default

    def get_config(self) -> Tuple[bytes, str]:
        if not self.SERVICE_PUBLIC_KEY_PATH:
            raise ServicesAuthenException()

        with open(f"{settings.ROOT_DIR}{self.SERVICE_PUBLIC_KEY_PATH}") as file:
            return RSA.import_key(file.read()).export_key(), settings.SERVICE_AUDIENCE

    def jwt_decode_handler_services(self, token):
        """[summary]
        service need "audience" in payload with value "portal"
        from settings.SERVICE_AUDIENCE
        alg: RS256
        for example
        {
            "aud": "portal",
            ...
        }

        Args:
            token ([type]): [description]

        Returns:
            [type]: [description]
        """
        options = {"verify_exp": True}

        public_key, audience = self.get_config()

        return jwt.decode(
            jwt=token,
            key=public_key,
            verify=True,
            options=options,
            audience=audience,
            algorithms=["RS256"],
        )

    def authenticate(self, request):
        """
        Returns a two-tuple of `User` and token if a valid signature has been
        supplied using JWT-based authentication.  Otherwise, returns `None`.
        """
        header = self.get_header(request)
        if header is None:
            return None

        jwt_value = self.get_raw_token(header)
        if jwt_value is None:
            raise ServiceJWTException()

        try:
            self.jwt_decode_handler_services(jwt_value)
        except jwt.ExpiredSignatureError:
            msg = _("Signature has expired.")
            raise exceptions.AuthenticationFailed(msg)
        except jwt.DecodeError:
            msg = _("Error decoding signature.")
            raise exceptions.AuthenticationFailed(msg)
        except InvalidAudienceError:
            msg = _("Invalid audience.")
            raise exceptions.AuthenticationFailed(msg)
        return


class MWJSONWebTokenAuthentication(__CustomJWTServices):
    """CUSTOM JWT for app MW"""

    SERVICE_PUBLIC_KEY_PATH = settings.MW_PUBLIC_KEY_PATH


class DTDJSONWebTokenAuthentication(__CustomJWTServices):
    """CUSTOM JWT for app 2d Transit"""

    SERVICE_PUBLIC_KEY_PATH = settings.DTD_PUBLIC_KEY_PATH


class InternalJSONWebTokenAuthentication(__CustomJWTServices):
    """CUSTOM JWT for internal services: PF, SKU, AC, DTD, ..."""

    SERVICE_PUBLIC_KEY_PATH = settings.INTERNAL_PUBLIC_KEY_PATH
