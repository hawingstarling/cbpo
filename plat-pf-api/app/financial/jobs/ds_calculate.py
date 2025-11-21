from celery import current_app
from django.utils import timezone
from app.financial.models import DataFlattenTrack
from celery.utils.log import get_task_logger

from app.financial.services.data_flatten import DataFlatten
from app.financial.services.utils.source_config import data_source_generator_config
from app.financial.variable.data_flatten_variable import DATA_FLATTEN_TYPE_CALCULATE_LIST
from app.financial.variable.job_status import SUCCESS, ERROR

logger = get_task_logger(__name__)


@current_app.task(bind=True)
def handler_trigger_generate_ds_calculate(self, client_id: str):
    logger.info(f"[Tasks][{self.request.id}][handler_trigger_generate_ds_calculate][{client_id}]: Beginning ....")
    data_flatten_tracks = DataFlattenTrack.objects.tenant_db_for(client_id).filter(
        client_id=client_id, live_feed=True, type__in=DATA_FLATTEN_TYPE_CALCULATE_LIST, status=SUCCESS
    )
    if data_flatten_tracks.count() == 0:
        logger.error(
            f"[Tasks][{self.request.id}][handler_trigger_generate_ds_calculate][{client_id}]: "
            f"Not found records match with type flatten {DATA_FLATTEN_TYPE_CALCULATE_LIST} "
            f"in Data Flatten Tracking. Pls generate before"
        )
        return

    time_now = timezone.now()
    ds_configs = data_source_generator_config()

    for data_flatten_track in data_flatten_tracks:
        type_flatten = data_flatten_track.type
        try:
            logger.info(
                f"[Tasks][{self.request.id}][handler_trigger_generate_ds_calculate][{client_id}]: "
                f"Processing {type_flatten} ...."
            )
            config = ds_configs[type_flatten]
            data_source_handler = DataFlatten(
                client_id=client_id,
                type_flatten=type_flatten,
                **config,
                source=data_flatten_track.source,
                batch_size=data_flatten_track.batch_size,
                last_run_synced=data_flatten_track.last_run,
                last_rows_synced=data_flatten_track.last_rows_synced
            )
            data_source_handler.do_flatten()

            data_flatten_track.last_rows_synced = data_source_handler.total_rows_synced
            data_flatten_track.last_run = time_now
            data_flatten_track.save(update_fields=["last_run", "last_rows_synced"])
        except Exception as ex:
            data_flatten_track.status = ERROR
            data_flatten_track.log = str(ex)
            logger.error(
                f"[Tasks][{self.request.id}][handler_trigger_generate_ds_calculate][{client_id}][{type_flatten}]: {ex}"
            )
            data_flatten_track.save(update_fields=["status", "log"])
