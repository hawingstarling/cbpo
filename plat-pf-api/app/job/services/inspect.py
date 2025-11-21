import logging
from celery.states import STARTED, PENDING, RECEIVED
from celery_once.helpers import queue_once_key
from django.conf import settings
from celery.result import AsyncResult
from celery import current_app
import redis
from django.db.models import Q
from django.db.utils import DEFAULT_DB_ALIAS

from app.job.models import RouteConfig, RouteWorkerTrack, TaskRouteConfig
from app.job.utils.variable import ROUTE_WORKER_STOPPED_STATUS, ROUTE_WORKER_STARTED_STATUS

logger = logging.getLogger(__name__)


class JobInspectManage(object):
    def __init__(self):
        self._task_id_active = None
        self.redis_client = redis.Redis.from_url(settings.USER_CLIENT_REDIS_CHANNEL)
        self.inspect = current_app.control.inspect()

    @property
    def task_id_active(self):
        return self._task_id_active

    def get_host_worker_current(self):
        try:
            return self.inspect.ping().keys()
        except Exception as ex:
            logger.error(f"[get_host_worker] {ex}")
        return {}

    def get_celery_route_worker_config(self):
        worker_ids = []
        try:
            actives = self.inspect.active_queues()
            for k, val in actives.items():
                worker_ids.append(k)
                try:
                    route = val[0]
                    queue = route['name']
                    exchange = f"{route['exchange']['name']}({route['exchange']['type']})"
                    routing_key = route["routing_key"]
                    route, _ = RouteConfig.objects.tenant_db_for(DEFAULT_DB_ALIAS) \
                        .get_or_create(queue=queue, exchange=exchange, routing_key=routing_key)
                    RouteWorkerTrack.objects.tenant_db_for(DEFAULT_DB_ALIAS) \
                        .update_or_create(worker_id=k, route=route, defaults=dict(status=ROUTE_WORKER_STARTED_STATUS))
                except Exception as ex:
                    logger.error(f"[{self.__class__.__name__}][get_config_celery_route_worker_config][{k}] {ex}")
            if worker_ids:
                RouteWorkerTrack.objects.tenant_db_for(DEFAULT_DB_ALIAS) \
                    .filter(~Q(worker_id__in=worker_ids)).update(status=ROUTE_WORKER_STOPPED_STATUS)
        except Exception as ex:
            logger.error(f"[{self.__class__.__name__}][get_config_celery_route_worker_config] {ex}")

    def get_total_worker_category_info(self, category):
        try:
            vals = TaskRouteConfig.objects.tenant_db_for(DEFAULT_DB_ALIAS) \
                .get(task_path=category, enabled=True).route.total_worker_info
        except Exception as ex:
            logger.error(f"[{self.__class__.__name__}][get_config_celery_worker_default] {ex}")
            vals = {
                "total_worker": 0,
                "max_concurrency": 0
            }
        return vals

    def get_async_result_status(self, task_id, job_name: str = None, kwargs: dict = {}):
        try:
            res = AsyncResult(task_id)
            status = res.status
            if status != STARTED and self.is_queue_redis(job_name, kwargs):
                status = RECEIVED
            else:
                status = self.is_active_in_worker_celery(task_id, status, job_name, kwargs)
            return status
        except Exception as ex:
            logger.error(f"[get_async_result_status][{task_id}] {ex}")
        return PENDING

    def is_active_in_worker_celery(self, task_id, status, job_name, kwargs):
        try:
            if status == STARTED:
                res = self.get_async_result_result(task_id)
                host_worker_current = self.get_host_worker_current()
                assert len(host_worker_current) > 0, "Celery worker maybe restart"
                logger.info(f"[{task_id}][is_active_in_worker_celery] {host_worker_current} {res}")
                if res.get('hostname') not in host_worker_current:
                    self.async_result_forget(task_id, job_name, kwargs)
                    status = PENDING
        except Exception as ex:
            logger.warning(f"[{task_id}][is_active_in_worker_celery] {ex}")
            status = PENDING
        return status

    def get_async_result_result(self, task_id):
        try:
            res = AsyncResult(task_id)
            return res.result
        except Exception as ex:
            logger.error(f"[get_async_result_result][{task_id}] {ex}")
        return None

    def is_queue_redis(self, job_name, kwargs):
        try:
            key = queue_once_key(job_name, kwargs)
            return self.redis_client.get(key) is not None
        except Exception as ex:
            logger.error(f"[{job_name}][is_queue_redis] {ex}")
        return False

    def async_result_forget(self, task_id, job_name, kwargs):
        try:
            AsyncResult(task_id).forget()
            self.clear_queue_once_lock_key(job_name, kwargs)
        except Exception as ex:
            logger.error(f"[{job_name}][async_result_forger] {ex}")

    def clear_queue_once_lock_key(self, job_name, kwargs):
        try:
            key = queue_once_key(job_name, kwargs)
            self.redis_client.delete(key)
        except Exception as ex:
            logger.error(f"[{job_name}][clear_queue_once_lock_key] {ex}")

    def is_active_in_celery(self, task_id, job_name, kwargs):
        try:
            return self.get_async_result_status(task_id, job_name, kwargs) in [RECEIVED, STARTED]
        except Exception as ex:
            logger.error(f"[{task_id}][{job_name}][{kwargs}][check_job_active_in_celery] {ex}")
        return False
