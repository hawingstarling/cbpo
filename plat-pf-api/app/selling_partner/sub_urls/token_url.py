from django.urls import path
from app.selling_partner.sub_views.token_view import OauthTokenRequestView

urlpatterns = [
    path('clients/<uuid:client_id>/sc-oauth/o2/token', OauthTokenRequestView.as_view(),
         name='client-sc-oauth-o2-token'),
]
