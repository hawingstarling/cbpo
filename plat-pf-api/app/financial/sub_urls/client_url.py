from django.urls import path
from app.financial.sub_views.bulk_view import (
    BulkRetrieveView, BulkListView, SaleItemBulkEditCreateView, SaleItemBulkDeleteCreateView,
    SaleItemBulkSyncCreateView, CancelBulkProgressView, BulkActionTypeFilterView, SaleItemRevertBulkEditCreateView)
from app.financial.sub_views.client_setting_permission_view import ClientUserSettingPermissionsView
from app.financial.sub_views.client_settings_view import RetrieveUpdateClientSettingsView, CreateClientSettingsView
from app.financial.sub_views.client_trans_event_view import ClientSaleItemTransEventView
from app.financial.sub_views.client_view import (
    ClientSyncPortalView, GenerateDataFlattenView, RetrieveDataFlattenView, DataSourceConnectionSaleDataView,
    SaleItemAuditLogListView, ClientSaleItemsSingleUpdateDeleteView, ClientSaleItemsBulkUpdateView,
    ClientSaleItemsBulkDeleteView, ListVariationView, ListSaleStatusView, ListProfitStatusView, ListFulfillmentTypeView,
    ListChannelView)

urlpatterns = [
    path('clients/<uuid:client_id>/sync', ClientSyncPortalView.as_view(),
         name='create-get-client-sync-portal'),

    path('clients/<uuid:client_id>/sale-items/<uuid:pk>', ClientSaleItemsSingleUpdateDeleteView.as_view(),
         name='update-delete-client-single-sale-items'),

    path('clients/<uuid:client_id>/sale-items', ClientSaleItemsBulkUpdateView.as_view(),
         name='update-client-bulk-sale-items'),

    # Common API to list bulk items (edit, delete, sync...)
    path('clients/<uuid:client_id>/sale-items/bulk', BulkListView.as_view(), name='list-bulk-items'),
    # Filter type
    path('clients/<uuid:client_id>/sale-items/bulk-filter-type', BulkActionTypeFilterView.as_view(),
         name='list-bulk-type'),

    # Common API to retrieve bulk items (edit, delete, sync...)
    path('clients/<uuid:client_id>/sale-items/bulk/<uuid:pk>', BulkRetrieveView.as_view(),
         name='retrieve-bulk-items'),

    path('clients/<uuid:client_id>/sale-items/bulk-edit', SaleItemBulkEditCreateView.as_view(),
         name='create-sale-items-bulk-edit'),

    path('clients/<uuid:client_id>/sale-items/revert-bulk-edit/<uuid:pk>', SaleItemRevertBulkEditCreateView.as_view(),
         name='create-revert-sale-items-bulk-edit'),

    path('clients/<uuid:client_id>/sale-items/bulk-delete', SaleItemBulkDeleteCreateView.as_view(),
         name='create-sale-items-bulk-delete'),

    path('clients/<uuid:client_id>/sale-items/bulk-sync', SaleItemBulkSyncCreateView.as_view(),
         name='create-sale-items-bulk-sync'),

    path('clients/<uuid:client_id>/bulk/sale-items', ClientSaleItemsBulkDeleteView.as_view(),
         name='delete-client-bulk-sale-items'),

    path('clients/<uuid:client_id>/bulk-progress/<uuid:bulk_progress_id>/cancellation',
         CancelBulkProgressView.as_view(),
         name='cancel-bulk-progress'),

    path('clients/<uuid:client_id>/sale-items/flatten/generate', GenerateDataFlattenView.as_view(),
         name='flatten-sale-items'),

    path('clients/<uuid:client_id>/sale-items/flatten/status', RetrieveDataFlattenView.as_view(),
         name='flatten-sale-items-status'),

    path('clients/<uuid:client_id>/sale-items/ds/connection', DataSourceConnectionSaleDataView.as_view(),
         name='sale-items-ds-connection'),

    path('clients/<uuid:client_id>/sale-items/<uuid:sale_item_pk>/audit-logs', SaleItemAuditLogListView.as_view(),
         name='sale-items-audit-log'),
    # variations sale item
    path('clients/<uuid:client_id>/variations/<slug:type>', ListVariationView.as_view(),
         name='sale-items-variations'),
    # list sale status of sale items
    path('clients/<uuid:client_id>/sale-status', ListSaleStatusView.as_view(),
         name='sale-items-sale-status'),
    # list profit status of sale items
    path('clients/<uuid:client_id>/profit-status', ListProfitStatusView.as_view(),
         name='sale-items-profit-status'),
    # settings permissions
    path('clients/<uuid:client_id>/setting-permissions', ClientUserSettingPermissionsView.as_view(),
         name='client-user-permissions-info'),
    # list channel
    path('clients/<uuid:client_id>/channels/', ListChannelView.as_view(),
         name='list-channel'),
    # list fulfillment type
    path('clients/<uuid:client_id>/fulfillment-types', ListFulfillmentTypeView.as_view(),
         name='client-list-fulfillment-types'),

    # list transaction item event
    path('clients/<uuid:client_id>/sale-items/<uuid:sale_item_id>/events', ClientSaleItemTransEventView.as_view(),
         name='client-list-transaction-event-sale-item'),
    # client settings
    path('clients/<uuid:client_id>/settings/', CreateClientSettingsView.as_view(),
         name='create-client-settings'),
    path('clients/<uuid:client_id>/settings/details/', RetrieveUpdateClientSettingsView.as_view(),
         name='retrieve-update-client-settings'),
]
