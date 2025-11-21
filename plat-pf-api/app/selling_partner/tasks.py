import logging
from datetime import timedelta

from django.db.utils import DEFAULT_DB_ALIAS
from django.utils import timezone

from app.financial.models import ClientPortal, ClientSettings
from app.selling_partner.jobs.report import handler_trigger_sp_report_clients
from app.selling_partner.jobs.report_brand_summary import create_jobs_sp_report_brands_summary_clients
from celery import current_app

from app.selling_partner.models import AppSetting

logger = logging.getLogger(__name__)


def get_client_ids_active():
    return ClientPortal.objects.tenant_db_for(DEFAULT_DB_ALIAS).filter(active=True).values_list('pk', flat=True)


@current_app.task(bind=True)
def get_sp_report_status_clients(self):
    client_ids = get_client_ids_active()
    handler_trigger_sp_report_clients(client_ids)
    logger.info(f"[Scheduler][{self.request.id}][get_sp_report_status_clients] beat job for {len(client_ids)} clients")


@current_app.task(bind=True)
def generate_sp_report_brands_summary_clients(self):
    client_ids = get_client_ids_active()
    create_jobs_sp_report_brands_summary_clients(client_ids=client_ids)
    logger.info(f"[Scheduler][{self.request.id}][generate_sp_report_brands_summary_clients]"
                f" beat job for {len(client_ids)} clients")


@current_app.task(bind=True)
def check_sp_amz_lwa_expired(self):
    logger.info(f"[Scheduler][{self.request.id}][check_sp_amz_lwa_expired] Beginning ...")

    app_settings = AppSetting.objects.tenant_db_for(DEFAULT_DB_ALIAS).all()
    date_now = timezone.now().date()

    for app_setting in app_settings:
        try:
            if not app_setting.amz_lwa_expired:
                raise ValueError("amz_lwa_expired is None")

            if app_setting.amz_lwa_expired.date() < date_now:
                logger.info(
                    f"[Scheduler][{self.request.id}][check_sp_amz_lwa_expired] "
                    f"LWA expired over 1 days ago for App ID {app_setting.spapi_app_id}"
                )
                ClientSettings.objects.tenant_db_for(DEFAULT_DB_ALIAS) \
                    .filter(ac_spapi_app_id=app_setting.spapi_app_id, ac_spapi_enabled=True) \
                    .update(ac_spapi_need_reconnect=True)
            else:
                logger.info(
                    f"[Scheduler][{self.request.id}][check_sp_amz_lwa_expired] "
                    f"LWA has not expired for App ID {app_setting.spapi_app_id}"
                )

        except Exception as ex:
            logger.error(
                f"[Scheduler][{self.request.id}][check_sp_amz_lwa_expired] "
                f"Error for App ID {app_setting.spapi_app_id}: {ex}"
            )

    return f"Checked {app_settings.count()} app settings"
