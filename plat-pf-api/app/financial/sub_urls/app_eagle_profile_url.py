from django.urls import path

from app.financial.sub_views.app_eagle_profile_view import ListAppEagleProfileView, \
    RetrieveUpdateDeleteAppEagleProfileView, ExportAppEagleProfileView

urlpatterns = [
    path('clients/<uuid:client_id>/app-eagle-profile/', ListAppEagleProfileView.as_view(),
         name='list-app-eagle-profile'),
    path('clients/<uuid:client_id>/app-eagle-profile/<uuid:pk>/', RetrieveUpdateDeleteAppEagleProfileView.as_view(),
         name='retrive-update-destroy-app-eagle-profile'),
    path('clients/<uuid:client_id>/app-eagle-profile/export/', ExportAppEagleProfileView.as_view(),
         name='export-app-eagle-profile'),
]
