import time
from datetime import timedelta
from django.utils import timezone
from app.core.helper import get_connections_client_channels
from app.core.variable.marketplace import SELLER_PARTNER_CONNECTION, CART_ROVER_CONNECTION
from app.financial.models import DataFlattenTrack, Channel
from app.financial.services.integrations.skuvaults.cart_rover import SaleCartRoverManager
from app.financial.variable.job_status import POSTED_FILTER_MODE, MODIFIED_FILTER_MODE
from app.financial.variable.data_flatten_variable import FLATTEN_SALE_ITEM_KEY
from app.financial.variable.job_status import SUCCESS
from celery import current_app
from celery.utils.log import get_task_logger
from app.job.utils.helper import register_list
from app.job.utils.variable import SYNC_ANALYSIS_CATEGORY, MODE_RUN_PARALLEL

logger = get_task_logger(__name__)


def handler_trigger_get_orders_cart_rover_recent(client_ids):
    """
    set frequency exceeds 1 week. (hour='0, 2, 6, 14, 30, 62, 126, 254')
    hour ratio x2 so we should set crontab per 2 hour at minute 0
    :return:
    """
    jobs_data = list()
    job_name = "app.financial.jobs.cart_rover.handler_trigger_cart_rover_sale_item_ws"
    module = "app.financial.jobs.cart_rover"
    method = "handler_trigger_cart_rover_sale_item_ws"
    time_now = timezone.now()
    frequency_times = [(0, 2), (2, 6), (6, 14), (14, 30), (30, 62), (62, 126), (126, 254)]
    for client_id in client_ids:
        marketplaces = Channel.objects.tenant_db_for(client_id).filter(is_pull_data=True).values_list('name', flat=True)
        client_connections = get_connections_client_channels(client_id, list(marketplaces),
                                                             [SELLER_PARTNER_CONNECTION, CART_ROVER_CONNECTION])
        for marketplace in marketplaces:
            try:
                assert client_connections[SELLER_PARTNER_CONNECTION].get(marketplace, False) is True, \
                    f"The workspace doesn't connect marketplace"
                assert client_connections[CART_ROVER_CONNECTION].get(marketplace, False) is True, \
                    f"The workspace doesn't connect cart rover"
                for item in frequency_times:
                    fd = time_now - timedelta(hours=item[1])
                    _fd = fd.strftime('%Y-%m-%d %H:%M:%S')
                    #
                    td = time_now - timedelta(hours=item[0])
                    _td = td.strftime('%Y-%m-%d %H:%M:%S')
                    #
                    data = dict(
                        name=f"get_orders_cart_rover_recent_{marketplace}_{item}",
                        client_id=client_id,
                        job_name=job_name,
                        module=module,
                        method=method,
                        is_run_validations=False,
                        meta=dict(client_id=client_id, marketplace=marketplace, filter_mode=MODIFIED_FILTER_MODE,
                                  from_date=_fd, to_date=_td)
                    )
                    jobs_data.append(data)
            except Exception as ex:
                logger.error(f"[{client_id}[{marketplace}][handler_trigger_get_orders_cart_rover_recent] {ex}")
    register_list(SYNC_ANALYSIS_CATEGORY, jobs_data, mode_run=MODE_RUN_PARALLEL)
    logger.info(f"[handler_trigger_get_cart_rover_is_active][{client_ids}] register_list app jobs completed")


@current_app.task(bind=True)
def handler_trigger_cart_rover_sale_item_ws(self, client_id: str, marketplace: str,
                                            filter_mode: str = POSTED_FILTER_MODE, **kwargs):
    assert client_id is not None, "Client ID is not empty"
    start = time.time()
    flatten = DataFlattenTrack.objects.tenant_db_for(client_id).get(client_id=client_id, type=FLATTEN_SALE_ITEM_KEY,
                                                                    live_feed=True, status=SUCCESS)
    logger.info(f"[handler_trigger_cart_rover_sale_item_ws][{self.request.id}][{client_id}][{marketplace}] "
                f"Beginner getting prime ...")
    builder = SaleCartRoverManager(client_id, flatten, marketplace, filter_mode=filter_mode, **kwargs)
    builder.progress()
    end = time.time()
    logger.info(f"[handler_trigger_cart_rover_sale_item_ws][{self.request.id}][{client_id}][{marketplace}] "
                f"Time exec : {end - start}")
