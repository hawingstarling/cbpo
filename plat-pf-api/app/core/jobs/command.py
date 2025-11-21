import importlib

from celery import current_app
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@current_app.task(bind=True)
def run_command_by_celery(self, module: str, kwargs: dict = {}):
    logger.info(f"[{module}][{kwargs}][{self.request.id}] start ...")
    modules = importlib.import_module(module)
    command = getattr(modules, 'Command')()
    command.handle(**kwargs)
