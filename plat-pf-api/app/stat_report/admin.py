import logging
from django.contrib import admin, messages
from app.core.admins.tenant_db_admin import TenantDBForModelAdmin
from app.stat_report.models import StatReport, StatClientChannelReport, OrgClientHealth, StatSaleRecentReport, \
    ClientReportCost, StatSaleRecentSummaryReport

logger = logging.getLogger(__name__)


@admin.register(StatReport)
class StatReportAdmin(TenantDBForModelAdmin):
    list_display = ["id", "client_time_control", "sales_time_control", "financial_event_time_control",
                    "informed_time_control", "created", "modified"]
    ordering = ["-created"]


@admin.register(StatSaleRecentReport)
class StatSaleRecentReportAdmin(TenantDBForModelAdmin):
    list_display = ["id", "channel", "report_type", "report_date", "total_sales_affected", "created", "modified"]
    list_filter = ["channel", "report_type"]
    ordering = ["-report_date"]


@admin.register(StatSaleRecentSummaryReport)
class StatSaleRecentSummaryReportAdmin(TenantDBForModelAdmin):
    list_display = ["id", "channel", "report_type", "report_date", "total_sales_affected", "created", "modified"]
    list_filter = ["report_type"]


@admin.register(StatClientChannelReport)
class StatClientChannelReportAdmin(TenantDBForModelAdmin):
    list_display = ["id", "organization", "client", "channel", "report_type", "report_date",
                    "total_sales", "total_time_control", "total_time_control_completed", "created", "modified"]
    list_filter = ["organization", "client", "channel", "report_type"]
    ordering = ["-report_date"]
    actions = ["recalculate_sale_recent_hour_summary"]

    def recalculate_sale_recent_hour_summary(self, request, queryset):
        errors = []
        try:
            # StatSaleRecentReport.calculate_sale_recent()
            StatSaleRecentSummaryReport.calculate_sale_recent()
            StatSaleRecentSummaryReport.calculated_job_recent()
        except Exception as ex:
            errors.append(str(ex))
        #
        if errors:
            msg = f" , ".join(errors)
            messages.error(request, msg)
        else:
            messages.success(request, f"{queryset.count()} recalculate sale rent hour summary successfully")

    recalculate_sale_recent_hour_summary.short_description = "Recalculate sale rent hour summary"


@admin.register(OrgClientHealth)
class OrgClientHealthAdmin(TenantDBForModelAdmin):
    list_display = ["id", "organization", "client", "service_name", "is_enabled", "is_healthy", "message", "modified"]
    search_fields = ["service_name"]
    list_filter = ["organization", "client", "service_name"]


@admin.register(ClientReportCost)
class ClientReportCostAdmin(TenantDBForModelAdmin):
    list_display = ['id', 'client', 'date', 'total_sales', 'total_30d_sales', 'created', 'modified']
    list_filter = ['client']
    ordering = ['-date']
