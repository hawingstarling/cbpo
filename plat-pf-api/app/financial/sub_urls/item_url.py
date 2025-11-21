from django.urls import path

from app.financial.sub_views.item_view import (
    ListCreateItemView, RetrieveUpdateDeleteItemView, ListCreateItemCogView, RetrieveUpdateDeleteItemCogView,
    BulkActionItemView)

urlpatterns = [
    path('clients/<uuid:client_id>/items/', ListCreateItemView.as_view(),
         name='list-create-item-view'),

    path('clients/<uuid:client_id>/items/<uuid:pk>/', RetrieveUpdateDeleteItemView.as_view(),
         name='update-delete-item-view'),

    path('clients/<uuid:client_id>/items/<uuid:item_id>/cogs/', ListCreateItemCogView.as_view(),
         name='list-create-item-cog'),

    path('clients/<uuid:client_id>/items/<uuid:item_id>/cogs/<uuid:pk>/', RetrieveUpdateDeleteItemCogView.as_view(),
         name='update-delete-item-cog'),

    path('clients/<uuid:client_id>/items/bulk-action/', BulkActionItemView.as_view(),
         name='item-bulk-action-view'),
]
