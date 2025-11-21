from typing import List, Dict
from app.core.logger import logger
from .api_data_source_centre import ApiCentreContainer, _ApiDataSourceCentre
from ..variable.data_flatten_variable import FLATTEN_PG_SOURCE
from ...database.helper import get_db_url_client
from ...es.helper import get_es_host_client


class DataSource:
    """
    - create data source document in DS services
    """

    def __init__(self, client_id, type_flatten, table, access_token,
                 api_centre: _ApiDataSourceCentre = ApiCentreContainer.data_source_central(),
                 source: str = FLATTEN_PG_SOURCE, token_type="JWT"):
        self.__api_centre = api_centre
        self.client_id = client_id
        self.access_token = access_token
        self.type_flatten = str.lower(type_flatten)
        self.table = table
        self.source = source
        self.token_type = token_type

    def get_or_create_data_source(self, external_id):
        logger.info(f"[{self.__class__.__name__}][get_or_create_data_source] Beginning ...")
        data_source = self.__api_centre.get_data_source(external_id, self.__header_for_ds_request)
        if data_source is None:
            body = self.__prepare_new_doc(external_id)
            data_source = self.__api_centre.create_data_source(body, self.__header_for_ds_request)
        return data_source

    def call_query(
            self, external_id: str,
            fields: List[dict] = None,
            group: Dict = None,
            query_type="exec",
            **kwargs
    ):
        """
        Call /exec to query data from datasource
        https://mayoretailinternetservices.atlassian.net/wiki/spaces/DSP/pages/3932256/Queries
        @param external_id:
        @param fields: list of dict of selected fields
        @param group: dict of selected fields aggregation
        @param kwargs: DS Standard Query args
        @param query_type: "exec" or "count"
        https://mayoretailinternetservices.atlassian.net/wiki/spaces/DSP/pages/3932256/Queries#Standard-Query-Object
        @return: {cols: [...], rows:[...]}
        """
        logger.debug(f"[{self.__class__.__name__}][call_query] Beginning ...")
        if fields is None:
            fields = list()
        if group is None:
            group = dict()
        body = {
            "query": {
                "fields": fields,
                "group": group,
                **kwargs,
            }
        }
        return self.__api_centre.query_data_source(external_id=external_id, body=body, query_type=query_type,
                                                   header=self.__header_for_ds_request)

    def __prepare_new_doc(self, external_id: str) -> dict:
        logger.info(f"[{self.__class__.__name__}][__prepare_new_doc] Beginning ...")
        if self.source == FLATTEN_PG_SOURCE:
            doc_type = "postgres"
            pg_url = get_db_url_client(self.client_id)
            db_config = DataSource.extract_info_from_db_uri(pg_url)
            #
            db_config.update({"table": self.table})
            config = {
                "indexer": {
                    "connection": db_config,
                    "type": "postgres"
                }
            }
        else:
            doc_type = "elasticsearch"
            es_url = get_es_host_client(self.client_id)
            es_config = DataSource.extract_info_from_es_uri(es_url)
            #
            es_config.update({"index": self.table})
            config = {
                "indexer": {
                    "connection": es_config,
                    "type": "elasticsearch"
                }
            }
        body = {
            "client_id": self.client_id,
            "external_id": external_id,
            "is_programmed": True,
            "name": f"PF Sale Items {self.source} Data Source",
            "description": f"Flatten {self.source} Sale Item Data In PF",
            "type": doc_type,
            "config": config
        }
        return body

    @staticmethod
    def extract_info_from_db_uri(uri: str) -> dict:
        """
        extract database configuration
        :rtype: object: {username, pass, port ,...}
        :param uri:
        :return:
        """
        extracted = uri.split("://")[1]
        username_pass = extracted.split("@")[0]
        username = username_pass.split(":")[0]
        password = username_pass.split(":")[1]
        host_port_database = extracted.split("@")[1]
        host_port = host_port_database.split("/")[0]
        host = host_port.split(":")[0]
        port = host_port.split(":")[1]
        database = host_port_database.split("/")[1]
        return {
            "username": username,
            "password": password,
            "host": host,
            "port": port,
            "database": database
        }

    @staticmethod
    def extract_info_from_es_uri(uri: str) -> dict:
        from urllib.parse import urlparse
        config = urlparse(uri)
        return {
            "username": config.username,
            "password": config.password,
            "host": config.hostname,
            "port": config.port,
            "https": config.scheme == "https"
        }

    @property
    def __header_for_ds_request(self):
        if self.token_type == "JWT":
            authorization = f"Bearer {self.access_token}"
        else:
            authorization = self.access_token
        return {
            "Content-Type": "application/json",
            "x-ps-client-id": self.client_id,
            "Authorization": authorization
        }
