from typing import Union

from bulk_sync import bulk_sync
from django.db.models import Q

from app.permission.config_static_varible.common import (
    CLIENT_LEVEL_KEY,
    ORG_LEVEL_KEY,
    ROLE_ADMIN_KEY,
    ROLE_MANAGER_KEY,
    ROLE_STAFF_KEY,
)
from app.permission.config_static_varible.custom_roles.client.cus_role_ws_admin_default import (
    custom_role_ws_admin_default,
)
from app.permission.config_static_varible.custom_roles.client.cus_role_ws_manage_default import (
    custom_role_ws_manage_default,
)
from app.permission.config_static_varible.custom_roles.client.cus_role_ws_staff_default import (
    custom_role_ws_staff_default,
)
from app.permission.models import (
    AccessRule,
    CustomRoleAccessRule,
    CustomRole,
    OrgClientCustomRoleUser,
    ClientUserProxy,
    OrganizationUserProxy,
)
from app.permission.services.access_rule_service import AccessRuleService
from app.tenancies.models import Client, UserClient, Organization
from app.tenancies.models import User, OrganizationUser


class CustomRoleService(object):
    @staticmethod
    def get_access_rules_of_role_default_level(level: str = None, role_default: str = None) -> list:
        """
        This method get all access rules config of role default [Org, WS]
        required:
            level in [Org, WS]
            role_default: ['ADMIN', MANAGER, STAFF]
        response = [
            {
                key: <str>
            }
        ]
        :param role_default:
        :param level:
        :return:
        """
        assert level is not None, "Level is not None"
        assert role_default is not None, "Role default is not None"
        assert level in [CLIENT_LEVEL_KEY, ORG_LEVEL_KEY], "Level must in [Org, WS]"
        assert role_default in [ROLE_ADMIN_KEY, ROLE_MANAGER_KEY, ROLE_STAFF_KEY], "Level must in [Org, WS]"
        args = {
            CLIENT_LEVEL_KEY: {
                ROLE_ADMIN_KEY: custom_role_ws_admin_default,
                ROLE_MANAGER_KEY: custom_role_ws_manage_default,
                ROLE_STAFF_KEY: custom_role_ws_staff_default,
            },
            ORG_LEVEL_KEY: {},
        }
        access_rule_config = args[level][role_default]["access_rule_config"]
        access_rule_keys = []
        for access_rule in access_rule_config:
            access_rule_keys += access_rule
        return access_rule_keys

    @staticmethod
    def get_permissions_groups_of_role_default_level(level: str = None, role_default: str = None) -> list:
        """
        This is method get all permissions groups of role default level
        required:
            level in [Org, WS]
            role_default: ['ADMIN', MANAGER, STAFF]
        :param level:
        :param role_default:
        :return:
        """
        access_rules_config = CustomRoleService.get_access_rules_of_role_default_level(
            level=level, role_default=role_default
        )
        return AccessRuleService.get_permissions_of_access_rules(level=level, access_rules_keys=access_rules_config)

    @staticmethod
    def delete_access_rule_of_custom_roles(content_object: Organization or Client, access_rule: AccessRule):
        """
        This is a method that deletes access rules in another custom roles
        @param content_object:
        @param access_rule:
        @return:
        """
        # delete permission groups of access rule
        # PermissionGroupService.delete_permissions_groups_of_access_rule_client(content_object, access_rule)
        # get custom roles list
        custom_role_ids = CustomRoleAccessRule.objects.filter(
            access_rule=access_rule,
        ).values_list("custom_role_id", flat=True)
        # delete access role of custom role
        CustomRoleAccessRule.objects.filter(access_rule=access_rule).delete()
        return [str(i) for i in custom_role_ids]

    @staticmethod
    def get_custom_roles_config_contain_access_rule_client(
        content_obj: Union[Client, Organization] = None, access_rule: AccessRule = None
    ):
        """
        This is method get list custom role contain access rule
        :param content_obj:
        :param access_rule:
        :return:
        """
        assert content_obj is not None, "Content obj must in [Org, Client]"
        assert access_rule is not None, "access rule not empty"

        # get custom roles list
        custom_role_ids = (
            CustomRoleAccessRule.objects.filter(
                custom_role__object_id=content_obj.pk, access_rule=access_rule, access_rule__object_id=content_obj.pk
            )
            .order_by("custom_role")
            .distinct()
            .values("custom_role")
        )
        return [str(item["custom_role"]) for item in custom_role_ids]

    @staticmethod
    def get_list_org_ws_user_ids_by_custom_roles(custom_role_ids: [str] = []):
        """
        This is method get list of user_client, user_org
        :param custom_roles:
        :return:
        @param custom_role_ids:
        """
        list_content_object = (
            OrgClientCustomRoleUser.objects.filter(custom_role_id__in=custom_role_ids)
            .order_by("object_id")
            .distinct("object_id")
        )
        return [str(item.object_id) for item in list_content_object]

    @staticmethod
    def sync_custom_roles_of_org_client_users(
        generic_obj: Union[OrganizationUser, UserClient] = None, custom_role_ids: [str] = []
    ):
        assert generic_obj is not None, "OrgUser or ClientUser is not None"
        if len(custom_role_ids) == 0:
            #  syncing with empty roles -> default role was executed before
            OrgClientCustomRoleUser.objects.filter(object_id=generic_obj.id).delete()
            return

        # sync to CustomRoleAccessRule
        data_config = []
        #
        for idx, role_id in enumerate(custom_role_ids):
            item = OrgClientCustomRoleUser(
                content_object=generic_obj, custom_role_id=role_id, priority=idx + 1, is_removed=False
            )
            data_config.append(item)
        # sync config custom role access rules
        bulk_sync(
            new_models=data_config,
            filters=Q(object_id=str(generic_obj.pk)),
            fields=["object_id", "custom_role_id", "priority", "is_removed"],
            key_fields=["object_id", "custom_role_id", "priority"],
        )

    @staticmethod
    def sync_config_access_rules_of_custom_role(custom_role: CustomRole = None, access_rules_config: [dict] = []):
        assert custom_role is not None, "Custom role is not None"
        assert len(access_rules_config) > 0, "Access rules config is not empty"
        # sync to CustomRoleAccessRule
        custom_role_access_rule_config = []
        for access_rule in access_rules_config:
            item = CustomRoleAccessRule(
                access_rule_id=access_rule["id"],
                custom_role=custom_role,
                priority=access_rule["priority"],
                is_removed=False,
            )
            custom_role_access_rule_config.append(item)
        # sync config custom role access rules
        bulk_sync(
            new_models=custom_role_access_rule_config,
            filters=Q(custom_role=custom_role),
            fields=["custom_role_id", "access_rule_id", "priority", "is_removed"],
            key_fields=["custom_role_id", "access_rule_id"],
        )

    @staticmethod
    def get_generic_objs_user_relate_custom_role(
        level: str = None,
        generic_obj: Union[Client, Organization] = None,
        custom_role_obj: CustomRole = None,
        user: User = None,
    ):
        assert level in [CLIENT_LEVEL_KEY, ORG_LEVEL_KEY], "level must in [WS, Org]"
        assert generic_obj is not None, "generic obj is not empty"
        query_set = None
        if level == CLIENT_LEVEL_KEY:
            query_set = ClientUserProxy.objects.filter(client=generic_obj)
        if level == ORG_LEVEL_KEY:
            query_set = OrganizationUserProxy.objects.filter(organization=generic_obj)
        # filter get custom_role_is_nullable
        query_set = query_set.filter(custom_roles__isnull=False)
        if user:
            # filter by users
            query_set = query_set.filter(user=user)
        if custom_role_obj:
            # filter by custom role instance
            query_set = query_set.filter(custom_roles__custom_role=custom_role_obj)
        return list(query_set)

    @staticmethod
    def delete_custom_roles_level(
        level: str = None, generic_obj: Union[Client, Organization] = None, custom_role_obj: CustomRole = None
    ):
        assert level in [CLIENT_LEVEL_KEY, ORG_LEVEL_KEY], "level must in [WS, Org]"
        assert generic_obj is not None, "generic obj is not None"
        assert custom_role_obj is not None, "custom role instance is not None"
        # Delete all custom role relate
        generic_objs_relate = CustomRoleService.get_generic_objs_user_relate_custom_role(
            level, generic_obj, custom_role_obj
        )
        for obj in generic_objs_relate:
            obj.custom_roles.all().delete()
        # delete access contain custom role
        AccessRuleService.delete_access_rules_of_custom_role(custom_role_obj=custom_role_obj)
        # Re sync permissions data of generic relate
        CustomRoleService.clean_permissions_data_generic_relate_user_of_custom_role()
        # delete custom role
        custom_role_obj.delete()

    @staticmethod
    def clean_permissions_data_generic_relate_user_of_custom_role():
        pass

    @staticmethod
    def sync_access_rule_relate_custom_roles(
        content_obj: Union[Client, Organization],
        access_rule: AccessRule = None,
        level: Union[CLIENT_LEVEL_KEY, ORG_LEVEL_KEY] = None,
    ):
        # get custom_role_configs
        custom_roles_config = CustomRoleService.get_custom_roles_config_contain_access_rule_client(
            content_obj=content_obj, access_rule=access_rule
        )
        #
        generic_objs_users = []
        if level == ORG_LEVEL_KEY:
            generic_objs_users = OrganizationUserProxy.objects.filter(organization=content_obj)
        if level == CLIENT_LEVEL_KEY:
            generic_objs_users = ClientUserProxy.objects.filter(client=content_obj)
        custom_role_ids = [str(item.custom_role.pk) for item in custom_roles_config]
        # sync custom role contains access rule update
        if len(custom_role_ids) > 0:
            for generic_obj_user in generic_objs_users.iterator():
                CustomRoleService.sync_custom_roles_of_org_client_users(
                    generic_obj=generic_obj_user, custom_role_ids=custom_role_ids
                )
            generic_objs_ids = list(generic_objs_users.values_list("id", flat=True))
            #
            from app.permission.services.compose_permission_service import ComposePermissionService

            ComposePermissionService.sync_permission_of_user_client_org(generic_objs_ids)

    @staticmethod
    def get_default_role_ids(
        user_member: Union[UserClient, OrganizationUser], level: Union[CLIENT_LEVEL_KEY, ORG_LEVEL_KEY]
    ):
        """
        get default custom role ids by role in User Client, Org User
        @param user_member:
        @param level:
        """
        if user_member.role.key in ["OWNER", "ADMIN"]:
            roles = CustomRole.objects.filter(key=ROLE_ADMIN_KEY, level=level)
        elif user_member.role.key == "STAFF":
            roles = CustomRole.objects.filter(key=ROLE_STAFF_KEY, level=level)
        else:
            roles = []
        role_ids = [str(item.pk) for item in roles]
        return role_ids
