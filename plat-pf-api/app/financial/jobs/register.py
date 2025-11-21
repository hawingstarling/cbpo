import logging
from django.db.models import Q
from rest_framework.status import HTTP_200_OK
from celery import current_app
from app.core.services.ac_service import ACManager
from app.financial.models import ClientPortal, ClientSettings, ClientCartRoverSetting
from app.core.variable.sc_method import MWS_CONNECT_METHOD, CART_ROVER_CONNECT_METHOD
from app.job.utils.helper import register_list
from app.job.utils.variable import COMMUNITY_CATEGORY, MODE_RUN_IMMEDIATELY

logger = logging.getLogger(__name__)


def register_ac_clients_settings(client_ids: [str]):
    jobs_data = []
    for client_id in client_ids:
        data = dict(
            client_id=client_id,
            name=f"register_ac_clients_{client_id}",
            job_name="app.financial.jobs.register.register_ac_clients",
            module="app.financial.jobs.register",
            method="register_ac_clients",
            meta=dict(client_id=client_id)
        )
        jobs_data.append(data)
    register_list(COMMUNITY_CATEGORY, jobs_data, mode_run=MODE_RUN_IMMEDIATELY)
    logger.info(f"[register_ac_clients_settings][{client_ids}] register_list app jobs completed")


@current_app.task(bind=True)
def register_ac_clients(self, client_id: str):
    #
    ac_manager = ACManager(client_id=client_id, using_api_key=True)
    client = ClientPortal.all_objects.tenant_db_for(client_id).get(pk=client_id)
    setting_client, _ = ClientSettings.objects.tenant_db_for(client_id).get_or_create(client_id=client_id)
    data = {
        "name": client.name,
        "mws_job_enabled": getattr(setting_client, "ac_mws_enabled", False),
        "spapi_job_enabled": getattr(setting_client, "ac_spapi_enabled", False),
        "enabled": client.active and not client.is_removed,
        "is_oe": client.is_oe
    }
    method = "POST"
    try:
        retrieve = ac_manager.manage_clients(method="GET")
        if retrieve.status_code == HTTP_200_OK:
            method = "PUT"
        else:
            data.update({"id": client_id})
    except Exception as ex:
        logger.error(f"[register_ac_clients] {ex}")
        data.update({"id": client_id})
    rs = ac_manager.manage_clients(method=method, data=data)
    status_code = rs.status_code
    content = rs.content.decode('utf-8')
    if not setting_client.ac_client_register and status_code == HTTP_200_OK:
        setting_client.ac_client_register = True
        setting_client.save()
    logger.info(f"[{self.request.id}][{client_id}][register_ac_clients] status {status_code} , content {content}")


def register_mws_keys_setting(client_ids: [str]):
    jobs_data = []
    for client_id in client_ids:
        client_id = str(client_id)
        instance = ClientSettings.objects.tenant_db_for(client_id).get(client_id=client_id)
        data_update = {
            'access_key': instance.ac_mws_access_key,
            'secret_key': instance.ac_mws_secret_key,
            'merchant_id': instance.ac_mws_merchant_id,
            'merchant_name': instance.ac_mws_merchant_name,
            'enabled': instance.ac_mws_enabled,
        }
        data = dict(
            client_id=client_id,
            name=f"register_mws_keys_{client_id}",
            job_name="app.financial.jobs.register.register_mws_keys",
            module="app.financial.jobs.register",
            method="register_mws_keys",
            meta=dict(client_id=client_id, data=data_update)
        )
        jobs_data.append(data)
    register_list(COMMUNITY_CATEGORY, jobs_data, mode_run=MODE_RUN_IMMEDIATELY)
    logger.info(f"[register_mws_keys_setting][{client_ids}] register_list app jobs completed")


@current_app.task(bind=True)
def register_mws_keys(self, client_id: str, data: dict):
    logger.info(f"[{self.request.id}][{client_id}][register_mws_keys] Begin register ...")
    rs = ACManager(client_id=client_id).register_integration_method_keys(sc_method=MWS_CONNECT_METHOD, data=data)
    logger.info(
        f"[{self.request.id}][{client_id}][register_mws_keys] status {rs.status_code} , content {rs.content.decode('utf-8')}")


def register_cart_rover_keys_setting(client_ids: [str]):
    logger.info(f"[{client_ids}][register_cart_rover_keys_setting] Begin register ...")
    jobs_data = []
    for client_id in client_ids:
        client_id = str(client_id)
        instance = ClientSettings.objects.tenant_db_for(client_id).get(client_id=client_id)
        ac_cart_rovers = instance.ac_cart_rover
        api_users = [item["api_user"] for item in ac_cart_rovers]
        ac_cart_rover_enabled = instance.ac_cart_rover_enabled
        if not ac_cart_rover_enabled or not ac_cart_rovers:
            cond_disabled = Q(client_id=client_id, enabled=True)
        else:
            for ac_cart_rover in ac_cart_rovers:
                ClientCartRoverSetting.objects.tenant_db_for(client_id).update_or_create(
                    client_id=client_id,
                    api_user=ac_cart_rover["api_user"],
                    api_key=ac_cart_rover["api_key"],
                    defaults=dict(
                        merchant_name=ac_cart_rover.get("merchant_name"),
                        description=ac_cart_rover.get("description"),
                        enabled=ac_cart_rover_enabled,
                        synced=False
                    ))
            cond_disabled = Q(client_id=client_id, enabled=True) & ~Q(api_user__in=api_users)
        # disabled account not in client settings
        ClientCartRoverSetting.objects.tenant_db_for(client_id).filter(cond_disabled) \
            .update(enabled=False, synced=False)
        # Sync cart rover has changed
        qs_syncing = ClientCartRoverSetting.objects.tenant_db_for(client_id) \
            .filter(client_id=client_id, synced=False)
        logger.info(f"[register_cart_rover_keys_setting][{client_id}] {qs_syncing.count()} objs syncing ...")
        for obj in qs_syncing:
            obj_id = str(obj.pk)
            data = dict(
                client_id=client_id,
                name=f"register_cart_rover_keys_{obj_id}",
                job_name="app.financial.jobs.register.register_cart_rover_keys",
                module="app.financial.jobs.register",
                method="register_cart_rover_keys",
                meta=dict(client_id=client_id, obj_id=obj_id)
            )
            jobs_data.append(data)

    if jobs_data:
        logger.info(f"[register_cart_rover_keys_setting][{client_ids}] {jobs_data}")
        register_list(COMMUNITY_CATEGORY, jobs_data, mode_run=MODE_RUN_IMMEDIATELY)
        logger.info(f"[register_cart_rover_keys_setting][{client_ids}] register_list app jobs completed")


@current_app.task(bind=True)
def register_cart_rover_keys(self, client_id: str, obj_id: str):
    logger.info(f"[{self.request.id}][{client_id}][register_cart_rover_keys] Begin sync Object ID = {obj_id} ...")
    obj = ClientCartRoverSetting.objects.tenant_db_for(client_id).get(pk=obj_id)
    data = {
        'merchant': obj.merchant_name,
        'api_user': obj.api_user,
        'api_key': obj.api_key,
        'enabled': obj.enabled
    }
    rs = ACManager(client_id=client_id).register_integration_method_account(sc_method=CART_ROVER_CONNECT_METHOD,
                                                                            data=data)
    obj.synced = True
    obj.save()
    logger.info(f"[{self.request.id}][{client_id}]"
                f"[register_cart_rover_keys] synced Object ID = {obj_id} "
                f"Result = status {rs.status_code} , content {rs.content.decode('utf-8')}")
