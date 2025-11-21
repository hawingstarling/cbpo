def gen_shopify_revoke_url(shop_url: str) -> str:
    """
    shopify does not support this API for Python
    """
    return f'https://{shop_url}/admin/api_permissions/current.json'
