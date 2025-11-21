import time
from typing import TypeVar, Type

from celery import current_app
from app.core.helper import get_connections_client_channels
from app.core.utils import hashlib_content
from app.core.variable.marketplace import SELLER_PARTNER_CONNECTION, CHANNEL_DEFAULT
from app.financial.models import DataFlattenTrack, Channel, SaleItemTransaction
from app.financial.services.integrations.sale import SaleIntegrationTransEvent
from app.financial.variable.data_flatten_variable import FLATTEN_SALE_ITEM_KEY
from app.financial.variable.job_status import SUCCESS
from celery.utils.log import get_task_logger
from app.job.utils.helper import register_list
from app.job.utils.variable import SYNC_ANALYSIS_CATEGORY, MODE_RUN_PARALLEL

logger = get_task_logger(__name__)


def handler_trigger_trans_event_to_sale_level_recent(client_ids: []):
    jobs_data = list()
    job_name = 'app.financial.jobs.sale_event.handler_trans_event_data_to_sale_level'
    module = "app.financial.jobs.sale_event"
    method = "handler_trans_event_data_to_sale_level"
    for client_id in client_ids:
        channels = Channel.objects.tenant_db_for(client_id).filter(is_pull_data=True)
        marketplaces = channels.values_list("name", flat=True)
        client_connections = get_connections_client_channels(client_id, list(marketplaces), [SELLER_PARTNER_CONNECTION])
        for channel in channels:
            marketplace = channel.name
            try:
                assert client_connections[SELLER_PARTNER_CONNECTION].get(marketplace, False) is True, \
                    f"The workspace doesn't connect marketplace"
                trans_dirty_qs = SaleItemTransaction.objects.tenant_db_for(client_id) \
                    .filter(client_id=client_id, channel=channel, dirty=True)
                assert trans_dirty_qs.exists() is True, f"The workspace doesn't transaction dirty"
                meta = dict(client_id=client_id, marketplace=marketplace)
                data = dict(
                    name=f"handler_trans_event_data_to_sale_level_{marketplace}_{hashlib_content(meta)}",
                    client_id=client_id,
                    job_name=job_name,
                    module=module,
                    method=method,
                    is_run_validations=False,
                    meta=meta
                )
                jobs_data.append(data)
            except Exception as ex:
                logger.error(f"[{client_id}[{marketplace}][handler_trigger_trans_event_to_sale_level_recent] {ex}")
    if len(jobs_data) > 0:
        register_list(SYNC_ANALYSIS_CATEGORY, jobs_data, mode_run=MODE_RUN_PARALLEL)
        logger.info(f"[handler_trigger_trans_event_to_sale_level_recent][{client_ids}] "
                    f"register_list app jobs completed")


U = TypeVar("U", bound=SaleIntegrationTransEvent)


@current_app.task(bind=True)
def handler_trans_event_data_to_sale_level(self, client_id: str, marketplace: str = CHANNEL_DEFAULT,
                                           class_trigger: Type[U] = SaleIntegrationTransEvent, **kwargs):
    start = time.time()
    #
    flatten = DataFlattenTrack.objects.tenant_db_for(client_id).get(client_id=client_id, type=FLATTEN_SALE_ITEM_KEY,
                                                                    live_feed=True, status=SUCCESS)
    #
    logger.info(f'[{self.request.id}][{client_id}][{marketplace}][handler_trans_event_data_to_sale_level] '
                f'Begin trans event data to sale, sale items workspace ....')
    is_it_department = flatten.client.clientsettings.is_it_department
    if not is_it_department:
        live_feed_manager = class_trigger(client_id, flatten, marketplace, **kwargs)
        live_feed_manager.progress()
    #
    end = time.time()
    logger.info(
        f'[{self.request.id}][{client_id}][{marketplace}][handler_trans_event_data_to_sale_level] '
        f'Time exec : {end - start}'
    )
