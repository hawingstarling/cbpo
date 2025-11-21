import copy
import time
from datetime import timedelta
from django.utils import timezone
from app.core.helper import get_connections_client_channels
from app.core.variable.marketplace import SELLER_PARTNER_CONNECTION
from app.financial.models import DataFlattenTrack, Channel
from app.financial.services.integrations.it_department_live_feed import ITDepartmentSaleItemsLiveFeedManager
from app.financial.variable.job_status import POSTED_FILTER_MODE
from app.financial.services.integrations.live_feed import SaleItemsLiveFeedManager
from app.financial.variable.data_flatten_variable import FLATTEN_SALE_ITEM_KEY
from app.financial.variable.job_status import SUCCESS
from celery import current_app
from app.core.variable.pf_trust_ac import LIVE_FEED_RECENT_TYPE_LIST, \
    LIVE_FEED_RECENT_POSTED_TODAY_TYPE, LIVE_FEED_RECENT_MODIFIED_TODAY_TYPE, \
    LIVE_FEED_RECENT_REPLACEMENT_RECENT_TODAY_TYPE
from celery.utils.log import get_task_logger
from app.job.utils.helper import register_list
from app.job.utils.variable import SYNC_ANALYSIS_CATEGORY, MODE_RUN_PARALLEL

logger = get_task_logger(__name__)


def handler_trigger_get_orders_recent(client_ids: list, recent_type: str):
    jobs_data = list()
    info_config_job = dict(
        job_name="app.financial.jobs.live_feed.handler_trigger_live_feed_sale_item_ws",
        module="app.financial.jobs.live_feed",
        method="handler_trigger_live_feed_sale_item_ws"
    )
    meta_info_job = get_meta_config_job_get_order_recent(recent_type)
    for client_id in client_ids:
        marketplaces = Channel.objects.tenant_db_for(client_id).filter(is_pull_data=True).values_list('name', flat=True)
        client_connections = get_connections_client_channels(client_id, list(marketplaces), [SELLER_PARTNER_CONNECTION])
        for marketplace in marketplaces:
            try:
                assert client_connections[SELLER_PARTNER_CONNECTION].get(marketplace, False) is True, \
                    f"The workspace doesn't connect marketplace"
                meta = copy.deepcopy(meta_info_job)
                meta.update(dict(client_id=client_id, marketplace=marketplace))
                data = dict(
                    name=f"get_orders_recent_{marketplace}_{recent_type}",
                    client_id=client_id,
                    job_name=info_config_job['job_name'],
                    module=info_config_job['module'],
                    method=info_config_job['method'],
                    is_run_validations=False,
                    meta=meta
                )
                jobs_data.append(data)
            except Exception as ex:
                logger.error(f"[{client_id}[{marketplace}][handler_trigger_get_orders_recent] {ex}")
    if jobs_data:
        register_list(SYNC_ANALYSIS_CATEGORY, jobs_data, mode_run=MODE_RUN_PARALLEL)
        logger.info(f"[handler_trigger_get_orders_is_active][{client_ids}] register_list app jobs completed")


def get_meta_config_job_get_order_recent(recent_type):
    assert recent_type in LIVE_FEED_RECENT_TYPE_LIST, "Recent type is not correct"
    time_now = timezone.now()
    start_date_posted_type = (time_now - timedelta(minutes=30)).strftime('%Y-%m-%d %H:%M:%S')
    end_date_posted_type = (time_now + timedelta(minutes=30)).strftime('%Y-%m-%d %H:%M:%S')
    #
    start_date_replacement_type = (time_now - timedelta(hours=12)).strftime('%Y-%m-%d %H:%M:%S')
    end_date_replacement_type = (time_now + timedelta(hours=12)).strftime('%Y-%m-%d %H:%M:%S')
    args = {
        LIVE_FEED_RECENT_MODIFIED_TODAY_TYPE: {},
        LIVE_FEED_RECENT_POSTED_TODAY_TYPE: dict(filter_mode=POSTED_FILTER_MODE, track_logs=False,
                                                 from_date=start_date_posted_type, to_date=end_date_posted_type),
        LIVE_FEED_RECENT_REPLACEMENT_RECENT_TODAY_TYPE: dict(track_logs=False,
                                                             from_date=start_date_replacement_type,
                                                             to_date=end_date_replacement_type,
                                                             is_replacement_order=True)
    }
    return args[recent_type]


@current_app.task(bind=True)
def handler_trigger_live_feed_sale_item_ws(self, client_id: str, marketplace: str, **kwargs):
    assert client_id is not None, f"[handler_trigger_live_feed_sale_item_ws][{self.request.id}][{client_id}] " \
                                  f"Client ID is not empty"
    date_now = timezone.now()
    start = time.time()
    flatten = DataFlattenTrack.objects.tenant_db_for(client_id) \
        .get(client_id=client_id,
             type=FLATTEN_SALE_ITEM_KEY,
             live_feed=True,
             status=SUCCESS)
    logger.info(
        f"[{client_id}][{marketplace}][handler_trigger_live_feed_sale_item_ws][{kwargs}] "
        f"Begin live feed to workspace ...."
    )
    is_it_department = flatten.client.clientsettings.is_it_department
    class_manager = ITDepartmentSaleItemsLiveFeedManager if is_it_department is True else SaleItemsLiveFeedManager
    logger.info(
        f"[{client_id}][{marketplace}][handler_trigger_live_feed_sale_item_ws][{kwargs}] "
        f"Class trigger {class_manager.__name__} ...."
    )
    live_feed_manager = class_manager(client_id, flatten, marketplace, **kwargs)
    live_feed_manager.progress()
    flatten.last_run = date_now
    flatten.save(update_fields=["last_run"])
    end = time.time()
    logger.info(
        f"[{client_id}][{marketplace}][handler_trigger_live_feed_sale_item_ws][{kwargs}] "
        f"Time exec : {end - start}"
    )
