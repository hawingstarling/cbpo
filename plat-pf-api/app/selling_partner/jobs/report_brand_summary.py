import logging, calendar
from datetime import timedelta
from celery import current_app
from django.conf import settings
from django.utils import timezone
from app.core.variable.marketplace import CHANNEL_DEFAULT
from app.financial.models import Channel
from app.financial.services.exports.schema import EXCEL, EXCEL_XLSX
from app.job.utils.helper import register_list
from app.job.utils.variable import SELLING_PARTNER_CATEGORY, MODE_RUN_PARALLEL
from app.selling_partner.models import SPReportClient, SPReportType
from app.selling_partner.services.reports.brand_summary import SPClientBrandAggregateReport

logger = logging.getLogger(__name__)


def get_date_range_brand_summary_report():
    time_now = timezone.now()
    start_date_month = time_now.replace(day=1)
    previous_month = start_date_month - timedelta(days=1)
    previous_month_days = calendar.monthrange(previous_month.year, previous_month.month)[1]
    start_date = previous_month.replace(day=1).date()
    end_date = previous_month.replace(day=previous_month_days).date()
    tz_export = settings.DS_TZ_CALCULATE
    return start_date, end_date, tz_export


def create_jobs_sp_report_brands_summary_clients(client_ids: []):
    jobs_data = list()
    start_date, end_date, time_zone = get_date_range_brand_summary_report()
    for client_id in client_ids:
        try:
            sp_report_type = SPReportType.objects.tenant_db_for(client_id) \
                .get(category__value="BRANDS_SUMMARY_DATA_REPORT", value="BRANDS_SUMMARY_MONTHLY_DATA_REPORT")
            channel = Channel.objects.tenant_db_for(client_id).get(name=CHANNEL_DEFAULT)
            sp_report_client, _ = SPReportClient.objects.tenant_db_for(client_id) \
                .get_or_create(client_id=client_id,
                               channel=channel,
                               report_type=sp_report_type,
                               date_range_covered_start=start_date,
                               date_range_covered_end=end_date,
                               defaults=dict(date_requested=timezone.now(), meta=dict(time_zone=time_zone)))
            data = dict(
                name=f"handler_generate_sp_report_brands_summary_workspace_{client_id}",
                client_id=client_id,
                job_name="app.selling_partner.jobs.report_brand_summary."
                         "handler_generate_sp_report_brands_summary_workspace",
                module="app.selling_partner.jobs.report_brand_summary",
                method="handler_generate_sp_report_brands_summary_workspace",
                meta=dict(client_id=client_id, sp_report_client_id=sp_report_client.pk)
            )
            jobs_data.append(data)
        except Exception as ex:
            logger.error(f"[create_jobs_sp_report_brands_summary_clients][{client_id}] {ex}")
    if jobs_data:
        register_list(SELLING_PARTNER_CATEGORY, jobs_data, mode_run=MODE_RUN_PARALLEL)
        logger.info(f"[create_jobs_sp_report_brands_summary_clients][{client_ids}] "
                    f"register_list app jobs completed")


@current_app.task(bind=True)
def handler_generate_sp_report_brands_summary_workspace(self, client_id: str, sp_report_client_id: str):
    logger.info(f"[{self.request.id}][{client_id}][generate_brand_summary_workspace] Begin ...")
    service = SPClientBrandAggregateReport(client_id=client_id, object_id=sp_report_client_id, file_type=EXCEL,
                                           file_extension=EXCEL_XLSX)
    service.validate()
    service.process()
    service.complete()
