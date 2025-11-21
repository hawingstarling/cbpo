from django.urls import path
from app.stat_report.sub_views.healthy_view import CheckServicesStatusView

urlpatterns = [
    path(
        "",
        CheckServicesStatusView.as_view(),
        name="services-status",
    ),
]
