import logging
import time
from celery import current_app

from django.utils import timezone
from app.core.helper import get_connections_client_channels
from app.core.variable.marketplace import CHANNEL_DEFAULT, SELLER_PARTNER_CONNECTION
from app.financial.models import DataFlattenTrack, Channel, SaleItem
from app.financial.services.integrations.sale_item_financial import SaleItemFinancialIntegration
from app.financial.variable.data_flatten_variable import FLATTEN_SALE_ITEM_FINANCIAL_KEY
from app.financial.variable.job_status import SUCCESS
from app.job.utils.helper import register_list
from app.job.utils.variable import MODE_RUN_PARALLEL, SYNC_ANALYSIS_CATEGORY

logger = logging.getLogger(__name__)


def handler_trigger_split_sale_item_financial_recent(client_ids: []):
    jobs_data = list()
    job_name = "app.financial.jobs.sale_financial.handler_trigger_split_sale_item_financial_ws"
    module = "app.financial.jobs.sale_financial"
    method = "handler_trigger_split_sale_item_financial_ws"
    for client_id in client_ids:
        channels = Channel.objects.tenant_db_for(
            client_id).filter(is_pull_data=True)
        marketplaces = channels.values_list("name", flat=True)
        client_connections = get_connections_client_channels(
            client_id, list(marketplaces), [SELLER_PARTNER_CONNECTION])
        for channel in channels:
            marketplace = channel.name
            try:
                assert client_connections[SELLER_PARTNER_CONNECTION].get(marketplace, False) is True, \
                    f"The workspace doesn't connect marketplace"
                qs = SaleItem.objects.tenant_db_for(client_id).filter(
                    sale__channel=channel, financial_dirty=True)
                assert qs.exists() is True, f"The workspace doesn't financial dirty"
                meta = dict(client_id=client_id, marketplace=marketplace)
                data = dict(
                    name=f"split_sale_item_financial_ws_{marketplace}",
                    client_id=client_id,
                    job_name=job_name,
                    module=module,
                    method=method,
                    is_run_validations=False,
                    meta=meta
                )
                jobs_data.append(data)
            except Exception as ex:
                logger.error(
                    f"[{client_id}[{marketplace}][handler_trigger_split_sale_item_financial_recent] {ex}"
                )
    if len(jobs_data) > 0:
        register_list(SYNC_ANALYSIS_CATEGORY, jobs_data,
                      mode_run=MODE_RUN_PARALLEL)
        logger.info(
            f"[handler_trigger_split_sale_item_financial_recent][{client_ids}] "
            f"register_list app jobs completed"
        )


@current_app.task(bind=True)
def handler_trigger_split_sale_item_financial_ws(self, client_id: str, marketplace: str = CHANNEL_DEFAULT, **kwargs):
    assert client_id is not None, f"[handler_trigger_split_sale_item_financial_ws][{self.request.id}][{client_id}] " \
                                  f"Client ID is not empty"
    start = time.time()

    flatten = DataFlattenTrack.objects.tenant_db_for(client_id)\
        .get(client_id=client_id,
             type=FLATTEN_SALE_ITEM_FINANCIAL_KEY,
             live_feed=True, status=SUCCESS)
    logger.info(
        f"[{client_id}][{marketplace}][handler_trigger_split_sale_item_financial_ws][{kwargs}] "
        f"Begin split sale item financial to workspace ...."
    )
    live_feed_manager = SaleItemFinancialIntegration(
        client_id, flatten, marketplace, **kwargs)
    live_feed_manager.progress()
    flatten.last_run = timezone.now()
    flatten.save(update_fields=["last_run"])

    end = time.time()
    logger.info(
        f"[{self.request.id}][{client_id}][{marketplace}]"
        f"[handler_trigger_split_sale_item_financial_ws] Time exec : {end - start}"
    )
