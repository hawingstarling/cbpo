import re

from bulk_sync import bulk_sync
from django.db import transaction
from django.db.models import Q
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from app.permission.config_static_varible.common import CUSTOM_TYPE_CREATED_SYSTEM_KEY
from app.permission.exceptions import AccessRuleException
from app.permission.models import CustomRole, AccessRule, CustomRoleAccessRule
from app.permission.serializers import UserCommonSerializer
from app.permission.services.access_rule_service import AccessRuleService
from app.permission.services.custom_role_service import CustomRoleService
from app.permission.sub_serializers.base_serializer import BaseSerializer


class AccessRuleConfigSerializer(BaseSerializer):
    id = serializers.UUIDField()
    name = serializers.CharField(max_length=100, required=False)
    priority = serializers.IntegerField(default=1)


# Base serializer custom role
class CustomRolePayloadBaseSerializer(BaseSerializer):
    access_rules = serializers.ListField(child=AccessRuleConfigSerializer(), required=True)

    def validate_access_rules(self, value):
        object_ids = self.context.get('object_ids')
        level = self.context.get('level')

        errors = []
        access_rule_config = {val['id']: val['priority'] for idx, val in enumerate(value)}
        access_rule_config_ids = access_rule_config.keys()

        look_up_rule = Q(id__in=access_rule_config_ids)
        look_up_object_created_or_system = Q(object_id__in=object_ids) | Q(level=level,
                                                                           type_created=CUSTOM_TYPE_CREATED_SYSTEM_KEY)

        diff = set(access_rule_config_ids) - set(
            AccessRule.objects.filter(look_up_rule & look_up_object_created_or_system).values_list('id', flat=True))
        if diff:
            diff = [str(item) for item in list(diff)]
            errors.append("access rule id {} not exist".format(", ".join(diff)))
        dup = len(value) - len(set(access_rule_config_ids))
        # check duplicate
        if dup > 0:
            errors.append("access rule don't duplicate")
        if errors:
            raise ValidationError(errors)
        # sort priority
        [val.update({'priority': idx + 1}) for idx, val in enumerate(value)]
        return value

    def preview_permissions_groups(self, data):
        level = self.context.get('level')
        rs = AccessRuleService.get_permissions_groups_by_access_rules_config(level=level, access_rules_config=data)
        return rs


# Payload update serializer custom role
class CustomRolePayloadUpdateSerializer(CustomRolePayloadBaseSerializer):
    name = serializers.CharField(max_length=100, required=False)
    access_rules = serializers.ListField(child=AccessRuleConfigSerializer(), required=False)

    def validate_name(self, value):
        errors = []
        regex = re.compile('[@_!#$%^&*()<>?/\|}{~:]')
        if regex.search(value) is not None:
            errors.append("contains character special")
        if errors:
            raise ValidationError(errors)
        return value

    def update(self, instance, validated_data):
        # write update data to model
        with transaction.atomic():
            name = validated_data.get('name', None)
            if name:
                # update info name in validated_data
                instance.name = name
                instance.save()
            access_rules_config = validated_data.get('access_rules', [])
            # print(access_rules_config)
            if access_rules_config:
                CustomRoleService.sync_config_access_rules_of_custom_role(custom_role=instance,
                                                                          access_rules_config=access_rules_config)

    def validate(self, attrs):
        if not attrs:
            raise ValidationError(["Request data not empty"])
        return attrs


class AccessRuleJSONSerializer(BaseSerializer):
    id = serializers.UUIDField()
    priority = serializers.IntegerField(min_value=1)


class CustomRoleSerializer(serializers.ModelSerializer):
    access_rules = serializers.ListField(child=AccessRuleJSONSerializer(), write_only=True)

    class Meta:
        model = CustomRole
        fields = ['id', 'name', 'owner', 'access_rules']
        read_only_fields = ['owner', ]

    def create(self, validated_data):
        with transaction.atomic():
            access_rules = validated_data.pop('access_rules')
            cus_rol_ac_rules = []
            instance = super(CustomRoleSerializer, self).create(validated_data)
            for ac_rule in access_rules:
                cus_rol_ac_rules.append(CustomRoleAccessRule(custom_role=instance,
                                                             access_rule_id=ac_rule.get('id'),
                                                             priority=ac_rule.get('priority'),
                                                             is_removed=False))
            self.sync_access_rule(cus_rol_ac_rules, instance)
            return instance

    def update(self, instance, validated_data):
        with transaction.atomic():
            access_rules = validated_data.pop('access_rules')
            instance = super().update(instance, validated_data)
            cus_rol_ac_rules = []
            for ac_rule in access_rules:
                cus_rol_ac_rules.append(CustomRoleAccessRule(custom_role=instance,
                                                             access_rule_id=ac_rule.get('id'),
                                                             priority=ac_rule.get('priority'),
                                                             is_removed=False))
            self.sync_access_rule(cus_rol_ac_rules, instance)
            return instance

    def validate_access_rules(self, value):
        object_ids = self.context.get('object_ids')

        all_ids = [item.get('id') for item in value]
        if len(all_ids) != len(set(all_ids)):
            raise AccessRuleException('All Access Rule Ids are not unique.')

        base_query = AccessRule.objects.filter(
            Q(object_id__in=object_ids) | (Q(type_created=CUSTOM_TYPE_CREATED_SYSTEM_KEY)))

        for ac_rule_id in all_ids:
            try:
                base_query.get(pk=ac_rule_id)
            except AccessRule.DoesNotExist:
                raise ValidationError('Access Rule id {} does not exist.'.format(ac_rule_id))

        all_priorities = sorted([item.get('priority') for item in value])
        sample_priorities = [i + 1 for i in range(len(all_priorities))]
        if all_priorities != sample_priorities:
            raise AccessRuleException('All Access Rule priorities must be unique, continues, started from 1')
        return value

    def sync_access_rule(self, cus_rol_ac_rules, custom_role: CustomRole):
        """
        sync access rules of a role
        create new role or update priority of access rule in a role
        :param custom_role: 
        :param cus_rol_ac_rules:
        """
        filters = Q(custom_role=custom_role)
        bulk_sync(new_models=cus_rol_ac_rules,
                  filters=filters,
                  fields=['custom_role_id', 'access_rule_id', 'priority', 'is_removed'],
                  key_fields=['custom_role_id', 'access_rule_id'])


class CustomRoleDetailSerializer(CustomRoleSerializer):
    access_rules = serializers.SerializerMethodField()

    def get_access_rules(self, obj):
        ac_rules = CustomRoleAccessRule.objects.filter(custom_role=obj) \
            .order_by('priority') \
            .values('access_rule__id', 'access_rule__name', 'priority')
        res = []
        for ac_rule in ac_rules:
            res.append({
                'id': ac_rule.get('access_rule__id'),
                'name': ac_rule.get('access_rule__name'),
                'priority': ac_rule.get('priority')
            })
        return res


class CustomRoleForListingSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomRole
        fields = ['id', 'name', 'owner', 'level', 'type_created', 'created', 'modified']

    def to_representation(self, instance):
        self.fields['owner'] = UserCommonSerializer(read_only=True)
        return super().to_representation(instance)
