import itertools

from app.permission.config_static_varible.common import CLIENT_LEVEL_KEY, ORG_LEVEL_KEY, GROUP_PERMISSION_CLIENT_DICT, \
    STATUS_PERMISSION_DENY_KEY, STATUS_PERMISSION_INHERIT_KEY, GROUP_PERMISSION_DICT, MODULE_DICT
from app.permission.config_static_varible.config import PERMISSIONS_GROUPS_CONFIG_CLIENT_LEVEL
from app.permission.models import AccessRulePermission, Permission
from app.permission.sub_serializers.permission_group_serializer import PermissionsInfoModelSerializer


class PermissionGroupService(object):

    @staticmethod
    def get_permissions_groups_config_level(level: str = None):
        assert level in [CLIENT_LEVEL_KEY, ORG_LEVEL_KEY], "Level must in [Org, WS]"
        args = {
            CLIENT_LEVEL_KEY: PERMISSIONS_GROUPS_CONFIG_CLIENT_LEVEL,
            ORG_LEVEL_KEY: {},
        }
        return args.get(level)

    @staticmethod
    def get_permissions_group_by_list_keys(level: str = None, groups_list_key: list = []):
        """
        groups_list_key = [
            {
                key: <str>
            }
        ]
        :param level:
        :param groups_list_key:
        :return:
        """
        permissions_groups = {}
        assert level is not None, "Level is not None"
        assert len(groups_list_key) > 0, "Groups list key is not empty"
        permissions_groups_level = PermissionGroupService.get_permissions_groups_config_level(level=level)
        for group in groups_list_key:
            permissions_groups[group['key']] = permissions_groups_level[group['key']]
        return permissions_groups

    @staticmethod
    def delete_permissions_groups_of_access_rule_client(client, access_rule):
        AccessRulePermission.objects.filter(access_rule=access_rule, access_rule__object_id=client.pk).delete()

    @staticmethod
    def get_permissions_groups_level(search: str = None, level: str = None, *args, **kwargs):
        assert level in [CLIENT_LEVEL_KEY, ORG_LEVEL_KEY], "Level must in [Org, WS]"
        #
        exclude_cond = kwargs.get("exclude_cond")
        if exclude_cond:
            query_set = Permission.objects.exclude(**exclude_cond)
        else:
            query_set = Permission.objects.all()

        result = []
        if level == ORG_LEVEL_KEY:
            pass
        else:
            query_set = query_set.filter(level=level)

        if search:
            query_set = query_set.filter(group_name__icontains=search)
        # get groups
        groups = query_set.values('group', 'module').distinct()
        groups_modules = {groups['group']: groups['module'] for groups in groups}
        for group in groups_modules.keys():
            item = {
                'group': {
                    'key': group,
                    'name': GROUP_PERMISSION_CLIENT_DICT[group]
                },
                'module': {
                    'key': groups_modules[group],
                    'name': MODULE_DICT[groups_modules[group]]
                }
            }
            permissions_group_query = query_set.filter(group=group)
            item['permissions'] = PermissionsInfoModelSerializer(permissions_group_query, many=True).data
            result.append(item)
        return result

    @staticmethod
    def merge_permissions_group(list_permissions_groups_configs: list = []):
        """
        Convert to list permissions of group
        permissions_groups = {
            group_A: [
                {group: group_A , permissions:[{key:A, status: ALLOW}, ...]},
                {group: group_A , permissions:[{key:A, status: DENY}, ...]},
                {group: group_A , permissions:[{key:A, status: INHERIT}, ...]},
            ],
            group_B: [
                {group: group_B , permissions:[{key:A, status: ALLOW}, ...]},
                {group: group_B , permissions:[{key:A, status: DENY}, ...]},
                {group: group_B , permissions:[{key:A, status: INHERIT}, ...]},
            ]
        }
        :param list_permissions_groups_configs:
        :return:
        """
        if len(list_permissions_groups_configs) == 0:
            return {}
        permissions_groups = {k: list(g) for k, g in
                              itertools.groupby(list_permissions_groups_configs, lambda k: k['group']['key'])}
        groups_modules = {k: list(g)[0]['module'] for k, g in
                          itertools.groupby(list_permissions_groups_configs, lambda k: k['group']['key'])}
        # print('module info : {}'.format(groups_modules))
        final = []

        permissions_info = {}

        def merge_permission(x):
            """
            Merge permission to permissions_info
            :param x:
            :return:
            """
            if x['status'] == STATUS_PERMISSION_INHERIT_KEY:
                permissions_info[x['key']] = {
                    'status': permissions_info.get(x['key'], {}).get('status', STATUS_PERMISSION_DENY_KEY),
                    'name': x['name']
                }
            else:
                permissions_info[x['key']] = {
                    'status': x['status'],
                    'name': x['name']
                }

        def merge_permissions(y):
            """
            Merge permissions config
            :param y:
            :return:
            """
            for x in y:
                # x = info permission
                merge_permission(x)

        def map_permissions_group(a):
            """
            Merge permissions of group
            :param a:
            :return:
            """
            for x in a:
                y = x['permissions']
                # override permission key & status
                merge_permissions(y)

        for group in permissions_groups.keys():
            list_permissions_group = permissions_groups[group]
            # merge permission key & status
            map_permissions_group(list_permissions_group)
            # normalize final
            group_permissions_final = {
                'group': {
                    'key': group,
                    'name': GROUP_PERMISSION_DICT[group]
                },
                'module': groups_modules[group],
                'permissions': [
                    {'key': key, 'name': permissions_info[key]['name'], 'status': permissions_info[key]['status']}
                    for key in permissions_info.keys()
                ]
            }
            final.append(group_permissions_final)
            permissions_info = {}
        return final
