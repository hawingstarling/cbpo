from django.urls import path

from ..sub_views.activity import ActivityListCreateViewSet, ActivityRetrieveUpdateDestroyViewSet, \
    OrganizationActivityListViewSet, ClientActivityListViewSet

urlpatterns = [
    path('activities/', ActivityListCreateViewSet.as_view(),
         name='activities-list-create'),
    path('activities/<uuid:pk>/', ActivityRetrieveUpdateDestroyViewSet.as_view(),
         name='activities-retrieve-update-destroy'),
    path('organizations/<uuid:pk>/activities/', OrganizationActivityListViewSet.as_view(),
         name='organization-activities-list'),
    path('clients/<uuid:pk>/activities/', ClientActivityListViewSet.as_view(),
         name='client-activities-list')
]
