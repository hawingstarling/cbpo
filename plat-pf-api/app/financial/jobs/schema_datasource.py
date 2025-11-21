from celery import current_app
from celery.utils.log import get_task_logger
from app.financial.services.flattens_settings.generate import GenerateClientSource
from app.financial.services.schema_datasource import SyncSchemaDatasource

logger = get_task_logger(__name__)


@current_app.task(bind=True)
def handler_sync_scheme_data_source(self, client_id: str, **kwargs):
    logger.info(
        f"[Tasks][{self.request.id}][handler_sync_scheme_data_source][{client_id}] Beginning ..."
    )
    sync_schema_ds = SyncSchemaDatasource(client_id=client_id, **kwargs)
    sync_schema_ds.process()


@current_app.task(bind=True)
def handler_generate_client_source(self, client_id: str, access_token: str, token_type: str, **kwargs):
    logger.info(
        f"[Tasks][{self.request.id}][handler_generate_client_source][{client_id}] Beginning ..."
    )
    flattens_settings_generate = GenerateClientSource(
        client_id=client_id,
        access_token=access_token,
        token_type=token_type,
        **kwargs
    )
    flattens_settings_generate.process()
