from rest_framework import serializers

from app.permission.config_static_varible.common import GROUP_PERMISSION_CLIENT_ENUM, PERMISSION_CLIENT_ENUM, \
    STATUS_PERMISSION_ENUM, MODULE_ENUM
from app.permission.models import Permission
from app.permission.sub_serializers.base_serializer import BaseSerializer


class PermissionsPayloadSerializer(BaseSerializer):
    key = serializers.ChoiceField(choices=PERMISSION_CLIENT_ENUM)
    status = serializers.ChoiceField(choices=STATUS_PERMISSION_ENUM)


class PermissionGroupSerializer(BaseSerializer):
    key = serializers.ChoiceField(choices=GROUP_PERMISSION_CLIENT_ENUM)
    name = serializers.CharField(max_length=100, required=False)


class ModuleObjectSerializer(BaseSerializer):
    key = serializers.ChoiceField(choices=MODULE_ENUM)
    name = serializers.CharField(max_length=100, required=False)


class PermissionGroupPayloadSerializer(BaseSerializer):
    group = PermissionGroupSerializer()
    module = ModuleObjectSerializer()
    permissions = serializers.ListField(child=PermissionsPayloadSerializer())


class PermissionsInfoSerializer(BaseSerializer):
    key = serializers.ChoiceField(choices=PERMISSION_CLIENT_ENUM)
    name = serializers.ChoiceField(choices=STATUS_PERMISSION_ENUM)


class PermissionGroupListSerializer(BaseSerializer):
    group = PermissionGroupSerializer(required=False)
    module = ModuleObjectSerializer(required=False)
    permissions = serializers.ListField(child=PermissionsInfoSerializer())


class PermissionsGroupModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = '__all__'


class PermissionsInfoModelSerializer(PermissionsGroupModelSerializer):
    class Meta(PermissionsGroupModelSerializer.Meta):
        fields = ('key', 'name',)
