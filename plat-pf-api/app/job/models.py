import logging
import uuid
from datetime import datetime

from celery.states import PENDING, RECEIVED, STARTED
from django.contrib.postgres.fields import ArrayField
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models, DEFAULT_DB_ALIAS
from django.db.models import Sum, Count, Q
from django.db.models.functions import Coalesce
from model_utils.models import TimeStampedModel
from app.database.db.objects_manage import MultiDbTableManagerBase
from app.financial.models import ClientPortal
from app.job.utils.variable import STATUS_CHOICE, JOB_CATEGORY_CHOICES, COMMUNITY_CATEGORY, MODE_RUN_SEQUENTIALLY, \
    MODE_RUN_CHOICE, ROUTE_WORKER_STATUS, ROUTE_WORKER_STARTED_STATUS

logger = logging.getLogger(__name__)


class RouteConfig(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    queue = models.CharField(max_length=255, default="celery", unique=True)
    exchange = models.CharField(max_length=255, default="celery(direct)")
    routing_key = models.CharField(max_length=255, default="celery")
    #
    objects = MultiDbTableManagerBase()
    all_objects = MultiDbTableManagerBase()

    def __str__(self):
        return f"{self.queue} - {self.exchange} - {self.routing_key}"

    @property
    def active(self) -> bool:
        return self.routeworkertrack_set.filter(status=ROUTE_WORKER_STARTED_STATUS).exists()

    @property
    def queue_info(self):
        return {
            'queue': self.queue,
            'exchange': self.exchange,
            'routing_key': self.routing_key
        }

    @property
    def total_worker_info(self):
        agg = self.routeworkertrack_set.filter(status=ROUTE_WORKER_STARTED_STATUS) \
            .aggregate(total_worker=Count('id'), max_concurrency=Coalesce(Sum('max_concurrency'), 0))
        return agg


class RouteWorkerTrack(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    route = models.ForeignKey(RouteConfig, on_delete=models.CASCADE)
    worker_id = models.CharField(max_length=255)
    max_concurrency = models.IntegerField(default=20)
    status = models.CharField(max_length=255, choices=ROUTE_WORKER_STATUS, default=ROUTE_WORKER_STARTED_STATUS)
    #
    objects = MultiDbTableManagerBase()
    all_objects = MultiDbTableManagerBase()

    def __str__(self):
        return f"{self.worker_id} - {self.route} - {self.status}"

    class Meta:
        indexes = [
            models.Index(fields=['route', 'status', 'created'])
        ]
        unique_together = ['route', 'worker_id']

    @staticmethod
    def summary():
        count = RouteWorkerTrack.objects.tenant_db_for(DEFAULT_DB_ALIAS).filter(
            status=ROUTE_WORKER_STARTED_STATUS).count()
        return dict(
            api=2,
            beat=1,
            worker=count
        )


class TaskRouteConfig(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task_path = models.CharField(max_length=255)
    category = models.CharField(max_length=255, choices=JOB_CATEGORY_CHOICES, default=COMMUNITY_CATEGORY)
    route = models.ForeignKey(RouteConfig, on_delete=models.CASCADE)
    enabled = models.BooleanField(default=True)
    #
    objects = MultiDbTableManagerBase()
    all_objects = MultiDbTableManagerBase()

    def __str__(self):
        return f"{self.task_path} - {self.route} - {self.enabled}"

    class Meta:
        unique_together = ['task_path', 'category', 'route']


class JobConfig(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.CharField(max_length=255, choices=JOB_CATEGORY_CHOICES, default=COMMUNITY_CATEGORY)
    name = models.CharField(max_length=255, verbose_name="Job name")
    priority = models.IntegerField(default=7, validators=[MinValueValidator(0), MaxValueValidator(9)])
    time_limit = models.IntegerField(default=2400, verbose_name="Time limit(s)")
    retry = models.BooleanField(default=True, verbose_name="Retry connection")
    retry_policy = models.JSONField(default=None, null=True, blank=True, verbose_name="Retry policy connection")
    max_recursive = models.IntegerField(default=0)
    disabled_sequentially = models.BooleanField(default=False)
    validations = ArrayField(models.CharField(max_length=200, unique=True), default=list,
                             blank=True)  # seller_partner_marketplace_connection, ...
    is_run_validations = models.BooleanField(default=True)
    #
    objects = MultiDbTableManagerBase()
    all_objects = MultiDbTableManagerBase()

    def __str__(self):
        return f"{self.id} - {self.category} - {self.name}"

    class Meta:
        indexes = [
            models.Index(fields=['category', 'name'])
        ]
        unique_together = ['category', 'name']


class JobClient(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task_id = models.UUIDField(default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)  # name job
    client = models.ForeignKey(ClientPortal, on_delete=models.CASCADE)
    group_id = models.UUIDField(default=None, null=True, blank=True)  # group_id for run parallel
    mode_run = models.CharField(max_length=200, choices=MODE_RUN_CHOICE, default=MODE_RUN_SEQUENTIALLY)
    job_name = models.CharField(max_length=200)
    module = models.CharField(max_length=500)  # name space location module contain method
    method = models.CharField(max_length=200)  # name method trigger
    meta = models.JSONField(default=dict)  # param for input job method
    validations = ArrayField(models.CharField(max_length=200, unique=True), default=list,
                             blank=True)  # seller_partner_marketplace_connection, ...
    is_run_validations = models.BooleanField(default=None, null=True)
    status = models.CharField(max_length=200, choices=STATUS_CHOICE, default=PENDING)
    msg = models.TextField(default=None, null=True)
    priority = models.IntegerField(default=None, null=True)  # priority 0 -> 9 , 0 is higher , 9 is lowest
    time_limit = models.IntegerField(default=None, null=True, verbose_name="Time limit (seconds)")
    retry = models.BooleanField(default=False, verbose_name="Retry connection")
    retry_policy = models.JSONField(default=None, null=True, blank=True, verbose_name="Retry policy connection")
    recursive = models.IntegerField(default=0)
    max_recursive = models.IntegerField(default=0)
    callback = models.JSONField(default=dict)
    #
    queue = models.CharField(max_length=255, null=True, default=None)
    exchange = models.CharField(max_length=255, null=True, default=None)
    routing_key = models.CharField(max_length=255, null=True, default=None)
    #
    objects = MultiDbTableManagerBase()
    all_objects = MultiDbTableManagerBase()

    def __str__(self):
        return f"{self.id} - {self.name} - {self.client} - {self.status}"

    class Meta:
        indexes = [
            models.Index(fields=['client', 'status']),
            models.Index(fields=['client', 'status', 'modified']),
            models.Index(fields=['client', 'status', 'modified', 'group_id']),
            models.Index(fields=['client', 'status', 'created', 'recursive']),
        ]
        unique_together = ['id', 'name', 'client', 'module', 'method', 'created']
        abstract = True

    @classmethod
    def total_jobs_started(cls):
        val = 0
        try:
            val = cls.objects.tenant_db_for(DEFAULT_DB_ALIAS) \
                .filter(status__in=[STARTED, RECEIVED]).count()
        except Exception as ex:
            logger.error(f"[{cls.__class__.__name__}][number_job_active] {ex}")
        return val

    @classmethod
    def get_total_number(cls, start_date: datetime, end_date: datetime, status: [str] = []):
        total = 0
        try:
            cond = Q(created__gte=start_date, created__lt=end_date)
            if status:
                cond.add(Q(status__in=status), Q.AND)
            for model_calculated in cls.__subclasses__():
                total += model_calculated.objects.tenant_db_for(DEFAULT_DB_ALIAS).filter(cond).count()
        except Exception as ex:
            logger.error(f"[{cls.__class__.__name__}][get_total_number] {ex}")
        return total


class CommunityJobClient(JobClient):
    pass


class ImportJobClient(JobClient):
    pass


class BulkJobClient(JobClient):
    pass


class SyncAnalysisJobClient(JobClient):
    pass


class TimeControlJobClient(JobClient):
    pass


class SyncDataSourceJobClient(JobClient):
    pass


class DataSourceCalculationJobClient(JobClient):
    pass


class SellingPartnerJobClient(JobClient):
    pass


class StatsReportJobClient(JobClient):
    pass


class COGSMappingJobClient(JobClient):
    pass
