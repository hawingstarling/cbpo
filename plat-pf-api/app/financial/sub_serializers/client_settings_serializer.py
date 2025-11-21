import copy
import logging
from typing import Dict, Union

from django.db import transaction
from rest_framework import serializers

from app.core.exceptions import InvalidFormatException
from app.core.utils import get_app_setting_latest
from app.financial.jobs.activity import create_activity_by_action
from app.financial.jobs.register import register_mws_keys_setting, register_ac_clients_settings
from app.financial.models import ClientSettings
from app.core.sub_serializers.base_serializer import BaseSerializer
from app.database.sub_serializers.tenant_db_for_serializer import TenantDBForSerializer
from app.financial.variable.activity_variable import UPDATE_COGS_SOURCE_SETTINGS_KEY
from app.selling_partner.jobs.register import register_spapi_keys_setting, tracking_oauth_client_register
from app.selling_partner.models import AppSetting

logger = logging.getLogger(__name__)


class CartRoverSerializer(BaseSerializer):
    merchant_name = serializers.CharField(max_length=200)
    description = serializers.CharField(
        max_length=255, required=False, allow_null=True)
    api_user = serializers.CharField(max_length=200)
    api_key = serializers.CharField(max_length=200)


class ClientSettingBaseSerializer(TenantDBForSerializer):
    class Meta:
        model = ClientSettings
        exclude = (
            'is_removed',
            'client',
            'ac_cart_rover_api_user',
            'ac_cart_rover_api_key',
            'ac_cart_rover',
            'ac_cart_rover_enabled'
        )

    def handler_ac_client_register_changes(self, ins_origin, ins_target):
        if not ins_target.ac_client_register \
                or ins_origin.ac_spapi_enabled != ins_target.ac_spapi_enabled:
            logger.info(
                f"[{self.client_id}][handler_ac_client_register_changes] reg/update AC Client ....")
            register_ac_clients_settings([self.client_id])

    def is_changes_ac_spapi_settings(self, ins_origin, ins_target):
        logger.debug(
            f"[{self.client_id}][is_changes_ac_spapi_settings] checking changes ac spapi settings ....")
        ac_sc_origin = ClientSPAPIKeySettingSerializer(ins_origin).data
        ac_sc_latest = ClientSPAPIKeySettingSerializer(ins_target).data
        return ac_sc_origin != ac_sc_latest

    def mapping_app_setting(self, instance: Union[ClientSettings, None], validated_data: Dict):
        if (instance is None or instance.ac_spapi_app_id is None) and "ac_spapi_app_id" not in validated_data:
            app_setting = get_app_setting_latest(client_id=self.client_id)
            validated_data.update(
                dict(
                    ac_spapi_app_id=app_setting.spapi_app_id
                )
            )


class ClientSettingsSerializer(ClientSettingBaseSerializer):

    def create(self, validated_data):
        view = self.context['view']
        client_id = view.kwargs.get("client_id")
        validated_data.update({"is_removed": False})
        self.mapping_app_setting(instance=None, validated_data=validated_data)
        ins, _ = ClientSettings.all_objects.tenant_db_for(client_id) \
            .update_or_create(client_id=client_id, defaults=validated_data)
        #
        transaction.on_commit(
            lambda: {
                self.handler_register_sc_config(ins),
                self.handler_register_cogs_source_settings(ins)
            },
            using=self.client_db
        )
        return ins

    def update(self, instance, validated_data):
        #
        instance_origin = copy.deepcopy(instance)
        self.mapping_app_setting(
            instance=instance_origin, validated_data=validated_data)
        instance = super().update(instance, validated_data)
        #
        transaction.on_commit(
            lambda: {
                self.handler_register_sc_config(instance, instance_origin),
                self.handler_register_cogs_source_settings(
                    instance, instance_origin)
            },
            using=self.client_db
        )
        return instance

    def handler_register_sc_config(self, ins_target, ins_origin=None):
        try:
            client_ids = [str(ins_target.client_id)]
            #
            integration_origin = ClientIntegrationSerializer(ins_origin).data
            integration_latest = ClientIntegrationSerializer(ins_target).data
            if integration_origin == integration_latest:
                return
            self.handler_ac_client_register_changes(ins_origin, ins_target)
            #
            ac_mws_origin = ClientMWSKeySettingSerializer(ins_origin).data
            ac_mws_latest = ClientMWSKeySettingSerializer(ins_target).data
            if ac_mws_origin != ac_mws_latest:
                logger.info(
                    f"[{client_ids}][handler_register_sc_config] reg AC MWS ....")
                register_mws_keys_setting(client_ids)
            #
            if self.is_changes_ac_spapi_settings(ins_origin, ins_target):
                logger.info(
                    f"[{client_ids}][handler_register_sc_config] reg AC SPAPI ....")
                tracking_oauth_client_register(
                    self.client_id, self.user_request_id)
                register_spapi_keys_setting(client_ids)
        except Exception as ex:
            raise InvalidFormatException(message=str(ex), verbose=True)

    def handler_register_cogs_source_settings(self, ins_target, ins_origin=None):
        try:
            integration_origin = ClientCOGSSourceSettingSerializer(
                ins_origin).data
            integration_latest = ClientCOGSSourceSettingSerializer(
                ins_target).data
            if integration_origin == integration_latest:
                return
            # Write log activity
            data = dict()
            if ins_origin.cog_use_extensiv != ins_target.cog_use_extensiv:
                data['COG Use Extensiv'] = 'Enabled' if bool(
                    ins_target.cog_use_extensiv) else 'Disabled'
            if ins_origin.cog_extensiv_token != ins_target.cog_extensiv_token:
                data['COG Extensiv Token'] = '********' if bool(
                    ins_target.cog_extensiv_token) else 'None'
            if ins_origin.cog_use_dc != ins_target.cog_use_dc:
                data['COG Use DC'] = 'Enabled' if bool(
                    ins_target.cog_use_dc) else 'Disabled'
            if ins_origin.cog_use_pf != ins_target.cog_use_pf:
                data['COG Use Item'] = 'Enabled' if bool(
                    ins_target.cog_use_pf) else 'Disabled'
            if ins_origin.cog_priority_source != ins_target.cog_priority_source:
                data['COG Priority Source'] = ins_target.cog_priority_source if bool(
                    ins_target.cog_priority_source) else 'None'
            create_activity_by_action(client_id=self.client_id, user_id=self.user_request_id,
                                      action=UPDATE_COGS_SOURCE_SETTINGS_KEY, data=data)
        except Exception as ex:
            raise InvalidFormatException(message=str(ex), verbose=True)


class ClientIntegrationSerializer(ClientSettingBaseSerializer):
    class Meta(ClientSettingsSerializer.Meta):
        fields = ['ac_mws_access_key', 'ac_mws_secret_key', 'ac_mws_merchant_id', 'ac_mws_merchant_name',
                  'ac_mws_enabled', 'ac_spapi_access_token', 'ac_spapi_refresh_token', 'ac_spapi_token_expired',
                  'ac_spapi_selling_partner_id', 'ac_spapi_auth_code', 'ac_spapi_state', 'ac_spapi_enabled',
                  'ac_cart_rover', 'ac_cart_rover_enabled']
        exclude = []


class ClientMWSKeySettingSerializer(ClientSettingBaseSerializer):
    class Meta(ClientSettingsSerializer.Meta):
        fields = ['ac_mws_access_key', 'ac_mws_secret_key', 'ac_mws_merchant_id', 'ac_mws_merchant_name',
                  'ac_mws_enabled']
        exclude = []


class ClientSPAPIKeySettingSerializer(ClientSettingBaseSerializer):
    class Meta(ClientSettingsSerializer.Meta):
        fields = ['ac_spapi_app_id', 'ac_spapi_access_token', 'ac_spapi_refresh_token', 'ac_spapi_token_expired',
                  'ac_spapi_selling_partner_id', 'ac_spapi_auth_code', 'ac_spapi_state', 'ac_spapi_enabled',
                  'ac_spapi_need_reconnect']
        exclude = []


class ClientCartRoverSettingSerializer(ClientSettingBaseSerializer):
    class Meta(ClientSettingsSerializer.Meta):
        fields = ['ac_cart_rover', 'ac_cart_rover_enabled']
        exclude = []


class ClientCOGSSourceSettingSerializer(ClientSettingBaseSerializer):
    class Meta(ClientSettingsSerializer.Meta):
        fields = ['cog_use_extensiv', 'cog_extensiv_token',
                  'cog_use_dc', 'cog_use_pf', 'cog_priority_source']
        exclude = []
