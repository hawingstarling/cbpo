from django.urls import path
from app.stat_report.sub_views.server_view import GCPSummaryView

urlpatterns = [
    path(
        "stats/gcp-summary/",
        GCPSummaryView.as_view(),
        name="stats-gcp-summary-view",
    )
]
