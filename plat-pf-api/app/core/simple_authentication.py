import logging
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import AccessToken

from app.core.context import AppContext
from app.core.services.workspace_management import WorkspaceManagement

logger = logging.getLogger(__name__)


class JWTTokenHandlerAuthentication(JWTAuthentication):
    def authenticate(self, request):
        """
        Returns a two-tuple of `User` and token if a valid signature has been
        supplied using JWT-based authentication.  Otherwise, returns `None`.
        """
        AppContext.instance().clean()

        header = self.get_header(request)
        if header is None:
            return None

        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None

        jwt_value = self.get_validated_token(raw_token)
        self.load_app_context(request, jwt_value)

        user = None

        return (user, jwt_value)

    def load_app_context(self, request: any = None, jwt_token: AccessToken = None):
        try:
            context = AppContext.instance()
            payloads = jwt_token.payload
            user_id = payloads.get('user_id')
            user_email = payloads.get('email')
            view_kwargs = request.parser_context.get("kwargs", {}) if hasattr(request, 'parser_context') else {}
            client_id = str(view_kwargs.get('client_id')) if 'client_id' in view_kwargs else None
            if not client_id and hasattr(request, 'META'):
                client_id = request.META.get('HTTP_X_PS_CLIENT_ID', None)
            context.jwt_token = jwt_token.token.decode("utf-8")
            context.user_id = user_id
            context.user_email = user_email
            context.client_id = client_id
            context.request = request
            if context.client_id:
                if request.path.endswith('/setting-permissions'):
                    logger.info(f"[JWTTokenHandlerAuthentication][load_app_context][request_path]: {request.path}")
                    WorkspaceManagement(client_id=context.client_id, jwt_token=context.jwt_token) \
                        .sync_client_setting_user_ps(user_id=context.user_id)
        except Exception as ex:
            logger.error("[JWTTokenHandlerAuthentication][load_app_context] {}".format(ex))
            raise ex
