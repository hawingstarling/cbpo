import logging
from django.core.management.base import BaseCommand
from django.db.utils import DEFAULT_DB_ALIAS
from ...models import SPReportCategory, SPReportType
from ...variables.report_config import REPORT_CATEGORIES_CONFIG

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "This command init sp report types"

    def add_arguments(self, parser):
        parser.add_argument('-sync', '--sync_data', action='store_true', help='ON/OFF create new table schema')
        parser.add_argument('-db', '--db_config', type=str, help='Provide database name')

    def handle(self, *args, **options):
        try:
            print("Begin init sp report types")
            sync_data = options.get('sync_data', False)
            db_config = options.get('db_config', DEFAULT_DB_ALIAS)
            total_types = SPReportType.objects.db_manager(using=db_config).exists()
            if total_types and not sync_data:
                print("SP report types has init in system")
                return
            categories_objs = []
            sub_categories_objs = []
            type_objs = []
            for idx, categories in enumerate(REPORT_CATEGORIES_CONFIG):
                categories_name = categories['categories']
                categories_value = categories['categories_value']
                try:
                    categories_obj = SPReportCategory.objects.db_manager(using=db_config) \
                        .get(parent=None, name=categories_name)
                    if not categories_obj.value:
                        categories_obj.value = categories_value
                        categories_obj.save()
                except Exception as ex:
                    categories_obj = SPReportCategory(name=categories_name, sort=idx)
                    categories_objs.append(categories_obj)

                if 'sub_categories' in categories:
                    for sub_idx, sub_categories in enumerate(categories["sub_categories"]):
                        sub_name = sub_categories["name"]
                        sub_value = sub_categories["value"]
                        try:
                            sub_categories_obj = SPReportCategory.objects.db_manager(using=db_config) \
                                .get(parent=categories_obj, name=sub_name)
                            if not sub_categories_obj.value:
                                sub_categories_obj.value = sub_value
                                sub_categories_obj.save()
                        except Exception as ex:
                            sub_categories_obj = SPReportCategory(parent=categories_obj, name=sub_name, sort=sub_idx)
                            sub_categories_objs.append(sub_categories_obj)

                        for sub_type_idx, sub_type in enumerate(sub_categories["types"]):
                            name = sub_type["name"]
                            val = sub_type["value"]
                            try:
                                SPReportType.objects.db_manager(using=db_config) \
                                    .get(category=sub_categories_obj, name=name, value=val)
                            except Exception as ex:
                                type_obj = SPReportType(category=sub_categories_obj, sort=sub_type_idx, **sub_type)
                                type_objs.append(type_obj)
                else:
                    for type_idx, item in enumerate(categories["types"]):
                        name = item["name"]
                        val = item["value"]
                        try:
                            SPReportType.objects.db_manager(using=db_config) \
                                .get(category=categories_obj, name=name, value=val)
                        except Exception as ex:
                            type_obj = SPReportType(category=categories_obj, **item, sort=type_idx)
                            type_objs.append(type_obj)

            if categories_objs:
                print(f"SP report types categories = {len(categories_objs)}")
                SPReportCategory.objects.db_manager(using=db_config).bulk_create(categories_objs, ignore_conflicts=True)

            if sub_categories_objs:
                print(f"SP report types sub categories = {len(sub_categories_objs)}")
                SPReportCategory.objects.db_manager(using=db_config) \
                    .bulk_create(sub_categories_objs, ignore_conflicts=True)

            if type_objs:
                print(f"SP report types = {len(type_objs)}")
                SPReportType.objects.db_manager(using=db_config).bulk_create(type_objs, ignore_conflicts=True)

            print("End init sp report types")
        except Exception as ex:
            logger.error('Command init sp report types error {}'.format(ex))
            print('Init sp report types error {}'.format(ex))
