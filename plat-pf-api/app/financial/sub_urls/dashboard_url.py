from django.urls import path

from app.financial.sub_views.dashboard_view import BulkSyncDivisionClientUserWidgetView, ListClientWidgetView, \
    SettingsDivisionClientUserWidgetView, UpdateClientWidgetView, \
    DivisionClientUserWidgetView, UpdateDivisionClientUserWidgetView

urlpatterns = [
    path('clients/<uuid:client_id>/dashboard/<slug:dashboard>/widgets', ListClientWidgetView.as_view(),
         name='list-client-widget-view'),
    path('clients/<uuid:client_id>/dashboard/<slug:dashboard>/widgets-manages', UpdateClientWidgetView.as_view(),
         name='update-client-widget-key-view'),
    path(
        'clients/<uuid:client_id>/dashboard/<slug:dashboard>/users/widget-<slug:category>',
        DivisionClientUserWidgetView.as_view(),
        name='list-client-users-widget-segments-view'
    ),
    path(
        'clients/<uuid:client_id>/dashboard/<slug:dashboard>/users-widget-<slug:category>',
        UpdateDivisionClientUserWidgetView.as_view(),
        name='update-client-users-widget-segments-view'
    ),
    path(
        'clients/<uuid:client_id>/dashboard/<slug:dashboard>/users/<slug:category>-widget-settings',
        SettingsDivisionClientUserWidgetView.as_view(),
        name='list-client-users-widget-settings-view'
    ),
    path(
        'clients/<uuid:client_id>/dashboard/<slug:dashboard>/users/<slug:category>-widget-bulk-settings',
        BulkSyncDivisionClientUserWidgetView.as_view(),
        name='list-client-users-widget-bulk-settings-view'
    )
]
