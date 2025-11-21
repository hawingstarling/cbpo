from app.financial.jobs.bulk_process import *
from app.financial.jobs.data_feed import *
from app.financial.jobs.data_flatten import *
from app.financial.jobs.ds_calculate import *
from app.financial.jobs.event import *
from app.financial.jobs.fedex_shipment import *
from app.financial.jobs.imports import *
from app.financial.jobs.informed import *
from app.financial.jobs.live_feed import *
from app.financial.jobs.mapping_common_fields_items import *
from app.financial.jobs.re_open import *
from app.financial.jobs.register import *
from app.financial.jobs.sale_event import *
from app.financial.jobs.sale_financial import *
from app.financial.jobs.schema_datasource import *
from app.financial.jobs.settings import *
from app.financial.jobs.shipping_cost import *
from app.financial.jobs.skuvault import *
from app.financial.jobs.cart_rover import *
from app.financial.jobs.time_control import *
from app.financial.jobs.alert import *
from app.financial.jobs.top_product_performance import *
from app.financial.jobs.activity import *
from app.financial.models import ClientPortal
from app.job.utils.helper import register_clients_method
from app.job.utils.variable import COMMUNITY_CATEGORY, SYNC_ANALYSIS_CATEGORY, BULK_CATEGORY, SYNC_DATA_SOURCE_CATEGORY

logger = logging.getLogger(__name__)


def get_client_ids_active():
    return ClientPortal.objects.tenant_db_for(DEFAULT_DB_ALIAS).filter(active=True).values_list('pk', flat=True)


@current_app.task(bind=True)
def recover_data_source(self):
    client_ids = get_client_ids_active()
    data = dict(
        name="recover_data_source",
        job_name="app.financial.jobs.schema_datasource.handler_sync_scheme_data_source",
        module="app.financial.jobs.schema_datasource",
        method="handler_sync_scheme_data_source",
        meta=dict(recover_data_source=True)
    )
    register_clients_method(COMMUNITY_CATEGORY, client_ids,
                            data, mode_run=MODE_RUN_PARALLEL)
    logger.info(
        f"[Scheduler][{self.request.id}][recover_data_source] beat job for {len(client_ids)} clients")


@current_app.task(bind=True)
def resync_data_source(self):
    client_ids = get_client_ids_active()
    data = dict(
        name="resync_data_source",
        job_name="app.financial.jobs.schema_datasource.handler_sync_scheme_data_source",
        module="app.financial.jobs.schema_datasource",
        method="handler_sync_scheme_data_source",
        time_limit=7200,
        meta=dict(resync_data_source=True)
    )
    register_clients_method(SYNC_DATA_SOURCE_CATEGORY,
                            client_ids, data, mode_run=MODE_RUN_PARALLEL)
    logger.info(
        f"[Scheduler][{self.request.id}][resync_data_source] beat job for {len(client_ids)} clients")


@current_app.task(bind=True)
def checking_status_deactivate_of_workspace(self):
    client_ids = get_client_ids_active()
    data = dict(
        name="checking_status_deactivate_of_workspace",
        job_name="app.financial.jobs.settings.handler_checking_status_deactivate_of_workspace",
        module="app.financial.jobs.settings",
        method="handler_checking_status_deactivate_of_workspace",
    )
    register_clients_method(COMMUNITY_CATEGORY, client_ids,
                            data, mode_run=MODE_RUN_PARALLEL)
    logger.info(f"[Scheduler][{self.request.id}][checking_status_deactivate_of_workspace] "
                f"beat job for {len(client_ids)} clients")


@current_app.task(bind=True)
def mapping_cog_sale_item(self):
    client_ids = get_client_ids_active()
    logger.info(f"[Scheduler][{self.request.id}][mapping_cog_sale_item]"
                f" beat job for {len(client_ids)} clients")
    pick_jobs_mapping_cog_sale_item_recent(client_ids)


@current_app.task(bind=True)
def mapping_common_fields_sale_item(self):
    client_ids = get_client_ids_active()
    data = dict(
        name="mapping_common_fields_sale_item",
        job_name="app.financial.jobs.mapping_common_fields_items.handler_mapping_common_fields_sale_item",
        module="app.financial.jobs.mapping_common_fields_items",
        method="handler_mapping_common_fields_sale_item"
    )
    register_clients_method(SYNC_ANALYSIS_CATEGORY,
                            client_ids, data, mode_run=MODE_RUN_PARALLEL)
    logger.info(f"[Scheduler][{self.request.id}][mapping_common_fields_sale_item]"
                f" beat job for {len(client_ids)} clients")


@current_app.task(bind=True)
def mapping_common_fields_sale_item_from_dc(self):
    client_ids = get_client_ids_active()
    data = dict(
        name="mapping_common_fields_sale_item_from_dc",
        job_name="app.financial.jobs.mapping_common_fields_items.handler_mapping_common_fields_sale_item_from_dc",
        module="app.financial.jobs.mapping_common_fields_items",
        method="handler_mapping_common_fields_sale_item_from_dc"
    )
    register_clients_method(SYNC_ANALYSIS_CATEGORY,
                            client_ids, data, mode_run=MODE_RUN_PARALLEL)
    logger.info(f"[Scheduler][{self.request.id}][mapping_common_fields_sale_item_from_dc]"
                f" beat job for {len(client_ids)} clients")


@current_app.task(bind=True)
def mapping_cog_fields_sale_item_from_dc(self):
    client_ids = get_client_ids_active()
    logger.info(f"[Scheduler][{self.request.id}][mapping_cog_fields_sale_item_from_dc]"
                f" beat job for {len(client_ids)} clients")
    pick_jobs_mapping_sale_item_cog_dc_recent(client_ids)


@current_app.task(bind=True)
def mapping_common_fields_sale_item_from_ac(self):
    client_ids = get_client_ids_active()
    data = dict(
        name="mapping_common_fields_sale_item_from_ac",
        job_name="app.financial.jobs.mapping_common_fields_items.handler_mapping_common_fields_sale_item_from_ac",
        module="app.financial.jobs.mapping_common_fields_items",
        method="handler_mapping_common_fields_sale_item_from_ac"
    )
    register_clients_method(SYNC_ANALYSIS_CATEGORY,
                            client_ids, data, mode_run=MODE_RUN_PARALLEL)
    logger.info(f"[Scheduler][{self.request.id}][mapping_common_fields_sale_item_from_ac]"
                f" beat job for {len(client_ids)} clients")


@current_app.task(bind=True)
def shipping_cost_fedex_shipment_calculation(self):
    client_ids = get_client_ids_active()
    data = dict(
        name="shipping_cost_fedex_shipment_calculation",
        job_name="app.financial.jobs.shipping_cost.handler_shipping_cost_fedex_shipment_calculation",
        module="app.financial.jobs.shipping_cost",
        method="handler_shipping_cost_fedex_shipment_calculation"
    )
    register_clients_method(SYNC_ANALYSIS_CATEGORY,
                            client_ids, data, mode_run=MODE_RUN_PARALLEL)
    logger.info(f"[Scheduler][{self.request.id}][shipping_cost_fedex_shipment_calculation]"
                f" beat job for {len(client_ids)} clients")


@current_app.task(bind=True)
def shipping_cost_calculation(self):
    client_ids = get_client_ids_active()
    data = dict(
        name="shipping_cost_calculation",
        job_name="app.financial.jobs.shipping_cost.handler_shipping_cost_calculation",
        module="app.financial.jobs.shipping_cost",
        method="handler_shipping_cost_calculation"
    )
    register_clients_method(SYNC_ANALYSIS_CATEGORY,
                            client_ids, data, mode_run=MODE_RUN_PARALLEL)
    logger.info(f"[Scheduler][{self.request.id}][shipping_cost_calculation]"
                f" beat job for {len(client_ids)} clients")


@current_app.task(bind=True)
def notice_new_missing_brand(self):
    client_ids = get_client_ids_active()
    data = dict(
        name="notice_new_missing_brand",
        job_name="app.financial.jobs.settings.handler_notice_new_missing_brand",
        module="app.financial.jobs.settings",
        method="handler_notice_new_missing_brand"
    )
    register_clients_method(COMMUNITY_CATEGORY, client_ids,
                            data, mode_run=MODE_RUN_PARALLEL)
    logger.info(f"[Scheduler][{self.request.id}][notice_new_missing_brand]"
                f" beat job for {len(client_ids)} clients")


@current_app.task(bind=True)
def notice_no_brand_settings(self):
    client_ids = get_client_ids_active()
    data = dict(
        name="notice_no_brand_settings",
        job_name="app.financial.jobs.settings.handler_notice_no_brand_settings",
        module="app.financial.jobs.settings",
        method="handler_notice_no_brand_settings"
    )
    register_clients_method(COMMUNITY_CATEGORY, client_ids,
                            data, mode_run=MODE_RUN_PARALLEL)
    logger.info(f"[Scheduler][{self.request.id}][notice_no_brand_settings]"
                f" beat job for {len(client_ids)} clients")


#
@current_app.task(bind=True)
def clean_log_live_feed_flatten(self):
    client_ids = get_client_ids_active()
    data = dict(
        name="clean_log_live_feed_flatten",
        job_name="app.financial.jobs.data_flatten.handler_clean_log_live_feed_flatten",
        module="app.financial.jobs.data_flatten",
        method="handler_clean_log_live_feed_flatten"
    )
    register_clients_method(COMMUNITY_CATEGORY, client_ids,
                            data, mode_run=MODE_RUN_PARALLEL)
    logger.info(f"[Scheduler][{self.request.id}][clean_log_live_feed_flatten]"
                f" beat job for {len(client_ids)} clients")


@current_app.task(bind=True)
def get_trans_event_financial_recent(self):
    client_ids = get_client_ids_active()
    logger.info(f"[Scheduler][{self.request.id}][get_trans_event_financial_recent]"
                f" beat job for {len(client_ids)} clients")
    handler_trigger_trans_event_recent(client_ids=client_ids)


@current_app.task(bind=True)
def calculation_trans_event_to_sale_level_recent(self):
    client_ids = get_client_ids_active()
    logger.info(f"[Scheduler][{self.request.id}][calculation_trans_event_to_sale_level_recent]"
                f" beat job for {len(client_ids)} clients")
    handler_trigger_trans_event_to_sale_level_recent(client_ids=client_ids)


@current_app.task(bind=True)
def split_financial_sale_item_recent(self):
    client_ids = get_client_ids_active()
    logger.info(f"[Scheduler][{self.request.id}][split_financial_sale_item_recent]"
                f" beat job for {len(client_ids)} clients")
    handler_trigger_split_sale_item_financial_recent(client_ids=client_ids)


# Every day create record time tracking financial event status
@current_app.task(bind=True)
def job_time_control_create_event(self):
    client_ids = get_client_ids_active()
    data = dict(
        name="job_time_control_create_event",
        job_name="app.financial.jobs.time_control.handler_time_control_create_event",
        module="app.financial.jobs.time_control",
        method="handler_time_control_create_event"
    )
    register_clients_method(TIME_CONTROL_CATEGORY,
                            client_ids, data, mode_run=MODE_RUN_PARALLEL)
    logger.info(f"[Scheduler][{self.request.id}][job_time_control_create_event]"
                f" beat job for {len(client_ids)} clients")


# Execute at 0 minute per 1 hour
@current_app.task(bind=True)
def job_time_control_financial_check_event_is_ready(self):
    client_ids = get_client_ids_active()
    logger.info(f"[Scheduler][{self.request.id}][job_time_control_financial_check_event_is_ready]"
                f" beat job for {len(client_ids)} clients")
    pick_jobs_time_control_check_types_is_ready_workspaces(client_ids)


# Execute every 10' minute
@current_app.task(bind=True)
def job_time_control_financial_process_event_is_ready(self):
    client_ids = get_client_ids_active()
    logger.info(f"[Scheduler][{self.request.id}][job_time_control_financial_process_event_is_ready]"
                f" beat job for {len(client_ids)} clients")
    pick_jobs_time_control_process_types_is_ready_workspaces(client_ids)


@current_app.task(bind=True)
def job_trigger_get_orders_recent_posted_today(self):
    client_ids = get_client_ids_active()
    logger.info(f"[Scheduler][{self.request.id}][job_trigger_get_orders_recent_posted_today]"
                f" beat job for {len(client_ids)} clients")
    handler_trigger_get_orders_recent(
        client_ids=client_ids, recent_type=LIVE_FEED_RECENT_POSTED_TODAY_TYPE)


@current_app.task(bind=True)
def job_trigger_get_orders_recent_modified_today(self):
    client_ids = get_client_ids_active()
    logger.info(f"[Scheduler][{self.request.id}][job_trigger_get_orders_recent_modified_today]"
                f" beat job for {len(client_ids)} clients")
    handler_trigger_get_orders_recent(
        client_ids=client_ids, recent_type=LIVE_FEED_RECENT_MODIFIED_TODAY_TYPE)


@current_app.task(bind=True)
def job_trigger_get_orders_recent_replacement_modified_today(self):
    client_ids = get_client_ids_active()
    logger.info(f"[Scheduler][{self.request.id}][job_trigger_get_orders_recent_replacement_modified_today]"
                f" beat job for {len(client_ids)} clients")
    handler_trigger_get_orders_recent(client_ids=client_ids,
                                      recent_type=LIVE_FEED_RECENT_REPLACEMENT_RECENT_TODAY_TYPE)


@current_app.task(bind=True)
def job_trigger_get_informed_recent(self):
    client_ids = get_client_ids_active()
    logger.info(f"[Scheduler][{self.request.id}][job_trigger_get_informed_recent]"
                f" beat job for {len(client_ids)} clients")
    handler_trigger_get_informed_recent(client_ids=client_ids)


@current_app.task(bind=True)
def job_trigger_get_orders_cart_rover_recent(self):
    client_ids = get_client_ids_active()
    logger.info(f"[Scheduler][{self.request.id}][job_trigger_get_orders_cart_rover_recent]"
                f" beat job for {len(client_ids)} clients")
    handler_trigger_get_orders_cart_rover_recent(client_ids)


@current_app.task(bind=True)
def auto_generate_sale_items_data_feed(self):
    client_ids = get_client_ids_active()
    data = dict(
        name="auto_generate_sale_items_data_feed",
        job_name="app.financial.jobs.data_feed.handler_auto_generate_sale_items_data_feed",
        module="app.financial.jobs.data_feed",
        method="handler_auto_generate_sale_items_data_feed",
        time_limit=7200
    )
    register_clients_method(COMMUNITY_CATEGORY, client_ids,
                            data, mode_run=MODE_RUN_PARALLEL)
    logger.info(f"[Scheduler][{self.request.id}][auto_generate_sale_items_data_feed]"
                f" beat job for {len(client_ids)} clients")


@current_app.task(bind=True)
def auto_generate_yoy_sales_data_feed(self):
    client_ids = get_client_ids_active()
    data = dict(
        name="auto_generate_yoy_sales_data_feed",
        job_name="app.financial.jobs.data_feed.handler_auto_generate_yoy_30d_sales_data_feed",
        module="app.financial.jobs.data_feed",
        method="handler_auto_generate_yoy_30d_sales_data_feed",
        time_limit=7200
    )
    register_clients_method(COMMUNITY_CATEGORY, client_ids,
                            data, mode_run=MODE_RUN_PARALLEL)
    logger.info(f"[Scheduler][{self.request.id}][auto_generate_yoy_sales_data_feed]"
                f" beat job for {len(client_ids)} clients")


# At minute 0 past every 10 minute
@current_app.task(bind=True)
def reopen_task_bulk_process(self):
    client_ids = get_client_ids_active()
    data = dict(
        name="reopen_task_bulk_process",
        job_name="app.financial.jobs.re_open.handler_reopen_task_bulk_process",
        module="app.financial.jobs.re_open",
        method="handler_reopen_task_bulk_process"
    )
    register_clients_method(BULK_CATEGORY, client_ids,
                            data, mode_run=MODE_RUN_PARALLEL)
    logger.info(f"[Scheduler][{self.request.id}][reopen_task_bulk_process]"
                f" beat job for {len(client_ids)} clients")


@current_app.task(bind=True)
def generate_ds_calculate(self):
    client_ids = get_client_ids_active()
    data = dict(
        name="generate_ds_calculate",
        job_name="app.financial.jobs.ds_calculate.handler_trigger_generate_ds_calculate",
        module="app.financial.jobs.ds_calculate",
        method="handler_trigger_generate_ds_calculate",
        time_limit=7200
    )
    register_clients_method(DATA_SOURCE_CALCULATION_CATEGORY,
                            client_ids, data, mode_run=MODE_RUN_PARALLEL)
    logger.info(f"[Scheduler][{self.request.id}][generate_ds_calculate]"
                f" beat job for {len(client_ids)} clients")


@current_app.task(bind=True)
def sync_ac_ad_spend_information(self):
    client_ids = get_client_ids_active()
    data = dict(
        name="sync_ac_ad_spend_information",
        job_name="app.financial.jobs.data_feed.handler_sync_ac_ad_spend_information",
        module="app.financial.jobs.data_feed",
        method="handler_sync_ac_ad_spend_information"
    )
    register_clients_method(COMMUNITY_CATEGORY, client_ids,
                            data, mode_run=MODE_RUN_PARALLEL)
    logger.info(f"[Scheduler][{self.request.id}][sync_ac_ad_spend_information]"
                f" beat job for {len(client_ids)} clients")


@current_app.task(bind=True)
def job_trigger_alert_digest(self):
    client_ids = get_client_ids_active()
    logger.info(
        f"[job_trigger_alert_digest] beat job for {len(client_ids)} clients")
    #
    trigger_alert_refresh_rate_ws(client_ids)
    #
    trigger_alert_throttling_period_ws(client_ids)
    logger.info(f"[Scheduler][{self.request.id}][job_trigger_alert_digest]"
                f" beat job for {len(client_ids)} clients")


@current_app.task(bind=True)
def reopen_fedex_shipment_by_extension_recent(self):
    client_ids = get_client_ids_active()
    data = dict(
        name="reopen_fedex_shipment_by_extension_recent",
        job_name="app.financial.jobs.fedex_shipment.sale_item_reopen_fedex_shipment_job",
        module="app.financial.jobs.fedex_shipment",
        method="sale_item_reopen_fedex_shipment_job"
    )
    register_clients_method(SYNC_ANALYSIS_CATEGORY,
                            client_ids, data, mode_run=MODE_RUN_PARALLEL)
    logger.info(f"[Scheduler][{self.request.id}][reopen_fedex_shipment_by_extension_recent]"
                f" beat job for {len(client_ids)} clients")


@current_app.task(bind=True)
def job_calculation_top_product_performance(self):
    client_ids = get_client_ids_active()
    logger.info(f"[Scheduler][{self.request.id}][job_calculation_top_product_performance] "
                f"beat job for {len(client_ids)} clients")
    handler_pick_job_calculation_top_product_performance_clients(client_ids)
