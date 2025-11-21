import logging
import uuid
from datetime import timedelta

from celery.states import SUCCESS, FAILURE, IGNORED, REJECTED
from typing import List
from django.contrib.postgres.aggregates import StringAgg
from django.db import models, DEFAULT_DB_ALIAS
from django.db.models import Count, Q, Value, CharField, Sum, QuerySet, Model
from django.db.models.functions import Cast, Concat
from django.utils import timezone
from model_utils.models import TimeStampedModel
from app.database.db.objects_manage import MultiDbTableManagerBase
from app.financial.models import ClientPortal, Organization, Channel
from app.job.models import JobClient
from app.stat_report.variables.healthy import SERVICE_CONFIG
from app.stat_report.variables.stat_channel_type import STAT_REPORT_TYPE, STAT_REPORT_DAILY, STAT_REPORT_HOUR

logger = logging.getLogger(__name__)


class StatReport(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client_time_control = models.JSONField(default=dict)
    sales_time_control = models.JSONField(default=dict)
    financial_event_time_control = models.JSONField(default=dict)
    informed_time_control = models.JSONField(default=dict)
    #
    objects = MultiDbTableManagerBase()
    all_objects = MultiDbTableManagerBase()


class StatSaleRecentReportAbstract(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    report_type = models.CharField(max_length=50, default=STAT_REPORT_HOUR, choices=STAT_REPORT_TYPE)
    report_date = models.DateTimeField(default=timezone.now)
    total_sales_affected = models.IntegerField(default=0)
    total_jobs = models.IntegerField(default=0)
    total_jobs_completed = models.IntegerField(default=0)
    total_jobs_failed = models.IntegerField(default=0)
    #
    objects = MultiDbTableManagerBase()
    all_objects = MultiDbTableManagerBase()

    def __str__(self):
        return f"Marketplace: {self.channel.name} - Type: {self.report_type} - Date: {self.report_date}"

    class Meta:
        abstract = True

    @classmethod
    def bulk_stats_sale_recent_summary(cls, queryset: QuerySet,
                                       columns_key: List[str], columns_update: List[str],
                                       report_type: str = STAT_REPORT_HOUR,
                                       cond_clean: Q = Q(report_type=STAT_REPORT_HOUR)):
        obj_ids = []
        objs_insert = []
        objs_update = []
        for data in queryset:
            keys_data = {key: data.pop(key) for key in columns_key}
            try:
                obj = cls.objects.tenant_db_for(DEFAULT_DB_ALIAS) \
                    .get(**keys_data)
                for column in columns_update:
                    if getattr(obj, column) == data[column]:
                        obj_ids.append(obj.pk)
                        continue
                    setattr(obj, column, data[column])
                obj.modified = timezone.now()
                objs_update.append(obj)
            except cls.DoesNotExist:
                obj = cls(**keys_data, **data)
                objs_insert.append(obj)
            except Exception as ex:
                logger.error(f"[{cls.__name__}][calculate_sale_recent][{report_type}][{data}] {ex}")
                obj = None
            if obj:
                obj_ids.append(obj.pk)
        if not objs_insert and not objs_update:
            logger.error(f"[{cls.__name__}][calculate_sale_recent][{report_type}] "
                         f"Not found summary of clients channel ...")
            return
        if objs_insert:
            logger.info(f"[{cls.__name__}][calculate_sale_recent][{report_type}][inserts] "
                        f"totals = {len(objs_insert)} ...")
            cls.objects.tenant_db_for(DEFAULT_DB_ALIAS).bulk_create(objs_insert, ignore_conflicts=True)
        if objs_update:
            logger.info(f"[{cls.__name__}][calculate_sale_recent][{report_type}][updates] "
                        f"totals = {len(objs_update)} ...")
            cls.objects.tenant_db_for(DEFAULT_DB_ALIAS) \
                .bulk_update(objs_update, fields=columns_update + ["modified"])
        if obj_ids:
            cond = cond_clean & ~Q(pk__in=obj_ids)
            cls.objects.tenant_db_for(DEFAULT_DB_ALIAS).filter(cond).delete()


class StatSaleRecentReport(StatSaleRecentReportAbstract):
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    report_date = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ["channel", "report_type", "report_date"]

    @classmethod
    def calculate_sale_recent(cls, report_type: str = STAT_REPORT_HOUR):
        # TODO: now we using DEFAULT_DB_ALIAS, therefore future we can make correct by sum client allocated which DB
        client_db = DEFAULT_DB_ALIAS
        queryset = StatClientChannelReport.objects.tenant_db_for(client_db) \
            .filter(report_type=report_type) \
            .values("channel_id", "report_type", "report_date") \
            .annotate(total_sales_affected=Sum("total_sales")) \
            .order_by("report_date")
        cls.bulk_stats_sale_recent_summary(
            queryset=queryset,
            columns_key=["channel_id", "report_type", "report_date"],
            columns_update=["total_sales_affected"],
            cond_clean=Q(report_type=report_type)
        )


class StatSaleRecentSummaryReport(StatSaleRecentReportAbstract):
    channel = models.ForeignKey(Channel, default=None, null=True, blank=True, on_delete=models.CASCADE)
    report_date = models.DateTimeField(default=None, null=True, blank=True)

    def __str__(self):
        return f"Marketplace: {self.channel} - Type: {self.report_type} - Date: {self.report_date}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['channel', 'report_type'],
                condition=Q(
                    report_date__isnull=True
                ),
                name='unique_stat_sale_marketplace_summary'),
            models.UniqueConstraint(
                fields=['report_date', 'report_type'],
                condition=Q(
                    channel__isnull=True
                ),
                name='unique_stat_sale_report_date_summary')
        ]

    @classmethod
    def calculate_sale_recent(cls, report_type: str = STAT_REPORT_HOUR):
        # TODO: now we using DEFAULT_DB_ALIAS, therefore future we can make correct by sum client allocated which DB
        client_db = DEFAULT_DB_ALIAS
        qs_marketplaces_summary = StatClientChannelReport.objects.tenant_db_for(client_db) \
            .filter(report_type=report_type) \
            .values("channel_id", "report_type") \
            .annotate(total_sales_affected=Sum("total_sales")) \
            .order_by("channel__name")
        cls.bulk_stats_sale_recent_summary(
            queryset=qs_marketplaces_summary,
            columns_key=["channel_id", "report_type"],
            columns_update=["total_sales_affected"],
            cond_clean=Q(report_type=report_type, channel__isnull=False, report_date__isnull=True)
        )
        qs_report_dates_summary = StatClientChannelReport.objects.tenant_db_for(client_db) \
            .filter(report_type=report_type) \
            .values("report_date", "report_type") \
            .annotate(total_sales_affected=Sum("total_sales")) \
            .order_by("report_date")
        cls.bulk_stats_sale_recent_summary(
            queryset=qs_report_dates_summary,
            columns_key=["report_type", "report_date"],
            columns_update=["total_sales_affected"],
            cond_clean=Q(report_type=report_type, channel__isnull=True, report_date__isnull=False)
        )

    @classmethod
    def calculated_job_recent(cls, report_type: str = STAT_REPORT_HOUR):
        qs = cls.objects.tenant_db_for(DEFAULT_DB_ALIAS).filter(report_type=report_type, channel__isnull=True,
                                                                report_date__isnull=False).order_by('created')
        objs = []
        for obj in qs.iterator():
            start_date = obj.report_date - timedelta(hours=1)
            end_date = obj.report_date
            obj.total_jobs = JobClient.get_total_number(start_date, end_date)
            obj.total_jobs_completed = JobClient.get_total_number(start_date, end_date, status=[SUCCESS])
            obj.total_jobs_failed = JobClient.get_total_number(start_date, end_date,
                                                               status=[FAILURE, IGNORED, REJECTED])
            obj.modified = timezone.now()
            objs.append(obj)
        cls.objects.tenant_db_for(DEFAULT_DB_ALIAS).bulk_update(objs, fields=["total_jobs", "total_jobs_completed",
                                                                              "total_jobs_failed", "modified"])


class StatClientChannelReport(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    client = models.ForeignKey(ClientPortal, on_delete=models.CASCADE, null=True)
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    report_type = models.CharField(max_length=50, default=STAT_REPORT_DAILY, choices=STAT_REPORT_TYPE)
    report_date = models.DateTimeField(default=timezone.now)
    total_sales = models.IntegerField(default=0)
    total_jobs = models.IntegerField(default=0)
    total_done_jobs = models.IntegerField(default=0)
    total_error_jobs = models.IntegerField(default=0)
    total_time_control = models.IntegerField(default=0)
    total_time_control_completed = models.IntegerField(default=0)
    #
    objects = MultiDbTableManagerBase()
    all_objects = MultiDbTableManagerBase()

    class Meta:
        unique_together = ['organization', 'client', 'channel', 'report_type', 'report_date']
        indexes = [
            models.Index(
                fields=['organization', 'client', 'channel', 'total_time_control', 'total_time_control_completed'])
        ]

    def __str__(self):
        return f"{self.organization} - {self.client} - {self.channel} - {self.report_type}"


class HealthAbstract(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    service_name = models.CharField(max_length=50, null=False)
    is_enabled = models.BooleanField(null=False)
    is_healthy = models.BooleanField(null=False)
    #
    objects = MultiDbTableManagerBase()
    all_objects = MultiDbTableManagerBase()

    class Meta:
        abstract = True


class OrgClientHealth(HealthAbstract):
    service_name = models.CharField(max_length=50, null=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    client = models.ForeignKey(ClientPortal, on_delete=models.CASCADE, null=True)
    message = models.JSONField(default=dict)

    class Meta:
        unique_together = ['organization', 'client', 'service_name']
        indexes = [
            models.Index(
                fields=['organization', 'client', 'service_name', 'is_healthy', 'is_enabled'])
        ]

    def __str__(self):
        return f"client: {self.client} - service: {self.service_name} - healthy: {self.is_healthy}"

    @staticmethod
    def summary_service_status():
        qs = OrgClientHealth.objects.tenant_db_for(DEFAULT_DB_ALIAS).values('service_name') \
            .annotate(number_not_healthy=Count('is_healthy', filter=Q(is_healthy=False)),
                      messages=StringAgg(Cast(Concat('client__name', Value(' not good')), CharField()),
                                         delimiter=' , ', distinct=True, filter=Q(is_healthy=False)))
        vals = dict()
        for item in qs:
            msgs = item['messages']
            if not msgs:
                msgs = "OK"
            vals.update({SERVICE_CONFIG[item['service_name']]: {
                'is_enabled': True,
                'is_healthy': False if item['number_not_healthy'] > 0 else True,
                'message': msgs
            }})
        return vals

    @staticmethod
    def summary():
        kwargs_is_not_healthy = dict(
            is_enabled=True, is_healthy=False
        )
        agg = OrgClientHealth.objects.tenant_db_for(DEFAULT_DB_ALIAS).aggregate(
            total_client=Count('client_id', distinct=True, filter=Q(is_enabled=True)),
            total_client_fails=Count('client_id', distinct=True, filter=Q(**kwargs_is_not_healthy)),
            total_client_ac=Count('pk', filter=Q(service_name='ac', is_enabled=True)),
            total_client_ac_fails=Count('pk', filter=Q(service_name='ac', **kwargs_is_not_healthy)),
            total_client_dc=Count('pk', filter=Q(service_name='dc', is_enabled=True)),
            total_client_dc_fails=Count('pk', filter=Q(service_name='dc', **kwargs_is_not_healthy)),
            total_client_ds=Count('pk', filter=Q(service_name='ds', is_enabled=True)),
            total_client_ds_fails=Count('pk', filter=Q(service_name='ds', **kwargs_is_not_healthy)),
            total_client_import=Count('pk', filter=Q(service_name='import', is_enabled=True)),
            total_client_import_fails=Count('pk', filter=Q(service_name='import', **kwargs_is_not_healthy)),
            total_client_bulk=Count('pk', filter=Q(service_name='bulk', is_enabled=True)),
            total_client_bulk_fails=Count('pk', filter=Q(service_name='bulk', **kwargs_is_not_healthy)),
            total_client_export=Count('pk', filter=Q(service_name='export', is_enabled=True)),
            total_client_export_fails=Count('pk', filter=Q(service_name='export', **kwargs_is_not_healthy)),
            total_client_es=Count('pk', filter=Q(service_name='es', is_enabled=True)),
            total_client_es_fails=Count('pk', filter=Q(service_name='es', **kwargs_is_not_healthy)),
        )
        return agg


class ClientReportCost(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(ClientPortal, on_delete=models.CASCADE)
    date = models.DateField()
    total_sales = models.IntegerField()
    total_30d_sales = models.IntegerField()
    #
    objects = MultiDbTableManagerBase()
    all_objects = MultiDbTableManagerBase()

    def __str__(self):
        return f"{self.client} - {self.date}"

    class Meta:
        unique_together = ['client', 'date']
