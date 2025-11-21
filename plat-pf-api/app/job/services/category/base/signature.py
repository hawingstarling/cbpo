import importlib
import logging
from abc import ABC
import json
from celery.states import REJECTED
from django.db.utils import DEFAULT_DB_ALIAS
from django.utils import timezone
from app.job.services.inspect import JobInspectManage
from app.job.services.validation import CategoryJobValidation
from app.job.utils.config import CATEGORY_MODEL

logger = logging.getLogger(__name__)


class JobSignature(ABC):
    def __init__(self):
        self.job_control_manager = JobInspectManage()

    @classmethod
    def is_valid(cls, category, job):
        logger.info(f"[{cls.__class__.__name__}][{category}][{job.pk}][is_valid] begin ...")
        validation = CategoryJobValidation(category, job).on_process().on_complete()
        status = validation.status
        msg = validation.msg
        if not status:
            CATEGORY_MODEL[category].objects.tenant_db_for(DEFAULT_DB_ALIAS).filter(pk=job.pk) \
                .update(status=REJECTED, msg=json.dumps(msg), modified=timezone.now())
        assert status is True, f"[{cls.__class__.__name__}] status is not valid, msg = {json.dumps(msg)}"

    def is_active(self, category, job):
        logger.info(f"[{self.__class__.__name__}][{category}][{job.pk}][is_active] begin ...")
        active = self.job_control_manager.is_active_in_celery(job.task_id, job.job_name, job.meta)
        if active:
            status = self.job_control_manager.get_async_result_status(job.task_id, job.job_name, job.meta)
            CATEGORY_MODEL[category].objects.tenant_db_for(DEFAULT_DB_ALIAS).filter(pk=job.pk) \
                .update(status=status, msg=f"The job already {status} celery", modified=timezone.now())
        assert active is False, f"[{self.__class__.__name__}] Already active celery"

    @classmethod
    def get_method_trigger(cls, category, job):
        method_trigger = None
        try:
            modules = importlib.import_module(job.module)
            method_trigger = getattr(modules, job.method)
        except Exception as ex:
            CATEGORY_MODEL[category].objects.tenant_db_for(DEFAULT_DB_ALIAS).filter(pk=job.pk) \
                .update(status=REJECTED, msg=f"{ex}", modified=timezone.now())
        return method_trigger

    def create(self, category, job):
        #
        logger.info(f"[{self.__class__.__name__}][{category}][{job.pk}][create] begin ...")

        self.is_valid(category, job)
        self.is_active(category, job)

        method_trigger = self.get_method_trigger(category, job)

        kwargs = job.meta
        options = dict(
            task_id=str(job.task_id),
            priority=job.priority,
            retry=job.retry,
            retry_policy=job.retry_policy,
            time_limit=job.time_limit,
            queue=job.queue,
            exchange=job.queue,
            routing_key=job.queue,
            headers=dict(category=category, category_job_id=str(job.pk))
        )
        return method_trigger.signature(None, kwargs, **options)
