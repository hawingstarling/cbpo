from django.core.management.base import BaseCommand

from app.job.models import RouteConfig, TaskRouteConfig
from app.job.utils.variable import LIST_JOB_CATEGORY


class Command(BaseCommand):
    help = "My shiny new management command."

    def add_arguments(self, parser):
        parser.add_argument('-db', '--database', type=str, help='Provide db name')

    def handle(self, *args, **options):
        try:
            route_default, _ = RouteConfig.objects \
                .get_or_create(queue="celery", defaults={"exchange": "celery(direct)", "routing_key": "celery"})

            objs = []

            for category in LIST_JOB_CATEGORY:
                try:
                    TaskRouteConfig.objects.get(task_path=category, category=category)
                except Exception as ex:
                    objs.append(TaskRouteConfig(task_path=category, category=category, route=route_default))
            if objs:
                TaskRouteConfig.objects.bulk_create(objs=objs, ignore_conflicts=True)
        except Exception as ex:
            print(f"Init route config err : {ex}")
