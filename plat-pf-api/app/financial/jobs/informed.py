import time

from app.core.helper import get_connections_client_channels
from app.core.variable.marketplace import SELLER_PARTNER_CONNECTION, INFORMED_MARKETPLACE_CONNECTION
from app.financial.models import DataFlattenTrack, Channel
from app.financial.services.integrations.informed import InformedProfileManager
from app.financial.variable.data_flatten_variable import FLATTEN_SALE_ITEM_KEY
from app.financial.variable.job_status import SUCCESS, MODIFIED_FILTER_MODE
from celery import current_app
from celery.utils.log import get_task_logger
from app.job.utils.helper import register_list
from app.job.utils.variable import SYNC_ANALYSIS_CATEGORY, MODE_RUN_PARALLEL

logger = get_task_logger(__name__)


def handler_trigger_get_informed_recent(client_ids: []):
    jobs_data = list()
    job_name = 'app.financial.jobs.informed.handler_trigger_informed_sale_item_ws'
    module = "app.financial.jobs.informed"
    method = "handler_trigger_informed_sale_item_ws"
    for client_id in client_ids:
        marketplaces = Channel.objects.tenant_db_for(client_id).filter(is_pull_data=True).values_list('name', flat=True)
        client_connections = get_connections_client_channels(client_id, list(marketplaces))
        for marketplace in marketplaces:
            try:
                assert client_connections[SELLER_PARTNER_CONNECTION].get(marketplace, False) is True, \
                    f"The workspace doesn't connect marketplace"
                assert client_connections[INFORMED_MARKETPLACE_CONNECTION].get(marketplace, False) is True, \
                    f"The workspace doesn't setup informed"
                data = dict(
                    name=f"get_informed_recent_{marketplace}",
                    client_id=client_id,
                    job_name=job_name,
                    module=module,
                    method=method,
                    is_run_validations=False,
                    meta=dict(client_id=client_id, marketplace=marketplace)
                )
                jobs_data.append(data)
            except Exception as ex:
                logger.error(
                    f"[{client_id}[{marketplace}][handler_trigger_get_informed_recent] {ex}"
                )
    register_list(SYNC_ANALYSIS_CATEGORY, jobs_data, mode_run=MODE_RUN_PARALLEL)
    logger.info(f"[handler_trigger_get_informed_is_active][{client_ids}] Register_list app jobs completed")


@current_app.task(bind=True)
def handler_trigger_informed_sale_item_ws(self, client_id: str, marketplace: str, filter_mode=MODIFIED_FILTER_MODE,
                                          **kwargs):
    assert bool(client_id), f"[{self.request.id}] Client ID not empty"
    try:
        do_action_informed(client_id=client_id, marketplace=marketplace, filter_mode=filter_mode, **kwargs)
    except DataFlattenTrack.DoesNotExist:
        logger.error(
            f"[{self.request.id}][{client_id}][{marketplace}][{kwargs}][handler_trigger_informed_sale_item_ws] "
            f"Data flatten track not found"
        )
    except Exception as ex:
        msg = f"[{self.request.id}][{client_id}][{marketplace}][{kwargs}][handler_trigger_informed_sale_item_ws] Unexpected error : {ex}"
        logger.error(msg)


def do_action_informed(client_id: str, marketplace: str, **kwargs):
    logger.info(
        f"[{client_id}][{marketplace}][{kwargs}][do_action_informed] Begin ..."
    )

    start = time.time()

    flatten = DataFlattenTrack.objects.tenant_db_for(client_id) \
        .get(client_id=client_id, type=FLATTEN_SALE_ITEM_KEY, live_feed=True, status=SUCCESS)

    live_feed_manager = InformedProfileManager(client_id, flatten, marketplace, **kwargs)
    live_feed_manager.progress()

    end = time.time()
    logger.info(f"[{client_id}][{marketplace}][{kwargs}][do_action_informed] Time exec : {end - start}")
