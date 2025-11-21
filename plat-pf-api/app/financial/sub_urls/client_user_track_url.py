from django.urls import path
from app.financial.sub_views.client_user_track_view import ClientUserTrackView

urlpatterns = [
    path('clients/<uuid:client_id>/user-track', ClientUserTrackView.as_view(), name='get-post-client-user-track')
]
