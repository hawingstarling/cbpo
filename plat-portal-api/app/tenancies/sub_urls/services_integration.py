from django.urls import path
from app.tenancies.sub_views.services_integration import RetrieveClientView


urlpatterns = [
    path(
        "services/clients/<uuid:client_id>/",
        RetrieveClientView.as_view(),
        name="services-retrieve-client",
    )
]
