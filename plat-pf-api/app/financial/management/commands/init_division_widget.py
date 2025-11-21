from django.core.management.base import BaseCommand
from django.db import DEFAULT_DB_ALIAS
from django.utils import timezone
from app.financial.jobs.settings import handler_init_sync_divisions_widget_clients
from app.financial.models import ClientPortal, DivisionManage
from app.financial.variable.segment_variable import OVERALL_SALES_CATEGORY, \
    OVERALL_SALES_CALCULATE_DEFAULT


class Command(BaseCommand):
    help = "Command init dashboard widget data."

    def add_arguments(self, parser):
        parser.add_argument('-over_settings', '--override_settings', action='store_true',
                            help='Accept/Denied override settings exists')
        parser.add_argument('-over_positions', '--override_positions', action='store_true',
                            help='Accept/Denied override positions exists')
        parser.add_argument('-sync', '--sync_clients', action='store_true', help='Accept/Denied override config exists')

    def handle(self, *args, **options):
        override_settings = options['override_settings']
        override_positions = options['override_positions']
        sync_clients = options['sync_clients']

        print(f"begin init divisions widgets .... ")
        #
        divisions_configs = {
            OVERALL_SALES_CATEGORY: [
                dict(
                    key="Dropship-Sales",
                    name="Dropship Sales",
                    settings={
                        "conditions": OVERALL_SALES_CALCULATE_DEFAULT["Dropship-Sales"]
                    },
                    position=1
                ),
                dict(
                    key="FBA-Sales",
                    name="FBA Sales",
                    settings={
                        "conditions": OVERALL_SALES_CALCULATE_DEFAULT["FBA-Sales"]
                    },
                    position=2
                ),
                dict(
                    key="MFN",
                    name="MFN",
                    settings={
                        "conditions": OVERALL_SALES_CALCULATE_DEFAULT["MFN"]
                    },
                    position=3
                ),
                dict(
                    key="Total-Units-Sold",
                    name="Total Units Sold",
                    settings={
                        "conditions": OVERALL_SALES_CALCULATE_DEFAULT["Total-Units-Sold"]
                    },
                    position=4
                ),
                dict(
                    key="Total-Sales",
                    name="Total Sales",
                    settings={
                        "conditions": OVERALL_SALES_CALCULATE_DEFAULT["Total-Sales"]
                    },
                    position=5
                )
            ]
        }

        division_inserts = []
        division_updates = []

        for category, configs in divisions_configs.items():
            for config in configs:
                try:
                    obj = DivisionManage.objects.get(category=category, key=config["key"])
                    if not override_settings and not override_positions:
                        continue
                    if override_settings:
                        obj.settings = config["settings"]
                    if override_positions:
                        obj.position = config["position"]
                    obj.modified = timezone.now()
                    division_updates.append(obj)  # update
                except Exception as ex:
                    division_inserts.append(DivisionManage(
                        category=category,
                        key=config["key"],
                        name=config["name"],
                        settings=config["settings"],
                        position=config["position"]
                    ))

        if len(division_inserts) == 0 and len(division_updates) == 0:
            print(f"No data need to insert or update division widget config")

        if len(division_inserts) > 0:
            print("Begin insert division widget config")
            DivisionManage.objects.using(DEFAULT_DB_ALIAS).bulk_create(division_inserts, ignore_conflicts=True)
        if len(division_updates) > 0:
            print("Begin update division widget config")
            DivisionManage.objects.using(DEFAULT_DB_ALIAS).bulk_update(division_updates,
                                                                       fields=["settings", "position", "modified"])

        if sync_clients:
            print(f"Begin init clients divisions widgets .... ")

            client_ids = ClientPortal.objects.tenant_db_for(DEFAULT_DB_ALIAS).values_list('pk', flat=True)

            handler_init_sync_divisions_widget_clients(client_ids=client_ids, override_settings=override_settings,
                                                       override_positions=override_positions)

        print(f"End init divisions widgets .... ")
