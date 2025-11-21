import io, json, logging

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from requests.compat import builtin_str
from requests.utils import super_len
from urllib3.response import HTTPResponse
from rest_framework import status, exceptions
from revproxy.response import get_django_response
from revproxy.views import ProxyView
from django.utils.translation import ugettext as _
from app.core.simple_authentication import JWTTokenHandlerAuthentication

logger = logging.getLogger(__name__)


class BaseCustomProxyView(ProxyView):
    column_filter = None
    status_code = status.HTTP_400_BAD_REQUEST

    def verify_request_proxy(self, request):
        self.verify_auth(request)
        self.verify_extension(request)

    def verify_auth(self, request):
        auth = JWTTokenHandlerAuthentication().authenticate(request)
        if not auth:
            msg = _('Authentication credentials were not provided.')
            raise exceptions.AuthenticationFailed(msg)

    def verify_extension(self, request):
        pass

    def handler_request_body(self, request):
        pass

    @property
    def is_proxy_ds_columns(self) -> bool:
        path: str = self.request.resolver_match.kwargs.get('path', None)
        prefix_required = 'v1/ds/'
        if not path.startswith(prefix_required):
            return False
        postfix_required = ['/columns']
        for e in postfix_required:
            if path.endswith(e):
                return True
        return False

    @method_decorator(cache_page(60 * 10))
    @method_decorator(vary_on_headers("x-ps-client-id", ))
    def cache_page_dispatch_ds_columns(self, request, path):
        return super().dispatch(request, path)

    def dispatch(self, request, path):
        """
        This is method custom for verify authentication/authorization to DS
            1. verify request proxy (jwt_token is valid , client id is required)
            2. handler request body
        :param request:
        :param path:
        :return:
        """
        # handler check verify request proxy
        try:
            self.verify_request_proxy(request)
            # handler request body
            self.handler_request_body(request)
        except Exception as ex:
            return self.handle_fail_request_proxy(request, ex)
        #
        if self.is_proxy_ds_columns:
            return self.cache_page_dispatch_ds_columns(request, path)
        else:
            return super().dispatch(request, path)

    def get_content_length(self, headers, content):
        try:
            length = super_len(content)
        except Exception as ex:
            length = None
        if length:
            headers['Content-Length'] = builtin_str(length)

    def get_body(self, content):
        try:
            body = io.BytesIO(content.encode("utf-8"))
        except TypeError:
            body = io.BytesIO()
        return body

    def get_status_code(self, ex):
        try:
            return ex.status_code
        except Exception as ex:
            return self.status_code

    def handle_fail_request_proxy(self, request, ex):
        headers = self.get_request_headers()
        headers['Content-Type'] = 'application/json'
        status_code = self.get_status_code(ex)
        #
        if hasattr(ex, 'serialize'):
            content = ex.serialize()
        else:
            content = {'detail': str(ex)}
        content = json.dumps(content)
        #
        self.get_content_length(headers, content)
        #
        body = self.get_body(content)
        #
        proxy_response = HTTPResponse(body=body, status=status_code, preload_content=False, headers=headers)
        self._replace_host_on_redirect_location(request, proxy_response)
        self._set_content_type(request, proxy_response)
        response = get_django_response(proxy_response, strict_cookies=self.strict_cookies)
        self.log.debug("RESPONSE RETURNED: %s", response)
        return response
