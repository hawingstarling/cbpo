from __future__ import absolute_import, unicode_literals

import logging
import os

from celery import Celery
# set the default Django settings module for the "celery" program.
from celery.signals import after_setup_logger
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
app = Celery("plat-pf-api", task_cls="app.job.base.tasks:TaskBasement")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace="CELERY" means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# @TODO: This is add to celery v5.3.4, future when upgrade python/celery need check on this
# WARNING - /usr/local/lib/python3.10/site-packages/celery/worker/consumer/consumer.py:507:
# CPendingDeprecationWarning: The broker_connection_retry configuration setting will no longer determine
# whether broker connection retries are made during startup in Celery 6.0 and above.
# If you wish to retain the existing behavior for retrying connections on startup,
# you should set broker_connection_retry_on_startup to True.
app.conf.broker_connection_retry_on_startup = True

app.conf.ONCE = {
    "backend": "celery_once.backends.Redis",
    "settings": {
        "url": settings.BROKER_URL,
        "default_timeout": 60 * 60
    }
}

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


# handler write logging celery to logs.log
@after_setup_logger.connect
def setup_loggers(*args, **kwargs):
    logger = logging.getLogger()
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # StreamHandler
    sh = logging.StreamHandler()
    sh.setFormatter(formatter)
    logger.addHandler(sh)

    # FileHandler
    fh = logging.FileHandler("logs/logs.log")
    fh.setFormatter(formatter)
    logger.addHandler(fh)


@app.task(bind=True)
def debug_task(self):
    print("Celery Request: {0!r}".format(self.request))
