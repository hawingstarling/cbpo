from django.urls import path
from app.selling_partner.sub_views.report_view import ListSPReportCategoriesView, ListSPReportTypesView, \
    ListCreateSPReportsView, RevokeSPReportsView, StatSPReportCategoriesView, StatsListSPReportTypesView, \
    StatsListSPReportCategoriesView

urlpatterns = [
    path('clients/<uuid:client_id>/sp-report-categories', ListSPReportCategoriesView.as_view(),
         name='list-sp-report-categories'),
    path('clients/<uuid:client_id>/sp-report-types', ListSPReportTypesView.as_view(),
         name='list-sp-report-types'),
    path('clients/<uuid:client_id>/sp-report-categories/<uuid:report_category_id>/report-types',
         ListSPReportTypesView.as_view(), name='list-sp-report-categories-report-types-detail'),
    path('clients/<uuid:client_id>/sp-reports', ListCreateSPReportsView.as_view(), name='list-create-sp-reports'),
    path('clients/<uuid:client_id>/sp-reports/<uuid:id>/revoke', RevokeSPReportsView.as_view(),
         name='revoke-sp-reports'),
    # Stats Report
    path('stats/orgs-clients/sp-report-categories', StatsListSPReportCategoriesView.as_view(),
         name='stats-list-sp-report-categories'),
    path('stats/orgs-clients/sp-report-types', StatsListSPReportTypesView.as_view(), name='stats-list-sp-report-types'),
    path('stats/orgs-clients/sp-reports', StatSPReportCategoriesView.as_view(), name='stats-sp-report-categories'),
]
