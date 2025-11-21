import logging
import time
import requests

from typing import Dict, Any, List
from urllib.parse import urlencode

from app.extensiv.integration.exception import ExtensivRateLimitError, ExtensivAPIError

logger = logging.getLogger(__name__)


class ExtensivBaseService:
    BASE_URL = "https://api.skubana.com"
    ENDPOINT = None

    def __init__(self, access_token: str, max_retries: int = 3, backoff_factor: int = 2):
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.access_token = access_token

    def _build_query_params(self, filters: Dict[str, Any]) -> str:
        """
        Format filters dict into a query string.
        Handles array-type parameters.
        """
        params = []
        for key, value in filters.items():
            if value is None:
                continue
            if isinstance(value, list):
                for v in value:
                    params.append((key, v))
            else:
                params.append((key, value))
        return urlencode(params)

    def _call_service(
            self,
            method: str = 'GET',
            filters: Dict[str, Any] = None,
            data: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch products with advanced filters.
        """
        url = f"{self.BASE_URL}/{self.ENDPOINT}"
        if filters:
            query_string = self._build_query_params(filters)
            url = f"{url}?{query_string}"

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json",
        }

        logger.debug(f"[{self.__class__.__name__}] {url} | {headers} | {method} | {filters} | {data}")

        caller = getattr(requests, method.lower())

        for attempt in range(1, self.max_retries + 1):
            response = caller(url, headers=headers)

            if response.status_code == 429:
                if attempt == self.max_retries:
                    raise ExtensivRateLimitError("Rate limit exceeded. Maximum retries reached.")
                wait = self.backoff_factor ** attempt
                time.sleep(wait)
                continue

            if response.status_code != 200:
                raise ExtensivAPIError(f"HTTP {response.status_code}: {response.text}")

            return response.json()

        return []
