from dataclasses import dataclass, field
from typing import List

from django.conf import settings

SHOPIFY_SCOPES_ON_READ = [
    "read_analytics", "read_assigned_fulfillment_orders", "read_shopify_payments_payouts", "read_customers",
    "read_discounts", "read_draft_orders", "read_files", "read_fulfillments", "read_gdpr_data_request",
    "read_gift_cards", "read_inventory", "read_legal_policies", "read_locations", "read_marketing_events",
    "read_merchant_managed_fulfillment_orders", "read_online_store_navigation", "read_online_store_pages",
    "read_order_edits", "read_orders", "read_payment_terms", "read_price_rules", "read_product_listings",
    "read_products", "read_reports", "read_resource_feedbacks", "read_script_tags", "read_shipping", "read_locales",
    "read_markets", "read_shopify_payments_accounts", "read_shopify_payments_bank_accounts",
    "read_shopify_payments_disputes", "read_content", "read_themes", "read_third_party_fulfillment_orders",
    "read_translations"
]


@dataclass
class ShopifyPartnerAppStaticSetting:
    api_version: str = settings.SHOPIFY_API_VERSION
    available_scopes: List[str] = field(default_factory=lambda: SHOPIFY_SCOPES_ON_READ)


SHOPIFY_PARTNER_STATIC_SETTING = ShopifyPartnerAppStaticSetting()

SHOPIFY_CTX_REQUIRED_REGISTER_SHOP_URL = {
    "subject": "PF - Shopify Integration",
    "message": "Your shop is not registered in Precise Financial App.",
    "helper": "Please register your shop url first, then install later.",
    "redirect": {
        "url": settings.BASE_HOME_URL,
        "message": "Precise Financial App"
    }
}
