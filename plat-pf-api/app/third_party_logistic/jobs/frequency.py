import logging
import time
from datetime import timedelta
from django.utils import timezone
from app.core.helper import get_connections_client_channels
from app.core.variable.marketplace import SELLER_PARTNER_CONNECTION, THIRD_PARTY_LOGISTIC_CENTRAL_CONNECTION
from app.financial.models import DataFlattenTrack, Channel
from app.financial.services.integrations.skuvaults.connect_3pl_central import Connect3PLCentralManager
from app.financial.variable.job_status import POSTED_FILTER_MODE, MODIFIED_FILTER_MODE
from app.financial.variable.data_flatten_variable import FLATTEN_SALE_ITEM_KEY
from app.financial.variable.job_status import SUCCESS
from celery import current_app
from app.job.utils.helper import register_list
from app.job.utils.variable import SYNC_ANALYSIS_CATEGORY, MODE_RUN_PARALLEL

logger = logging.getLogger(__name__)


def pick_jobs_getting_prime_3pl_central_recent(client_ids: [str]):
    """
    set frequency exceeds 1 week. (hour='0, 2, 6, 14, 30, 62, 126, 254')
    hour ratio x2 so we should set crontab per 2 hour at minute 0
    :return:
    """
    jobs_data = list()
    job_name = "app.third_party_logistic.jobs.frequency.handler_getting_prime_3pl_central_ws"
    module = "app.third_party_logistic.jobs.frequency"
    method = "handler_getting_prime_3pl_central_ws"
    time_now = timezone.now()
    frequency_times = [(0, 2), (2, 6), (6, 14), (14, 30), (30, 62), (62, 126), (126, 254)]
    for client_id in client_ids:
        marketplaces = Channel.objects.tenant_db_for(client_id).filter(is_pull_data=True).values_list('name', flat=True)
        client_connections = get_connections_client_channels(client_id, list(marketplaces),
                                                             [SELLER_PARTNER_CONNECTION,
                                                              THIRD_PARTY_LOGISTIC_CENTRAL_CONNECTION])
        for marketplace in marketplaces:
            try:
                assert client_connections[SELLER_PARTNER_CONNECTION].get(marketplace, False) is True, \
                    f"The workspace doesn't connect marketplace"
                assert client_connections[THIRD_PARTY_LOGISTIC_CENTRAL_CONNECTION].get(marketplace, False) is True, \
                    f"The workspace doesn't connect 3pl central"
                for item in frequency_times:
                    fd = time_now - timedelta(hours=item[1])
                    _fd = fd.strftime('%Y-%m-%d %H:%M:%S')
                    #
                    td = time_now - timedelta(hours=item[0])
                    _td = td.strftime('%Y-%m-%d %H:%M:%S')
                    #
                    data = dict(
                        name=f"get_orders_prime_3pl_central_recent_{marketplace}_{item}",
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
                logger.error(f"[{client_id}[{marketplace}][pick_jobs_getting_prime_3pl_central_recent] {ex}")
    if jobs_data:
        register_list(SYNC_ANALYSIS_CATEGORY, jobs_data, mode_run=MODE_RUN_PARALLEL)
        logger.info(f"[pick_jobs_getting_prime_3pl_central_recent][{client_ids}] register_list app jobs completed")


@current_app.task(bind=True)
def handler_getting_prime_3pl_central_ws(self, client_id: str, marketplace: str, filter_mode: str = POSTED_FILTER_MODE,
                                         **kwargs):
    assert client_id is not None, "Client ID is not empty"
    start = time.time()
    flatten = DataFlattenTrack.objects.tenant_db_for(client_id).get(client_id=client_id, type=FLATTEN_SALE_ITEM_KEY,
                                                                    live_feed=True, status=SUCCESS)
    logger.info(f"[handler_getting_prime_3pl_central_ws][{self.request.id}][{client_id}][{marketplace}] "
                f"Beginner getting prime ...")
    live_feed_manager = Connect3PLCentralManager(client_id, flatten, marketplace, filter_mode=filter_mode, **kwargs)
    live_feed_manager.progress()
    end = time.time()
    logger.info(f"[handler_getting_prime_3pl_central_ws][{self.request.id}][{client_id}][{marketplace}] "
                f"Time exec : {end - start}")
