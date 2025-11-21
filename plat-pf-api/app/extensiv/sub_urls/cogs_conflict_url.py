from django.urls import path

from app.extensiv.sub_views.cogs_conflict_view import ExtensivCOGsConflictView

urlpatterns = [
    path('clients/<uuid:client_id>/extensiv-cogs-conflict', ExtensivCOGsConflictView.as_view(),
         name='extensiv-cogs-conflict-view')
]
