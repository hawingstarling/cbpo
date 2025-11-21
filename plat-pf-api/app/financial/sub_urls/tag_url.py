from django.urls import path

from app.financial.sub_views.tag_view import ListCreateTagView, RetrieveUpdateDeleteTagView, ClientTagsBulkView

urlpatterns = [
    path('clients/<uuid:client_id>/tags', ListCreateTagView.as_view(),
         name='list-create-tags'),
    path('clients/<uuid:client_id>/tags/<uuid:pk>', RetrieveUpdateDeleteTagView.as_view(),
         name='clients-retrieve-update-destroy-tags'),
    path('clients/<uuid:client_id>/tags/bulk-views', ClientTagsBulkView.as_view(),
         name='clients-tags-bulk-views'),
]
