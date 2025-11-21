from django.urls import path
from app.financial.sub_views.top_asins_view import ListCreateTopASINsView, RetrieveUpdateDeleteTopASINsView

urlpatterns = [
    path('clients/<uuid:client_id>/top-asins/', ListCreateTopASINsView.as_view(),
         name='list-create-top-asins-view'),

    path('clients/<uuid:client_id>/top-asins/<uuid:pk>/', RetrieveUpdateDeleteTopASINsView.as_view(),
         name='update-delete-top-asins-view'),

    # path('clients/<uuid:client_id>/top-asins/bulk-action/', BulkActionTopASINsView.as_view(),
    #      name='top-asins-bulk-action-view'),
]
