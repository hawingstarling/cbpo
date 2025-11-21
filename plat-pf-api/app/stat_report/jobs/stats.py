import logging
from datetime import datetime
from celery import current_app
from app.stat_report.models import StatSaleRecentReport, StatSaleRecentSummaryReport
from app.stat_report.services.report_types.stat_sale_recent_report import StatSaleRecentService
from app.stat_report.services.report_types.stat_sale_workspace_cost_report import StatSaleClientCostReport
from app.stat_report.services.report_types.stat_time_control_report import StatTimeControlReport
from app.stat_report.variables.stat_channel_type import STAT_REPORT_HOUR

logger = logging.getLogger(__name__)


@current_app.task(bind=True)
def stats_time_control_report_client_task(self, client_id: str):
    logger.info(f"[{self.request.id}][stats_time_control_report_client_task] Begin check ...")
    StatTimeControlReport(client_id=client_id).process()


@current_app.task(bind=True)
def stats_sale_recent_report_client_task(self, client_id: str):
    logger.info(f"[{self.request.id}][stats_sale_recent_report_client_task] Begin check ...")
    StatSaleRecentService(client_id=client_id).process()


@current_app.task(bind=True)
def stats_sale_recent_summary_all_workspaces(self, report_type: str = STAT_REPORT_HOUR):
    logger.info(f"[{self.request.id}][stats_sale_recent_summary_all_workspaces] Begin check ...")
    # StatSaleRecentReport.calculate_sale_recent(report_type=report_type)
    StatSaleRecentSummaryReport.calculate_sale_recent(report_type=report_type)
    StatSaleRecentSummaryReport.calculated_job_recent(report_type=report_type)


@current_app.task(bind=True)
def handler_calculate_client_report_cost(self, client_ids: [str], from_date: datetime.date, to_date: datetime.date):
    logger.info(f"[{self.request.id}][{from_date} - {to_date}] Beginner calculate report cost ...")
    StatSaleClientCostReport.calculate_client_report_cost(client_ids, from_date, to_date)
