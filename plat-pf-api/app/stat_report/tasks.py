import calendar
from dateutil.relativedelta import relativedelta
from django.db import DEFAULT_DB_ALIAS
from django.utils import timezone
from app.financial.models import ClientPortal
from app.job.utils.helper import register_clients_method
from app.job.utils.variable import STATS_REPORT_CATEGORY, MODE_RUN_PARALLEL
from .jobs.healthy import *
from .jobs.stats import *

logger = logging.getLogger(__name__)


def get_client_ids_active():
    return ClientPortal.objects.tenant_db_for(DEFAULT_DB_ALIAS).filter(active=True).values_list('pk', flat=True)


@current_app.task(bind=True)
def health_check_clients_scheduler(self):
    logger.info(f"[Scheduler][{self.request.id}][health_check_task] begin health check ...")
    client_ids = get_client_ids_active()
    data = dict(
        name="health_check_client_task",
        job_name="app.stat_report.jobs.healthy.health_check_client_task",
        module="app.stat_report.jobs.healthy",
        method="health_check_client_task"
    )
    register_clients_method(STATS_REPORT_CATEGORY, client_ids, data, mode_run=MODE_RUN_PARALLEL)


@current_app.task(bind=True)
def stats_time_control_report_clients_scheduler(self):
    logger.info(f"[Scheduler][{self.request.id}][stats_time_control_report_clients_scheduler] begin health check ...")
    client_ids = get_client_ids_active()
    data = dict(
        name="stats_time_control_report_client_task",
        job_name="app.stat_report.jobs.stats.stats_time_control_report_client_task",
        module="app.stat_report.jobs.stats",
        method="stats_time_control_report_client_task"
    )
    register_clients_method(STATS_REPORT_CATEGORY, client_ids, data, mode_run=MODE_RUN_PARALLEL)

    logger.info(f"[Tasks][stats_time_control_report_clients_scheduler] begin health check ...")
    StatTimeControlReport.calculation_for_stat_report_summary()


@current_app.task(bind=True)
def stats_sale_recent_report_clients_scheduler(self):
    logger.info(f"[Scheduler][{self.request.id}][stats_sale_recent_report_clients_scheduler] begin health check ...")
    client_ids = get_client_ids_active()
    data = dict(
        name="stats_sale_recent_report_client_task",
        job_name="app.stat_report.jobs.stats.stats_sale_recent_report_client_task",
        module="app.stat_report.jobs.stats",
        method="stats_sale_recent_report_client_task"
    )
    register_clients_method(STATS_REPORT_CATEGORY, client_ids, data, mode_run=MODE_RUN_PARALLEL)


@current_app.task(bind=True)
def calculation_clients_report_cost(self):
    logger.info(f"[Scheduler][calculation_clients_report_cost][{self.request.id}] begin calculations ...")
    client_ids = get_client_ids_active()
    date_previous_month = timezone.now().date() - relativedelta(months=1)
    fd = date_previous_month.replace(day=1)
    number_day = calendar.monthrange(date_previous_month.year, date_previous_month.month)[1]
    td = date_previous_month.replace(day=number_day)
    handler_calculate_client_report_cost(client_ids, fd, td)
