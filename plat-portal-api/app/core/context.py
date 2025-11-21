import logging
import jwt
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication
from rest_framework_simplejwt.state import token_backend

from ..core.helpers import get_app_name_profile
from django.utils.deprecation import MiddlewareMixin
from ..core.services.app_confg import AppService
from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions
from ..tenancies.models import ClientModule

logger = logging.getLogger(__name__)


# jwt_decode_handler = api_settings.JWT_DECODE_HANDLER

class AppContext(object):
    """
    A singleton object to scrape META data from HTTP Request Header

    usage:
    ip_address = AppContext.instance().ip_address
    app_version = AppContext.instance().app_version

    @since sprint-v3.9
    """
    __instance = None

    def __init__(self):
        if AppContext.__instance is not None:
            return
        self._app_name_profile = None
        self._modules_app = None
        self._module_permissions_app = None
        self._all_module_enum = None
        self._permissions_app = None
        self._user = None
        self._request = None

        AppContext.__instance = self

    @staticmethod
    def instance():
        if AppContext.__instance is None:
            AppContext()
        return AppContext.__instance

    @property
    def app_name_profile(self):
        return self._app_name_profile

    @app_name_profile.setter
    def app_name_profile(self, value):
        self._app_name_profile = value

    @property
    def modules_app(self):
        return self._modules_app

    @modules_app.setter
    def modules_app(self, value):
        self._modules_app = value

    @property
    def module_permissions_app(self):
        return self._module_permissions_app

    @module_permissions_app.setter
    def module_permissions_app(self, value):
        self._module_permissions_app = value

    @property
    def all_module_enum(self):
        return self._all_module_enum

    def module_enabled(self, client_id: str):
        return ClientModule.objects.filter(client_id=client_id,
                                           module__in=self._all_module_enum,
                                           enabled=True).values_list('module', flat=True)

    @all_module_enum.setter
    def all_module_enum(self, value):
        self._all_module_enum = value

    @property
    def permissions_app(self):
        return self._permissions_app

    @permissions_app.setter
    def permissions_app(self, value):
        self._permissions_app = value

    def clean(self):
        self._app_name_profile = None
        self._modules_app = None
        self._module_permissions_app = None
        self._all_module_enum = None
        self._permissions_app = None
        self._user = None
        self._request = None


class PortalAppContextMiddleware(MiddlewareMixin):
    """ Middleware for authenticating JSON Web Tokens in Authorize Header """

    @staticmethod
    def get_jwt_value(request):
        jwt_user_authentication = JWTTokenUserAuthentication()
        header = jwt_user_authentication.get_header(request)
        if header is None:
            return None
        jwt_value = jwt_user_authentication.get_raw_token(request)
        if jwt_value is None:
            return None
        try:
            payload = token_backend.decode(jwt_value)
        except jwt.ExpiredSignature:
            msg = _('Signature has expired.')
            raise exceptions.AuthenticationFailed(msg)
        except jwt.DecodeError:
            msg = _('Error decoding signature.')
            raise exceptions.AuthenticationFailed(msg)
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed()

        return jwt_value

    def process_request(self, request):
        # do something only if request contains a Bearer token
        if request.META.get("HTTP_AUTHORIZATION", "").startswith("Bearer"):
            # Update app config
            try:
                jwt_value = self.get_jwt_value(request)
                app_name = get_app_name_profile(jwt_value=jwt_value)
                context = AppContext.instance()
                if jwt_value and app_name is not None and context.app_name_profile != app_name:
                    # show info 
                    logger.info(f"[{self.__class__.__name__}]: jwt_value : {jwt_value}, app name : {app_name}")
                    # write info app , module config for jwt request
                    context.app_name_profile = app_name
                    context.all_module_enum = AppService.get_all_module_enum()
                    context.modules_app = AppService.get_modules_app(app_name=app_name)
                    context.module_permissions_app = AppService.get_module_permissions_app(app_name=app_name)
                    context.permissions_app = AppService.get_permissions_app(app_name=app_name)
            except Exception as ex:
                logger.error(f"[{self.__class__.__name__}] {ex}")
