from django.urls import path

from app.financial.sub_views.top_product_performance_view import TopProductChannelPerformanceView

urlpatterns = [
    path('clients/<uuid:client_id>/top-product-performance', TopProductChannelPerformanceView.as_view(),
         name='list-client-top-product-performance')
]
