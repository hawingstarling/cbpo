import copy
import logging
import uuid

from celery.result import AsyncResult
from django.db.models import Q
from celery.states import PENDING, IGNORED, STARTED, REVOKED, RECEIVED, FAILURE
from django.core.exceptions import MultipleObjectsReturned
from django.db.utils import DEFAULT_DB_ALIAS
from django.utils import timezone
from .variable import COMMUNITY_CATEGORY, IMPORT_CATEGORY, BULK_CATEGORY, SYNC_ANALYSIS_CATEGORY, TIME_CONTROL_CATEGORY, \
    SYNC_DATA_SOURCE_CATEGORY, MODE_RUN_SEQUENTIALLY, MODE_RUN_PARALLEL, MODE_RUN_IMMEDIATELY, \
    DATA_SOURCE_CALCULATION_CATEGORY, SELLING_PARTNER_CATEGORY, LIST_JOB_CATEGORY, STATS_REPORT_CATEGORY, \
    COGS_MAPPING_CATEGORY
from app.job.utils.config import CATEGORY_MODEL, CATEGORY_PRIORITY_CONFIG, CATEGORY_TIME_LIMIT_CONFIG
from ..models import JobConfig, TaskRouteConfig
from ..services.category.cogs_mapping import COGSMappingJob
from ..services.category.selling_partner import SellingPartnerJob
from ..services.inspect import JobInspectManage
from ...core.celery_task_manger import CeleryTaskManager

logger = logging.getLogger(__name__)
job_config_queryset = JobConfig.objects.all()
task_routing_config_queryset = TaskRouteConfig.objects.all()
job_control_manager = JobInspectManage()


def register(category: str, client_id: str, task_id: str = None, mode_run: str = MODE_RUN_SEQUENTIALLY, **kwargs):
    logger.info(f"[{category}][{client_id}][register] begin ...")
    obj, created = init_category_job_instance(category=category, client_id=client_id, task_id=task_id,
                                              mode_run=mode_run,
                                              **kwargs)
    if not obj:
        logger.warning(f"[{category}][{client_id}][register] job conditions already register")
        return obj
    objs_insert = []
    objs_update = []
    if created:
        objs_insert.append(obj)
    else:
        objs_update.append(obj)
    register_category_bulk(category, objs_insert, objs_update, mode_run=mode_run)
    return obj


def init_category_job_instance(category: str, client_id: str, task_id: str = None,
                               mode_run: str = MODE_RUN_SEQUENTIALLY, **kwargs):
    obj = None
    created = True
    try:
        cond = Q(
            client_id=client_id,
            name=kwargs["name"],
            job_name=kwargs["job_name"],
            module=kwargs["module"],
            method=kwargs["method"],
            meta=kwargs["meta"],
            status__in=[PENDING, RECEIVED, STARTED],
        )
        find = CATEGORY_MODEL[category].objects.get(cond)
        if find.status == PENDING and mode_run != MODE_RUN_SEQUENTIALLY \
                and find.status == MODE_RUN_SEQUENTIALLY:
            obj = find
            obj.mode_run = mode_run
            if mode_run == MODE_RUN_PARALLEL and obj.group_id is None:
                obj.group_id = kwargs['group_id']
            obj.modified = timezone.now()
            created = False
    except CATEGORY_MODEL[category].DoesNotExist:
        obj = CATEGORY_MODEL[category](client_id=client_id, task_id=task_id, mode_run=mode_run, **kwargs)
        if task_id is None:
            obj.task_id = obj.pk
        obj.priority = kwargs.get("priority", get_priority_category_job_config(category, kwargs["job_name"]))
        obj.time_limit = kwargs.get("time_limit", get_time_limit_category_job_config(category, kwargs["job_name"]))
        obj.retry = kwargs.get("retry", get_retry_category_job_config(category, kwargs["job_name"]))
        obj.retry_policy = kwargs.get("retry_policy",
                                      get_retry_policy_category_job_config(category, kwargs["job_name"]))
        obj.max_recursive = kwargs.get("max_recursive",
                                       get_max_recursive_category_job_config(category, kwargs["job_name"]))
        obj.validations = kwargs.get("validations",
                                     get_validations_category_job_config(category, kwargs["job_name"]))
        obj.is_run_validations = kwargs.get("is_run_validations",
                                            get_is_run_validations_category_job_config(category, kwargs["job_name"]))
        task_queue_config = get_task_routing_config(category, obj.module)
        obj.queue = task_queue_config['queue']
        obj.exchange = task_queue_config['exchange']
        obj.routing_key = task_queue_config['routing_key']
    except MultipleObjectsReturned:
        logger.info(
            f"[init_category_job_instance][{category}][{client_id}][{task_id}] Job with conditions {kwargs} still in running ...")
    except Exception as ex:
        logger.error(f"[init_category_job_instance][{category}][{client_id}][{task_id}][{kwargs}] {ex}")
    return obj, created


def consolidate_mode_run_category(category: str, mode_run: str, total_jobs_request: int):
    try:
        assert mode_run == MODE_RUN_IMMEDIATELY, f"Verify switch mode run must in [{MODE_RUN_IMMEDIATELY}]"
        worker_default_config = job_control_manager.get_total_worker_category_info(category)
        logger.debug(f"[{category}][register_list] worker_default_config = {worker_default_config}")
        celery_job_concurrency_total = worker_default_config["total_worker"] \
                                       * worker_default_config["max_concurrency"]
        total_jobs_started = CATEGORY_MODEL[category].total_jobs_started()
        if total_jobs_started > celery_job_concurrency_total or total_jobs_request > celery_job_concurrency_total:
            mode_run = MODE_RUN_SEQUENTIALLY
            logger.info(f"[{category}][register_list] "
                        f"mode run {mode_run} switch to sequentially because total jobs started category = {category} "
                        f"greater than {celery_job_concurrency_total} that category accepted")
    except Exception as ex:
        logger.error(f"[{category}][register_list][{mode_run}] {ex}")
    return mode_run


def register_list(category: str, data: list = [], mode_run: str = MODE_RUN_SEQUENTIALLY):
    if len(data) == 0:
        logger.info(f"[{category}] request register list data empty")
        return
    logger.info(f"[{category}][register_list] begin ...")
    objs_insert = []
    objs_update = []
    group_id = None
    mode_run = consolidate_mode_run_category(category, mode_run, len(data))
    if mode_run == MODE_RUN_PARALLEL:
        group_id = uuid.uuid4()
    for item in data:
        obj, created = init_category_job_instance(category=category, group_id=group_id, mode_run=mode_run, **item)
        if obj:
            if created:
                objs_insert.append(obj)
            else:
                objs_update.append(obj)
    if objs_insert or objs_update:
        register_category_bulk(category, objs_insert, objs_update, mode_run)
    return objs_insert, objs_update


def get_category_services_config():
    from app.job.services.category.bulk_job import BulkJob
    from app.job.services.category.community import CommunityJob
    from app.job.services.category.import_job import ImportJob
    from app.job.services.category.sync_analysis import SyncAnalysisJob
    from app.job.services.category.time_control import TimeControlJob
    from app.job.services.category.sync_data_source import SyncDataSourceJob
    from app.job.services.category.data_source_calculation import DataSourceCalculationJob
    from app.job.services.category.stats_report import StatsReportJob
    return {
        COMMUNITY_CATEGORY: CommunityJob,
        IMPORT_CATEGORY: ImportJob,
        BULK_CATEGORY: BulkJob,
        SYNC_ANALYSIS_CATEGORY: SyncAnalysisJob,
        TIME_CONTROL_CATEGORY: TimeControlJob,
        SYNC_DATA_SOURCE_CATEGORY: SyncDataSourceJob,
        DATA_SOURCE_CALCULATION_CATEGORY: DataSourceCalculationJob,
        SELLING_PARTNER_CATEGORY: SellingPartnerJob,
        STATS_REPORT_CATEGORY: StatsReportJob,
        COGS_MAPPING_CATEGORY: COGSMappingJob,
    }


def register_category_bulk(category, objs_insert: [], objs_update: [], mode_run: str = MODE_RUN_SEQUENTIALLY):
    if objs_insert:
        objs_insert = CATEGORY_MODEL[category].objects.tenant_db_for(DEFAULT_DB_ALIAS) \
            .bulk_create(objs_insert, ignore_conflicts=True)
    if objs_update:
        CATEGORY_MODEL[category].objects.tenant_db_for(DEFAULT_DB_ALIAS) \
            .bulk_update(objs_update, fields=['mode_run', 'group_id', 'modified'])
    if mode_run == MODE_RUN_PARALLEL:
        if objs_insert:
            group_id = objs_insert[0].group_id
        else:
            group_id = objs_update[0].group_id
        get_category_services_config()[category](group_id=group_id,
                                                 mode_run=mode_run).on_validate().on_process().on_complete()
    elif mode_run == MODE_RUN_IMMEDIATELY:
        get_category_services_config()[category](mode_run=mode_run).on_validate().on_process().on_complete()


def register_clients_method(category: str, client_ids: list, data: dict = {}, mode_run: str = MODE_RUN_SEQUENTIALLY):
    assert len(client_ids) > 0, "Client IDS request is not empty"
    if not data:
        logger.info(f"[{category}][{client_ids}] request register list data empty")
        return
    logger.info(f"[{category}][{client_ids}][register_clients_method] begin ...")
    objs_insert = []
    objs_update = []
    group_id = None
    if mode_run == MODE_RUN_PARALLEL:
        group_id = uuid.uuid4()
    for client_id in client_ids:
        item_data = copy.deepcopy(data)
        meta_update = dict(client_id=str(client_id))
        if "meta" not in item_data:
            item_data.update(dict(meta=meta_update))
        else:
            item_data["meta"].update(meta_update)
        obj, created = init_category_job_instance(category=category, client_id=client_id, group_id=group_id,
                                                  mode_run=mode_run,
                                                  **item_data)
        if obj:
            if created:
                objs_insert.append(obj)
            else:
                objs_update.append(obj)
    if objs_insert or objs_update:
        register_category_bulk(category, objs_insert, objs_update, mode_run=mode_run)
    return objs_insert, objs_update


def ignore_category_job(category, task_ids: [] = [], **cond):
    logger.info(f"[{category}][ignore_category_job] begin ...")
    qs = CATEGORY_MODEL[category].objects.tenant_db_for(DEFAULT_DB_ALIAS)
    if task_ids:
        logger.info(f"[{category}][ignore_category_job] task ids = {task_ids}")
        qs = qs.filter(task_id__in=task_ids, status=PENDING)
    elif cond:
        logger.info(f"[{category}][ignore_category_job] cond = {cond}")
        qs = qs.filter(**cond, status=PENDING)
    else:
        return

    for obj in qs.iterator():
        try:
            AsyncResult(obj.task_id).forget()
            job_control_manager.clear_queue_once_lock_key(obj.job_name, obj.meta)
            logger.info(f"[{category}][ignore_category_job] task id = {obj.task_id} completed")
        except Exception as ex:
            logger.error(f"[{category}][ignore_category_job] {ex}")
    qs.update(status=IGNORED)


def revoked_category_job(category, task_ids: [] = [], **cond):
    logger.info(f"[{category}][revoked_category_job] begin ...")
    qs = CATEGORY_MODEL[category].objects.tenant_db_for(DEFAULT_DB_ALIAS)
    if task_ids:
        logger.info(f"[{category}][revoked_category_job] task ids = {task_ids}")
        qs = qs.filter(task_id__in=task_ids, status__in=[PENDING, STARTED, RECEIVED, FAILURE])
    elif cond:
        logger.info(f"[{category}][revoked_category_job] cond = {cond}")
        qs = qs.filter(**cond, status__in=[PENDING, STARTED, RECEIVED, FAILURE])
    else:
        return

    for obj in qs.iterator():
        if obj.status in [PENDING, FAILURE]:
            continue
        try:
            CeleryTaskManager(obj.task_id).revoke()
            job_control_manager.clear_queue_once_lock_key(obj.job_name, obj.meta)
            logger.info(f"[{category}][revoked_category_job] task id = {obj.task_id} completed")
        except Exception as ex:
            logger.error(f"[{category}][revoked_category_job] {ex}")
    qs.update(status=REVOKED)


def get_priority_category_job_config(category, job_name):
    try:
        priority = job_config_queryset.get(category=category, name=job_name).priority
    except Exception as ex:
        priority = job_config_queryset.get(category=category, name="default").priority
    return priority


def get_time_limit_category_job_config(category, job_name):
    try:
        time_limit = job_config_queryset.get(category=category, name=job_name).time_limit
    except Exception as ex:
        time_limit = job_config_queryset.get(category=category, name="default").time_limit
    return time_limit


def get_retry_category_job_config(category, job_name):
    try:
        retry = job_config_queryset.get(category=category, name=job_name).retry
    except Exception as ex:
        retry = job_config_queryset.get(category=category, name="default").retry
    return retry


def get_retry_policy_category_job_config(category, job_name):
    try:
        retry_policy = job_config_queryset.get(category=category, name=job_name).retry_policy
    except Exception as ex:
        retry_policy = job_config_queryset.get(category=category, name="default").retry_policy
    return retry_policy


def get_max_recursive_category_job_config(category, job_name):
    try:
        val = job_config_queryset.get(category=category, name=job_name).max_recursive
    except Exception as ex:
        val = job_config_queryset.get(category=category, name="default").max_recursive
    return val


def get_validations_category_job_config(category, job_name):
    try:
        val = job_config_queryset.get(category=category, name=job_name).validations
    except Exception as ex:
        val = job_config_queryset.get(category=category, name="default").validations
    return val


def get_is_run_validations_category_job_config(category, job_name):
    try:
        val = job_config_queryset.get(category=category, name=job_name).is_run_validations
    except Exception as ex:
        val = job_config_queryset.get(category=category, name="default").is_run_validations
    return val


def get_task_routing_config(category: str, module: str):
    try:
        val = task_routing_config_queryset.get(task_path=f"{module}.*", enabled=True).route.queue_info
    except Exception as ex:
        logger.error(f"[get_task_routing_config][not_found_task_patch] {ex}")
        try:
            val = task_routing_config_queryset.get(task_path=category, enabled=True).route.queue_info
        except Exception as err:
            logger.error(f"[get_task_routing_config][not_found_category] {err}")
            val = {
                "queue": "celery",
                "exchange": "celery(direct)",
                "routing_key": "celery"
            }
    return val


def create_job_config_record_settings():
    try:
        objs = []
        for category in LIST_JOB_CATEGORY:
            keys = list(CATEGORY_PRIORITY_CONFIG[category].keys()) + list(CATEGORY_TIME_LIMIT_CONFIG[category].keys())
            for key in keys:
                priority = CATEGORY_PRIORITY_CONFIG[category].get(key, CATEGORY_PRIORITY_CONFIG[category]['default'])
                time_limit = CATEGORY_TIME_LIMIT_CONFIG[category].get(key,
                                                                      CATEGORY_TIME_LIMIT_CONFIG[category]['default'])
                obj = JobConfig(name=key, category=category, priority=priority, time_limit=time_limit)
                objs.append(obj)
        JobConfig.objects.bulk_create(objs, ignore_conflicts=True)
    except Exception as ex:
        logger.error(f"[create_record_settings] {ex}")


def get_category_job_queryset(category: str):
    return CATEGORY_MODEL[category].objects.tenant_db_for(DEFAULT_DB_ALIAS)
