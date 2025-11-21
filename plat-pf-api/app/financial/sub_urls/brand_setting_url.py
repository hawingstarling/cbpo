from django.urls import path

from app.financial.sub_views.brand_setting_view import (
    ListCreateBrandSettingView, RetrieveUpdateDeleteBrandSettingView, UpdateSaleView, CountUpdateSaleView,
    ExportBrandSettingView)

urlpatterns = [
    path('clients/<uuid:client_id>/brand-settings/',
         ListCreateBrandSettingView.as_view(),
         name='list-create-brand-settings'),
    path('clients/<uuid:client_id>/brand-settings/export/',
         ExportBrandSettingView.as_view(),
         name='export-brand-settings'),
    path('clients/<uuid:client_id>/brand-settings/<uuid:brand_setting_id>/',
         RetrieveUpdateDeleteBrandSettingView.as_view(),
         name='retrieve-update-delete-brand-setting'),
    path('clients/<uuid:client_id>/brand-settings/<uuid:brand_setting_id>/update-sales/',
         UpdateSaleView.as_view(),
         name='brand-setting-update-sales'),
    path('clients/<uuid:client_id>/brand-settings/<uuid:brand_setting_id>/count-sales/',
         CountUpdateSaleView.as_view(),
         name='count-brand-setting-update-sales'),
]
