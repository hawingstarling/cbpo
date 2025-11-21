import requests
from shopify.session import Session

from app.shopify_partner.models import Setting, ShopifyPartnerOauthClientRegister
from app.shopify_partner.services.oauth.shopify_utils import gen_shopify_revoke_url
from app.shopify_partner.static_setting import SHOPIFY_PARTNER_STATIC_SETTING


def generate_oauth_url(shop_url: str, state: str, setting: Setting) -> str:
    Session.setup(
        api_key=setting.api_key,
        secret=setting.get_decrypt_secret
    )
    session = Session(
        shop_url,
        SHOPIFY_PARTNER_STATIC_SETTING.api_version
    )
    scope = setting.scope.split(",")
    return session.create_permission_url(
        scope,
        setting.redirect_url_oauth,
        state
    )


def get_access_token_callback(shop_url: str, query_params_from_callback: dict, setting: Setting) -> str:
    Session.setup(
        api_key=setting.api_key,
        secret=setting.get_decrypt_secret
    )
    session = Session(shop_url, SHOPIFY_PARTNER_STATIC_SETTING.api_version)
    return session.request_token(query_params_from_callback)


def validate_shopify_app_integration(params: dict, setting: Setting):
    """
    make request is from the shopify admin
    """
    Session.setup(
        api_key=setting.api_key,
        secret=setting.get_decrypt_secret
    )
    shop_url = params['shop']
    session = Session(
        shop_url,
        SHOPIFY_PARTNER_STATIC_SETTING.api_version
    )
    return session.validate_params(params)


def shopify_revoke(client_id: str) -> bool:
    """
    API request to Shopify
    uninstall the application from merchant
    """

    client_register_data = ShopifyPartnerOauthClientRegister.objects.tenant_db_for(client_id).get(client_id=client_id)
    revoke_url = gen_shopify_revoke_url(client_register_data.oauth_token_request.shop_url)
    r = requests.delete(
        revoke_url,
        headers={
            "X-Shopify-Access-Token": client_register_data.oauth_token_request.get_decrypted_access_token,
            "content_type": "application/json",
        }
    )
    return True if r.status_code == 200 else False
