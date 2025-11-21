from itertools import groupby
from typing import Union, List
from collections import defaultdict
from bulk_sync import bulk_sync
from django.db.models import Q
from rest_framework.exceptions import ValidationError

from app.core.context import AppContext
from app.core.logger import logger
from app.payments.services.utils import get_exclude_condition
from app.permission.config_static_varible.common import (
    STATUS_PERMISSION_ALLOW_KEY,
    STATUS_PERMISSION_DENY_KEY,
    GROUP_PERMISSION_CLIENT_DICT,
    MODULE_DICT,
    STATUS_PERMISSION_INHERIT_KEY,
    ORG_LEVEL_KEY,
    CLIENT_LEVEL_KEY, )
from app.permission.models import (
    AccessRule,
    AccessRulePermission,
    CustomRoleAccessRule,
    Permission,
    OrganizationUserProxy,
    ClientUserProxy,
    OverridingOrgClientUserPermission, )
from app.permission.models import OrgClientUserPermission
from app.permission.services.custom_role_service import CustomRoleService
from app.permission.sub_serializers.access_rule_serializer import (
    AccessRulePermissionSerializer,
    PermissionSerializer,
    PermissionGroupJSONSerializer,
)
from app.tenancies.config_static_variable import MEMBER_STATUS
from app.tenancies.models import UserClient, OrganizationUser, Client, Organization

OWNER_INFO = {"key": "OWNER", "name": "Owner"}

ADMIN_INFO = {"key": "ADMIN", "name": "Admin"}

STAFF_INFO = {"key": "STAFF", "name": "Staff"}


class ComposePermissionService:
    @staticmethod
    def save_composed_permission(permission, object_reference: UserClient or OrganizationUser):
        res = [
            OrgClientUserPermission(
                key=per["key"],
                module=per["module"],
                name=per["name"],
                group=per["group"],
                enabled=True if per["status"] == STATUS_PERMISSION_ALLOW_KEY else False,
                content_object=object_reference,
            ) for per in permission
        ]
        if len(res) == 0:
            return None
        bulk_sync(
            new_models=res,
            filters=Q(object_id=object_reference.id),
            fields=["module", "module_name", "group", "key", "name", "enabled"],
            key_fields=("group", "key"),
        )

    @staticmethod
    def save_overriding_permission(
        overriding_permissions_groups: [PermissionGroupJSONSerializer],
        object_reference: UserClient or OrganizationUser,
    ):

        if not overriding_permissions_groups:
            OverridingOrgClientUserPermission.objects.filter(object_id=object_reference.id).delete()
            return

        list_permission = []
        for per_group in overriding_permissions_groups:
            group_key = per_group.get("group")["key"]
            list_per = per_group.get("permissions")
            for per in list_per:
                per_key = per.get("key")
                per_status = per.get("status")
                try:
                    per_ins = Permission.objects.get(key=per_key, group=group_key)
                    list_permission.append(
                        OverridingOrgClientUserPermission(
                            permission=per_ins,
                            status=per_status,
                            is_removed=False,
                            content_object=object_reference,
                        )
                    )
                except Permission.DoesNotExist:
                    raise ValidationError("Permission does not exist. [{}, {}]".format(per_key, group_key))

        if len(list_permission) == 0:
            return None

        bulk_sync(
            filters=Q(object_id=object_reference.id),
            new_models=list_permission,
            fields=["permission_id", "status", "is_removed"],
            key_fields=["permission_id", "status"],
        )

    @staticmethod
    def delete_saved_override_permission(object_reference: List[Union[UserClient, OrganizationUser]], **kwargs):
        query_set = OverridingOrgClientUserPermission.objects.filter(object_id__in=[ele.id for ele in object_reference])
        permission_ids = kwargs.get("permission_ids", [])
        if len(permission_ids):
            query_set.filter(permission__id__in=permission_ids).delete()

    @staticmethod
    def compose_access_rules_from_custom_roles(role_ids: [str]) -> [AccessRule]:
        query_set = []
        for role_id in role_ids:
            acc_rule_ids = (
                CustomRoleAccessRule.objects.filter(custom_role_id=role_id).values("access_rule").order_by("priority")
            )
            access_rules = AccessRule.objects.filter(pk__in=acc_rule_ids)
            query_set.extend(access_rules)
        return query_set

    @staticmethod
    def compose_permission_from_access_rules(query_set: [AccessRule], overriding_permissions_groups=None) -> [dict]:
        """
        compose permission from list of access rules
        :return:
        @param query_set:
        @param overriding_permissions_groups: permissions are in high priority, they will override permissions from
        custom roles and access rules defined
        """
        res = []
        res_inherit_not_handle = []

        def append_method(x, which="res"):
            if which == "res":
                find_exist = [item for item in res if item["key"] == x["key"]]
                if len(find_exist) == 0:
                    res.append(x)
            else:
                find_exist = [item for item in res_inherit_not_handle if item["key"] == x["key"]]
                if len(find_exist) == 0:
                    res_inherit_not_handle.append(x)

        def classify_permission(classified_per):
            if classified_per["status"] == STATUS_PERMISSION_INHERIT_KEY:
                append_method(
                    {
                        "key": classified_per["key"],
                        "name": classified_per["name"],
                        "group": classified_per["group"],
                        "module": classified_per["module"],
                    },
                    which="res_inherit_not_handle",
                )
            else:
                append_method(
                    {
                        "key": classified_per["key"],
                        "name": classified_per["name"],
                        "group": classified_per["group"],
                        "module": classified_per["module"],
                        "status": classified_per["status"],
                    },
                    which="res",
                )

        def handler_overriding_permissions_groups(_group_key, _module, _list_per):
            for _per in list_per:
                _status = _per.get("status")
                _key = _per.get("key")
                try:
                    ins = Permission.objects.get(key=_key, group=_group_key)
                    permission_data = PermissionSerializer(ins).data
                    classify_permission(
                        {
                            "key": _key,
                            "name": permission_data["name"],
                            "group": _group_key,
                            "module": _module,
                            "status": _status,
                        }
                    )
                except Permission.DoesNotExist:
                    raise ValidationError("Permission does not exist. [{}, {}]".format(_key, _group_key))

        list_permission = []
        for access_rule in query_set:
            access_rule_permission_query_set = AccessRulePermission.objects.filter(access_rule=access_rule)
            list_permission += AccessRulePermissionSerializer(access_rule_permission_query_set, many=True).data

        if overriding_permissions_groups:
            for per_group in overriding_permissions_groups:
                group_key = per_group.get("group")["key"]
                module = per_group.get("module")["key"]
                list_per = per_group.get("permissions")
                handler_overriding_permissions_groups(group_key, module, list_per)

        # implement handle permissions
        for perm in list_permission:
            classify_permission(perm)

        for per in res_inherit_not_handle:
            append_method(
                {
                    "key": per["key"],
                    "name": per["name"],
                    "group": per["group"],
                    "module": per["module"],
                    "status": STATUS_PERMISSION_DENY_KEY,
                },
                which="res",
            )
        return res

    @staticmethod
    def group_composed_permission(composed_permission):
        # compare element [(key_for_grouping, content), ...]
        composed_permission_for_grouping = [
            (
                item["group"],
                {"key": item["key"], "name": item["name"], "status": item["status"]},
            )
            for item in composed_permission
        ]
        composed_permission_for_grouping.sort(key=lambda x: x[0])

        # group module information
        group_module_info = {k: list(g)[0]["module"] for k, g in groupby(composed_permission, lambda k: k["group"])}

        res = []
        for group_key, value_in_group in groupby(composed_permission_for_grouping, lambda x: x[0]):
            group = {
                "group": {
                    "key": group_key,
                    "name": GROUP_PERMISSION_CLIENT_DICT[group_key],
                },
                "module": {
                    "key": group_module_info[group_key],
                    "name": MODULE_DICT[group_module_info[group_key]],
                },
                "permissions": [item[1] for item in value_in_group],
            }
            res.append(group)
        return res

    @staticmethod
    def rearrange_data_to_log_activity(data):
        """
        re-arrange data to log activity
        @param data:
        """
        res = defaultdict(dict)
        for k, g in groupby(data, lambda x: x["group"]["name"]):
            for item in g:
                for p in item["permissions"]:
                    res[k][p["name"]] = p["status"]

        return res

    @staticmethod
    def get_overriding_permissions_groups(object_id: str):
        """
        get overriding permissions groups
        @param object_id:
        """
        query_set = OverridingOrgClientUserPermission.objects.filter(object_id=object_id)
        res = [
            {
                "group": item.permission.group,
                "key": item.permission.key,
                "name": item.permission.name,
                "status": item.status,
                "module": item.permission.module,
            } for item in query_set
        ]
        res = ComposePermissionService.group_composed_permission(res)
        return res

    @staticmethod
    def sync_permission_of_user_client_org(affected_object_ids: [str]):
        for object_id in affected_object_ids:
            logger.info("sync permission for user object id %s" % object_id)
            # level = None
            try:
                object_ref = OrganizationUserProxy.objects.get(pk=object_id)
                level = ORG_LEVEL_KEY
            except OrganizationUserProxy.DoesNotExist:
                try:
                    object_ref = ClientUserProxy.objects.get(pk=object_id)
                    level = CLIENT_LEVEL_KEY
                except ClientUserProxy.DoesNotExist:
                    continue
            except Exception as err:
                logger.error(err)
                continue

            roles = object_ref.custom_roles.values("custom_role").order_by("priority")
            role_ids = [str(item["custom_role"]) for item in roles]
            default_role_ids = CustomRoleService.get_default_role_ids(object_ref, level)
            composed_role_ids = [*role_ids, *default_role_ids]
            if len(composed_role_ids) == 0:
                #  external_user -> pass
                continue

            access_rule_query_set = ComposePermissionService.compose_access_rules_from_custom_roles(composed_role_ids)
            overriding_permissions_groups = ComposePermissionService.get_overriding_permissions_groups(object_id)
            res = ComposePermissionService.compose_permission_from_access_rules(
                access_rule_query_set, overriding_permissions_groups
            )
            ComposePermissionService.save_composed_permission(res, object_ref)

    @staticmethod
    def sync_permission_of_user_client_org_bucket(object_id: str, bucket, level: str):
        """

        @param object_id:
        @param bucket: dict of OrganizationUserProxy or ClientUserProxy
        @param level: ORGANIZATION, CLIENT
        @return:
        """
        logger.info("sync permission for user object id %s" % object_id)

        find_object = filter(lambda ele: ele.id == object_id, bucket)
        try:
            object_ref = next(find_object)
        except StopIteration:
            return

        roles = object_ref.custom_roles.values("custom_role").order_by("priority")
        role_ids = [str(item["custom_role"]) for item in roles]
        default_role_ids = CustomRoleService.get_default_role_ids(object_ref, level)
        composed_role_ids = [*role_ids, *default_role_ids]
        if len(composed_role_ids) == 0:
            #  external_user -> pass
            logger.error(f"user {object_id} does have any roles")
            return

        access_rule_query_set = ComposePermissionService.compose_access_rules_from_custom_roles(composed_role_ids)
        overriding_permissions_groups = ComposePermissionService.get_overriding_permissions_groups(object_id)
        res = ComposePermissionService.compose_permission_from_access_rules(
            access_rule_query_set, overriding_permissions_groups
        )
        ComposePermissionService.save_composed_permission(res, object_ref)

    @staticmethod
    def get_client_user_settings_permissions(
        client_id: str = None, user_id: str = None, status: str = MEMBER_STATUS[0][0]
    ):
        """
        This is method for get last cache permissions by module config of app
        using for endpoint GET: /v1/clients/{client_id}/users/{user_id}/settings/
        :param client_id:
        :param user_id:
        :param status:
        :return:
        """
        assert client_id is not None, "Client Id is not None"
        assert user_id is not None, "User Id is not None"
        user_client = UserClient.objects.get(client_id=client_id, user_id=user_id, status=status)
        # get module define in client module
        modules_enabled = AppContext().instance().module_enabled(client_id)
        list_permissions = OrgClientUserPermission.objects.filter(object_id=user_client.id)
        for per in list_permissions:
            if per.module not in modules_enabled:
                per.enabled = False
        return list_permissions, modules_enabled

    @staticmethod
    def get_org_client_user_permission_cache_and_grouping(
        generic_user_level: Union[OrganizationUserProxy, ClientUserProxy],
        level: Union[CLIENT_LEVEL_KEY, ORG_LEVEL_KEY],
    ):
        """
        get all user user permissions in cache (org or client) and grouping
        @param level:
        @param generic_user_level:
        @return:
        """
        if level == ORG_LEVEL_KEY:
            #  Get all for now
            # TODO: ...
            permissions = generic_user_level.group_permissions.all().values("group", "module", "key", "enabled", "name")
        else:
            modules_enabled = AppContext().instance().module_enabled(generic_user_level.client.id)
            permissions = generic_user_level.group_permissions_from_settings().filter(
                module__in=modules_enabled).values("group", "module", "key", "enabled", "name")

        translate_status_permission = []
        for item in permissions:
            item["status"] = STATUS_PERMISSION_ALLOW_KEY if item["enabled"] is True else STATUS_PERMISSION_DENY_KEY
            translate_status_permission.append(item)
        del permissions
        permissions_groups = ComposePermissionService.group_composed_permission(translate_status_permission)
        return permissions_groups

    @staticmethod
    def filter_org_client_user_permission_dict(
        list_composed_dict_permission,
        level: Union[CLIENT_LEVEL_KEY, ORG_LEVEL_KEY],
        content_object: Union[Organization, Client],
    ):
        """
        Filter list of dict of composed permission by active modules
        @param content_object:
        @param list_composed_dict_permission:
        @param level:
        """
        if level == ORG_LEVEL_KEY:
            #  Get all for now
            # TODO: ...
            return list_composed_dict_permission

        modules_enabled = AppContext().instance().module_enabled(content_object.id)
        res = filter(lambda _ele: _ele["module"] in modules_enabled, list_composed_dict_permission)
        exclude_cond = get_exclude_condition(org_id=content_object.organization.id)
        if exclude_cond:
            res = filter(lambda _ele: _ele["group"] not in exclude_cond.get("group__in", []), res)
        return list(res)
