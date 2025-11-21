import itertools

from django.db import transaction
from django.db.models import Q

from app.permission.config_static_varible.common import (
    CLIENT_LEVEL_KEY, ORG_LEVEL_KEY, STATUS_PERMISSION_DENY_KEY, GROUP_PERMISSION_CLIENT_DICT, MODULE_DICT)
from app.permission.models import AccessRulePermission, AccessRule, Permission, CustomRole, CustomRoleAccessRule
from app.permission.services.permssion_group_service import PermissionGroupService


class AccessRuleService(object):

    @staticmethod
    def update_access_rule_of_client(access_rule: AccessRule = None, data: dict = {}):
        assert access_rule is not None, "Access Rule instance is not None"
        assert len(data) > 0, "Data permissions is not None"
        # update name if exist
        name = data.get("name", None)
        group_data_permissions = data.get('permissions_groups', [])
        if name:
            access_rule.name = name
            access_rule.save()
        # transaction on commit update access rule
        if len(group_data_permissions) > 0:
            transaction.on_commit(
                lambda: AccessRuleService.bulk_sync_access_rule_permissions_groups(
                    access_rule=access_rule,
                    group_data_permissions=group_data_permissions)
            )

    @staticmethod
    def bulk_sync_access_rule_permissions_groups(access_rule: AccessRule, group_data_permissions: list = {}):
        """
        This is method bulk sync list instance access rule permissions groups to Model
        :param group_data_permissions:
        :param access_rule:
        :return:
        """
        assert access_rule is not None, "Access Rule instance is not None"
        assert len(group_data_permissions) > 0, "Data permissions is not None"
        groups = [item['group']['key'] for item in group_data_permissions]
        list_access_rules_create, list_access_rules_update = AccessRuleService.make_permissions_groups_access_rule_instance_client(
            access_rule=access_rule, group_data_permissions=group_data_permissions)
        AccessRulePermission.objects.bulk_create(list_access_rules_create)
        #
        AccessRulePermission.all_objects.bulk_update(list_access_rules_update, fields=['is_removed', 'status'])
        # delete all permissions groups not exists in config
        cond = ~Q(permission__group__in=groups) & Q(access_rule=access_rule)
        AccessRulePermission.objects.filter(cond).delete()

    @staticmethod
    def make_permissions_groups_access_rule_instance_client(access_rule: AccessRule = None,
                                                            group_data_permissions: list = {}):
        """
        Make list instance access rule permissions for bulk sync to Model
        :param access_rule:
        :param group_data_permissions:
        :return:
        """
        assert access_rule is not None, "Access Rule instance is not None"
        assert len(group_data_permissions) > 0, "Groups list key is not empty"
        list_access_rules_create = []
        list_access_rules_update = []
        for permissions_group in group_data_permissions:
            # normalize key permission and status
            permissions_status = {item['key']: item['status'] for item in permissions_group['permissions']}
            # query get all permissions list of groups
            permissions_groups_instance = Permission.objects.filter(group=permissions_group['group']['key'])
            # normalize permissions id status
            permissions_id_status = {}
            for permission in permissions_groups_instance.iterator():
                permissions_id_status[str(permission.pk)] = permissions_status[
                    permission.key] if permission.key in permissions_status else STATUS_PERMISSION_DENY_KEY
            # make instance access rule permissions groups
            for permission in permissions_id_status:
                # get status
                status = permissions_id_status[permission]
                # find
                find = AccessRulePermission.all_objects.filter(access_rule=access_rule,
                                                               permission_id=permission).first()
                if find:
                    find.is_removed = False
                    find.status = status
                    list_access_rules_update.append(find)
                else:
                    item = AccessRulePermission(access_rule=access_rule, permission_id=permission, status=status)
                    list_access_rules_create.append(item)
        return list_access_rules_create, list_access_rules_update

    @staticmethod
    def get_permission_detail_by_access_rule(access_rule: AccessRule):
        list_access_rule_permission = AccessRulePermission.objects.filter(access_rule=access_rule)
        list_permission = list_access_rule_permission.values('status', 'permission__name',
                                                             'permission__key', 'permission__group',
                                                             'permission__module', 'permission__module_name')
        del list_access_rule_permission
        #  format [] = [('group_key_for_grouping', 'permission_dict'), ...]
        list_permission_info = []
        groups_modules = {}
        for item in list_permission:
            list_permission_info.append((item.get('permission__group'),
                                         {'status': item.get('status'),
                                          'name': item.get('permission__name'),
                                          'key': item.get('permission__key')}))
            groups_modules.update({item.get('permission__group'): item.get('permission__module')})

        list_permission_info = sorted(list_permission_info, key=lambda x: x[0])
        res = []
        for group_key, value_in_group in itertools.groupby(list_permission_info, lambda x: x[0]):
            group = {
                'group': {
                    'key': group_key,
                    'name': GROUP_PERMISSION_CLIENT_DICT[group_key]
                },
                'module': {
                    'key': groups_modules[group_key],
                    'name': MODULE_DICT[groups_modules[group_key]]
                },
                'permissions': [item[1] for item in value_in_group]
            }
            res.append(group)
        return res

    @staticmethod
    def get_access_rules_of_custom_role(custom_role_obj: CustomRole = None):
        assert custom_role_obj is not None, "Custom role obj is not None"
        query_set = CustomRoleAccessRule.objects.filter(custom_role=custom_role_obj).all()
        return list(query_set)

    @staticmethod
    def delete_access_rules_of_custom_role(custom_role_obj: CustomRole = None):
        assert custom_role_obj is not None, "Custom role obj is not None"
        CustomRoleAccessRule.objects.filter(custom_role=custom_role_obj).delete()

    @staticmethod
    def get_permissions_groups_by_access_rules_config(level: str = None, access_rules_config: list = []):
        """
        list_permissions_groups_configs = SUM(get_permission_detail_by_access_rule)
        :param level:
        :param access_rules_config:
        :return:
        """
        assert level in [CLIENT_LEVEL_KEY, ORG_LEVEL_KEY], "level must in [WS, Org]"
        assert len(access_rules_config) > 0, "access rules config is not empty"
        list_permissions_groups_configs = []
        for item in access_rules_config:
            access_rule = AccessRule.objects.get(pk=item['id'])
            list_permissions_groups_configs += AccessRuleService.get_permission_detail_by_access_rule(access_rule)
        return PermissionGroupService.merge_permissions_group(
            list_permissions_groups_configs=list_permissions_groups_configs)
