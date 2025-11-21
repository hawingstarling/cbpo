import logging
from celery.result import AsyncResult
from django.db.utils import DEFAULT_DB_ALIAS
from django.utils import timezone
from celery import current_app
from celery.app.trace import FAILURE
from celery.states import SUCCESS
from app.job.utils.config import CATEGORY_MODEL

logger = logging.getLogger(__name__)


@current_app.task(priority=0, bind=True)
def on_success_job_category(self, result, job_id, category):
    logger.info(
        f"[on_success_job_category][{self.request.id}][{category}] job id {job_id} status is updating ....")
    logger.info(f"[on_success_job_category][{self.request.id}] result {result}")
    CATEGORY_MODEL[category].objects.tenant_db_for(DEFAULT_DB_ALIAS).filter(pk=job_id).update(status=SUCCESS,
                                                                                              modified=timezone.now())


@current_app.task(priority=0, bind=True)
def on_failure_job_category(self, job_id, category):
    logger.info(f"[on_failure_job_category][{self.request.id}][{category}] job id {job_id} status is updating ....")
    try:
        result = AsyncResult(job_id)
        exc = result.get(propagate=False)
        msg = f"Task {job_id} raised exception: {exc!r}\n{result.traceback!r}"
    except Exception as ex:
        msg = f"Task {job_id} raised exception: can't detect error"
    CATEGORY_MODEL[category].objects.tenant_db_for(DEFAULT_DB_ALIAS).filter(pk=job_id).update(status=FAILURE, msg=msg,
                                                                                              modified=timezone.now())
