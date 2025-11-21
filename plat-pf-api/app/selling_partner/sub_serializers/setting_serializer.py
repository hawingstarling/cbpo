import copy
import logging
from django.db import transaction
from app.database.sub_serializers.tenant_db_for_serializer import TenantDBForSerializer
from app.financial.jobs.activity import create_activity_by_action
from app.financial.sub_serializers.client_settings_serializer import ClientSPAPIKeySettingSerializer
from app.financial.variable.activity_variable import CONNECTION_SP_ACCOUNT_KEY, REVOKE_SP_ACCOUNT_KEY
from app.selling_partner.jobs.register import register_spapi_keys_setting, tracking_oauth_client_register
from app.selling_partner.models import AppSetting

logger = logging.getLogger(__name__)


class AppSettingSerializer(TenantDBForSerializer):
    class Meta:
        model = AppSetting
        fields = ["aws_default_region", "spapi_app_id"]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data.update(
            dict(
                aws_oauth_consent_url=instance.setting.aws_oauth_consent_url,
                api_aws_oauth_redirect=instance.setting.api_aws_oauth_redirect
            )
        )
        return data


class ConnectionSPAccountSerializer(ClientSPAPIKeySettingSerializer):

    def update(self, instance, validated_data):
        instance_origin = copy.deepcopy(instance)
        self.mapping_app_setting(instance=instance_origin, validated_data=validated_data)
        instance = super().update(instance, validated_data)
        if not self.is_changes_ac_spapi_settings(instance_origin, instance):
            return instance_origin
        #
        transaction.on_commit(
            lambda: {
                self.handler_ac_client_register_changes(instance_origin, instance),
                tracking_oauth_client_register(client_id=self.client_id, creator_id=self.user_request_id),
                register_spapi_keys_setting(client_ids=[self.client_id]),
                create_activity_by_action(client_id=self.client_id, user_id=self.user_request_id,
                                          action=CONNECTION_SP_ACCOUNT_KEY, data={}),
            },
            using=self.client_db
        )
        return instance


class RevokeSPAccountSerializer(ClientSPAPIKeySettingSerializer):
    def update(self, instance, validated_data):
        instance_origin = copy.deepcopy(instance)
        instance = super().update(instance, validated_data)
        if not self.is_changes_ac_spapi_settings(instance_origin, instance):
            return instance_origin
        #
        transaction.on_commit(
            lambda: {
                self.handler_ac_client_register_changes(instance_origin, instance),
                register_spapi_keys_setting([self.client_id]),
                create_activity_by_action(client_id=self.client_id, user_id=self.user_request_id,
                                          action=REVOKE_SP_ACCOUNT_KEY, data={}),
            },
            using=self.client_db
        )
        return instance
