import logging
from typing import List

from celery import current_app
from app.job.utils.helper import register_list
from app.job.utils.variable import COMMUNITY_CATEGORY, MODE_RUN_IMMEDIATELY
from app.shopify_partner.services.integrations.ac_register_or_revoke import ac_register, ac_revoke

logger = logging.getLogger(__name__)


def register_sp_keys_setting(client_ids: List[str]):
    """
    used in django admin action
    """
    job_data = []
    for client_id in client_ids:
        data = {
            "name": "register_sp_keys",
            "client_id": client_id,
            "job_name": "register_sp_keys_job",
            "module": "app.shopify_partner.jobs.register",
            "method": "register_sp_keys_job",
            "priority": 0,
            "meta": {
                "data": {},
                "client_id": client_id
            }
        }
        job_data.append(data)

    register_list(COMMUNITY_CATEGORY, job_data, mode_run=MODE_RUN_IMMEDIATELY)
    logger.info(
        f"[register_sp_keys_setting][{client_ids}] register app jobs completed")


@current_app.task(bind=True)
def register_sp_keys_job(self, client_id: str, *args):
    logger.info(f"[{self.request.id}][{client_id}][register_sp_keys_job][Shopify Partner] "
                f"Begin register_sp_keys_job ...")
    ac_register(client_id)


@current_app.task(bind=True)
def revoke_sp_key_job(self, client_id: str, *args):
    logger.info(f"[{self.request.id}][{client_id}][revoke_sp_key_job][Shopify Partner] "
                f"Begin revoke_sp_key_job ...")
    ac_revoke(client_id)
