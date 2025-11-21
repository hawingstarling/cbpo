import logging

from celery import current_app
from app.es.helper import get_es_sources_configs

logger = logging.getLogger(__name__)


@current_app.task(bind=True)
def handler_bulk_size_flatten_source(self, sql: str, client_id: str, type_flatten: str, action: str, key_id: str,
                                     **kwargs):
    logger.info(f"[{self.request.id}][handler_bulk_size_flatten_source][{client_id}][{type_flatten}] begin")
    logger.info(f"[{self.request.id}][handler_bulk_size_flatten_source][{client_id}][{type_flatten}] sql = {sql}")
    service_flatten_type = get_es_sources_configs()[type_flatten](client_id=client_id, **kwargs)
    service_flatten_type.on_validate()
    service_flatten_type.on_process(sql, action, key_id)
    service_flatten_type.on_complete()
