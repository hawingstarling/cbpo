import logging, json
# from typing import Union
# from rest_framework_jwt.settings import api_settings
from django.conf import settings
from app.core.services.base_service import BaseServiceManager

# jwt_decode_handler = api_settings.JWT_DECODE_HANDLER
logger = logging.getLogger(__name__)


class PortalService(BaseServiceManager):
    DOMAIN = settings.URL_PORTAL_SERVICE

    def prefetch_headers(self):
        self.headers = {
            f"Authorization": f"Bearer {self.jwt_token}"
        }

    @staticmethod
    def roles_access_readonly():
        return ["OWNER", "ADMIN", "STAFF", "CLIENT"]

    @staticmethod
    def roles_access_modify():
        return ["OWNER", "ADMIN"]

    def get_client_setting_user_ps(self, user_id: str = None):
        url = f"{self.domain}/v1/clients/{self.client_id}/users/{user_id}/settings/"
        rs = self._call_service(url=url, method="GET")
        client_setting = json.loads(rs.content.decode('utf-8'))
        return client_setting

    def get_client_information_internally(self, client_id: str, **kwargs):
        url = f"{self.domain}/v1/in/clients/{client_id}/"
        rs = self._call_service(url=url, method="GET", **kwargs)
        payload = json.loads(rs.content.decode('utf-8'))
        return payload

    def get_user_info_auth(self):
        url = f"{self.domain}/v1/rest-auth/user/"
        rs = self._call_service(url=url, method="GET")
        user_info = json.loads(rs.content.decode('utf-8'))
        return user_info

    def get_client_users_ps(self, key: str = None, limit: int = 30):
        url = f"{self.domain}/v1/clients/{self.client_id}/users/"
        if key:
            url = url + '?key={}&limit={}'.format(key, limit)
        rs = self._call_service(url=url, method="GET")
        client_setting = json.loads(rs.content.decode('utf-8'))
        return client_setting
