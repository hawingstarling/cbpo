from django.urls import path

from app.financial.sub_views.data_feed_view import DataFeedRetrieveView, DataFeedForceRunView

urlpatterns = [
    path('clients/<uuid:client_id>/feeds', DataFeedRetrieveView.as_view(),
         name='retrieve-client-data-feed'),
    path('clients/<uuid:client_id>/feeds/force-run', DataFeedForceRunView.as_view(),
         name='retrieve-client-data-feed-type-force-run')
]
