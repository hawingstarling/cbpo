import logging
import uuid
from django.contrib import admin, messages
from celery.states import PENDING, FAILURE, STARTED, SUCCESS
from django.db.models import Q
from django.db.utils import DEFAULT_DB_ALIAS
from django.utils import timezone
from app.job.models import ImportJobClient, BulkJobClient, SyncAnalysisJobClient, CommunityJobClient, \
    TimeControlJobClient, SyncDataSourceJobClient, JobConfig, DataSourceCalculationJobClient, SellingPartnerJobClient, \
    RouteConfig, TaskRouteConfig, RouteWorkerTrack, StatsReportJobClient, COGSMappingJobClient
from app.job.tasks import process_task_route_config
from app.job.utils.config import CATEGORY_MODEL
from app.job.utils.helper import create_job_config_record_settings, ignore_category_job, revoked_category_job, \
    register_category_bulk
from app.job.utils.variable import COMMUNITY_CATEGORY, IMPORT_CATEGORY, BULK_CATEGORY, SYNC_ANALYSIS_CATEGORY, \
    TIME_CONTROL_CATEGORY, SYNC_DATA_SOURCE_CATEGORY, DATA_SOURCE_CALCULATION_CATEGORY, SELLING_PARTNER_CATEGORY, \
    STATS_REPORT_CATEGORY, MODE_RUN_IMMEDIATELY, MODE_RUN_PARALLEL, COGS_MAPPING_CATEGORY

logger = logging.getLogger(__name__)


@admin.register(RouteConfig)
class RouteConfigAdmin(admin.ModelAdmin):
    list_display = ["id", "queue", "exchange", "routing_key", "active", "created", "modified"]
    search_fields = ["queue", "exchange", "routing_key"]
    ordering = ["created"]
    actions = ['prefetch_route_worker_config']

    def prefetch_route_worker_config(self, request, queryset):
        process_task_route_config()
        messages.success(request, f"Prefetch Route Worker Config Successfully")


@admin.register(RouteWorkerTrack)
class RouteWorkerTrackAdmin(admin.ModelAdmin):
    list_display = ["id", "worker_id", "route", "status", "created", "modified"]
    search_fields = ["worker_id"]
    list_filter = ["route", "status"]
    ordering = ["created"]


@admin.register(TaskRouteConfig)
class TaskRouteConfigAdmin(admin.ModelAdmin):
    list_display = ["id", "task_path", "category", "route", "enabled", "created", "modified"]
    search_fields = ["task_path"]
    ordering = ["created"]
    list_filter = ["route", "category", "enabled"]
    actions = ['prefetch_route_category_task_path']

    def handler_prefetch_route_category_task_path(self, obj: TaskRouteConfig):
        cond = Q()
        if obj.task_path == obj.category:
            cond.add(Q(status__in=[PENDING, STARTED, FAILURE]), Q.AND)
        elif '.*' in obj.task_path:
            job_path = obj.task_path.replace('.*', '')
            cond.add(Q(module=job_path, status__in=[PENDING, STARTED, FAILURE]), Q.AND)
        else:
            cond.add(Q(job_name=obj.task_path, status__in=[PENDING, STARTED, FAILURE]), Q.AND)
        route = obj.route
        CATEGORY_MODEL[obj.category].objects.tenant_db_for(DEFAULT_DB_ALIAS) \
            .filter(cond).update(queue=route.queue, exchange=route.exchange, routing_key=route.routing_key)
        logger.info(f"[{self.__class__.__name__}][handler_prefetch_route_category_task_path] "
                    f"complete prefetch for task path = {obj.task_path}, category = {obj.category}")

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if change:
            obj.refresh_from_db()
            self.handler_prefetch_route_category_task_path(obj)

    def prefetch_route_category_task_path(self, request, queryset):
        num_records = queryset.count()
        try:
            for item in queryset.iterator():
                self.handler_prefetch_route_category_task_path(item)
            messages.success(request, f"{num_records} prefetch route category task path successfully")
        except Exception as ex:
            msg = f"{num_records} prefetch route category task path {ex}"
            messages.error(request, msg)

    prefetch_route_category_task_path.short_description = 'Prefetch route category task path'


@admin.register(JobConfig)
class JobConfigAdmin(admin.ModelAdmin):
    list_display = ['id', 'category', 'name', 'priority', 'time_limit', 'max_recursive', 'created', 'modified']
    search_fields = ['name']
    list_filter = ['category', 'priority', 'retry']
    ordering = ['category', 'created']
    actions = ['create_job_config_record_settings']

    def create_job_config_record_settings(self, request, queryset):
        create_job_config_record_settings()

    create_job_config_record_settings.short_description = 'Init job config record settings'


class JobClientBase(admin.ModelAdmin):
    category = None
    list_display = ['id', 'name', 'group_id', 'mode_run', 'client', 'status', 'recursive', 'max_recursive', 'created',
                    'modified']
    list_filter = ['client', 'status', 'priority', 'queue', 'retry', 'mode_run']
    search_fields = ['name', 'job_name', 'method', 'group_id']
    ordering = ['created']
    actions = ['re_open', 'run_now', 'revoke', 'ignore', 'done']

    def re_open(self, request, queryset):
        num_records = queryset.count()
        try:
            client_ids = list(set(queryset.values_list('client_id', flat=True)))
            data = {client_id: [] for client_id in client_ids}
            for item in queryset.iterator():
                item.status = PENDING
                item.group_id = None
                item.modified = timezone.now()
                item.task_id = uuid.uuid4()
                data[item.client_id].append(item)
            for client_id, items in data.items():
                self.model.objects.tenant_db_for(client_id).bulk_update(items, fields=['status', 'modified', 'task_id',
                                                                                       'group_id'])
            messages.success(request, f"{num_records} records REOPEN successfully")
        except Exception as ex:
            msg = f"{num_records} REOPEN {ex}"
            messages.error(request, msg)

    def revoke(self, request, queryset):
        num_records = queryset.count()
        try:
            task_ids = list(queryset.values_list('task_id', flat=True))
            revoked_category_job(self.category, task_ids)
            messages.success(request, f"{num_records} records REVOKED successfully")
        except Exception as ex:
            msg = f"{num_records} REVOKED {ex}"
            messages.error(request, msg)

    def ignore(self, request, queryset):
        num_records = queryset.count()
        try:
            task_ids = list(queryset.values_list('task_id', flat=True))
            ignore_category_job(self.category, task_ids)
            messages.success(request, f"{num_records} records IGNORED successfully")
        except Exception as ex:
            msg = f"{num_records} IGNORED {ex}"
            messages.error(request, msg)

    def run_now(self, request, queryset):
        queryset = queryset.filter(Q(status=PENDING) & ~Q(mode_run=MODE_RUN_PARALLEL))
        num_records = queryset.count()
        try:
            objs = []
            time_now = timezone.now()
            for obj in queryset.iterator():
                obj.mode_run = MODE_RUN_IMMEDIATELY
                obj.group_id = None
                obj.modified = time_now
                objs.append(obj)
            register_category_bulk(category=self.category, objs_insert=[], objs_update=objs,
                                   mode_run=MODE_RUN_IMMEDIATELY)
            messages.success(request, f"{num_records} records RUN IMMEDIATELY successfully")
        except Exception as ex:
            msg = f"{num_records} RUN IMMEDIATELY {ex}"
            messages.error(request, msg)

    def done(self, request, queryset):
        num_records = queryset.count()
        try:
            client_ids = list(set(queryset.values_list('client_id', flat=True)))
            data = {client_id: [] for client_id in client_ids}
            for item in queryset.iterator():
                item.status = SUCCESS
                item.modified = timezone.now()
                data[item.client_id].append(item)
            for client_id, items in data.items():
                self.model.objects.tenant_db_for(client_id) \
                    .bulk_update(items, fields=['status', 'modified'])
            messages.success(request, f"{num_records} records Done successfully")
        except Exception as ex:
            msg = f"{num_records} DONE {ex}"
            messages.error(request, msg)

    re_open.short_description = "Re Open"
    run_now.short_description = "Run Now"
    revoke.short_description = "Revoke"
    ignore.short_description = "Ignore"
    done.short_description = "Done"


@admin.register(CommunityJobClient)
class CommunityJobClient(JobClientBase):
    category = COMMUNITY_CATEGORY


@admin.register(ImportJobClient)
class ImportJobClientAdmin(JobClientBase):
    category = IMPORT_CATEGORY


@admin.register(BulkJobClient)
class BulkJobClientAdmin(JobClientBase):
    category = BULK_CATEGORY


@admin.register(SyncAnalysisJobClient)
class SyncAnalysisJobClientAdmin(JobClientBase):
    category = SYNC_ANALYSIS_CATEGORY


@admin.register(TimeControlJobClient)
class TimeControlJobClientAdmin(JobClientBase):
    category = TIME_CONTROL_CATEGORY


@admin.register(SyncDataSourceJobClient)
class SyncDataSourceJobClientAdmin(JobClientBase):
    category = SYNC_DATA_SOURCE_CATEGORY


@admin.register(DataSourceCalculationJobClient)
class DataSourceCalculationJobClientAdmin(JobClientBase):
    category = DATA_SOURCE_CALCULATION_CATEGORY


@admin.register(SellingPartnerJobClient)
class SellingPartnerJobClientAdmin(JobClientBase):
    category = SELLING_PARTNER_CATEGORY


@admin.register(StatsReportJobClient)
class StatsReportJobClientAdmin(JobClientBase):
    category = STATS_REPORT_CATEGORY


@admin.register(COGSMappingJobClient)
class COGSMappingJobClientAdmin(JobClientBase):
    category = COGS_MAPPING_CATEGORY
