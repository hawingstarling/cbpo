import logging
from typing import List

from django.db.utils import DEFAULT_DB_ALIAS
from rest_framework import status
from app.core.services.ac_service import ACManager
from app.financial.models import ClientSettings
from app.core.variable.sc_method import SPAPI_CONNECT_METHOD
from app.job.utils.helper import register_list
from app.job.utils.variable import COMMUNITY_CATEGORY, MODE_RUN_IMMEDIATELY
from celery import current_app
from app.selling_partner.models import SPOauthClientRegister, OauthTokenRequest, AppSetting

logger = logging.getLogger(__name__)


def tracking_oauth_client_register(client_id: str, creator_id: str):
    instance = ClientSettings.objects.tenant_db_for(client_id).get(client_id=client_id)
    assert instance.ac_spapi_state and instance.ac_spapi_auth_code and instance.ac_spapi_selling_partner_id, \
        "Selling partner setting is not Empty"
    oauth_token = OauthTokenRequest.objects.tenant_db_for(client_id) \
        .get(
        state=instance.ac_spapi_state,
        spapi_oauth_code=instance.ac_spapi_auth_code,
        selling_partner_id=instance.ac_spapi_selling_partner_id,
        status_code=status.HTTP_200_OK
    )
    app_setting = AppSetting.objects.tenant_db_for(client_id).get(spapi_app_id=instance.ac_spapi_app_id)
    SPOauthClientRegister.objects.tenant_db_for(client_id) \
        .update_or_create(client_id=client_id, oauth_token_request=oauth_token,
                          defaults=dict(app_setting=app_setting, latest=True, creator_id=creator_id))


def detecting_oauth_client_revoke(client_id: str, instance: ClientSettings):
    is_revoke_conn = instance.ac_spapi_state and instance.ac_spapi_auth_code and instance.ac_spapi_selling_partner_id
    oauth_client = SPOauthClientRegister.objects.tenant_db_for(client_id).filter(client_id=client_id)
    if not is_revoke_conn:
        oauth_client.update(latest=False)


def register_spapi_keys_setting(client_ids: List[str]):
    jobs_data = []
    for client_id in client_ids:
        client_id = str(client_id)
        #
        try:
            instance = ClientSettings.objects.tenant_db_for(client_id).get(client_id=client_id)
            detecting_oauth_client_revoke(client_id, instance)
            #
            spapi_setting = AppSetting.objects.tenant_db_for(client_id).get(spapi_app_id=instance.ac_spapi_app_id)
            assert spapi_setting is not None, "SPAPI setting is not None"
            #
            data_update = {
                'aws_access_key_id': spapi_setting.aws_access_key_id,
                'aws_secret_access_key': spapi_setting.aws_secret_access_key,
                'aws_default_region': spapi_setting.aws_default_region,
                'aws_role_arn': spapi_setting.aws_role_arn,
                'spapi_app_id': spapi_setting.spapi_app_id,
                'amz_lwa_client_id': spapi_setting.amz_lwa_client_id,
                'amz_lwa_client_secret': spapi_setting.amz_lwa_client_secret,
                #
                'amz_auth_code': instance.ac_spapi_auth_code,
                'amz_access_token': instance.ac_spapi_refresh_token,
                'amz_refresh_token': instance.ac_spapi_refresh_token,
                'amz_token_expired': instance.ac_spapi_token_expired,
                'amz_selling_partner_id': instance.ac_spapi_selling_partner_id,
                'enabled': instance.ac_spapi_enabled
            }
            data = dict(
                client_id=client_id,
                name=f"register_spapi_keys_{client_id}",
                job_name="app.selling_partner.jobs.register.register_spapi_keys",
                module="app.selling_partner.jobs.register",
                method="register_spapi_keys",
                meta=dict(client_id=client_id, data=data_update)
            )
            jobs_data.append(data)
        except Exception as ex:
            logger.error(f"[register_spapi_keys_setting] {ex}")
    if jobs_data:
        register_list(COMMUNITY_CATEGORY, jobs_data, mode_run=MODE_RUN_IMMEDIATELY)
        logger.info(f"[register_spapi_keys_setting][{client_ids}] register_list app jobs completed")


@current_app.task(bind=True)
def register_spapi_keys(self, client_id: str, data: dict):
    logger.info(f"[{self.request.id}][{client_id}][register_spapi_keys] Begin register ...")
    rs = ACManager(client_id=client_id).register_integration_method_keys(sc_method=SPAPI_CONNECT_METHOD, data=data)
    logger.info(f"[{self.request.id}][{client_id}][register_spapi_keys] "
                f"status {rs.status_code} , content {rs.content.decode('utf-8')}")


def recheck_spapi_connection_settings(client_ids: List[str]):
    jobs_data = []
    for client_id in client_ids:
        client_id = str(client_id)
        try:
            # @TODO: Handler more logics in the future
            data = dict(
                client_id=client_id,
                name=f"recheck_spapi_connection_{client_id}",
                job_name="app.selling_partner.jobs.register.recheck_spapi_connection",
                module="app.selling_partner.jobs.register",
                method="recheck_spapi_connection",
                meta=dict(client_id=client_id)
            )
            jobs_data.append(data)
        except Exception as ex:
            logger.error(f"[register_spapi_keys_setting] {ex}")
    if jobs_data:
        register_list(COMMUNITY_CATEGORY, jobs_data, mode_run=MODE_RUN_IMMEDIATELY)
        logger.info(f"[register_spapi_keys_setting][{client_ids}] register_list app jobs completed")


@current_app.task(bind=True)
def recheck_spapi_connection(self, client_id: str):
    logger.info(f"[{self.request.id}][recheck_spapi_connection] Beginning ...")
    setting = ClientSettings.objects.tenant_db_for(DEFAULT_DB_ALIAS).get(client_id=client_id)
    rs = ACManager(client_id=client_id).check_sc_connection(sc_method=SPAPI_CONNECT_METHOD)
    logger.info(f"[{self.request.id}][{client_id}][recheck_spapi_connection] "
                f"status {rs.status_code} , content {rs.content.decode('utf-8')}")
    if rs.status_code == status.HTTP_403_FORBIDDEN:
        setting.ac_spapi_need_reconnect = True
        setting.save()
