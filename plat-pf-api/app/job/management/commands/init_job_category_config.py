from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Q
from django.db.utils import DEFAULT_DB_ALIAS
from django.utils import timezone

from app.job.models import JobConfig
from app.job.utils.config import CATEGORY_PRIORITY_CONFIG, CATEGORY_TIME_LIMIT_CONFIG, CATEGORY_MAX_RECURSIVE_CONFIG, \
    CATEGORY_VALIDATIONS_CONFIG
from app.job.utils.variable import LIST_JOB_CATEGORY


class Command(BaseCommand):
    help = "My shiny new management command."

    def add_arguments(self, parser):
        parser.add_argument('-db', '--database', type=str, help='Provide db name')
        parser.add_argument('-override', '--override_job', action='store_true', help='Enable/Disable Override')

    def handle(self, *args, **options):
        try:
            override = options['override_job']
            with transaction.atomic():
                jobs_name_exclude = []
                objs_inserts = []
                objs_updates = []
                for category in LIST_JOB_CATEGORY:
                    keys = list(CATEGORY_PRIORITY_CONFIG[category].keys()) \
                           + list(CATEGORY_TIME_LIMIT_CONFIG[category].keys()) \
                           + list(CATEGORY_MAX_RECURSIVE_CONFIG[category].keys()) \
                           + list(CATEGORY_VALIDATIONS_CONFIG[category].keys())
                    keys = list(set(keys))
                    jobs_name_exclude += keys
                    for key in keys:
                        priority = CATEGORY_PRIORITY_CONFIG[category] \
                            .get(key, CATEGORY_PRIORITY_CONFIG[category]['default'])
                        time_limit = CATEGORY_TIME_LIMIT_CONFIG[category] \
                            .get(key, CATEGORY_TIME_LIMIT_CONFIG[category]['default'])
                        max_recursive = CATEGORY_MAX_RECURSIVE_CONFIG[category] \
                            .get(key, CATEGORY_MAX_RECURSIVE_CONFIG[category]['default'])
                        validations = CATEGORY_VALIDATIONS_CONFIG[category] \
                            .get(key, CATEGORY_VALIDATIONS_CONFIG[category]['default'])
                        try:
                            obj = JobConfig.objects.tenant_db_for(DEFAULT_DB_ALIAS).get(name=key, category=category)
                            if override:
                                obj.priority = priority
                                obj.time_limit = time_limit
                                obj.max_recursive = max_recursive
                                obj.validations = validations
                            else:
                                if not obj.validations:
                                    obj.validations = validations
                            obj.modified = timezone.now()
                            objs_updates.append(obj)
                        except Exception as ex:
                            obj = JobConfig(name=key, category=category, priority=priority, time_limit=time_limit,
                                            max_recursive=max_recursive, validations=validations)
                            objs_inserts.append(obj)
                jobs_name_exclude = list(set(jobs_name_exclude))
                JobConfig.objects.tenant_db_for(DEFAULT_DB_ALIAS).filter(~Q(name__in=jobs_name_exclude)).delete()
                if objs_inserts:
                    JobConfig.objects.tenant_db_for(DEFAULT_DB_ALIAS).bulk_create(objs_inserts, ignore_conflicts=True)
                if objs_updates:
                    JobConfig.objects.tenant_db_for(DEFAULT_DB_ALIAS).bulk_update(objs_updates,
                                                                                  fields=["validations", "modified"])
        except Exception as ex:
            print(f"Init job category config config err : {ex}")
