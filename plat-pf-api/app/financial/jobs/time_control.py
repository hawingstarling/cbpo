import logging
from typing import Any
from celery.states import STARTED
from django.db.models import Q, F
from django.utils import timezone
from celery import current_app
from app.core.helper import get_connections_client_channels
from app.core.variable.marketplace import SELLER_PARTNER_CONNECTION, INFORMED_MARKETPLACE_CONNECTION
from app.financial.models import DataStatus, Channel
from app.financial.services.integrations.time_control.sales_time_control import SalesTimeControl
from app.financial.services.integrations.time_control.trans_event_time_control import FinancialEventTimeControl
from app.financial.services.integrations.time_control.informed_time_control import InformedTimeControl
from app.core.variable.pf_trust_ac import SALE_EVENT_TYPE, FINANCIAL_EVENT_TYPE, INFORMED_TYPE, \
    TIME_CONTROl_TYPE_LIST, READY_STATUS, PROCESS_STATUS, PF_TIME_CONTROL_PRIORITY_TYPE, IGNORE_STATUS, ERROR_STATUS, \
    OPEN_STATUS
from app.core.variable.pf_trust_ac import TIME_CONTROL_NUMBER_BEAT_JOB
from app.job.utils.helper import register_list, get_category_job_queryset
from app.job.utils.variable import TIME_CONTROL_CATEGORY, MODE_RUN_IMMEDIATELY

logger = logging.getLogger(__name__)

TIME_CONTROL_MANAGE = {
    SALE_EVENT_TYPE: SalesTimeControl,
    FINANCIAL_EVENT_TYPE: FinancialEventTimeControl,
    INFORMED_TYPE: InformedTimeControl,
}


@current_app.task(bind=True)
def handler_time_control_create_event(self, client_id, date_type: Any = None, **kwargs):
    if date_type is None:
        date_type = timezone.now().date()
    channels = Channel.objects.tenant_db_for(client_id).filter(is_pull_data=True)
    marketplaces = channels.values_list('name', flat=True)
    client_connections = get_connections_client_channels(client_id, list(marketplaces))
    for tracking_type in TIME_CONTROl_TYPE_LIST:
        for channel in channels:
            try:
                assert client_connections[SELLER_PARTNER_CONNECTION].get(channel.name, False) is True, \
                    f"The workspace doesn't connect marketplace"
                if tracking_type == INFORMED_TYPE:
                    assert client_connections[INFORMED_MARKETPLACE_CONNECTION].get(channel.name, False) is True, \
                        f"The workspace doesn't setup informed"
                try:
                    priority = PF_TIME_CONTROL_PRIORITY_TYPE[tracking_type]
                except Exception as err:
                    priority = None
                DataStatus.objects.tenant_db_for(client_id).get_or_create(client_id=client_id, channel=channel,
                                                                          type=tracking_type,
                                                                          date=date_type, priority=priority)
            except Exception as ex:
                logger.error(f"[{self.request.id}][handler_time_control_create_event][{client_id}]"
                             f"[{channel.name}] {ex}")


def pick_jobs_time_control_check_types_is_ready_workspaces(client_ids):
    jobs_data = list()
    job_name = "app.financial.jobs.time_control.handler_job_time_control_check_type_is_ready_workspace"
    module = "app.financial.jobs.time_control"
    method = "handler_job_time_control_check_type_is_ready_workspace"
    for client_id in client_ids:
        data = dict(
            name=f"time_control_check_event_is_ready",
            client_id=client_id,
            job_name=job_name,
            module=module,
            method=method,
            is_run_validations=False,
            meta=dict(client_id=client_id)
        )
        jobs_data.append(data)
    if len(jobs_data) > 0:
        register_list(TIME_CONTROL_CATEGORY, jobs_data, mode_run=MODE_RUN_IMMEDIATELY)
        logger.info(f"[financial_is_ready_event_open][{client_ids}] register_list app jobs completed")


# Execute every 10' minute
def pick_jobs_time_control_process_types_is_ready_workspaces(client_ids):
    jobs_data = list()
    job_name = "app.financial.jobs.time_control.handler_time_control_process_type_is_ready_workspace"
    module = "app.financial.jobs.time_control"
    method = "handler_time_control_process_type_is_ready_workspace"
    #
    time_now = timezone.now()
    #
    for client_id in client_ids:
        marketplaces = Channel.objects.tenant_db_for(client_id).filter(is_pull_data=True) \
            .values_list('name', flat=True)
        client_connections = get_connections_client_channels(client_id, list(marketplaces))
        cond = Q(client_id=client_id, date__lt=time_now.date(), type__in=TIME_CONTROl_TYPE_LIST)
        processing = DataStatus.objects.tenant_db_for(client_id).filter(cond) \
            .filter(status__in=[PROCESS_STATUS])
        # check job is processing
        meta_cond = Q()
        for pk in processing.values_list('pk', flat=True):
            meta_cond.add(Q(meta__contains=dict(data_status_id=str(pk))), Q.OR)
        category_qs = get_category_job_queryset(TIME_CONTROL_CATEGORY)
        job_ids_exists = list(
            category_qs.filter(
                Q(name__icontains="time_control_process_event_is_ready_", client_id=client_id, status__in=[STARTED])
            ).filter(meta_cond).values_list('meta__data_status_id', flat=True)
        )
        processing.exclude(pk__in=job_ids_exists).update(status=READY_STATUS)
        # handler by keep DB not raise higher CPU
        processing_count = processing.count()
        logger.info(f"[pick_jobs_time_control_process_types_is_ready_workspaces][{client_id}] "
                    f"job ids exists = {job_ids_exists}, processing count = {processing_count}")
        number_job_pick = TIME_CONTROL_NUMBER_BEAT_JOB - processing_count
        if number_job_pick <= 0:
            continue
        logger.info(f"[pick_jobs_time_control_process_types_is_ready_workspaces][{client_id}] "
                    f"number data time control pick job = {number_job_pick}")
        # pick job to processing
        queryset = DataStatus.objects.tenant_db_for(client_id).filter(cond).filter(status__in=[READY_STATUS]) \
                       .order_by(F('priority').asc(nulls_last=True),
                                 'channel__time_control_priority', '-date', )[:TIME_CONTROL_NUMBER_BEAT_JOB]
        for obj in queryset:
            try:
                assert client_connections[SELLER_PARTNER_CONNECTION].get(obj.channel.name, False) is True, \
                    f"The workspace doesn't connect marketplace"
                if obj.type == INFORMED_TYPE:
                    assert client_connections[INFORMED_MARKETPLACE_CONNECTION].get(obj.channel.name, False) is True, \
                        f"The workspace doesn't setup informed"
                data_status_id = str(obj.pk)
                data = dict(
                    name=f"time_control_process_event_is_ready_{data_status_id}",
                    client_id=client_id,
                    job_name=job_name,
                    module=module,
                    method=method,
                    time_limit=None,
                    is_run_validations=False,
                    meta=dict(client_id=client_id, data_status_id=data_status_id, marketplace=obj.channel.name)
                )
                jobs_data.append(data)
            except Exception as ex:
                obj.log = str(ex)
                obj.status = IGNORE_STATUS
                obj.save()
    if len(jobs_data) > 0:
        register_list(TIME_CONTROL_CATEGORY, jobs_data)
        logger.info(f"[pick_jobs_time_control_process_types_is_ready_workspaces][{client_ids}] "
                    f"register_list app jobs completed")


@current_app.task(bind=True)
def handler_job_time_control_check_type_is_ready_workspace(self, client_id: str, **kwargs):
    """
    Time control for check data status is ready
    :param self:
    :param client_id:
    :return:
    """
    try:
        time_now = timezone.now()
        marketplaces = Channel.objects.tenant_db_for(client_id).filter(is_pull_data=True) \
            .values_list('name', flat=True)
        client_connections = get_connections_client_channels(client_id, list(marketplaces))
        queryset = DataStatus.objects.tenant_db_for(client_id) \
            .filter(client_id=client_id, status__in=[OPEN_STATUS, ERROR_STATUS], date__lt=time_now.date(),
                    type__in=TIME_CONTROl_TYPE_LIST) \
            .order_by('-date')
        for obj in queryset:
            try:
                assert client_connections[SELLER_PARTNER_CONNECTION].get(obj.channel.name, False) is True, \
                    f"The workspace doesn't connect marketplace"
                if obj.type == INFORMED_TYPE:
                    assert client_connections[INFORMED_MARKETPLACE_CONNECTION].get(obj.channel.name, False) is True, \
                        f"The workspace doesn't setup informed"
                logger.info(f'[{obj.client_id}][{obj.channel.name}][{obj.type}]'
                            f'[handler_job_time_control_check_type_is_ready_workspace] Begin check is ready event '
                            f'type ...')
                event = TIME_CONTROL_MANAGE.get(obj.type)(data_tracking=obj, marketplace=obj.channel.name, **kwargs)
                event.handler_is_ready_event()
            except Exception as ex:
                obj.log = str(ex)
                obj.status = IGNORE_STATUS
                obj.save()
    except Exception as ex:
        logger.error(f'[{self.request.id}][handler_job_time_control_check_type_is_ready_workspace][{client_id}] {ex}')
        raise ex


@current_app.task(bind=True)
def handler_time_control_process_type_is_ready_workspace(self, client_id: str, data_status_id: str, **kwargs):
    """
    Time control for process event data is ready
    :param self:
    :param client_id:
    :param data_status_id:
    :return:
    """
    try:
        data_tracking = DataStatus.objects.tenant_db_for(client_id).get(pk=data_status_id)
        logger.info(f'[{data_tracking.client_id}][{data_tracking.channel.name}][{data_tracking.type}]'
                    f'[handler_time_control_process_type_is_ready_workspace] Begin process is ready event type ...')
        event = TIME_CONTROL_MANAGE.get(data_tracking.type)(data_tracking=data_tracking, **kwargs)
        event.progress()
    except Exception as ex:
        logger.error(
            f'[{self.request.id}][handler_time_control_process_type_is_ready_workspace][{data_status_id}] {ex}')
        raise ex
