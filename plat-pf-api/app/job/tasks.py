from .models import JobConfig
from .services.inspect import JobInspectManage
from .utils.helper import get_category_services_config
from .utils.variable import LIST_JOB_CATEGORY
from ..job.utils.ping import *

logger = logging.getLogger(__name__)


@current_app.task(bind=True, priority=0)
def process_task_route_config(self):
    logger.info(f"[Scheduler][{self.request.id}][process_task_route_config] Begin ...")
    job_control_manager = JobInspectManage()
    job_control_manager.get_celery_route_worker_config()


@current_app.task(bind=True, priority=0)
def process_scheduled_job_category(self):
    logger.info(f"[Scheduler][{self.request.id}][process_scheduled_job_category] Begin ...")
    for category in LIST_JOB_CATEGORY:
        try:
            config = JobConfig.objects.get(category=category, name="default")
            if config.disabled_sequentially:
                logger.info(f"[Scheduler][process_scheduled_job_category][{category}]"
                            f" disabled job pending sequentially")
                continue
            logger.info(f"[Scheduler][process_scheduled_job_category] start beat job category {category} ...")
            get_category_services_config()[category]().on_validate().on_process().on_complete(acks_late=True)
        except Exception as ex:
            logger.error(f"[Scheduler][process_scheduled_job_category][{category}] {ex}")


@current_app.task(bind=True)
def clean_scheduled_job_category(self):
    logger.info(f"[Scheduler][{self.request.id}][process_scheduled_job_category] Begin ...")
    for category in LIST_JOB_CATEGORY:
        logger.info(f"[Scheduler][clean_scheduled_job_category] start clean category {category} ...")
        get_category_services_config()[category]().on_clean()
