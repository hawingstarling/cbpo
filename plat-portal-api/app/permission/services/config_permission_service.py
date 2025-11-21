from app.permission.config_static_varible.common import LEVEL_ENUM, LIST_PERMISSION_CLIENT_ENUM, LIST_PERMISSION_ORG_ENUM, \
    CLIENT_LEVEL_KEY, ORG_LEVEL_KEY
from app.permission.models import Permission, CustomRole, AccessRule, AccessRulePermission


class ConfigPermissionService:

    @staticmethod
    def get_list_permission_instance_from_level_permission_config(level_permission, type_level_key):
        all_key_level = [item[0] for item in LEVEL_ENUM]
        if type_level_key not in all_key_level:
            raise ValueError('config is wrong')
        list_permission_instance = []
        for ele in level_permission:
            group_key = ele.get('group')
            permission = ele.get('permission')
            for per in permission:
                permission_key = per.get('key')
                permission_label = per.get('label')
                list_permission_instance.append(
                    Permission(key=permission_key, name=permission_label, group=group_key, level=type_level_key))

        return list_permission_instance

    @staticmethod
    def get_list_role_instance_from_level_role_config(level_role, type_level_key):
        all_key_level = [item[0] for item in LEVEL_ENUM]
        if type_level_key not in all_key_level:
            raise ValueError('config is wrong')
        res = []
        for ele in level_role:
            role_key = ele.get('key')
            type_created = ele.get('type_created')
            res.append(
                CustomRole(key=role_key, level=type_level_key, type_created=type_created, client=None, owner=None,
                           name=None))
        return res

    @staticmethod
    def get_list_access_rule_instance_from_level_role_config(level_access_rule, type_level_key):
        all_key_level = [item[0] for item in LEVEL_ENUM]
        if type_level_key not in all_key_level:
            raise ValueError('config is wrong')
        res = []
        for ele in level_access_rule:
            access_rule_key = ele.get('key')
            type_created = ele.get('type_created')
            res.append(
                AccessRule(key=access_rule_key, level=type_level_key, type_created=type_created, client=None,
                           owner=None, name=None))
        return res

    @staticmethod
    def get_list_default_permission_for_default_access_rules(level_access_rule, type_level_key):
        all_permission_keys = []
        if type_level_key == CLIENT_LEVEL_KEY:
            #  client
            all_permission_keys = [item[0] for item in LIST_PERMISSION_CLIENT_ENUM]
        if type_level_key == ORG_LEVEL_KEY:
            #  org
            all_permission_keys = [item[0] for item in LIST_PERMISSION_ORG_ENUM]

        all_key_level = [item[0] for item in LEVEL_ENUM]
        if type_level_key not in all_key_level or len(all_permission_keys) == 0:
            raise ValueError('config is wrong')

        res = []
        for ele in level_access_rule:
            access_rule_key = ele.get('key')
            type_created = ele.get('type_created')
            access_rule_ins = AccessRule.objects.get(key=access_rule_key, type_created=type_created)
            permission = ele.get('permission')
            for per in permission:
                permission_key = per.get('key')
                if permission_key not in all_permission_keys:
                    raise ValueError('config is wrong')
                permission_ins = Permission.objects.get(key=permission_key, level=type_level_key)
                status = per.get('status')
                res.append(
                    AccessRulePermission(access_rule=access_rule_ins, permission=permission_ins, status=status))

        return res
