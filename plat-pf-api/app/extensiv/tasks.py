from django.db import DEFAULT_DB_ALIAS

from app.extensiv.jobs.mapping import *
from app.financial.models import ClientPortal


def get_client_ids_active():
    return ClientPortal.objects.tenant_db_for(DEFAULT_DB_ALIAS).filter(active=True).values_list('pk', flat=True)


@current_app.task(bind=True)
def job_trigger_mapping_sale_item_cog_extensiv_recent(self):
    client_ids = get_client_ids_active()
    logger.info(f"[Scheduler][{self.request.id}][job_trigger_mapping_sale_item_cog_extensiv_recent]"
                f" beat job for {len(client_ids)} clients")
    pick_jobs_mapping_sale_item_cog_extensiv_recent(client_ids)
