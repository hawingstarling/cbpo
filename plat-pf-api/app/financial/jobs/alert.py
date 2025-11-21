import logging
from datetime import timedelta
from django.utils import timezone
from celery import current_app
from app.financial.models import Alert
from app.financial.services.alert.collect import CollectSaleAlert
from app.financial.services.alert.delivery import AlertDeliveryChannel
from app.financial.variable.alert import CONVERT_EVERY_CONFIG_TO_MINUTES
from app.job.utils.helper import register_list
from app.job.utils.variable import COMMUNITY_CATEGORY, MODE_RUN_PARALLEL

logger = logging.getLogger(__name__)


def trigger_alert_refresh_rate_ws(client_ids):
    now = timezone.now()
    jobs_data = []
    job_name = 'app.financial.jobs.alert.process_alert_refresh_rate_ws'
    module = "app.financial.jobs.alert"
    method = "process_alert_refresh_rate_ws"
    for client_id in client_ids:
        logger.info(f"[trigger_alert_refresh_rate_ws][{client_id}] Begin ...")
        #
        queryset = Alert.objects.tenant_db_for(client_id).filter(client_id=client_id)
        for item in queryset:
            logger.info(f"[trigger_alert_refresh_rate_ws][{client_id}] alert name {item.name}")
            distance = now - timedelta(minutes=CONVERT_EVERY_CONFIG_TO_MINUTES[item.refresh_rate])
            if item.last_refresh_rate is None or item.last_refresh_rate <= distance:
                data = dict(
                    name=f"process_alert_refresh_rate_{item.name}",
                    client_id=client_id,
                    job_name=job_name,
                    module=module,
                    method=method,
                    meta=dict(client_id=client_id, alert_id=item.pk)
                )
                jobs_data.append(data)
    if jobs_data:
        register_list(COMMUNITY_CATEGORY, jobs_data, mode_run=MODE_RUN_PARALLEL)
        logger.info(f"[trigger_alert_refresh_rate_ws][{client_ids}] register_list app jobs completed")


@current_app.task(bind=True)
def process_alert_refresh_rate_ws(self, client_id, alert_id):
    logger.info(f"[process_alert_refresh_rate][{self.request.id}][{client_id}][{alert_id}] Begin ...")
    alert = Alert.objects.tenant_db_for(client_id).get(pk=alert_id)
    CollectSaleAlert(client_id, alert_id).on_validate().on_process().on_complete()
    #
    if not alert.throttling_alert:
        process_alert_throttling_period_ws(client_id, alert_id)


def trigger_alert_throttling_period_ws(client_ids):
    now = timezone.now()
    jobs_data = []
    job_name = 'app.financial.jobs.alert.process_alert_throttling_period_ws'
    module = "app.financial.jobs.alert"
    method = "process_alert_throttling_period_ws"
    for client_id in client_ids:
        logger.info(f"[trigger_alert_throttling_period_ws][{client_id}] Begin ...")
        #
        queryset = Alert.objects.tenant_db_for(client_id).filter(client_id=client_id, throttling_alert=True)
        for item in queryset:
            logger.info(f"[trigger_alert_throttling_period_ws][{client_id}] alert name {item.name}")
            distance = now - timedelta(minutes=CONVERT_EVERY_CONFIG_TO_MINUTES[item.throttling_period])
            if item.last_throttling_period is None or item.last_throttling_period <= distance:
                data = dict(
                    name=f"process_alert_throttling_period_ws_{item.name}",
                    client_id=client_id,
                    job_name=job_name,
                    module=module,
                    method=method,
                    meta=dict(client_id=client_id, alert_id=item.pk)
                )
                jobs_data.append(data)
    if jobs_data:
        register_list(COMMUNITY_CATEGORY, jobs_data, mode_run=MODE_RUN_PARALLEL)
        logger.info(f"[trigger_alert_throttling_period_ws][{client_ids}] register_list app jobs completed")


@current_app.task(bind=True)
def process_alert_throttling_period_ws(self, client_id, alert_id):
    logger.info(f"[process_alert_throttling_period_ws][{self.request.id}][{client_id}][{alert_id}] Begin ...")
    AlertDeliveryChannel(client_id, alert_id).on_validate().on_process().on_complete()
