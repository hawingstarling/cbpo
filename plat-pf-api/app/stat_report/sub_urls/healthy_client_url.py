from django.urls import path
from app.stat_report.sub_views.healthy_view import StatHealthySummaryView, StatOrgClientView, \
    StatHealthyService

urlpatterns = [
    path(
        "stats/healthy-summary/",
        StatHealthySummaryView.as_view(),
        name="stats-healthy-summary-view",
    ),
    path(
        "stats/healthy-clients/",
        StatOrgClientView.as_view(),
        name="stats-healthy-clients-view",
    ),
    path(
        "stats/healthy-services/",
        StatHealthyService.as_view(),
        name="stats-healthy-services",
    )
]
