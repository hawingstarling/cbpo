from django.urls import path
from app.financial.sub_views.sale_by_sku_view import SaleBySKUListView

urlpatterns = [
    path('clients/<uuid:client_id>/<slug:flatten_type>/sale-by-sku', SaleBySKUListView.as_view(),
         name='list-sale-by-sku')
]
