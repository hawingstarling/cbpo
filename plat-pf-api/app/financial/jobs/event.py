import time
from app.financial.models import DataFlattenTrack, Channel
from app.financial.services.integrations.trans_event import TransactionSaleItemEvent
from app.financial.variable.data_flatten_variable import FLATTEN_SALE_ITEM_KEY
from app.financial.variable.job_status import SUCCESS
from celery import current_app
from celery.utils.log import get_task_logger

from ...core.helper import get_connections_client_channels
from ...core.variable.marketplace import SELLER_PARTNER_CONNECTION
from ...job.utils.helper import register_list
from ...job.utils.variable import SYNC_ANALYSIS_CATEGORY, MODE_RUN_PARALLEL

logger = get_task_logger(__name__)


def handler_trigger_trans_event_recent(client_ids: []):
    jobs_data = list()
    job_name = 'app.financial.jobs.event.handler_trigger_trans_event_sale_item_ws'
    module = "app.financial.jobs.event"
    method = "handler_trigger_trans_event_sale_item_ws"
    for client_id in client_ids:
        marketplaces = Channel.objects.tenant_db_for(client_id).filter(is_pull_data=True).values_list('name', flat=True)
        client_connections = get_connections_client_channels(client_id, list(marketplaces), [SELLER_PARTNER_CONNECTION])
        for marketplace in marketplaces:
            try:
                assert client_connections[SELLER_PARTNER_CONNECTION].get(marketplace, False) is True, \
                    f"The workspace doesn't connect marketplace"
                data = dict(
                    name=f"get_financial_event_recent_{marketplace}",
                    client_id=client_id,
                    job_name=job_name,
                    module=module,
                    method=method,
                    is_run_validations=False,
                    meta=dict(client_id=client_id, marketplace=marketplace)
                )
                jobs_data.append(data)
            except Exception as ex:
                logger.error(f"[{client_id}[{marketplace}][handler_trigger_trans_event_recent] {ex}")
    if len(jobs_data) > 0:
        register_list(SYNC_ANALYSIS_CATEGORY, jobs_data, mode_run=MODE_RUN_PARALLEL)
        logger.info(f"[handler_trigger_trans_event_is_active][{client_ids}] "
                    f"register_list app jobs completed")


@current_app.task(bind=True)
def handler_trigger_trans_event_sale_item_ws(self, client_id: str, marketplace: str, **kwargs):
    assert client_id is not None, f"[handler_trigger_trans_event_sale_item_ws][{self.request.id}][{client_id}] " \
                                  f"Client ID is not empty"
    start = time.time()
    #
    flatten = DataFlattenTrack.objects.tenant_db_for(client_id).get(client_id=client_id, type=FLATTEN_SALE_ITEM_KEY,
                                                                    live_feed=True,
                                                                    status=SUCCESS)
    logger.info(
        f'[{client_id}][{marketplace}][handler_trigger_trans_event_sale_item_ws] Begin trans event to workspace ..... ')
    is_it_department = flatten.client.clientsettings.is_it_department
    if not is_it_department:
        live_feed_manager = TransactionSaleItemEvent(client_id, flatten, marketplace, **kwargs)
        live_feed_manager.progress()
    #
    end = time.time()
    logger.info(f'[{client_id}][{marketplace}][handler_trigger_trans_event_sale_item_ws] Time exec : {end - start}')
