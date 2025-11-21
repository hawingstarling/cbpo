import logging

from app.core.services.ac_service import ACManager
from app.financial.jobs.register import register_ac_clients
from app.shopify_partner.models import ShopifyPartnerOauthClientRegister

logger = logging.getLogger(__name__)


def ac_register(client_id: str):
    """
    register AC with access_token
    """

    register_ac_clients(client_id)

    client_register_data = ShopifyPartnerOauthClientRegister.objects.get(client_id=client_id)

    if client_register_data.enabled:
        return

    data = {
        "shop": client_register_data.oauth_token_request.shop_url,
        "access_token": client_register_data.oauth_token_request.get_decrypted_access_token,
        "enabled": True,
    }

    rs = ACManager(client_id=client_id).register_or_revoke_sp_keys(data=data)
    logger.info(
        f"[{client_id}][ac_register] status {rs.status_code} , content {rs.content.decode('utf-8')}")

    client_register_data.enabled = True
    client_register_data.save(update_fields=['enabled'])


def ac_revoke(client_id: str):
    """
    revoke AC with null access_token
    """
    client_register_data = ShopifyPartnerOauthClientRegister.objects.get(client_id=client_id)

    data = {
        "shop": client_register_data.oauth_token_request.shop_url,
        "access_token": None,
        "enabled": False,
    }

    rs = ACManager(client_id=client_id).register_or_revoke_sp_keys(data=data)
    logger.info(
        f"[{client_id}][ac_revoke] status {rs.status_code} , content {rs.content.decode('utf-8')}")

    client_register_data.enabled = False
    client_register_data.save(update_fields=["enabled"])
