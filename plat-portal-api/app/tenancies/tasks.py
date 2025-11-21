from app.core.logger import logger
from celery import current_app
from app.tenancies.models import User
from app.tenancies.activity_services import ActivityService


@current_app.task(bind=True)
def log_activity_task(self, user_id: str, action: str, data: dict, **kwargs):

    logger.info(f"[{self.__class__.__name__}] user {user_id} {action.lower().replace('_', ' ')} Begin ...")
    user = User.objects.get(pk=user_id)
    ActivityService.create_activity(user=user, action=action, data=data)

    logger.info(f"[{self.__class__.__name__}] user {user_id} {action.lower().replace('_', ' ')} End")
