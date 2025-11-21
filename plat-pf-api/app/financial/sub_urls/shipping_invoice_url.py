from django.urls import path
from app.financial.sub_views.shipping_invoice_trans_view import ListShippingInvoiceTransView, \
    CustomReportShippingInvoiceCreateView, ListTransMatchedSalesView, CustomReportShippingInvoiceTransCreateView, \
    CustomReportShippingInvoiceTransUnmatchedInfoCreateView
from app.financial.sub_views.shipping_invoice_view import ListShippingInvoiceView

urlpatterns = [
    path('clients/<uuid:client_id>/shipping-invoices/', ListShippingInvoiceView.as_view(),
         name='list-shipping-invoices'),
    path('clients/<uuid:client_id>/fedex-shipment/export/', CustomReportShippingInvoiceCreateView.as_view(),
         name='create-export-fedex-shipment'),
    path('clients/<uuid:client_id>/shipping-invoices/export/', CustomReportShippingInvoiceCreateView.as_view(),
         name='create-export-shipping-invoices'),
    #
    path('clients/<uuid:client_id>/shipping-invoices-transactions/', ListShippingInvoiceTransView.as_view(),
         name='list-shipping-invoices-transactions'),
    path('clients/<uuid:client_id>/shipping-invoices/<uuid:shipping_invoice_id>/transactions',
         ListShippingInvoiceTransView.as_view(), name='list-transactions-by-shipping-invoice'),
    path('clients/<uuid:client_id>/shipping-invoices-transactions/export/',
         CustomReportShippingInvoiceTransCreateView.as_view(), name='create-export-shipping-invoices-trans'),
    path('clients/<uuid:client_id>/shipping-invoices-transactions/export/unmatched',
         CustomReportShippingInvoiceTransUnmatchedInfoCreateView.as_view(),
         name='create-export-shipping-invoices-trans-unmatched'),
    path('clients/<uuid:client_id>/shipping-invoices/<uuid:shipping_invoice_id>/matched-sales',
         ListTransMatchedSalesView.as_view(), name='shipping-invoices-trans-matched-sales'),
]
