from typing import List, Dict, Any


def build_product_lookup(products: List[Dict[str, Any]], fields: List[str] = None) -> Dict[str, Dict[str, Any]]:
    """
    Converts a list of product dicts into a lookup dict keyed by masterSku.

    Args:
        products: List of product dictionaries.
        fields: List of fields to include in the lookup dict.

    Returns:
        A dict with masterSku as keys and full product data as values.
    """
    return {
        product["masterSku"]: product if fields is None else {field: product[field] for field in fields}
        for product in products
        if product.get("masterSku")  # avoid None keys
    }
