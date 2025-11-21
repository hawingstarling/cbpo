from django.core.management import BaseCommand

from app.permission.services.organization import OrganizationPermissionManager
from app.tenancies.models import Organization


class Command(BaseCommand):
    args = "<foo bar ...>"
    help = "our help string comes here"

    """
    sync permissions from new config
    """

    def add_arguments(self, parser):
        parser.add_argument(
            "--org",
            help="Filter by Org id",
        )

    def handle(self, *args, **options):
        org_id = options.get("org", None)
        if org_id:
            all_org = [org_id]
        else:
            all_org = Organization.objects.all().values_list("id", flat=True)
        for org in all_org:
            self.sync(org)

    @classmethod
    def sync(cls, organization_id: str):
        return OrganizationPermissionManager(organization_id).run()
