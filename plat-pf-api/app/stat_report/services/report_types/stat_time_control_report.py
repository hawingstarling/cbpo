import copy
import logging
from datetime import timedelta
from django.db import DEFAULT_DB_ALIAS
from django.utils import timezone
from app.stat_report.services.report_types.stat_report import StatReporter
from app.core.variable.pf_trust_ac import SALE_EVENT_TYPE, DONE_STATUS, \
    IGNORE_STATUS, INFORMED_TYPE, FINANCIAL_EVENT_TYPE, OPEN_STATUS, READY_STATUS, PROCESS_STATUS, ERROR_STATUS
from app.stat_report.models import StatClientChannelReport, StatReport
from app.stat_report.variables.stat_channel_type import STAT_REPORT_DAILY, STAT_REPORT_MONTHLY
from django.db.models import Q, Count
from app.financial.models import SaleItem, DataStatus

logger = logging.getLogger(__name__)


class StatTimeControlReport(StatReporter):
    def __init__(self, client_id: str, *args, **kwargs):
        super().__init__(client_id, *args, **kwargs)
        self.date_recent_7_days = self._get_date_last_7_days()
        self.date_recent_6_months = self._get_date_last_6_month()

    def _prefetch_condition_filters(self):
        time_control_filters = dict()
        sale_filters = dict()
        for channel in self.channels:
            for i in self.date_recent_7_days:
                cond = Q(client_id=self.client_id, channel=channel, date=i.date())
                cond_completed = Q(client_id=self.client_id, channel=channel, date=i.date(),
                                   status__in=[DONE_STATUS, IGNORE_STATUS])
                key_cond = f"time_control_{channel.name}_day_{i.date().strftime('%Y%m%d')}"
                key_cond_completed = f"time_control_{channel.name}_day_{i.date().strftime('%Y%m%d')}_completed"
                time_control_filters.update({
                    key_cond: Count('pk', filter=cond),
                    key_cond_completed: Count('pk', filter=cond_completed),
                })
                #
                _val = copy.deepcopy(i)
                _from_date = _val.replace(hour=0, minute=0, second=0, microsecond=0)
                _to_date = _val.replace(hour=23, minute=59, second=59, microsecond=999)
                cond = Q(sale_date__gte=_from_date, sale_date__lte=_to_date, sale__channel=channel)
                key_cond = f"sale_{channel.name}_day_{i.date().strftime('%Y%m%d')}"
                sale_filters.update({
                    key_cond: Count('pk', filter=cond)
                })

            for i in self.date_recent_6_months:
                _val = copy.deepcopy(i)
                _from_date = _val.replace(day=1, hour=0, minute=0, second=0)
                _to_date = _val.replace(hour=23, minute=59, second=59)
                #
                cond = Q(client_id=self.client_id, channel=channel, date__gte=_from_date.date(),
                         date__lte=_to_date.date())
                cond_completed = Q(client_id=self.client_id, channel=channel,
                                   date__gte=_from_date.date(),
                                   date__lte=_to_date.date(), status__in=[DONE_STATUS, IGNORE_STATUS])
                key_cond = f"time_control_{channel.name}_month_{i.date().strftime('%Y%m%d')}"
                key_cond_completed = f"time_control_{channel.name}_month_{i.date().strftime('%Y%m%d')}_completed"
                time_control_filters.update({
                    key_cond: Count('pk', filter=cond),
                    key_cond_completed: Count('pk', filter=cond_completed),
                })
                #
                cond = Q(sale_date__gte=_from_date, sale_date__lte=_to_date, sale__channel=channel)
                key_cond = f"sale_{channel.name}_month_{i.date().strftime('%Y%m%d')}"
                sale_filters.update({
                    key_cond: Count('pk', filter=cond)
                })

        return time_control_filters, sale_filters

    def _prefetch_instance_stat_report(self):
        time_control_filters, sale_filters = self._prefetch_condition_filters()

        objs = []

        agg_time_control = DataStatus.objects.tenant_db_for(self.client_id).aggregate(**time_control_filters)
        agg_sales = SaleItem.objects.tenant_db_for(self.client_id).aggregate(**sale_filters)

        for channel in self.channels:
            for i in self.date_recent_7_days:
                _val = copy.deepcopy(i)
                _from_date = _val.replace(day=1, hour=0, minute=0, second=0)
                key_cond = f"time_control_{channel.name}_day_{i.date().strftime('%Y%m%d')}"
                total_time_control = agg_time_control[key_cond]
                key_cond = f"time_control_{channel.name}_day_{i.date().strftime('%Y%m%d')}_completed"
                total_time_control_completed = agg_time_control[key_cond]
                key_cond = f"sale_{channel.name}_day_{i.date().strftime('%Y%m%d')}"
                total_sales = agg_sales[key_cond]

                obj = StatClientChannelReport(
                    organization=self.client.organization,
                    client_id=self.client_id,
                    channel=channel,
                    report_type=STAT_REPORT_DAILY,
                    report_date=_from_date,
                    total_sales=total_sales,
                    total_time_control=total_time_control,
                    total_time_control_completed=total_time_control_completed
                )
                objs.append(obj)

            for i in self.date_recent_6_months:
                _val = copy.deepcopy(i)
                _from_date = _val.replace(day=1, hour=0, minute=0, second=0)

                key_cond = f"time_control_{channel.name}_month_{i.date().strftime('%Y%m%d')}"
                total_time_control = agg_time_control[key_cond]
                key_cond = f"time_control_{channel.name}_month_{i.date().strftime('%Y%m%d')}_completed"
                total_time_control_completed = agg_time_control[key_cond]
                key_cond = f"sale_{channel.name}_month_{i.date().strftime('%Y%m%d')}"
                total_sales = agg_sales[key_cond]

                obj = StatClientChannelReport(
                    organization=self.client.organization,
                    client_id=self.client_id,
                    channel=channel,
                    report_type=STAT_REPORT_MONTHLY,
                    report_date=_from_date.date(),
                    total_sales=total_sales,
                    total_time_control=total_time_control,
                    total_time_control_completed=total_time_control_completed
                )
                objs.append(obj)
        return objs

    def validate(self):
        pass

    def process(self):
        if not self.channels:
            logger.error(f"[{self.__class__.__name__}][process_data]: Config settings financial is error")
            return
        try:
            #
            objs = self._prefetch_instance_stat_report()

            assert len(objs) > 0, "Objs is not empty!"

            self.__save_as_stat_client_channel_report(objs)

        except Exception as ex:
            logger.error(f"[{self.__class__.__name__}][process_data] {ex}")

    def __save_as_stat_client_channel_report(self, objs):
        try:
            StatClientChannelReport.objects.tenant_db_for(DEFAULT_DB_ALIAS).filter(client_id=self.client_id).delete()
            StatClientChannelReport.objects.tenant_db_for(DEFAULT_DB_ALIAS).bulk_create(objs, ignore_conflicts=True)
        except Exception as ex:
            logger.error(f"[{self.__class__.__name__}][__save_as_stat_client_channel_report] {ex}")

    @classmethod
    def calculation_for_stat_report_summary(cls) -> dict:
        logger.info(f"[{cls.__class__.__name__}][calculation_for_stat_report_summary] Begin ...")
        date_recent_7_days = cls._get_date_last_7_days()
        date_recent_6_months = cls._get_date_last_6_month()
        #
        date_7d_start = date_recent_7_days[-1].date()
        date_7d_end = date_recent_7_days[0].date()
        #
        date_6m_start = date_recent_6_months[-1].date()
        yesterday = timezone.now() - timedelta(days=1)
        date_6m_end = date_recent_6_months[0].date().replace(day=yesterday.date().day)
        #
        agg_stat_details = DataStatus.objects.tenant_db_for(DEFAULT_DB_ALIAS) \
            .aggregate(
            client_total=Count('client_id', distinct=True),
            client_not_completed=Count('client_id', distinct=True,
                                       filter=Q(status__in=[OPEN_STATUS, READY_STATUS, PROCESS_STATUS, ERROR_STATUS])),
            sale_event_7d_total=Count('pk',
                                      filter=Q(type=SALE_EVENT_TYPE, date__gte=date_7d_start, date__lte=date_7d_end)),
            sale_event_7d_completed=Count('pk',
                                          filter=Q(type=SALE_EVENT_TYPE, status__in=[DONE_STATUS, IGNORE_STATUS],
                                                   date__gte=date_7d_start, date__lte=date_7d_end)),
            financial_event_7d_total=Count('pk', filter=Q(type=FINANCIAL_EVENT_TYPE, date__gte=date_7d_start,
                                                          date__lte=date_7d_end)),
            financial_event_7d_completed=Count('pk',
                                               filter=Q(type=FINANCIAL_EVENT_TYPE,
                                                        status__in=[DONE_STATUS, IGNORE_STATUS],
                                                        date__gte=date_7d_start, date__lte=date_7d_end)),
            informed_event_7d_total=Count('pk',
                                          filter=Q(type=INFORMED_TYPE, date__gte=date_7d_start, date__lte=date_7d_end)),
            informed_event_7d_completed=Count('pk',
                                              filter=Q(type=INFORMED_TYPE, status__in=[DONE_STATUS, IGNORE_STATUS],
                                                       date__gte=date_7d_start, date__lte=date_7d_end)),
            #
            sale_event_6m_total=Count('pk',
                                      filter=Q(type=SALE_EVENT_TYPE, date__gte=date_6m_start, date__lte=date_6m_end)),
            sale_event_6m_completed=Count('pk',
                                          filter=Q(type=SALE_EVENT_TYPE, status__in=[DONE_STATUS, IGNORE_STATUS],
                                                   date__gte=date_6m_start, date__lte=date_6m_end)),
            financial_event_6m_total=Count('pk', filter=Q(type=FINANCIAL_EVENT_TYPE, date__gte=date_6m_start,
                                                          date__lte=date_6m_end)),
            financial_event_6m_completed=Count('pk',
                                               filter=Q(type=FINANCIAL_EVENT_TYPE,
                                                        status__in=[DONE_STATUS, IGNORE_STATUS],
                                                        date__gte=date_6m_start, date__lte=date_6m_end)),
            informed_event_6m_total=Count('pk',
                                          filter=Q(type=INFORMED_TYPE, date__gte=date_6m_start, date__lte=date_6m_end)),
            informed_event_6m_completed=Count('pk',
                                              filter=Q(type=INFORMED_TYPE, status__in=[DONE_STATUS, IGNORE_STATUS],
                                                       date__gte=date_6m_start, date__lte=date_6m_end)),
        )
        StatReport.objects.tenant_db_for(DEFAULT_DB_ALIAS).all().delete()
        #
        kwargs = dict(
            client_time_control=dict(
                client_total=agg_stat_details['client_total'],
                client_completed=agg_stat_details['client_total'] - agg_stat_details['client_not_completed']
            ),
            sales_time_control=dict(
                sale_event_7d_total=agg_stat_details['sale_event_7d_total'],
                sale_event_7d_completed=agg_stat_details['sale_event_7d_completed'],
                sale_event_6m_total=agg_stat_details['sale_event_6m_total'],
                sale_event_6m_completed=agg_stat_details['sale_event_6m_completed'],
            ),
            financial_event_time_control=dict(
                financial_event_7d_total=agg_stat_details['financial_event_7d_total'],
                financial_event_7d_completed=agg_stat_details['financial_event_7d_completed'],
                financial_event_6m_total=agg_stat_details['financial_event_6m_total'],
                financial_event_6m_completed=agg_stat_details['financial_event_6m_completed'],
            ),
            informed_time_control=dict(
                informed_event_7d_total=agg_stat_details['informed_event_7d_total'],
                informed_event_7d_completed=agg_stat_details['informed_event_7d_completed'],
                informed_event_6m_total=agg_stat_details['informed_event_6m_total'],
                informed_event_6m_completed=agg_stat_details['informed_event_6m_completed'],
            )
        )
        StatReport.objects.tenant_db_for(DEFAULT_DB_ALIAS).create(**kwargs)
        # return kwargs

    def complete(self):
        logger.info(f"[{self.__class__.__name__}][{self.client_id}][process] Begin ...")
