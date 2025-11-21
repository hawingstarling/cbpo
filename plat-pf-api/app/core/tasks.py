from celery.schedules import crontab
from .jobs.command import *
from ..financial.services.fedex_shipment.config import SCHEDULER_HOURS_REOPEN_BY_EXTENSION


@current_app.task(bind=True)
def test_periodic_task(self):
    print(f"[Scheduler][{self.request.id}] Periodic Task is running ....")


current_app.conf.beat_schedule = {
    # Core
    "app.core.tasks.test_periodic_task": {
        "task": "app.core.tasks.test_periodic_task",
        "schedule": crontab(hour="0", minute="0")
    },
    # Job
    "app.job.tasks.process_task_route_config": {
        "task": "app.job.tasks.process_task_route_config",
        "schedule": crontab(hour="*/1", minute="0")
    },
    "app.job.tasks.process_scheduled_job_category": {
        "task": "app.job.tasks.process_scheduled_job_category",
        "schedule": crontab(minute="*/5")
    },
    "app.job.tasks.clean_scheduled_job_category": {
        "task": "app.job.tasks.clean_scheduled_job_category",
        "schedule": crontab(minute="0", hour="0", day_of_month="1,15")
    },
    # Stat reports
    "app.stat_report.tasks.health_check_clients_scheduler": {
        "task": "app.stat_report.tasks.health_check_clients_scheduler",
        "schedule": crontab(hour="*/4", minute="0")
    },
    "app.stat_report.tasks.stats_time_control_report_clients_scheduler": {
        "task": "app.stat_report.tasks.stats_time_control_report_clients_scheduler",
        "schedule": crontab(hour="*/4", minute="0")
    },
    "app.stat_report.tasks.stats_sale_recent_report_clients_scheduler": {
        "task": "app.stat_report.tasks.stats_sale_recent_report_clients_scheduler",
        "schedule": crontab(hour="*/1", minute="0")
    },
    "app.stat_report.tasks.calculation_clients_report_cost": {
        "task": "app.stat_report.tasks.calculation_clients_report_cost",
        "schedule": crontab(minute="0", hour="0", day_of_month="1")
    },
    # EDI
    "app.edi.tasks.prefetch_edi_invoice_source": {
        "task": "app.edi.tasks.prefetch_edi_invoice_source",
        "schedule": crontab(minute="*/5")
    },
    "app.edi.tasks.up_edi_to_fedex_shipment": {
        "task": "app.edi.tasks.up_edi_to_fedex_shipment",
        "schedule": crontab(hour="*/10")
    },
    "app.edi.tasks.reopen_edi_invoice_source": {
        "task": "app.edi.tasks.reopen_edi_invoice_source",
        "schedule": crontab(minute="0", hour="*/2")
    },
    "app.edi.tasks.clean_edi_invoice_tracking": {
        "task": "app.edi.tasks.clean_edi_invoice_tracking",
        "schedule": crontab(minute="0", hour="0", day_of_month="1")
    },
    # Selling Partner
    "app.selling_partner.tasks.get_sp_report_status_clients": {
        "task": "app.selling_partner.tasks.get_sp_report_status_clients",
        "schedule": crontab(minute="*/10")
    },
    "app.selling_partner.tasks.generate_sp_report_brands_summary_clients": {
        "task": "app.selling_partner.tasks.generate_sp_report_brands_summary_clients",
        "schedule": crontab(minute="0", hour="0", day_of_month="15")
    },
    "app.selling_partner.tasks.check_sp_amz_lwa_expired": {
        "task": "app.selling_partner.tasks.check_sp_amz_lwa_expired",
        "schedule": crontab(minute="0", hour="0")
    },
    # Financial
    "app.financial.tasks.recover_data_source": {
        "task": "app.financial.tasks.recover_data_source",
        "schedule": crontab(minute="0", hour="*/1")
    },
    "app.financial.tasks.resync_data_source": {
        "task": "app.financial.tasks.resync_data_source",
        "schedule": crontab(minute="0", hour="*/1")
    },
    "app.financial.tasks.checking_status_deactivate_of_workspace": {
        "task": "app.financial.tasks.checking_status_deactivate_of_workspace",
        "schedule": crontab(minute="0", hour="0")
    },
    "app.financial.tasks.mapping_cog_sale_item": {
        "task": "app.financial.tasks.mapping_cog_sale_item",
        "schedule": crontab(minute="*/10")
    },
    "app.financial.tasks.mapping_common_fields_sale_item": {
        "task": "app.financial.tasks.mapping_common_fields_sale_item",
        "schedule": crontab(minute="*/10")
    },
    "app.financial.tasks.mapping_common_fields_sale_item_from_dc": {
        "task": "app.financial.tasks.mapping_common_fields_sale_item_from_dc",
        "schedule": crontab(minute="*/10")
    },
    "app.financial.tasks.mapping_cog_fields_sale_item_from_dc": {
        "task": "app.financial.tasks.mapping_cog_fields_sale_item_from_dc",
        "schedule": crontab(minute="*/10")
    },
    "app.financial.tasks.mapping_common_fields_sale_item_from_ac": {
        "task": "app.financial.tasks.mapping_common_fields_sale_item_from_ac",
        "schedule": crontab(minute="*/10")
    },
    "app.financial.tasks.shipping_cost_fedex_shipment_calculation": {
        "task": "app.financial.tasks.shipping_cost_fedex_shipment_calculation",
        "schedule": crontab(minute="*/10")
    },
    "app.financial.tasks.shipping_cost_calculation": {
        "task": "app.financial.tasks.shipping_cost_calculation",
        "schedule": crontab(minute="*/10")
    },
    "app.financial.tasks.notice_new_missing_brand": {
        "task": "app.financial.tasks.notice_new_missing_brand",
        "schedule": crontab(minute="0", hour="*/1")
    },
    "app.financial.tasks.notice_no_brand_settings": {
        "task": "app.financial.tasks.notice_no_brand_settings",
        "schedule": crontab(minute="0", hour="0")
    },
    "app.financial.tasks.clean_log_live_feed_flatten": {
        "task": "app.financial.tasks.clean_log_live_feed_flatten",
        "schedule": crontab(minute="0", hour="0")
    },
    "app.financial.tasks.get_trans_event_financial_recent": {
        "task": "app.financial.tasks.get_trans_event_financial_recent",
        "schedule": crontab(minute="*/10")
    },
    "app.financial.tasks.calculation_trans_event_to_sale_level_recent": {
        "task": "app.financial.tasks.calculation_trans_event_to_sale_level_recent",
        "schedule": crontab(minute="*/30")
    },
    "app.financial.tasks.split_financial_sale_item_recent": {
        "task": "app.financial.tasks.split_financial_sale_item_recent",
        "schedule": crontab(minute="0", hour="*/1")
    },
    "app.financial.tasks.job_time_control_create_event": {
        "task": "app.financial.tasks.job_time_control_create_event",
        "schedule": crontab(minute="0", hour="0")
    },
    "app.financial.tasks.job_time_control_financial_check_event_is_ready": {
        "task": "app.financial.tasks.job_time_control_financial_check_event_is_ready",
        "schedule": crontab(minute="0", hour="*/1")
    },
    "app.financial.tasks.job_time_control_financial_process_event_is_ready": {
        "task": "app.financial.tasks.job_time_control_financial_process_event_is_ready",
        "schedule": crontab(minute="*/10")
    },
    "app.financial.tasks.job_trigger_get_orders_recent_posted_today": {
        "task": "app.financial.tasks.job_trigger_get_orders_recent_posted_today",
        "schedule": crontab(minute="*/5")
    },
    "app.financial.tasks.job_trigger_get_orders_recent_modified_today": {
        "task": "app.financial.tasks.job_trigger_get_orders_recent_modified_today",
        "schedule": crontab(minute="*/15")
    },
    "app.financial.tasks.job_trigger_get_orders_recent_replacement_modified_today": {
        "task": "app.financial.tasks.job_trigger_get_orders_recent_replacement_modified_today",
        "schedule": crontab(minute="*/15")
    },
    "app.financial.tasks.job_trigger_get_informed_recent": {
        "task": "app.financial.tasks.job_trigger_get_informed_recent",
        "schedule": crontab(minute="*/10")
    },
    # "app.financial.tasks.job_trigger_get_orders_cart_rover_recent": {
    #     "task": "app.financial.tasks.job_trigger_get_orders_cart_rover_recent",
    #     "schedule": crontab(minute="0", hour="*/2")
    # },
    "app.financial.tasks.auto_generate_sale_items_data_feed": {
        "task": "app.financial.tasks.auto_generate_sale_items_data_feed",
        "schedule": crontab(minute="1", hour="0")
    },
    "app.financial.tasks.auto_generate_yoy_sales_data_feed": {
        "task": "app.financial.tasks.auto_generate_yoy_sales_data_feed",
        "schedule": crontab(minute="1", hour="0")
    },
    "app.financial.tasks.reopen_task_bulk_process": {
        "task": "app.financial.tasks.reopen_task_bulk_process",
        "schedule": crontab(minute="*/10")
    },
    "app.financial.tasks.generate_ds_calculate": {
        "task": "app.financial.tasks.generate_ds_calculate",
        "schedule": crontab(minute="*/30")
    },
    "app.financial.tasks.sync_ac_ad_spend_information": {
        "task": "app.financial.tasks.sync_ac_ad_spend_information",
        "schedule": crontab(hour="*/3", minute="0")
    },
    "app.financial.tasks.job_trigger_alert_digest": {
        "task": "app.financial.tasks.job_trigger_alert_digest",
        "schedule": crontab(minute="*/5")
    },
    "app.financial.tasks.reopen_fedex_shipment_by_extension_recent": {
        "task": "app.financial.tasks.reopen_fedex_shipment_by_extension_recent",
        "schedule": crontab(hour=f"*/{SCHEDULER_HOURS_REOPEN_BY_EXTENSION}", minute="0")
    },
    "app.financial.tasks.job_calculation_top_product_performance": {
        "task": "app.financial.tasks.job_calculation_top_product_performance",
        "schedule": crontab(hour="*/3", minute="0")
    },
    # Third Party Logistic
    "app.third_party_logistic.tasks.job_trigger_get_orders_prime_3pl_central_recent": {
        "task": "app.third_party_logistic.tasks.job_trigger_get_orders_prime_3pl_central_recent",
        "schedule": crontab(minute="0", hour="*/2")
    },
    "app.third_party_logistic.tasks.resync_3pl_accounts_central": {
        "task": "app.third_party_logistic.tasks.resync_3pl_accounts_central",
        "schedule": crontab(minute="0", hour="0")
    },
    # Lib Import
    "plat_import_lib_api.tasks.auto_check_health_module": {
        "task": "plat_import_lib_api.tasks.auto_check_health_module",
        "schedule": crontab(minute="0", hour="*/2")
    },
    "plat_import_lib_api.tasks.auto_clean_import_temp_completed": {
        "task": "plat_import_lib_api.tasks.auto_clean_import_temp_completed",
        "schedule": crontab(minute="0", hour="0", day_of_month="1")
    },
    "plat_import_lib_api.tasks.reopen_lib_import_process_action": {
        "task": "plat_import_lib_api.tasks.reopen_lib_import_process_action",
        "schedule": crontab(minute="*/10")
    },
    # Extensiv
    "app.extensiv.tasks.job_trigger_mapping_sale_item_cog_extensiv_recent": {
        "task": "app.extensiv.tasks.job_trigger_mapping_sale_item_cog_extensiv_recent",
        "schedule": crontab(minute="*/10")
    }
}
