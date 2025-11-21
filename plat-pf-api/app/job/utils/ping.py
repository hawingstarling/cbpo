import logging
from celery import current_app

logger = logging.getLogger(__name__)


@current_app.task(priority=0, bind=True)
def job_ping_request(self, client_id, category):
    logger.info(f"[{self.request.id}][{category}][{client_id}] Pong")
