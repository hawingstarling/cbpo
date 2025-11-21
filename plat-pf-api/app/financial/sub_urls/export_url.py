from django.urls import path
from app.financial.sub_views.custom_report_dynamic_view import CustomReportDynamicViewListCreateView, \
    CustomReportDynamicRetrieveUpdateDestroyView, CancelCustomReportDynamicView

urlpatterns = [
    path('clients/<uuid:client_id>/custom-reports/<slug:cr_type>/export',
         CustomReportDynamicViewListCreateView.as_view(),
         name='client-custom-reports-dynamic-list-create'),
    path('clients/<uuid:client_id>/custom-reports/<slug:cr_type>/<uuid:pk>',
         CustomReportDynamicRetrieveUpdateDestroyView.as_view(),
         name='client-custom-reports-dynamic-update-retrieve-destroy'),
    path('clients/<uuid:client_id>/custom-reports/<slug:cr_type>/<uuid:pk>/cancellation',
         CancelCustomReportDynamicView.as_view(),
         name='cancel-custom-reports-dynamic-cancellation'),
]
