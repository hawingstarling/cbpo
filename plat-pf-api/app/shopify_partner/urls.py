from django.urls import path

from app.shopify_partner.sub_views.common_integration import (
    GetShopifyPartnerOauthClientRegisterView, RevokeAccessShopifyPartner, ShopifyPartnerCallBackView)
from app.shopify_partner.sub_views.integration_from_pf_side import RequestOauthView
from app.shopify_partner.sub_views.integration_from_shopify_store_side import (
    ShopifyPartnerAppIntegrationView, RegisterShopUrlView)
from app.shopify_partner.sub_views.webhook_for_shop_interaction import (
    WebHookCustomerDataRequestView, WebHookCustomerDataRequestDeleteView, WebHookShopRequestDeleteView)
from app.shopify_partner.views import ShopifyIntegrationIndexView

urlpatterns = [
    path('clients/<uuid:client_id>/sp-oauth/o2/token', RequestOauthView.as_view(),
         name='client-sp-oauth-o2-token'),
    path('clients/<uuid:client_id>/register-merchant', RegisterShopUrlView.as_view(),
         name='register-shop-url'),
    path('clients/<uuid:client_id>/sp-setting', GetShopifyPartnerOauthClientRegisterView.as_view(), name='sp-setting'),
    path('clients/<uuid:client_id>/sp/revoke-access', RevokeAccessShopifyPartner.as_view(),
         name='sp-revoke-access'),
    path('pf/sp/webhook/customers/data_request', WebHookCustomerDataRequestView.as_view(),
         name='sp-webhook-customer-data'),
    path('pf/sp/webhook/customers/redact', WebHookCustomerDataRequestDeleteView.as_view(),
         name='sp-webhook-customer-data-erasure'),
    path('pf/sp/webhook/shop/redact', WebHookShopRequestDeleteView.as_view(),
         name='sp-webhook-shop-data-erasure'),
    # callback to get access token
    path('pf/sp-oauth-callback', ShopifyPartnerCallBackView.as_view(), name='sp-oauth-callback'),
    # shopify admin app integration
    path('pf/sp/app-submmit', ShopifyPartnerAppIntegrationView.as_view(),
         name='sp-app-submit'),
    path('shopify-integration/', ShopifyIntegrationIndexView.as_view(), name='shopify-integration'),
]
