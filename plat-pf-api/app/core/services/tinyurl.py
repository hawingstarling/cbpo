import logging
from django.conf import settings

from app.core.services.base_service import BaseServiceManager

logger = logging.getLogger(__name__)


class TinyURLManager(BaseServiceManager):
    DOMAIN = 'https://api.tinyurl.com'
    AUTH_KEY = settings.TINYURL_API_TOKEN

    def prefetch_headers(self):
        pass

    def create_link(self, payloads):
        url = f'{self.domain}/create'
        query_params = {'api_token': self.auth_key}
        return self._call_service(url=url, method='POST', query_params=query_params, data=payloads)
