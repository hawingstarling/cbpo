from app.core.custom_bulk_sync_all_objects import custom_bulk_sync
from django.core.management import BaseCommand
from django.db import transaction
from django.db.models import Q

from app.permission.config_static_varible.common import (
    CUSTOM_TYPE_CREATED_SYSTEM_KEY,
    CLIENT_LEVEL_KEY,
    ORG_LEVEL_KEY,
)
from app.permission.config_static_varible.custom_roles.client.config_custom_role_client import (
    custom_role_client_system_default_created,
)
from app.permission.config_static_varible.custom_roles.org.config_custom_role_org import (
    custom_role_org_system_default_created,
)
from app.permission.models import (
    AccessRule,
    CustomRole,
    CustomRoleAccessRule,
    OrgClientCustomRoleUser,
)


class Command(BaseCommand):
    args = "<foo bar ...>"
    help = "our help string comes here"

    """
    config custom role
    """

    def handler_config_custom_role(self, config: dict, level: str):
        assert level in [CLIENT_LEVEL_KEY, ORG_LEVEL_KEY], "level is invalid"
        print("config Default Custom Role for %s" % level)
        role_default_keys = config.keys()
        for _key in role_default_keys:
            role_content = config[_key]
            role_name = role_content["name"]
            custom_role_obj = CustomRole(
                key=_key,
                name=role_name,
                owner=None,
                type_created=CUSTOM_TYPE_CREATED_SYSTEM_KEY,
                level=level,
                is_removed=False,
            )
            custom_bulk_sync(
                new_models=[custom_role_obj],
                fields=["key", "name", "owner", "type_created", "level", "is_removed"],
                key_fields=["key", "type_created", "level"],
                filters=Q(
                    key=_key, level=level, type_created=CUSTOM_TYPE_CREATED_SYSTEM_KEY
                ),
            )
            custom_role_ins = CustomRole.objects.get(
                key=_key,
                name=role_name,
                owner=None,
                type_created=CUSTOM_TYPE_CREATED_SYSTEM_KEY,
                level=level,
            )
            access_rule_keys = role_content["access_rules"]
            new_models = []
            for index, access_rule_key in enumerate(access_rule_keys):
                access_rule_ins = AccessRule.objects.get(
                    key=access_rule_key,
                    level=level,
                    type_created=CUSTOM_TYPE_CREATED_SYSTEM_KEY,
                )
                new_models.append(
                    CustomRoleAccessRule(
                        custom_role=custom_role_ins,
                        access_rule=access_rule_ins,
                        priority=index + 1,
                        is_removed=False,
                    )
                )
            stats = custom_bulk_sync(
                new_models=new_models,
                fields=["custom_role_id", "access_rule_id", "priority", "is_removed"],
                key_fields=["custom_role_id", "access_rule_id"],
                filters=Q(custom_role__id=custom_role_ins.id),
            )

            print("_custom_role stats %s" % _key)
            print(stats)

    def handle(self, *args, **options):
        with transaction.atomic():
            self.handler_config_custom_role(
                custom_role_client_system_default_created, CLIENT_LEVEL_KEY
            )
            self.handler_config_custom_role(
                custom_role_org_system_default_created, ORG_LEVEL_KEY
            )
            deleted_ids = CustomRole.all_objects.filter(is_removed=True).values_list(
                "id", flat=True
            )
            CustomRoleAccessRule.objects.filter(
                custom_role__id__in=deleted_ids
            ).delete()
            OrgClientCustomRoleUser.objects.filter(
                custom_role__id__in=deleted_ids
            ).delete()
