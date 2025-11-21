from bulk_sync import bulk_sync
from django.db import transaction
from django.db.models import Q
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from app.permission.config_static_varible.common import STATUS_PERMISSION_ENUM, PERMISSION_CLIENT_ENUM
from app.permission.models import AccessRulePermission, AccessRule, Permission
from app.permission.serializers import UserCommonSerializer
from app.permission.services.access_rule_service import AccessRuleService
from app.permission.services.custom_role_service import CustomRoleService
from app.permission.sub_serializers.base_serializer import BaseSerializer
from app.permission.sub_serializers.permission_group_serializer import PermissionGroupPayloadSerializer, \
    PermissionGroupSerializer, ModuleObjectSerializer


class AccessRuleClientPayloadUpdateSerializer(BaseSerializer):
    name = serializers.CharField(max_length=100, required=False)
    permissions_groups = serializers.ListField(child=PermissionGroupPayloadSerializer(), required=False)

    def update(self, instance, validated_data):
        with transaction.atomic():
            self.sync_access_rule_update(instance=instance, validated_data=validated_data)

    def sync_access_rule_update(self, instance: AccessRule, validated_data: dict = {}):
        content_obj = self.context.get('content_obj')
        level = self.context.get('level')
        AccessRuleService.update_access_rule_of_client(access_rule=instance, data=validated_data)
        if len(validated_data.get('permissions_groups')) > 0:
            print('test')
            CustomRoleService.sync_access_rule_relate_custom_roles(content_obj=content_obj, level=level,
                                                                   access_rule=instance)

    def validate(self, attrs):
        if not attrs:
            raise ValidationError(["data request"])
        return attrs


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['name', 'key', 'group', 'module']


class AccessRulePermissionSerializer(serializers.ModelSerializer):
    key = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    group = serializers.SerializerMethodField()
    module = serializers.SerializerMethodField()

    class Meta:
        model = AccessRulePermission
        fields = ['key', 'name', 'status', 'group', 'module']

    def get_key(self, instance):
        return instance.permission.key

    def get_name(self, instance):
        return instance.permission.name

    def get_group(self, instance):
        return instance.permission.group

    def get_module(self, instance):
        return instance.permission.module


class PermissionJSONSerializer(serializers.Serializer):
    key = serializers.ChoiceField(choices=PERMISSION_CLIENT_ENUM)
    status = serializers.ChoiceField(choices=STATUS_PERMISSION_ENUM)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class PermissionGroupJSONSerializer(serializers.Serializer):
    group = PermissionGroupSerializer(required=False)
    permissions = serializers.ListField(child=PermissionJSONSerializer())
    module = ModuleObjectSerializer(required=False)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class AccessRuleSerializer(serializers.ModelSerializer):
    permissions_groups = serializers.ListField(child=PermissionGroupJSONSerializer(), write_only=True)

    class Meta:
        model = AccessRule
        exclude = ('is_removed', 'object_id', 'content_type', 'type_created', 'key',)

        read_only_fields = ['owner', ]

    def create(self, validated_data):
        with transaction.atomic():
            permissions_groups = validated_data.pop('permissions_groups')
            instance = super(AccessRuleSerializer, self).create(validated_data)
            self.handle_list_of_access_rule_permission(instance, permissions_groups)
            return instance

    def update(self, instance, validated_data):
        with transaction.atomic():
            permissions_groups = validated_data.pop('permissions_groups')
            instance = super().update(instance, validated_data)
            self.handle_list_of_access_rule_permission(instance, permissions_groups)
            return instance

    def handle_list_of_access_rule_permission(self, instance_access_rule, validated_permissions_groups):
        list_access_rule_permission = []
        for per_group in validated_permissions_groups:
            group_key = per_group.get('group')['key']
            list_per = per_group.get('permissions')
            for per in list_per:
                per_key = per.get('key')
                per_status = per.get('status')
                try:
                    per_ins = Permission.objects.get(key=per_key, group=group_key)
                    list_access_rule_permission.append(AccessRulePermission(access_rule=instance_access_rule,
                                                                            permission=per_ins,
                                                                            status=per_status,
                                                                            is_removed=False))
                except Permission.DoesNotExist:
                    raise ValidationError('Permission does not exist. [{}, {}]'.format(per_key, group_key))

        bulk_sync(
            filters=Q(access_rule=instance_access_rule),
            new_models=list_access_rule_permission,
            fields=['access_rule_id', 'permission_id', 'status', 'is_removed'],
            key_fields=['access_rule_id', 'permission_id']
        )


class AccessRuleDetailSerializer(AccessRuleSerializer):
    permissions_groups = serializers.SerializerMethodField(method_name='get_detail_permission', read_only=True)

    def get_detail_permission(self, obj):
        return AccessRuleService.get_permission_detail_by_access_rule(obj)

    def to_representation(self, instance):
        self.fields['owner'] = UserCommonSerializer(read_only=True)
        return super().to_representation(instance)


class AccessRuleForListingSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessRule
        fields = ['id', 'name', 'level', 'type_created', 'created', 'modified', 'owner']

    def to_representation(self, instance):
        self.fields['owner'] = UserCommonSerializer(read_only=True)
        return super().to_representation(instance)
