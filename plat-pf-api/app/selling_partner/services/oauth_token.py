import json
import logging

import requests
from django.db import DEFAULT_DB_ALIAS
from httplib2 import Response
from rest_framework import status

from app.selling_partner.models import AppSetting

logger = logging.getLogger(__name__)


class SPAPIOAuthManage:
    def __init__(self):
        self.sp_api_setting = self._get_app_setting()

    @staticmethod
    def _get_app_setting(spapi_app_id: str = None):
        app_setting = AppSetting.objects.tenant_db_for(DEFAULT_DB_ALIAS)
        if spapi_app_id is not None:
            app_setting = app_setting.get(spapi_app_id=spapi_app_id)
        else:
            app_setting = app_setting.order_by("-created").first()
        assert app_setting is not None, "SPAPI app setting is not empty"
        return app_setting

    @property
    def headers(self):
        return {
            "Content-Type": "application/json"
        }

    @staticmethod
    def _handler_result(rs: Response):
        status_code = rs.status_code
        if status_code == status.HTTP_200_OK:
            content = rs.content.decode('utf-8')
            payload = json.loads(content)
        else:
            payload = {"errors": rs.content.decode('utf-8')}
        return status_code, payload

    def get_access_token(self, auth_code: dict):
        status_code, payload = status.HTTP_400_BAD_REQUEST, {}
        try:
            data = {
                "grant_type": "authorization_code",
                "code": auth_code,
                "client_id": self.sp_api_setting.amz_lwa_client_id,
                "client_secret": self.sp_api_setting.amz_lwa_client_secret
            }
            rs = requests.post(self.sp_api_setting.setting.aws_oauth_access_token_url, data=json.dumps(data),
                               headers=self.headers)
            status_code, payload = self._handler_result(rs)
        except Exception as ex:
            logger.error(f"[{self.__class__.__name__}] {ex}")
        return status_code, payload
