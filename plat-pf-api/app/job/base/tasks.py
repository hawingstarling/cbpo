import importlib
import logging
from celery_once import QueueOnce
from celery.states import FAILURE, STARTED, SUCCESS
from django.db import DEFAULT_DB_ALIAS
# from django.utils import timezone
from celery.worker.request import Request

from app.job.utils.config import CATEGORY_MODEL

logger = logging.getLogger(__name__)


class JobCallBack(object):
    @classmethod
    def _job_category_callback(cls, job):
        try:
            callback = job.callback
            callback_type = callback["type"]
            info = callback["info"]
            if callback_type == "func":
                modules = importlib.import_module(info["module"])
                method_trigger = getattr(modules, info["method"])
                method_trigger(**info["meta"])
            elif callback_type == "delay":
                modules = importlib.import_module(info["module"])
                method_trigger = getattr(modules, info["method"])
                method_trigger.delay(**info["meta"])
            elif callback_type == "job":
                from app.job.utils.helper import register
                category = callback["category"]
                mode_run = callback["mode_run"]
                client_id = callback["client_id"]
                register(category=category, client_id=client_id, mode_run=mode_run, **info)
            else:
                pass
        except Exception as ex:
            job.msg = str(ex)
            job.status = FAILURE
            job.save()


class JobRequest(Request, JobCallBack):

    @property
    def category(self):
        return self._request_dict.get('category')

    @property
    def category_job_id(self):
        return self._request_dict.get('category_job_id')

    def on_timeout(self, soft, timeout):
        super().on_timeout(soft, timeout)
        if not soft:
            try:
                assert self.category is not None, "Category is not empty"
                assert self.category_job_id is not None, "Category Job ID is not empty"
                msg = f"A hard timeout was enforced for task timeout is {timeout} seconds"
                jobs = CATEGORY_MODEL[self.category].objects.db_manager(using=DEFAULT_DB_ALIAS).filter(
                    pk=self.category_job_id, task_id=self.task_id)
                for job in jobs:
                    job.status = FAILURE
                    job.msg = msg
                    job.save()
                    if len(job.callback) > 0:
                        self._job_category_callback(job)
            except Exception as ex:
                logger.error(f"[{self.__class__.__name__}][on_timeout] {ex}")


class TaskBasement(QueueOnce, JobCallBack):
    once = {
        'graceful': True,
        'unlock_before_run': True
    }

    Request = JobRequest

    @property
    def category(self):
        return self.request.get('category')

    @property
    def category_job_id(self):
        return self.request.get('category_job_id')

    def track_job_category(self, task_id, is_callback: bool = False, **kwargs):
        try:
            assert self.category is not None, "Category is not empty"
            assert self.category_job_id is not None, "Category Job ID is not empty"
            jobs = CATEGORY_MODEL[self.category].objects.filter(pk=self.category_job_id, task_id=task_id)
            for job in jobs:
                for attr, value in kwargs.items():
                    setattr(job, attr, value)
                job.save()
                if is_callback and len(job.callback) > 0:
                    self._job_category_callback(job)
        except Exception as ex:
            logger.error(f"[{self.__class__.__name__}][track_job_category] {ex}")

    def track_before_run(self):
        msg = f"Job begin STARTED in worker"
        self.track_job_category(task_id=self.request.id, status=STARTED, msg=msg)

    def __call__(self, *args, **kwargs):
        self.track_before_run()
        return super().__call__(*args, **kwargs)

    def run(self, *args, **kwargs):
        pass

    def on_success(self, retval, task_id, args, kwargs):
        super().on_success(retval, task_id, args, kwargs)
        self.track_job_category(task_id=task_id, is_callback=True, status=SUCCESS, msg=str(retval))

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        super().on_failure(exc, task_id, args, kwargs, einfo)
        self.track_job_category(task_id=task_id, is_callback=True, status=FAILURE, msg=str(einfo))
