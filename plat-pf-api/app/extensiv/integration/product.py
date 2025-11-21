from typing import Optional, List, Dict, Any

from app.extensiv.integration.base import ExtensivBaseService


class ExtensivProductService(ExtensivBaseService):
    ENDPOINT = "v1.1/products"

    def get_vendor_cost_by_sku(self, list_sku: List[str]) -> Optional[List[Dict[str, Any]]]:
        """
        Shortcut for fetching vendor cost for a single SKU.
        """
        filters = {"sku": ",".join(list_sku), "limit": len(list_sku), "page": 1}
        results = self._call_service(method="GET", filters=filters)
        return results
