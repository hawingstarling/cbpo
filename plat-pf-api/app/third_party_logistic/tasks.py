from django.db import DEFAULT_DB_ALIAS
from .jobs.sync_account import *
from .jobs.frequency import *
from ..financial.models import ClientPortal

logger = logging.getLogger(__name__)


def get_client_ids_active():
    return ClientPortal.objects.tenant_db_for(DEFAULT_DB_ALIAS).filter(active=True).values_list('pk', flat=True)


@current_app.task(bind=True)
def job_trigger_get_orders_prime_3pl_central_recent(self):
    client_ids = get_client_ids_active()
    logger.info(f"[Scheduler][{self.request.id}][job_trigger_get_orders_prime_3pl_central_recent]"
                f" beat job for {len(client_ids)} clients")
    pick_jobs_getting_prime_3pl_central_recent(client_ids)


@current_app.task(bind=True)
def resync_3pl_accounts_central(self):
    client_ids = get_client_ids_active()
    pick_jobs_sync_account_3pl_central(client_ids)
    logger.info(f"[Scheduler][{self.request.id}][resync_3pl_accounts_central] beat job for {len(client_ids)} clients")
