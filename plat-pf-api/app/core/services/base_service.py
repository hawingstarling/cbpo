import copy
import json
import logging
import requests
from rest_framework import status

logger = logging.getLogger(__name__)


class BaseServiceManager:
    DOMAIN = None
    AUTH_KEY = None

    def __init__(self, client_id: str, connect_timeout: float = 5.0, read_timeout: float = 30.0, **kwargs):
        self.client_id = str(client_id)
        self._domain = self.DOMAIN
        self._auth_key = self.AUTH_KEY
        self._headers = {}
        self._connect_timeout, self._read_timeout = connect_timeout, read_timeout
        self.kwargs = kwargs

        self.prefetch_headers()

    @property
    def domain(self):
        return self._domain

    @domain.setter
    def domain(self, val: dict):
        self._domain = val

    @property
    def auth_key(self):
        return self._auth_key

    @auth_key.setter
    def auth_key(self, val: dict):
        self._auth_key = val

    @property
    def headers(self):
        return self._headers

    @headers.setter
    def headers(self, val: dict):
        self._headers = val

    def prefetch_headers(self):
        raise NotImplementedError

    @property
    def connect_timeout(self):
        return self._connect_timeout

    @connect_timeout.setter
    def connect_timeout(self, val: float):
        self._connect_timeout = val

    @property
    def read_timeout(self):
        return self._read_timeout

    @read_timeout.setter
    def read_timeout(self, val: float):
        self._read_timeout = val

    @property
    def jwt_token(self):
        return self.kwargs.get('jwt_token')

    def _call_service(self, url: str = None, method: str = 'GET', query_params: dict = {}, data: dict = {},
                      headers: dict = {}):
        try:
            if not headers:
                headers = copy.deepcopy(self.headers)
            method_action = getattr(requests, method.lower())
            logger.debug(f"[{self.__class__.__name__}] {url} | {self.headers} | {method} | {query_params} | {data}")
            kwargs_request = dict(
                url=url,
                headers=headers,
                timeout=(self.connect_timeout, self.read_timeout)
            )
            if data:
                kwargs_request.update(dict(data=json.dumps(data)))
            if query_params:
                kwargs_request.update(dict(params=query_params))
            rs = method_action(**kwargs_request)
            assert rs.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED,
                                      status.HTTP_204_NO_CONTENT], f"status code = {rs.status_code}, " \
                                                                   f"content = {rs.content.decode('utf-8')}"
            return rs
        except Exception as ex:
            logger.error(f"[{self.__class__.__name__}] {url} | {headers} | {method} | {query_params} | {data} "
                         f"__call_service error : {ex}")
            raise ex
