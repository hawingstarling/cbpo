import logging

from celery import current_app
from app.financial.services.activity import ActivityService

logger = logging.getLogger(__name__)


@current_app.task(bind=True)
def create_activity_by_action(self, client_id: str, user_id: str, action: str, data: dict = {}):
    logger.info(f'[Task][create_activity_sync_client_ps][{self.request.id}][{client_id}][{action}]: Begin ....')
    service = ActivityService(client_id=client_id, user_id=user_id)
    service.create_activity_by_action(action, **data)
    logger.info(f'[Task][create_activity_sync_client_ps][{self.request.id}][{client_id}][{action}]: Completed')
