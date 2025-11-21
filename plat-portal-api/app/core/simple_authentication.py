import logging
from typing import Union
from rest_framework_simplejwt.authentication import JWTAuthentication, JWTTokenUserAuthentication
from rest_framework_simplejwt.state import token_backend
from rest_framework_simplejwt.tokens import AccessToken
from app.core.context import AppContext
from app.core.services.app_confg import AppService

logger = logging.getLogger(__name__)


class JWTTokenHandlerAuthentication(JWTAuthentication):
    def authenticate(self, request):
        """
        Returns a two-tuple of `User` and token if a valid signature has been
        supplied using JWT-based authentication.  Otherwise, returns `None`.
        """
        # AppContext.instance().clean()

        header = self.get_header(request)
        if header is None:
            return None

        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None
        #@TODO: Recheck if this is necessary
        validated_token = self.get_validated_token(raw_token)
        self.load_app_context(request, validated_token)

        return self.get_user(validated_token), validated_token

    def load_app_context(self, request: any = None, jwt_token: AccessToken = None):
        # do something only if request contains a Bearer token
        if request.META.get("HTTP_AUTHORIZATION", "").startswith("Bearer"):
            # Update app config
            try:
                payloads = jwt_token.payload
                app_name = payloads.get('app', None)
                # app_name = get_app_name_profile(jwt_value=jwt_token)
                context = AppContext.instance()
                if jwt_token and app_name is not None and context.app_name_profile != app_name:
                    # show info
                    logger.info(f"[{self.__class__.__name__}]: jwt_value : {jwt_token}, app name : {app_name}")
                    # write info app , module config for jwt request
                    context.app_name_profile = app_name
                    context.all_module_enum = AppService.get_all_module_enum()
                    context.modules_app = AppService.get_modules_app(app_name=app_name)
                    context.module_permissions_app = AppService.get_module_permissions_app(app_name=app_name)
                    context.permissions_app = AppService.get_permissions_app(app_name=app_name)
            except Exception as ex:
                logger.error(f"[{self.__class__.__name__}] {ex}")


def get_app_name_from_request(request) -> Union[str, None]:
    try:
        jwt_user_authentication = JWTTokenUserAuthentication()
        header = jwt_user_authentication.get_header(request)
        if header is None:
            return None
        jwt_value = jwt_user_authentication.get_raw_token(header)
        payload = token_backend.decode(jwt_value)
    except Exception as err:
        logger.error(f"{err}")
        return None
    return payload.get("app", None)
