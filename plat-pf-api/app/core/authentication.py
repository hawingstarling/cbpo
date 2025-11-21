# import jwt, logging
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
# from rest_framework_jwt.utils import jwt_decode_handler
# from django.utils.translation import ugettext as _
# from rest_framework import exceptions
#
# from app.core.context import AppContext
# from app.core.services.authentication_service import AuthenticationService, PortalService
#
# logger = logging.getLogger(__name__)
#
#
# class JWTTokenHandlerAuthentication(JSONWebTokenAuthentication):
#     def authenticate(self, request):
#         """
#         Returns a two-tuple of `User` and token if a valid signature has been
#         supplied using JWT-based authentication.  Otherwise returns `None`.
#         """
#         AppContext.instance().clean()
#         jwt_value = self.get_jwt_value(request)
#         if jwt_value is None:
#             return None
#
#         try:
#             jwt_decode_handler(jwt_value)
#         except jwt.ExpiredSignature:
#             msg = _('Signature has expired.')
#             raise exceptions.AuthenticationFailed(msg)
#         except jwt.DecodeError:
#             msg = _('Error decoding signature.')
#             raise exceptions.AuthenticationFailed(msg)
#         except jwt.InvalidTokenError:
#             raise exceptions.AuthenticationFailed()
#
#         self.load_app_context(request, jwt_value)
#
#         user = None
#
#         return (user, jwt_value)
#
#     def load_app_context(self, request: any = None, jwt_token: str = None):
#         try:
#             context = AppContext.instance()
#             payloads = AuthenticationService.verify_jwt_token_signature(jwt_token=jwt_token)
#             user_id = payloads.get('user_id')
#             user_email = payloads.get('email')
#             view_kwargs = request.parser_context.get("kwargs", {}) if hasattr(request, 'parser_context') else {}
#             client_id = str(view_kwargs.get('client_id')) if 'client_id' in view_kwargs else None
#             if not client_id and hasattr(request, 'META'):
#                 client_id = request.META.get('HTTP_X_PS_CLIENT_ID', None)
#             context.jwt_token = jwt_token.decode("utf-8")
#             context.user_id = user_id
#             context.user_email = user_email
#             context.client_id = client_id
#             context.request = request
#             if context.client_id:
#                 if request.path.endswith('/setting-permissions'):
#                     logger.info(f"[JWTTokenHandlerAuthentication][load_app_context][request_path]: {request.path}")
#                     WorkspaceManagement(client_id=context.client_id, jwt_token=jwt_token.decode('utf-8')) \
#                         .sync_client_setting_user_ps(user_id=context.user_id)
#         except Exception as ex:
#             logger.error("[JWTTokenHandlerAuthentication][load_app_context] {}".format(ex))
#             raise ex
