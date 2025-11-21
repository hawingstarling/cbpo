from app.core.custom_bulk_sync_all_objects import custom_bulk_sync
from django.core.management import BaseCommand
from django.db import transaction
from django.db.models import Q

from app.permission.config_static_varible.access_rules.client.config_access_rule_client import (
    access_rule_client_system_default_created,
)
from app.permission.config_static_varible.access_rules.org.config_access_rule_org import (
    access_rule_org_system_default_created,
)
from app.permission.config_static_varible.common import (
    CUSTOM_TYPE_CREATED_SYSTEM_KEY,
    CLIENT_LEVEL_KEY,
    ORG_LEVEL_KEY,
)
from app.permission.models import (
    Permission,
    AccessRule,
    AccessRulePermission,
    CustomRoleAccessRule,
)


class Command(BaseCommand):
    args = "<foo bar ...>"
    help = "our help string comes here"

    """
    config access rule
    """

    def handler_access_rule_config(self, config: dict, level: str):
        assert level in [CLIENT_LEVEL_KEY, ORG_LEVEL_KEY], "level is invalid"
        print("config Default Access Rule for %s" % level)
        rule_default_keys = config.keys()

        all_system_rules = []
        for _key in rule_default_keys:
            #  sync rule in total system rules
            rule_content = config[_key]
            name = rule_content["name"]
            module = rule_content.get("module", None)
            access_rule_obj = AccessRule(
                key=_key,
                name=name,
                owner=None,
                is_removed=False,
                type_created=CUSTOM_TYPE_CREATED_SYSTEM_KEY,
                level=level,
                module=module,
            )
            all_system_rules.append(access_rule_obj)

        custom_bulk_sync(
            new_models=all_system_rules,
            fields=[
                "key",
                "name",
                "owner",
                "type_created",
                "level",
                "is_removed",
                "module",
            ],
            key_fields=["key", "type_created", "level"],
            filters=Q(level=level, type_created=CUSTOM_TYPE_CREATED_SYSTEM_KEY),
        )

        for _key in rule_default_keys:
            #  sync permissions in rule
            new_models = []
            rule_content = config[_key]

            access_rule_ins = AccessRule.objects.get(
                key=_key,
                owner=None,
                type_created=CUSTOM_TYPE_CREATED_SYSTEM_KEY,
                level=level,
            )
            permissions_groups_content = rule_content["permissions_groups"]
            group_keys = permissions_groups_content.keys()
            for _group_key in group_keys:
                list_permissions = permissions_groups_content[_group_key]
                for permission in list_permissions:
                    permission_key = permission["key"]
                    status = permission["status"]
                    permission_ins = Permission.objects.get(
                        group=_group_key, key=permission_key
                    )
                    new_models.append(
                        AccessRulePermission(
                            access_rule=access_rule_ins,
                            permission=permission_ins,
                            status=status,
                            is_removed=False,
                        )
                    )

            stats = custom_bulk_sync(
                new_models=new_models,
                filters=Q(access_rule=access_rule_ins),
                fields=["access_rule_id", "permission_id", "status", "is_removed"],
                key_fields=["access_rule_id", "permission_id"],
            )
            print("_access_rule stats %s" % _key)
            print(stats)

    def handle(self, *args, **options):
        with transaction.atomic():
            self.handler_access_rule_config(
                access_rule_client_system_default_created, CLIENT_LEVEL_KEY
            )
            self.handler_access_rule_config(
                access_rule_org_system_default_created, ORG_LEVEL_KEY
            )

            deleted_access_rules_ids = AccessRule.all_objects.filter(
                is_removed=True
            ).values_list("id", flat=True)

            CustomRoleAccessRule.objects.filter(
                access_rule__id__in=deleted_access_rules_ids
            ).delete()
