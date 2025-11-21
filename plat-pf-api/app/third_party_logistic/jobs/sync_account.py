import logging
from celery import current_app
from django.db.models import Q
from app.core.services.ac_service import ACManager
from app.core.variable.sc_method import THIRD_PARTY_LOGISTIC_CONNECT_METHOD
from app.financial.models import ClientSettings
from app.job.utils.helper import register_list
from app.job.utils.variable import SELLING_PARTNER_CATEGORY, MODE_RUN_IMMEDIATELY
from app.third_party_logistic.models import Account3PLCentral

logger = logging.getLogger(__name__)


def pick_jobs_sync_account_3pl_central(client_ids: [str]):
    data = []
    for client_id in client_ids:
        objs = Account3PLCentral.objects.tenant_db_for(client_id).filter(client_id=client_id, synced=False)
        for obj in objs:
            job_id = str(obj.pk)
            data.append(
                dict(
                    name=f"sync_account_3pl_central_{job_id}",
                    client_id=client_id,
                    job_name="app.third_party_logistic.jobs.sync_account.sync_account_3pl_central",
                    module="app.third_party_logistic.jobs.sync_account",
                    method="sync_account_3pl_central",
                    meta=dict(client_id=client_id, obj_id=job_id)
                )
            )
    if len(data) > 0:
        register_list(SELLING_PARTNER_CATEGORY, data, mode_run=MODE_RUN_IMMEDIATELY)
        logger.info(f"[pick_jobs_sync_account_3pl_central][{client_ids}] register_list app jobs completed")


def sync_accounts_3pl_central_keys_setting(client_ids: [str]):
    logger.info(f"[{client_ids}][sync_account_3pl_central_keys_setting] Begin register ...")
    jobs_data = []
    for client_id in client_ids:
        client_id = str(client_id)
        setting = ClientSettings.objects.tenant_db_for(client_id).get(client_id=client_id)
        Account3PLCentral.objects.tenant_db_for(client_id).filter(~Q(enabled=setting.ac_3pl_central_enabled)) \
            .update(enabled=setting.ac_3pl_central_enabled, synced=False)
        # Sync cart rover has changed
        qs_syncing = Account3PLCentral.objects.tenant_db_for(client_id) \
            .filter(client_id=client_id, synced=False)
        logger.info(f"[sync_accounts_3pl_central_keys_setting][{client_id}] {qs_syncing.count()} objs syncing ...")
        for obj in qs_syncing:
            obj_id = str(obj.pk)
            data = dict(
                client_id=client_id,
                name=f"sync_account_3pl_central_{obj_id}",
                job_name="app.third_party_logistic.jobs.sync_account.sync_account_3pl_central",
                module="app.third_party_logistic.jobs.sync_account",
                method="sync_account_3pl_central",
                meta=dict(client_id=client_id, obj_id=obj_id)
            )
            jobs_data.append(data)

    if jobs_data:
        logger.info(f"[sync_accounts_3pl_central_keys_setting][{client_ids}] {jobs_data}")
        register_list(SELLING_PARTNER_CATEGORY, jobs_data, mode_run=MODE_RUN_IMMEDIATELY)
        logger.info(f"[sync_accounts_3pl_central_keys_setting][{client_ids}] register_list app jobs completed")


@current_app.task(bind=True)
def sync_account_3pl_central(self, client_id: str, obj_id: str):
    logger.info(f"[{self.request.id}][{client_id}][sync_account_3pl_central] "
                f"Begin register Object ID = {obj_id}....")
    obj = Account3PLCentral.objects.tenant_db_for(client_id).get(pk=obj_id)
    data = {
        "api_client_id": obj.client_auth_id,
        "api_client_secret": obj.client_auth_secret,
        "user_login_id": obj.user_login,
        "enabled": obj.enabled
    }
    ac_service = ACManager(client_id=client_id)
    rs = ac_service.register_integration_method_account(sc_method=THIRD_PARTY_LOGISTIC_CONNECT_METHOD, data=data)
    logger.info(f"[{self.request.id}][{client_id}]"
                f"[register_cart_rover_keys] status {rs.status_code} , content {rs.content.decode('utf-8')}")
    obj.synced = True
    obj.save()
    logger.info(f"[{self.request.id}][{client_id}][sync_account_3pl_central] "
                f"Register Object ID = {obj_id} completed")
