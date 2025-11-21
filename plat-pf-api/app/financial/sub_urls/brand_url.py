from django.urls import path

from app.financial.sub_views.brand_view import ListBrandView, \
    RetrieveUpdateDeleteBrandView, ExportBrandView

urlpatterns = [
# list brand
    path('clients/<uuid:client_id>/brands', ListBrandView.as_view(),
         name='client-list-brands'),
    path('clients/<uuid:client_id>/brands/<uuid:pk>', RetrieveUpdateDeleteBrandView.as_view(),
         name='retrieve-update-destroy-brand'),
    path('clients/<uuid:client_id>/brands/export', ExportBrandView.as_view(),
         name='export-brand'),
]