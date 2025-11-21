import copy
import math
from abc import ABC
import logging
from typing import List

from celery import group
from datetime import timedelta
from celery.states import STARTED, PENDING, FAILURE, RECEIVED, REJECTED
from django.conf import settings
from django.db.models import Q, F, Count
from django.utils import timezone
from app.job.utils.config import CATEGORY_MODEL
from .signature import JobSignature
from app.job.utils.variable import MODE_RUN_SEQUENTIALLY, MODE_RUN_PARALLEL, MODE_RUN_IMMEDIATELY
from .abstract import JobAbstract
from django.db.utils import DEFAULT_DB_ALIAS

logger = logging.getLogger(__name__)


class JobClientBase(JobAbstract, ABC):
    category = None

    def __init__(self, *args, **kwargs):
        self.job_signature = JobSignature()
        self.args = args
        self.kwargs = kwargs
        self.job_ids = []
        self.time_now = timezone.now()
        self.time_filter_wait_block = self.time_now - timedelta(days=1)
        self.time_filter_started = self.time_now - timedelta(seconds=settings.CELERYD_TASK_SOFT_TIME_LIMIT)
        self.time_filter_pending_group = self.time_now - timedelta(seconds=(5 * 60))
        self.time_filter_on_clean = self.time_now - timedelta(days=15)

    def on_validate(self):
        assert self.category is not None, "Category is not empty"
        return self

    @property
    def category_model(self):
        return CATEGORY_MODEL[self.category]

    @property
    def group_id(self):
        return self.kwargs.get("group_id", None)

    @property
    def mode_run(self):
        return self.kwargs.get("mode_run", MODE_RUN_SEQUENTIALLY)

    @property
    def status_accept(self):
        return [PENDING]

    def get_client_ids_pending(self):
        cond = Q(status__in=self.status_accept)
        if self.group_id:
            cond &= Q(group_id=self.group_id)
        client_ids_pending = self.category_model.objects.tenant_db_for(DEFAULT_DB_ALIAS).filter(cond) \
            .values_list("client_id", flat=True).distinct()
        return list(set(client_ids_pending))

    def get_number_job_pick_clients(self, client_ids: List[str]):
        rs = {}
        try:
            clients_jobs_started = self.category_model.objects.tenant_db_for(DEFAULT_DB_ALIAS) \
                .filter(client_id__in=client_ids, mode_run=MODE_RUN_SEQUENTIALLY, status__in=[RECEIVED, STARTED]) \
                .values("client_id") \
                .annotate(num_started=Count("id"))
            total_clients = len(client_ids)
            worker_default_config = self.job_signature.job_control_manager.get_total_worker_category_info(self.category)
            logger.info(
                f"[{self.__class__.__name__}][{self.category}][get_number_job_pick_clients] "
                f"worker_default_config = {worker_default_config}"
            )
            celery_job_concurrency_total = worker_default_config["total_worker"] \
                                           * worker_default_config["max_concurrency"]
            celery_job_standard_total = total_clients * worker_default_config["max_concurrency"]
            if celery_job_standard_total <= celery_job_concurrency_total:
                num_job_default = worker_default_config["max_concurrency"]
            else:
                num_job_default = math.ceil(celery_job_concurrency_total / total_clients)
            for item in clients_jobs_started:
                num_job_pick = num_job_default - item["num_started"]
                if num_job_pick < 0:
                    num_job_pick = 0
                rs.update({item["client_id"]: num_job_pick})
            for client_id in client_ids:
                if client_id in rs.keys():
                    continue
                rs.update({client_id: num_job_default})
            logger.info(f"[{self.__class__.__name__}][get_number_job_pick_clients] result = {rs}")
        except Exception as ex:
            logger.error(f"[{self.__class__.__name__}][get_number_job_pick_clients] {ex}")
            rs = {}
        return rs

    def create_jobs_signature(self, sub_jobs):
        for items in sub_jobs:
            for job in items:
                try:
                    yield self.job_signature.create(self.category, job)
                    self.job_ids.append(job.pk)
                except Exception as ex:
                    logger.error(f"[{self.__class__.__name__}][create_jobs_signature][{job.pk}] {ex}")

    def on_process(self):
        client_ids = self.get_client_ids_pending()
        if self.mode_run == MODE_RUN_PARALLEL:
            self.on_process_run_parallel(client_ids)
        elif self.mode_run == MODE_RUN_IMMEDIATELY:
            self.on_process_run_immediately(client_ids)
        else:
            number_job_pick_clients = self.get_number_job_pick_clients(client_ids)
            self.on_process_run_sequentially(client_ids, number_job_pick_clients)
        return self

    def on_process_run_parallel(self, client_ids):
        sub_jobs = []
        for client_id in client_ids:
            cond = Q(client_id=client_id, status__in=self.status_accept, group_id=self.group_id,
                     mode_run=MODE_RUN_PARALLEL)
            sub_jobs.append(self.category_model.objects \
                            .filter(cond) \
                            .order_by("created", "modified"))
        groups = group(self.create_jobs_signature(sub_jobs))
        groups.apply_async()
        logger.info(f"[{self.__class__.__name__}][on_process_run_parallel] run {len(self.job_ids)} jobs")

    def on_process_run_immediately(self, client_ids):
        sub_jobs = []
        for client_id in client_ids:
            cond = Q(client_id=client_id, status__in=self.status_accept, mode_run=MODE_RUN_IMMEDIATELY)
            sub_jobs.append(self.category_model.objects \
                            .filter(cond) \
                            .order_by("created", "modified"))
        for tasks_signature in self.create_jobs_signature(sub_jobs):
            tasks_signature.apply_async()
        logger.info(f"[{self.__class__.__name__}][on_process_run_immediately] run {len(self.job_ids)} jobs")

    def on_process_run_sequentially(self, client_ids, number_job_pick_clients):
        sub_jobs = []
        for client_id in client_ids:
            number_job_pick_client = number_job_pick_clients.get(client_id, 0)
            if number_job_pick_client == 0:
                continue
            cond = Q(client_id=client_id, status__in=self.status_accept, mode_run=MODE_RUN_SEQUENTIALLY)
            sub_jobs.append(self.category_model.objects.tenant_db_for(DEFAULT_DB_ALIAS).filter(cond) \
                            .order_by(F("priority").asc(nulls_last=True),
                                      "created", "modified")[:number_job_pick_client])
        for tasks_signature in self.create_jobs_signature(sub_jobs):
            tasks_signature.apply_async()
        logger.info(f"[{self.__class__.__name__}][on_process_run_sequentially] run {len(self.job_ids)} jobs")

    def on_complete(self, acks_late: bool = False):
        logger.info(f"[{self.__class__.__name__}][on_complete] begin ....")
        if self.job_ids:
            self.category_model.objects.tenant_db_for(DEFAULT_DB_ALIAS) \
                .filter(id__in=self.job_ids).update(status=RECEIVED, modified=self.time_now)
            #
            self.job_ids = []
        if acks_late:
            self.on_complete_max_recursive()
            self.on_complete_acks_late()

    def marked_completed_pending(self, obj):
        try:
            logger.info(f"[{self.__class__.__name__}][marked_completed_pending][{obj.pk}] begin ...")
            assert obj.mode_run not in [MODE_RUN_PARALLEL], f"Reject the Object mode run parallel revert to pending"
            cond = Q(
                client_id=obj.client_id,
                name=obj.name,
                job_name=obj.job_name,
                module=obj.module,
                method=obj.method,
                status__in=[PENDING, RECEIVED, STARTED]
            ) & ~Q(pk=obj.pk)
            assert not self.category_model.objects.filter(cond).exists(), f"another job pending in category"
            obj.status = PENDING
            if obj.mode_run in [MODE_RUN_IMMEDIATELY]:
                obj.priority = 3
            obj.mode_run = MODE_RUN_SEQUENTIALLY
            obj.is_run_validations = True
        except Exception as ex:
            obj.status = REJECTED
            obj.msg = str(ex)
            logger.error(f"[{self.__class__.__name__}][marked_completed_pending][{obj.pk}] {ex}")
        obj.modified = self.time_now

    def on_complete_max_recursive(self):
        try:
            logger.info(f"[{self.__class__.__name__}][on_complete_max_recursive] Begin ....")
            cond = Q(created__gte=self.time_filter_on_clean,
                     status=FAILURE,
                     recursive__gte=0,
                     recursive__lt=F("max_recursive"))
            # Timeout
            cond |= Q(modified__gte=self.time_filter_wait_block,
                      msg__icontains="A hard timeout was enforced for task timeout",
                      status=FAILURE)
            # waits for ShareLock
            cond |= Q(modified__gte=self.time_filter_wait_block, msg__icontains="waits for ShareLock on transaction",
                      status=FAILURE)
            qs = self.category_model.objects.tenant_db_for(DEFAULT_DB_ALIAS).filter(cond)
            num_records = qs.count()
            logger.info(f"[{self.__class__.__name__}][on_complete_max_recursive] reopen {num_records} items")
            if num_records == 0:
                return
            qs = qs.order_by(F("priority").asc(nulls_last=True), "created", "modified")
            objs = []
            for item in qs:
                try:
                    obj = copy.deepcopy(item)
                    if 0 < obj.max_recursive == obj.recursive:
                        continue
                    self.marked_completed_pending(obj)
                    if obj.status == PENDING:
                        self.job_signature.job_control_manager.async_result_forget(obj.task_id, obj.job_name, obj.meta)
                        if obj.recursive < obj.max_recursive:
                            obj.recursive += 1
                            obj.msg = "Job reopen by max recursive"
                        else:
                            if obj.msg is not None and "A hard timeout was enforced for task timeout" in obj.msg:
                                obj.time_limit = F("time_limit") + 3600  # increase 1 hour
                                obj.msg = "Job reopen by time limit"
                    objs.append(obj)
                    self.on_complete_acks_late_callback(item)
                except Exception as ex:
                    logger.error(f"[{self.__class__.__name__}][on_complete_max_recursive] {item.pk} {ex}")
            if len(objs) > 0:
                logger.info(
                    f"[{self.__class__.__name__}][on_complete_max_recursive] Reopen {len(objs)} to PENDING jobs")
                self.category_model.objects.tenant_db_for(DEFAULT_DB_ALIAS) \
                    .bulk_update(objs,
                                 fields=["status", "group_id", "mode_run", "msg", "recursive", "is_run_validations",
                                         "modified"])
        except Exception as ex:
            logger.error(f"[{self.__class__.__name__}][on_complete_max_recursive] {ex}")

    def on_complete_acks_late_callback(self, item):
        pass

    def on_complete_acks_late(self):
        cond = Q(status=RECEIVED)
        cond |= Q(modified__lte=self.time_filter_pending_group, mode_run__in=[MODE_RUN_PARALLEL, MODE_RUN_IMMEDIATELY],
                  status=PENDING)
        cond |= Q(modified__lte=self.time_filter_started, status=STARTED)
        #
        qs = self.category_model.objects.tenant_db_for(DEFAULT_DB_ALIAS).filter(cond)
        num_records = qs.count()
        logger.info(f"[{self.__class__.__name__}][on_complete_acks_late] reopen {num_records} items")
        if num_records == 0:
            return
        qs = qs.order_by(F("priority").asc(nulls_last=True), "created", "modified")
        msg = f"Job acks late in worker"
        objs = []
        for obj in qs:
            try:
                status = self.job_signature.job_control_manager.get_async_result_status(obj.task_id, obj.job_name,
                                                                                        obj.meta)
                obj.status = status
                obj.msg = msg
                if obj.status == PENDING:
                    self.marked_completed_pending(obj)
                objs.append(obj)
                self.on_complete_acks_late_callback(obj)
            except Exception as ex:
                logger.error(f"[{self.__class__.__name__}][on_complete_acks_late] {obj.pk} {ex}")
        if len(objs) > 0:
            logger.info(f"[{self.__class__.__name__}][on_complete_acks_late] Reopen {len(objs)} to PENDING jobs")
            self.category_model.objects.tenant_db_for(DEFAULT_DB_ALIAS) \
                .bulk_update(objs, fields=["status", "group_id", "priority", "mode_run", "msg", "is_run_validations",
                                           "modified"])

    def on_clean(self):
        logger.info(f"[{self.__class__.__name__}][on_clean] begin ...")
        self.category_model.objects.tenant_db_for(DEFAULT_DB_ALIAS) \
            .filter(created__date__lte=self.time_filter_on_clean.date()).exclude(status__in=[PENDING, STARTED]).delete()
