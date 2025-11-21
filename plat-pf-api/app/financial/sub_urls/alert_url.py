from django.urls import path

from app.financial.sub_views.alert_view import ListCreateAlertView, RetrieveUpdateDeleteAlertView

urlpatterns = [
    path('clients/<uuid:client_id>/alerts', ListCreateAlertView.as_view(),
         name='list-create-alerts'),
    path('clients/<uuid:client_id>/alerts/<uuid:pk>', RetrieveUpdateDeleteAlertView.as_view(),
         name='retrieve-update-destroy-alerts'),
]
