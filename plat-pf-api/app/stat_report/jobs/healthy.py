import logging
from celery import current_app
from app.stat_report.services.healthy import Healthy

logger = logging.getLogger(__name__)


@current_app.task(bind=True)
def health_check_client_task(self, client_id: str):
    logger.info(f"[{self.request.id}][health_check_task] Begin healthy check task ...")
    Healthy(client_id=client_id).process()