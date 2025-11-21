import logging
from typing import List

from app.core.variable.marketplace import AMAZON_DOMAIN_KEY, SHOPIFY_DOMAIN_KEY, SELLER_PARTNER_CONNECTION, \
    CART_ROVER_CONNECTION, INFORMED_MARKETPLACE_CONNECTION, THIRD_PARTY_LOGISTIC_CENTRAL_CONNECTION
from app.core.variable.ws_setting import DS_TRACK_ENABLED, WS_IS_OE, COG_USE_PF, COG_USE_EXTENSIV, COG_USE_DC
from app.financial.models import ClientSettings, InformedMarketplace, DataFlattenTrack
from app.financial.variable.data_flatten_variable import FLATTEN_SALE_ITEM_KEY
from app.financial.variable.job_status import SUCCESS
from app.shopify_partner.models import ShopifyPartnerOauthClientRegister

logger = logging.getLogger(__name__)


def get_connections_client_channels(client_id: str, marketplaces: List[str], connection_types: List[str] = None):
    if not connection_types:
        connection_types = [
            DS_TRACK_ENABLED,
            WS_IS_OE,
            SELLER_PARTNER_CONNECTION,
            CART_ROVER_CONNECTION,
            THIRD_PARTY_LOGISTIC_CENTRAL_CONNECTION,
            INFORMED_MARKETPLACE_CONNECTION,
            COG_USE_PF,
            COG_USE_EXTENSIV,
            COG_USE_DC
        ]
    vals = dict()
    try:
        client_setting, _ = ClientSettings.objects.tenant_db_for(client_id) \
            .get_or_create(client_id=client_id)
        is_ds_analysis_ready = DataFlattenTrack.objects.tenant_db_for(client_id) \
            .filter(
            client_id=client_id,
            type=FLATTEN_SALE_ITEM_KEY, live_feed=True,
            status=SUCCESS
        ).exists() if DS_TRACK_ENABLED in connection_types else False
        informed_marketplaces = list(
            InformedMarketplace.objects.tenant_db_for(client_id)
            .filter(client_id=client_id, channel__name__in=marketplaces)
            .values_list("channel__name", flat=True).distinct()) \
            if INFORMED_MARKETPLACE_CONNECTION in connection_types \
            else []
        #
        for connection_type in connection_types:
            vals.update({connection_type: {}})
            for marketplace in marketplaces:
                if connection_type == SELLER_PARTNER_CONNECTION:
                    if AMAZON_DOMAIN_KEY in marketplace:
                        vals[connection_type].update(
                            {
                                marketplace: getattr(
                                    client_setting, "ac_spapi_enabled", False)
                            }
                        )
                    elif SHOPIFY_DOMAIN_KEY in marketplace:
                        shopify_enabled = ShopifyPartnerOauthClientRegister.objects.tenant_db_for(client_id) \
                            .filter(client_id=client_id, enabled=True).exists()
                        vals[connection_type].update(
                            {
                                marketplace: shopify_enabled
                            }
                        )
                    else:
                        vals[connection_type].update(
                            {
                                marketplace: False
                            }
                        )
                elif connection_type == CART_ROVER_CONNECTION:
                    if AMAZON_DOMAIN_KEY in marketplace:
                        vals[connection_type].update(
                            {
                                marketplace: getattr(
                                    client_setting, "ac_cart_rover_enabled", False)
                            }
                        )
                    else:
                        vals[connection_type].update({marketplace: False})
                elif connection_type == THIRD_PARTY_LOGISTIC_CENTRAL_CONNECTION:
                    if AMAZON_DOMAIN_KEY in marketplace:
                        vals[connection_type].update(
                            {
                                marketplace: getattr(
                                    client_setting, "ac_3pl_central_enabled", False)
                            }
                        )
                    else:
                        vals[connection_type].update({marketplace: False})
                elif connection_type == DS_TRACK_ENABLED:
                    vals[connection_type].update(
                        {
                            marketplace: is_ds_analysis_ready
                        }
                    )
                elif connection_type == WS_IS_OE:
                    vals[connection_type].update(
                        {
                            marketplace: client_setting.client.is_oe
                        }
                    )
                elif connection_type == INFORMED_MARKETPLACE_CONNECTION:
                    vals[connection_type].update(
                        {
                            marketplace: True if marketplace in informed_marketplaces else False
                        }
                    )
                elif connection_type == COG_USE_EXTENSIV:
                    vals[connection_type].update(
                        {
                            marketplace: client_setting.cog_use_extensiv
                        }
                    )
                elif connection_type == COG_USE_DC:
                    vals[connection_type].update(
                        {
                            marketplace: client_setting.cog_use_dc
                        }
                    )
                elif connection_type == COG_USE_PF:
                    vals[connection_type].update(
                        {
                            marketplace: client_setting.cog_use_pf
                        }
                    )
                else:
                    vals[connection_type].update(
                        {
                            marketplace: False
                        }
                    )
    except Exception as ex:
        logger.error(
            f"[get_connections_client_channels][{client_id}][{marketplaces}] {ex}")
    return vals


def get_validations_channel(marketplace: str, validations: list = []):
    try:
        marketplace_domain = marketplace.split('.')[0]
        validations.append([f'ac_{marketplace_domain}_enabled'])
    except Exception as ex:
        logger.error(f"[get_validations_channel][{marketplace}] {ex}")
    return validations
