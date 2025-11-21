from django.conf import settings
from app.core.services.base_service import BaseServiceManager


class DCManager(BaseServiceManager):
    DOMAIN = settings.URL_DC_SERVICE

    def prefetch_headers(self):
        pass

    def get_upc(self, data):
        url = f"{self.domain}/v1/pf/lookup/items"
        return self._call_service(url=url, method='POST', data=data)
