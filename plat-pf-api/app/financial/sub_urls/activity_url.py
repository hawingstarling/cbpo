from django.urls import path
from app.financial.sub_views.client_activity import ActivityListView

urlpatterns = [
    path('clients/<uuid:client_id>/activity', ActivityListView.as_view(),
         name='list-client-user-activity')
]
