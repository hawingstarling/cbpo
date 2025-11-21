from django.conf import settings
from app.core.services.base_service import BaseServiceManager


class DSManager(BaseServiceManager):
    DOMAIN = settings.URL_DS_SERVICE
    AUTH_KEY = settings.DS_TOKEN

    def prefetch_headers(self):
        self._headers = {
            'x-ac-client-id': self.client_id,
            'Authorization': self.auth_key,
            'Content-Type': 'application/json'
        }

    def clear_cache_ds(self, ds_id: str):
        url = f"{self.domain}/v1/data-sources/{ds_id}/clear-cache"
        return self._call_service(url=url, method='GET')
