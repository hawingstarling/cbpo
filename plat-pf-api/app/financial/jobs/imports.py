import logging

from celery import current_app
from app.financial.services.activity import ActivityService

logger = logging.getLogger(__name__)


@current_app.task(bind=True)
def create_activity_import_sale_data(self, client_id: str = None, user_id: str = None):
    try:
        ActivityService(client_id=client_id, user_id=user_id).create_activity_import_sale_data()
    except Exception as ex:
        logger.error(f'[Task][{self.request.id}][create_activity_import_sale_data][{client_id}]: {ex}')


@current_app.task(bind=True)
def create_activity_sync_client_ps(self, client_id: str = None, user_id: str = None):
    try:
        ActivityService(client_id=client_id, user_id=user_id).create_activity_sync_client_ps()
    except Exception as ex:
        logger.error(f'[Task][{self.request.id}][create_activity_sync_client_ps][{client_id}]: {ex}')
