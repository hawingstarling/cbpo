from app.core.helper import get_connections_client_channels
from app.core.variable.marketplace import SELLER_PARTNER_CONNECTION
from app.financial.models import Channel
from celery import current_app
from celery.utils.log import get_task_logger

from app.financial.services.dashboard.top_product_performance import TopProductPerformanceService
from app.job.utils.helper import register_list
from app.job.utils.variable import MODE_RUN_PARALLEL, DATA_SOURCE_CALCULATION_CATEGORY

logger = get_task_logger(__name__)


def handler_pick_job_calculation_top_product_performance_clients(client_ids: list):
    jobs_data = list()
    for client_id in client_ids:
        marketplaces = Channel.objects.tenant_db_for(client_id).filter(is_pull_data=True).values_list('name', flat=True)
        client_connections = get_connections_client_channels(client_id, list(marketplaces), [SELLER_PARTNER_CONNECTION])
        for marketplace in marketplaces:
            try:
                assert client_connections[SELLER_PARTNER_CONNECTION].get(marketplace, False) is True, \
                    f"The workspace doesn't connect marketplace"
                data = dict(
                    name=f"calculation_top_product_performance_{marketplace}",
                    client_id=client_id,
                    job_name="app.financial.jobs.top_product_performance.handler_calculation_top_product_performance_ws",
                    module="app.financial.jobs.top_product_performance",
                    method="handler_calculation_top_product_performance_ws",
                    is_run_validations=False,
                    meta=dict(client_id=client_id, marketplace=marketplace)
                )
                jobs_data.append(data)
            except Exception as ex:
                logger.error(f"[{client_id}[{marketplace}]"
                             f"[handler_pick_job_calculation_top_product_performance_clients] {ex}")
    if len(jobs_data) > 0:
        register_list(DATA_SOURCE_CALCULATION_CATEGORY, jobs_data, mode_run=MODE_RUN_PARALLEL)
        logger.info(
            f"[handler_pick_job_calculation_top_product_performance_clients][{client_ids}] register_list app jobs completed")


@current_app.task(bind=True)
def handler_calculation_top_product_performance_ws(self, client_id: str, marketplace: str):
    logger.info(f"[{self.request.id}][handler_calculation_top_product_performance_ws]"
                f"[{client_id}][{marketplace}] Start job ....")
    service = TopProductPerformanceService(client_id, marketplace)
    service.process()
    service.complete()
