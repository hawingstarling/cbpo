from django.urls import path

from app.stat_report.sub_views.event_view import StatReportChannelView, StatOrgClientReportView, StatReportSummaryView

urlpatterns = [
    path(
        "stats/tc-events/summary/",
        StatReportSummaryView.as_view(),
        name="stats-tc-events-summary-view",
    ),
    path(
        "stats/tc-events/clients/",
        StatOrgClientReportView.as_view(),
        name="stats-tc-events-clients-view",
    ),
    path(
        "stats/tc-events/channels/",
        StatReportChannelView.as_view(),
        name="stats-tc-events-channels-view",
    )
]
