from django.urls import path
from app.stat_report.sub_views.sale_recent_view import StatSaleRecentReportView, StatSaleRecentCategorySummaryView

urlpatterns = [
    path(
        "stats/sale-recent/",
        StatSaleRecentReportView.as_view(),
        name="stats-sale-recent-view",
    ),
    path(
        "stats/sale-recent/<slug:category>/summary",
        StatSaleRecentCategorySummaryView.as_view(),
        name="stats-sale-recent-category-summary-view",
    )
]
