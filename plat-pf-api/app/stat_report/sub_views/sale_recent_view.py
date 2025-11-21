from django.db import DEFAULT_DB_ALIAS
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny
from app.core.permissions.whilelist import SafeListPermission
from app.stat_report.models import StatSaleRecentReport, StatSaleRecentSummaryReport
from app.stat_report.sub_serializers.sale_recent_serializer import StatSaleRecentReportSerializer, \
    StatSaleRecentSummarySerializer, StatSaleMarketPlaceSerializer, StatSaleRecentReportDateSerializer
from app.stat_report.variables.stat_channel_type import STAT_REPORT_HOUR


class StatSaleRecentReportView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = StatSaleRecentReportSerializer

    marketplace = openapi.Parameter('marketplace', in_=openapi.IN_QUERY,
                                    description="Marketplace Name",
                                    type=openapi.TYPE_STRING)

    report_date = openapi.Parameter('report_date', in_=openapi.IN_QUERY,
                                    description="""Search by value of report date""",
                                    type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE)

    report_type = openapi.Parameter('report_type', in_=openapi.IN_QUERY,
                                    description="""Report Type""",
                                    type=openapi.TYPE_STRING)

    sort_field = openapi.Parameter('sort_field', in_=openapi.IN_QUERY,
                                   description="""sort_field""",
                                   type=openapi.TYPE_STRING)

    sort_direction = openapi.Parameter('sort_direction', in_=openapi.IN_QUERY,
                                       description="""sort_direction""",
                                       type=openapi.TYPE_STRING)

    def get_sorting_field(self):
        sort_field = self.request.query_params.get("sort_field", "report_date").lower()
        sort_direction = self.request.query_params.get("sort_direction", "desc").lower()
        val = sort_field if sort_direction == "asc" else f"-{sort_field}"
        return val

    def get_queryset(self):
        cond = Q()
        marketplace = self.request.query_params.get("marketplace")
        if marketplace:
            cond.add(Q(channel__name=marketplace), Q.AND)
        report_type = self.request.query_params.get("report_type", STAT_REPORT_HOUR)
        if report_type:
            cond.add(Q(report_type=report_type), Q.AND)
        qs = StatSaleRecentReport.objects.tenant_db_for(DEFAULT_DB_ALIAS).filter(cond).order_by(
            self.get_sorting_field())
        return qs

    @swagger_auto_schema(tags=["Stats Reports"], operation_description='Get list sale rent summary report',
                         manual_parameters=[marketplace, report_type, report_date])
    @method_decorator(cache_page(60 * 10))
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class StatSaleRecentCategorySummaryView(StatSaleRecentReportView):
    serializer_class = StatSaleRecentSummarySerializer

    def get_serializer_class(self):
        category_slug = self.kwargs.get('category')
        if category_slug == "marketplace":
            return StatSaleMarketPlaceSerializer
        elif category_slug == "report-date":
            return StatSaleRecentReportDateSerializer
        else:
            return StatSaleRecentSummarySerializer

    def get_queryset(self):
        category_slug = self.kwargs.get('category')
        assert category_slug in ["marketplace", "report-date"]
        cond = Q()
        report_type = self.request.query_params.get('report_type', STAT_REPORT_HOUR)
        if report_type:
            cond.add(Q(report_type=report_type), Q.AND)
        if category_slug == "marketplace":
            cond.add(Q(channel__isnull=False, report_date__isnull=True), Q.AND)
            marketplace = self.request.query_params.get('marketplace')
            if marketplace:
                cond.add(Q(channel__name=marketplace), Q.AND)
        else:
            cond.add(Q(channel__isnull=True, report_date__isnull=False), Q.AND)
            report_date = self.request.query_params.get('date')
            if report_date:
                cond.add(Q(report_date=report_date), Q.AND)
        qs = StatSaleRecentSummaryReport.objects.tenant_db_for(DEFAULT_DB_ALIAS).filter(cond) \
            .order_by(self.get_sorting_field())
        return qs

    @swagger_auto_schema(tags=["Stats Reports"], operation_description="Get list sale rent summary {category} type "
                                                                       "[marketplace, report-date] report",
                         manual_parameters=[
                             StatSaleRecentReportView.marketplace,
                             StatSaleRecentReportView.report_type,
                             StatSaleRecentReportView.report_date,
                             StatSaleRecentReportView.sort_field,
                             StatSaleRecentReportView.sort_direction,
                         ])
    @method_decorator(cache_page(60 * 10))
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
