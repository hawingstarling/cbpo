from app.core.variable.pf_trust_ac import MARKETPLACE_SHOPIFY_TYPE, MARKETPLACE_AMZ_TYPE
from app.core.variable.sc_method import SPAPI_CONNECT_METHOD, SC_SHOPIFY_CONNECT


def get_marketplace_type(marketplace):
    if 'shopify' in marketplace:
        return MARKETPLACE_SHOPIFY_TYPE
    return MARKETPLACE_AMZ_TYPE


def get_sc_method(marketplace_type):
    assert marketplace_type in [MARKETPLACE_AMZ_TYPE, MARKETPLACE_SHOPIFY_TYPE], \
        f"Marketplace type must in [MARKETPLACE_AMZ_TYPE, MARKETPLACE_SHOPIFY_TYPE]"
    args = {
        MARKETPLACE_AMZ_TYPE: SPAPI_CONNECT_METHOD,
        MARKETPLACE_SHOPIFY_TYPE: SC_SHOPIFY_CONNECT
    }
    method = args[marketplace_type]
    return method
