import logging
import dependency_injector.containers as containers
import dependency_injector.providers as providers
from django.urls.base import reverse
import requests
from django.conf import settings

from app.core.exceptions import ServicesErrorException

logger = logging.getLogger(__name__)


class _ApiDataSourceCentre:

    def __init__(self):
        self.__base_uri = settings.URL_DS_SERVICE

    def ping_service_proxy(self):
        uri = settings.BASE_URL + reverse("ping-proxy-pf-to-ds")
        logger.debug(f"[{self.__class__.__name__}][ping_service_proxy] {uri}")
        try:
            res = requests.get(uri)
        except Exception as ex:
            logger.error(f"[{self.__class__.__name__}][ping_service_proxy] Errors {ex}")
            raise ServicesErrorException("Data Source Service Error")
        if res.status_code == 200:
            return res.text
        elif 401 <= res.status_code < 500:
            raise ServicesErrorException("Data Source Service Permission Error")
        elif res.status_code >= 500:
            raise ServicesErrorException("Data Source Service Error")
        return None

    def get_data_source(self, external_id: str, header):
        """
        get data source document from DS service
        :param header:
        :param external_id:
        :return: json doc or None
        """
        uri = f"{self.__base_uri}/v1/data-sources/{external_id}"
        logger.debug(f"[{self.__class__.__name__}][get_data_source] {uri} | {header}")
        try:
            res = requests.get(uri, headers=header)
        except Exception as err:
            logger.error(f"[{self.__class__.__name__}][get_data_source] Errors {err}")
            raise ServicesErrorException("Data Source Service Error")
        if res.status_code == 200:
            return res.json()
        elif 401 <= res.status_code < 500:
            raise ServicesErrorException("Data Source Service Permission Error")
        elif res.status_code >= 500:
            raise ServicesErrorException("Data Source Service Error")
        return None

    def create_data_source(self, body, header) -> object or None:
        """
        create data source document in DS service
        :param header:
        :rtype: object: data source document
        :param body: json
        :return:
        """
        uri = f"{self.__base_uri}/v1/data-sources"
        logger.debug(f"[{self.__class__.__name__}][create_data_source] {uri} | {body} | {header}")
        try:
            res = requests.post(uri, json=body, headers=header)
        except Exception as err:
            logger.error(f"[{self.__class__.__name__}][create_data_source] Errors {err}")
            raise ServicesErrorException("Data Source Service Error")
        if res.status_code == 200 or res.status_code == 201:
            return res.json()
        elif res.status_code == 400:
            raise ServicesErrorException("Data Source Service Bad Request")
        elif 401 <= res.status_code < 500:
            raise ServicesErrorException("Data Source Service Permission Error")
        else:
            raise ServicesErrorException("Data Source Service Error")

    def query_data_source(self, external_id: str, body, header, query_type="exec") -> object or None:
        """
        query data from a data source in DS service
        @param external_id: Ex. pf:<client_id>:sale_items
        @param body: { "query": { "filter": {}, "fields": {}... }}
        @param header:
        @param query_type: "exec" or "count"
        @return: { "cols": [{"name": "...", "type": "...", ...}], "rows": [["value1", 2, ...], ...]}
        """
        uri = f"{self.__base_uri}/v1/ds/{external_id}/{query_type}"
        logger.debug(f"[{self.__class__.__name__}][query_data_source] {uri} | {body} | {header} | {query_type}")
        try:
            res = requests.post(uri, json=body, headers=header)
            logger.debug(f"[{self.__class__.__name__}][query_data_source] Result {res}")
        except Exception as err:
            logger.error(f"[{self.__class__.__name__}][query_data_source] Errors {err}")
            raise ServicesErrorException("Data Source Service Error")
        if res.status_code == 200:
            return res.json()
        elif res.status_code == 400:
            raise ServicesErrorException("Data Source Service Bad Request")
        elif 401 <= res.status_code < 500:
            raise ServicesErrorException("Data Source Service Permission Error")
        else:
            raise ServicesErrorException("Data Source Service Error")


class ApiCentreContainer(containers.DeclarativeContainer):
    data_source_central = providers.Singleton(_ApiDataSourceCentre)
