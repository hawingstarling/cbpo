from django.core.management import BaseCommand

from app.payments.config import APP_MWRW
from app.payments.models import (
    ApprovalOrganizationalStandardizationConfig,
    Subscription,
    MapWatcherStandardizationConfig,
)


class Command(BaseCommand):
    args = "<foo bar ...>"
    help = "our help string comes here"

    """
    migrate existing ApprovalOrganizationalStandardizationConfig for specific organization
    """

    def handle(self, *args, **options):
        org_configs = (
            ApprovalOrganizationalStandardizationConfig.objects.all().select_related(
                "organization"
            )
        )
        org_ids = [ele.organization_id for ele in org_configs]

        all_subscription = Subscription.objects.filter(
            organization__id__in=org_ids, application=APP_MWRW
        ).select_related("plan")

        standard_configs = MapWatcherStandardizationConfig.objects.all()

        for ele in org_configs:
            print(f"migrate organization {ele.organization.name}")
            # find org subscription to get type
            find_org_sub = filter(
                lambda _ele: _ele.organization_id == ele.organization_id,
                all_subscription,
            )
            try:
                org_sub = next(find_org_sub)
            except StopIteration:
                raise Exception("config error")

            _type = org_sub.plan.type
            print(f"plan type {_type}")

            # get standard balance config by type
            find_standard_config = filter(
                lambda _ele: _ele.type == _type, standard_configs
            )
            try:
                org_standard_config = next(find_standard_config)
            except StopIteration:
                raise Exception("config error")

            # update new field in meta config for organization

            ele.config.update(
                {
                    "amazon_inventory_scraping": org_standard_config.amazon_inventory_scraping
                }
            )
            print(f"new config {ele.config}")
            ele.save(update_fields=["config"])
