from celery import current_app
from app.core.logger import logger


class CeleryTaskManager:

    def __init__(self, task_id):
        self.__task_id = task_id

    def revoke(self):
        try:
            current_app.control.revoke(self.__task_id, terminate=True)
        except Exception as error:
            logger.error(f'[CeleryTaskManager] {error}')
            pass
