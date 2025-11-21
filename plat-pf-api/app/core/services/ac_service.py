import logging
from django.conf import settings
from app.core.services.base_service import BaseServiceManager
from app.core.variable.sc_method import SPAPI_CONNECT_METHOD, SKUVAULT_CONNECT_METHOD

logger = logging.getLogger(__name__)


class ACManager(BaseServiceManager):
    DOMAIN = settings.URL_AC_SERVICE
    AUTH_KEY = settings.AC_API_KEY

    def prefetch_headers(self):
        if not self.kwargs.get('using_api_key', False):
            self._headers.update({'x-ac-client-id': self.client_id})
        else:
            self._headers.update({'x-api-key': self.auth_key})

    def get_sale_items(self, sc_method: str = SPAPI_CONNECT_METHOD, **query_params):
        url = f'{self.domain}/v1/{sc_method}/sale_items'
        return self._call_service(url=url, method='POST', data=query_params)

    def get_sale_items_immediately(self, sc_method: str = SPAPI_CONNECT_METHOD, **query_params):
        url = f'{self.domain}/v1/{sc_method}/sale_items/immediately'
        return self._call_service(url=url, method='GET', query_params=query_params)

    def get_orders_status(self, sc_method: str = SPAPI_CONNECT_METHOD, **query_params):
        url = f'{self.domain}/v1/{sc_method}/orders_status'
        return self._call_service(url=url, query_params=query_params)

    def get_financial_events(self, sc_method: str = SPAPI_CONNECT_METHOD, **query_params):
        url = f'{self.domain}/v1/{sc_method}/financial_events'
        return self._call_service(url=url, method='POST', data=query_params)

    def get_financial_events_immediately(self, sc_method: str = SPAPI_CONNECT_METHOD, **query_params):
        url = f'{self.domain}/v1/{sc_method}/financial_events/immediately'
        return self._call_service(url=url, method='GET', query_params=query_params)

    def get_sc_sale_items(self, sc_method: str = SPAPI_CONNECT_METHOD, **query_params):
        url = f'{self.domain}/v1/{sc_method}/sc-sale-item-query'
        return self._call_service(url=url, method='POST', data=query_params)

    def get_financial_events_status(self, sc_method: str = SPAPI_CONNECT_METHOD, **query_params):
        url = f'{self.domain}/v1/{sc_method}/financial_events_status'
        return self._call_service(url=url, query_params=query_params)

    def get_product_details(self, sc_method: str = SPAPI_CONNECT_METHOD, **data):
        url = f'{self.domain}/v1/{sc_method}/product_details'
        return self._call_service(url=url, method='POST', data=data)

    def get_ad_spend_information(self, **query_params):
        url = '{ac_url}/v1/aws/campaign/sponsored_products'.format(
            ac_url=self.domain)
        return self._call_service(url=url, method='GET', query_params=query_params)

    def get_prime_fulfillment_type_integration_method(self, sc_method: str = SKUVAULT_CONNECT_METHOD, **query_params):
        url = f'{self.domain}/v1/{sc_method}/fulfillment-type'
        return self._call_service(url=url, method='GET', query_params=query_params)

    def get_informed_profiles_report(self, client_id: str, **query_params):
        url = '{ac_url}/v1/clients/{client_id}/informed/profiles_report'.format(
            client_id=client_id, ac_url=self.domain)
        return self._call_service(url=url, method='GET', query_params=query_params)

    def get_informed_report_request_status(self, client_id: str, **query_params):
        url = '{ac_url}/v1/clients/{client_id}/informed/report_request_status'.format(client_id=client_id,
                                                                                      ac_url=self.domain)
        return self._call_service(url=url, method='GET', query_params=query_params)

    def manage_clients(self, method: str, data: dict = {}, **query_params):
        method = method.upper()
        if method in ["POST", "LIST"]:
            url = f'{self.domain}/v1/clients'
            if method == "LIST":
                method = "GET"
        else:
            url = f'{self.domain}/v1/clients/{self.client_id}'
        return self._call_service(url=url, method=method, query_params=query_params, data=data)

    def register_integration_method_keys(self, sc_method: str = SPAPI_CONNECT_METHOD, data: dict = {}, **query_params):
        url = f'{self.domain}/v1/{sc_method}/keys'
        return self._call_service(url=url, method='POST', query_params=query_params, data=data)

    def register_integration_method_account(self, sc_method: str = SPAPI_CONNECT_METHOD, data: dict = {},
                                            **query_params):
        url = f'{self.domain}/v1/{sc_method}/account'
        return self._call_service(url=url, method='POST', query_params=query_params, data=data)

    def register_or_revoke_sp_keys(self, data: dict, **query_params):
        """_summary_
        register or revoke  Shopify Partner in AC service
        Args:
            data (dict): _description_
            """
        url = f'{self.domain}/v1/shopify/keys/create'
        return self._call_service(url=url, method='POST', query_params=query_params, data=data)

    def check_sc_connection(self, sc_method: str = SPAPI_CONNECT_METHOD, data: dict = {}, **query_params):
        url = (f'{self.domain}/v1/{sc_method}/product_details?marketplace=amazon.com'
               f'&id_type=ASIN&ids=B0CMRT4Y6G&use_cache=false&include_sale_ranks=false')
        return self._call_service(url=url, method='GET', query_params=query_params, data=data)

    def request_sc_report(self, sc_method: str = SPAPI_CONNECT_METHOD, data: dict = {}, **query_params):
        url = f'{self.domain}/v1/{sc_method}/request_report'
        return self._call_service(url=url, method='POST', query_params=query_params, data=data)

    def status_sc_report(self, report_id: str, sc_method: str = SPAPI_CONNECT_METHOD, data: dict = {},
                         **query_params):
        url = f'{self.domain}/v1/{sc_method}/report_status/{report_id}'
        return self._call_service(url=url, method='GET', query_params=query_params, data=data)

    def cancelled_sc_report(self, report_id: str, sc_method: str = SPAPI_CONNECT_METHOD, data: dict = {},
                            **query_params):
        url = f'{self.domain}/v1/{sc_method}/cancel_report/{report_id}'
        return self._call_service(url=url, method='GET', query_params=query_params, data=data)
