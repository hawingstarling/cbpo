from itertools import groupby
from typing import List, Union, Dict

from app.permission.config_static_varible.common import (
    ROLE_ADMIN_KEY,
    ROLE_STAFF_KEY,
    CLIENT_LEVEL_KEY,
    ORG_LEVEL_KEY,
    STATUS_PERMISSION_ALLOW_KEY,
)
from app.permission.models import (
    CustomRole,
    OrgClientCustomRoleUser,
    OrgClientUserPermission,
    OverridingOrgClientUserPermission,
)
from app.permission.services.compose_permission_service import ComposePermissionService
from app.tenancies.models import OrganizationUser, Client, UserClient

CHUNK_SIZE = 100


class OrganizationPermissionManager:
    """
    Help to grant permissions in ORG or CLIENT in a structured way
    """

    def __init__(self, organization_id: str):
        self.organization_id = organization_id

    def run_with_user_client(self, client_ids: List[str], user_ids: List[str]):
        """
        grant permission for UserClient
        """
        queryset = (
            UserClient.objects.filter(
                # order_by role is required
                # group and query for bulk processing
                client_id__in=client_ids, user_id__in=user_ids).order_by("role").select_related("role")
        )
        len_queryset = queryset.count()
        if len_queryset == 0:
            return
        self.__process(queryset=queryset, level=CLIENT_LEVEL_KEY)

    def run_with_org_user(self, user_ids: List[str]):
        """
        grant permission for OrganizationUser
        """
        queryset = (
            OrganizationUser.objects.filter(organization_id=self.organization_id, user_id__in=user_ids)
            .order_by("role")
            .select_related("role")
        )
        len_queryset = queryset.count()
        if len_queryset == 0:
            return
        self.__process(queryset=queryset, level=ORG_LEVEL_KEY)

    def run(self):
        """
        grant permissions the ORGANIZATION entirely
        """
        self.process_user_in_org()
        self.process_user_in_ws(client_ids=None)
        return f"DONE ORGANIZATION {self.organization_id}"

    def process_user_in_org(self):
        queryset = (
            OrganizationUser.objects.filter(organization_id=self.organization_id)
            .order_by("role")
            .select_related("role")
        )
        len_queryset = queryset.count()
        if len_queryset == 0:
            return
        print(f"{len_queryset} user in org {self.organization_id}")
        self.__process(queryset=queryset, level=ORG_LEVEL_KEY)

    def process_user_in_ws(self, client_ids: Union[List[str], None]):
        if not client_ids:
            client_ids = Client.objects.filter(
                organization_id=self.organization_id
            ).values_list("id", flat=True)

        queryset = (
            UserClient.objects.filter(client_id__in=client_ids)
            .order_by("role")
            .select_related("role")
        )
        len_queryset = queryset.count()
        if len_queryset == 0:
            return
        print(
            f"=========Org {self.organization_id} has {len_queryset} users in clients"
        )
        self.__process(queryset=queryset, level=CLIENT_LEVEL_KEY)

    def __process(self, queryset, level: str):
        for key_role_grouped, items in groupby(queryset, lambda ele: ele.role.key):
            if key_role_grouped in ["OWNER", "ADMIN"]:
                default_role_ids = CustomRole.objects.filter(
                    key=ROLE_ADMIN_KEY, level=level
                ).values_list("id", flat=True)
            else:
                default_role_ids = CustomRole.objects.filter(
                    key=ROLE_STAFF_KEY, level=level
                ).values_list("id", flat=True)
            objects = list(items)
            # chunk size 100
            chunks = [
                objects[x: x + CHUNK_SIZE] for x in range(0, len(objects), CHUNK_SIZE)
            ]
            for sub_list in chunks:
                self.__sync(objects=sub_list, default_role_ids=default_role_ids)

    def __sync(self, objects, default_role_ids):
        """
        Sync permission for user in WS or ORG
        level and role of users in ORG (WS) must be the same to reduce query

        """
        all_object_ids = [ele.id for ele in objects]

        custom_role_ids_bucket = self.__get_custom_role_bucket(all_object_ids)
        override_permissions_bucket = self.__get_override_permissions_bucket(
            all_object_ids
        )

        res = []
        for object_ref in objects:
            object_id = str(object_ref.id)
            custom_role_ids = custom_role_ids_bucket.get(object_id, [])
            access_rule_query_set = (
                ComposePermissionService.compose_access_rules_from_custom_roles(
                    [*custom_role_ids, *default_role_ids]
                )
            )

            overriding_permissions_groups = override_permissions_bucket.get(
                object_id, []
            )
            permission = ComposePermissionService.compose_permission_from_access_rules(
                access_rule_query_set, overriding_permissions_groups
            )

            permission = [
                OrgClientUserPermission(
                    key=per["key"],
                    module=per["module"],
                    name=per["name"],
                    group=per["group"],
                    enabled=True
                    if per["status"] == STATUS_PERMISSION_ALLOW_KEY
                    else False,
                    content_object=object_ref,
                )
                for per in permission
            ]
            res.extend(permission)

        OrgClientUserPermission.objects.filter(object_id__in=all_object_ids).delete()
        OrgClientUserPermission.objects.bulk_create(res, batch_size=5000)
        return

    @classmethod
    def __get_custom_role_bucket(cls, object_ids: List[str]) -> Dict[str, List[str]]:
        # get custom role of users
        custom_role_query_set = OrgClientCustomRoleUser.objects.filter(
            object_id__in=object_ids
        ).order_by("object_id", "priority")

        bucket = {}
        for object_id_grouped, items in groupby(
            custom_role_query_set, lambda ele: ele.object_id
        ):
            bucket.update(
                {str(object_id_grouped): [item.custom_role_id for item in items]}
            )
        return bucket

    @classmethod
    def __get_override_permissions_bucket(
        cls, object_ids: List[str]
    ) -> Dict[str, List[str]]:
        query_set = OverridingOrgClientUserPermission.objects.filter(
            object_id__in=object_ids
        ).order_by("object_id")
        bucket = {}
        for object_id_grouped, items in groupby(query_set, lambda ele: ele.object_id):
            permission = [
                {
                    "group": item.permission.group,
                    "key": item.permission.key,
                    "name": item.permission.name,
                    "status": item.status,
                    "module": item.permission.module,
                }
                for item in items
            ]
            bucket.update(
                {
                    str(
                        object_id_grouped
                    ): ComposePermissionService.group_composed_permission(permission)
                }
            )

        return bucket
