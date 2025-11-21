from django.db.models import Q
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from app.permission.config_static_varible.common import CUSTOM_TYPE_CREATED_SYSTEM_KEY
from app.permission.models import CustomRole, OrgClientUserPermission
from app.permission.services.compose_permission_service import ComposePermissionService
from app.permission.sub_serializers.access_rule_serializer import PermissionGroupJSONSerializer
from app.permission.sub_serializers.base_serializer import BaseSerializer, OrgClientRoleConfigSerializer

COMPOSE_TYPE_PREVIEW_KEY = 'PREVIEW'
COMPOSE_TYPE_APPROVE_KEY = 'APPROVE'


class PermissionGroupingResSerializer(serializers.Serializer):
    permission_groups = serializers.ListField(child=PermissionGroupJSONSerializer())

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class RoleJSONSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    priority = serializers.IntegerField(default=1)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class ComposePermissionSerializer(BaseSerializer):
    type = serializers.ChoiceField(choices=((COMPOSE_TYPE_PREVIEW_KEY, 'Preview'),
                                            (COMPOSE_TYPE_APPROVE_KEY, 'Approve')))
    roles = serializers.ListField(child=RoleJSONSerializer(), allow_empty=True)
    permissions_groups = serializers.ListField(required=False, write_only=True, child=PermissionGroupJSONSerializer())

    def validate_roles(self, value):
        object_ids = self.context.get('object_ids')
        all_ids = [item.get('id') for item in value]
        if len(all_ids) != len(set(all_ids)):
            raise ValidationError('All Role Ids are not unique.')

        base_query = CustomRole.objects.filter(
            Q(object_id__in=object_ids) | Q(type_created=CUSTOM_TYPE_CREATED_SYSTEM_KEY))

        for role_id in all_ids:
            try:
                # Check role that belongs to Workspace or Organization
                base_query.get(pk=role_id)
            except CustomRole.DoesNotExist:
                raise ValidationError('Custom Role id {} does not exist.'.format(role_id))

        all_priorities = sorted([item.get('priority') for item in value])
        sample_priorities = [i + 1 for i in range(len(all_priorities))]
        if all_priorities != sample_priorities:
            raise ValidationError('All Role priorities must be unique, continues, started from 1')
        return value


class OrgClientUserPermissionSerializer(serializers.ModelSerializer):
    permission = serializers.SerializerMethodField()
    label = serializers.SerializerMethodField()

    class Meta:
        model = OrgClientUserPermission
        fields = ('module', 'permission', 'label', 'enabled',)

    def get_permission(self, obj):
        return obj.key

    def get_label(self, obj):
        return obj.name


class UserClientCustomRoleGETPayloadSerializer(BaseSerializer):

    def get_payloads_data(self):
        generic_obj_user_request = self.context['generic_obj_user_request']
        level = self.context['level']
        if not generic_obj_user_request:
            return {
                'roles': [],
                'permissions_groups': [],
                'optional_permissions_groups': []
            }
        # query set get config role
        config_role_query = generic_obj_user_request.custom_roles.order_by('priority').all()
        #
        res = ComposePermissionService.get_org_client_user_permission_cache_and_grouping(generic_obj_user_request,
                                                                                         level)
        overriding_permissions_groups = ComposePermissionService.get_overriding_permissions_groups(
            generic_obj_user_request.id)
        #  TODO: change 'optional_permissions_groups' -> 'overriding_permissions_groups'
        data = {
            'roles': OrgClientRoleConfigSerializer(config_role_query, many=True).data,
            'permissions_groups': res,
            'optional_permissions_groups': overriding_permissions_groups
        }
        return data
