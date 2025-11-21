from django.urls import path

from app.selling_partner.sub_views.setting_view import RetrieveSPAPIAppSettingView, ConnectionSPAccountView, \
    RevokeSPAccountView

urlpatterns = [
    path('clients/<uuid:client_id>/spapi-setting', RetrieveSPAPIAppSettingView.as_view(),
         name='get-spapi-setting'),
    path('clients/<uuid:client_id>/sp-account-connection', ConnectionSPAccountView.as_view(),
         name='sp-account-connection'),
    path('clients/<uuid:client_id>/sp-account-revoke', RevokeSPAccountView.as_view(),
         name='sp-account-revoke'),
]
