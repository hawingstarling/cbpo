from django.urls import path

from app.selling_partner.sub_views.callback_view import SellerCentralOauthCallbackView, LWAClientCallback

urlpatterns = [
    path('pf/sc-oauth-callback', SellerCentralOauthCallbackView.as_view(), name='sc-oauth-callback'),
    path('pf/lwa-client-callback', LWAClientCallback.as_view(), name='pf-lwa-client-callback')
]
