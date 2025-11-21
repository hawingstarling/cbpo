import logging
from datetime import timedelta, timezone
from django.db import DEFAULT_DB_ALIAS
from django.db.models import Count, Q
from app.financial.models import SaleItem
from app.job.utils.helper import register
from app.job.utils.variable import STATS_REPORT_CATEGORY, MODE_RUN_IMMEDIATELY
from app.stat_report.models import StatClientChannelReport
from app.stat_report.services.report_types.stat_report import StatReporter
from django.db.models.functions import TruncHour

from app.stat_report.variables.stat_channel_type import STAT_REPORT_HOUR

logger = logging.getLogger(__name__)


class StatSaleRecentService(StatReporter):
    def __init__(self, client_id: str, *args, **kwargs):
        super().__init__(client_id, *args, **kwargs)
        self.sale_recent_type = self.kwargs.get("sale_recent_type", STAT_REPORT_HOUR)

    @property
    def filters_recent_type(self):
        try:
            last_tracking = StatClientChannelReport.objects.tenant_db_for(DEFAULT_DB_ALIAS).filter(
                organization_id=self.client.organization_id,
                client_id=self.client_id,
                report_type=self.sale_recent_type
            ).order_by("-report_date").first()
            modified__gte = last_tracking.report_date
        except Exception as ex:
            modified__gte = self.time_now - timedelta(days=3)
        modified__gte.replace(minute=0, second=0, microsecond=0)
        rs = dict()
        if self.sale_recent_type == STAT_REPORT_HOUR:
            rs.update(modified__gte=modified__gte)
        else:
            pass
        assert len(rs) > 0, "filter type doesn't accept empty"
        return rs

    def validate(self):
        assert self.sale_recent_type in [STAT_REPORT_HOUR], "Sale rent type not in list accept of system"

    def get_queryset_data(self):
        qs = SaleItem.objects.tenant_db_for(self.client_id) \
            .filter(**self.filters_recent_type) \
            .annotate(report_date=TruncHour("modified", tzinfo=timezone.utc)) \
            .values("report_date", "sale__channel_id") \
            .annotate(total_sales=Count("pk")).order_by("report_date")
        return qs

    def process(self):
        logger.info(f"[{self.__class__.__name__}][{self.client_id}][process] Begin ...")
        queryset = self.get_queryset_data()
        if queryset.count() == 0:
            logger.info(f"[{self.__class__.__name__}][{self.client}][process] "
                        f"Not found data for calculate sale rent ...")
            self.complete()
            return
        obj_ids = []
        objs_insert = []
        objs_update = []
        for data in queryset:
            try:
                obj = StatClientChannelReport.objects.tenant_db_for(DEFAULT_DB_ALIAS).get(
                    organization_id=self.client.organization_id,
                    client_id=self.client_id,
                    report_type=self.sale_recent_type,
                    channel_id=data["sale__channel_id"],
                    report_date=data["report_date"]
                )
                if obj.total_sales == data["total_sales"]:
                    obj_ids.append(obj.pk)
                    continue
                obj.total_sales = data["total_sales"]
                obj.modified = self.time_now
                objs_update.append(obj)
            except StatClientChannelReport.DoesNotExist:
                obj = StatClientChannelReport(
                    organization_id=self.client.organization_id,
                    client_id=self.client_id,
                    report_type=self.sale_recent_type,
                    channel_id=data["sale__channel_id"],
                    report_date=data["report_date"],
                    total_sales=data["total_sales"]
                )
                objs_insert.append(obj)
            except Exception as ex:
                logger.error(f"[{self.__class__.__name__}][{self.client_id}][process][{data}] {ex}")
                obj = None
            if obj:
                obj_ids.append(obj.pk)
        if not objs_insert and not objs_update:
            logger.error(f"[{self.__class__.__name__}][{self.client_id}][process] "
                         f"Not found data for type {self.sale_recent_type} compress ...")
            self.complete()
            return
        if objs_insert:
            logger.info(f"[{self.__class__.__name__}][{self.client_id}][process][inserts] totals = {len(objs_insert)}")
            StatClientChannelReport.objects.tenant_db_for(DEFAULT_DB_ALIAS) \
                .bulk_create(objs_insert, ignore_conflicts=True)
        if objs_update:
            logger.info(f"[{self.__class__.__name__}][{self.client_id}][process][updates] totals = {len(objs_update)}")
            StatClientChannelReport.objects.tenant_db_for(DEFAULT_DB_ALIAS) \
                .bulk_update(objs_update, fields=["total_sales", "modified"])
        if obj_ids:
            created__lt = (self.time_now - timedelta(days=3)).replace(minute=0, second=0, microsecond=0)
            cond = Q(organization_id=self.client.organization_id, client_id=self.client_id,
                     report_type=self.sale_recent_type, created__lt=created__lt) & ~Q(pk__in=obj_ids)
            StatClientChannelReport.objects.tenant_db_for(DEFAULT_DB_ALIAS).filter(cond).delete()
        # make as completed and pick job for calculate summary Stats sale rent
        self.complete()

    def complete(self):
        logger.info(f"[{self.__class__.__name__}][{self.client_id}][complete] Begin ...")
        # make job for calculated to model summary StatSaleRecentReport
        data = dict(
            name=f"stats_sale_recent_summary_all_workspaces",
            job_name="app.stat_report.jobs.stats.stats_sale_recent_summary_all_workspaces",
            module="app.stat_report.jobs.stats",
            method="stats_sale_recent_summary_all_workspaces",
            is_run_validations=False,
            meta=dict(report_type=STAT_REPORT_HOUR)
        )
        register(category=STATS_REPORT_CATEGORY, client_id=self.client_id, **data,
                 mode_run=MODE_RUN_IMMEDIATELY)
