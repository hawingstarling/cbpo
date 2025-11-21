from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "This command using for init required initial data for the system"

    def handle(self, *args, **options):
        call_command("init_sale_status")
        call_command("init_profit_status")
        call_command("init_fulfillment_channel")
        call_command("init_job_category_config")
        call_command("init_task_route_config")
