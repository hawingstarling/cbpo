from django.core.management import BaseCommand

from app.permission.config_static_varible.common import CLIENT_LEVEL_KEY, MODULE_DICT
from app.permission.config_static_varible.config import (
    PERMISSIONS_GROUPS_CONFIG_CLIENT_LEVEL,
)
from app.permission.models import (
    Permission,
    AccessRulePermission,
    OverridingOrgClientUserPermission,
)

from app.core.custom_bulk_sync_all_objects import custom_bulk_sync


class Command(BaseCommand):
    args = "<foo bar ...>"
    help = "our help string comes here"

    """
    config permission
    """

    def _permission(self):
        list_permission_ins = []

        # PERMISSIONS_GROUPS_CONFIG_CLIENT_LEVEL
        group_keys = list(PERMISSIONS_GROUPS_CONFIG_CLIENT_LEVEL.keys())
        for group_key in group_keys:
            module = PERMISSIONS_GROUPS_CONFIG_CLIENT_LEVEL[group_key]["module"]
            module_name = MODULE_DICT[module]
            group_name = PERMISSIONS_GROUPS_CONFIG_CLIENT_LEVEL[group_key]["name"]
            for permission in PERMISSIONS_GROUPS_CONFIG_CLIENT_LEVEL[group_key][
                "permissions"
            ]:
                key = permission.get("key")
                name = permission.get("name")
                list_permission_ins.append(
                    Permission(
                        key=key,
                        name=name,
                        is_removed=False,
                        module=module,
                        module_name=module_name,
                        group=group_key,
                        group_name=group_name,
                        level=CLIENT_LEVEL_KEY,
                    )
                )

        #  TODO: permission org

        stats = custom_bulk_sync(
            new_models=list_permission_ins,
            filters=None,
            fields=[
                "key",
                "name",
                "module",
                "module_name",
                "group",
                "group_name",
                "level",
                "is_removed",
            ],
            key_fields=["key"],
        )
        print("_permission stats")
        print(stats)

    def handle(self, *args, **options):
        self._permission()

        deleted_permission_ids = Permission.all_objects.filter(
            is_removed=True
        ).values_list("id", flat=True)
        AccessRulePermission.objects.filter(
            permission__id__in=deleted_permission_ids
        ).delete()
        OverridingOrgClientUserPermission.objects.filter(
            permission__id__in=deleted_permission_ids
        ).delete()
