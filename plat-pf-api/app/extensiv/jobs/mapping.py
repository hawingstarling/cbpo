import logging
import time

from app.core.helper import get_connections_client_channels
from app.core.variable.ws_setting import COG_USE_EXTENSIV
from app.extensiv.services.mapping_sale_item_cog import ExtensivCogCalculation
from app.financial.models import DataFlattenTrack, Channel
from app.financial.variable.job_status import POSTED_FILTER_MODE, MODIFIED_FILTER_MODE
from app.financial.variable.data_flatten_variable import FLATTEN_SALE_ITEM_KEY
from app.financial.variable.job_status import SUCCESS
from celery import current_app
from app.job.utils.helper import register_list
from app.job.utils.variable import COGS_MAPPING_CATEGORY, MODE_RUN_PARALLEL

logger = logging.getLogger(__name__)


def pick_jobs_mapping_sale_item_cog_extensiv_recent(client_ids: [str]):
    jobs_data = list()
    job_name = "app.extensiv.jobs.mapping.handler_mapping_sale_item_cog_extensiv_ws"
    module = "app.extensiv.jobs.mapping"
    method = "handler_mapping_sale_item_cog_extensiv_ws"
    for client_id in client_ids:
        marketplaces = Channel.objects.tenant_db_for(client_id).filter(is_pull_data=True).values_list('name', flat=True)
        client_connections = get_connections_client_channels(client_id, list(marketplaces), [COG_USE_EXTENSIV])
        for marketplace in marketplaces:
            try:
                assert client_connections[COG_USE_EXTENSIV].get(marketplace, False) is True, \
                    f"The workspace doesn't enable to use Extensiv for {marketplace}"
                data = dict(
                    name=f"mapping_sale_item_cog_extensiv_recent_{marketplace}",
                    client_id=client_id,
                    job_name=job_name,
                    module=module,
                    method=method,
                    is_run_validations=False,
                    meta=dict(client_id=client_id, marketplace=marketplace, filter_mode=MODIFIED_FILTER_MODE)
                )
                jobs_data.append(data)
            except Exception as ex:
                logger.error(f"[{client_id}][{marketplace}][pick_jobs_mapping_sale_item_cog_extensiv_recent] {ex}")
    if jobs_data:
        register_list(COGS_MAPPING_CATEGORY, jobs_data, mode_run=MODE_RUN_PARALLEL)
        logger.info(f"[pick_jobs_mapping_sale_item_cog_extensiv_recent][{client_ids}] register_list app jobs completed")


@current_app.task(bind=True)
def handler_mapping_sale_item_cog_extensiv_ws(self, client_id: str, marketplace: str,
                                              filter_mode: str = POSTED_FILTER_MODE,
                                              **kwargs):
    assert client_id is not None, "Client ID is not empty"
    start = time.time()
    flatten = DataFlattenTrack.objects.tenant_db_for(client_id).get(client_id=client_id, type=FLATTEN_SALE_ITEM_KEY,
                                                                    live_feed=True, status=SUCCESS)
    logger.info(f"[handler_mapping_sale_item_cog_extensiv_ws][{self.request.id}][{client_id}][{marketplace}] "
                f"Beginning...")
    live_feed_manager = ExtensivCogCalculation(client_id=client_id, flatten=flatten, marketplace=marketplace,
                                               filter_mode=filter_mode, **kwargs)
    live_feed_manager.progress()
    end = time.time()
    logger.info(f"[handler_mapping_sale_item_cog_extensiv_ws][{self.request.id}][{client_id}][{marketplace}] "
                f"Time exec : {end - start}")
