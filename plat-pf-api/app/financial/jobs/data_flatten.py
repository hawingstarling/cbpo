from typing import List

from celery import current_app
from celery.utils.log import get_task_logger
from app.financial.models import DataFlattenTrack
from app.financial.services.data_flatten import DataFlatten
from app.financial.variable.data_flatten_variable import FLATTEN_SALE_ITEM_KEY
from app.financial.variable.job_status import SUCCESS, ERROR
from app.financial.services.utils.source_config import data_source_generator_config

logger = get_task_logger(__name__)


@current_app.task(bind=True)
def flat_sale_items(self, client_id, type_flatten):
    """
    Using for generate datasource from config
    generate datasource
    update status live feed
    write log generate flatten
    """
    logger.info(
        f"[Tasks][{self.request.id}][{client_id}][flat_sale_items][{type_flatten}]: Beginning ..."
    )
    data_flatten_track = DataFlattenTrack.objects.tenant_db_for(client_id).get(client_id=client_id, type=type_flatten)
    try:
        config = data_source_generator_config()[type_flatten]
        #
        data_flatten_service = DataFlatten(
            client_id=client_id,
            type_flatten=type_flatten,
            **config,
            source=data_flatten_track.source,
            batch_size=data_flatten_track.batch_size
        )
        data_flatten_service.do_flatten()
        # update status
        data_flatten_track.status = SUCCESS
        data_flatten_track.live_feed = True
        data_flatten_track.last_rows_synced = data_flatten_service.total_rows_synced
        data_flatten_track.save(update_fields=["status", "live_feed", "last_rows_synced"])
    except Exception as ex:
        logger.error(
            f"[flat_sale_items][{self.request.id}][{client_id}][{type_flatten}]: {ex}"
        )
        data_flatten_track.status = ERROR
        data_flatten_track.log = str(ex)
        data_flatten_track.save()


@current_app.task(bind=True)
def flat_sale_items_bulks_sync_task(self, client_id: str, type_flatten: str = FLATTEN_SALE_ITEM_KEY):
    """
    Using for sync data to flatten analysis
    """
    logger.info(
        f"[Tasks][{self.request.id}][{client_id}][flat_sale_items_bulks_sync_task][{type_flatten}]: Beginning ..."
    )

    data_flatten_track = DataFlattenTrack.objects.tenant_db_for(client_id).get(client_id=client_id, type=type_flatten)

    config = data_source_generator_config()[type_flatten]
    data_flatten_service = DataFlatten(
        client_id=client_id,
        type_flatten=type_flatten,
        **config,
        source=data_flatten_track.source,
        batch_size=data_flatten_track.batch_size
    )
    data_flatten_service.sync_to_table()

    data_flatten_track.last_rows_synced = data_flatten_service.total_rows_synced
    data_flatten_track.save(update_fields=["last_rows_synced"])


@current_app.task(bind=True)
def flat_sale_items_bulk_sync_additional_task(self, client_id: str, type_flattens: List[str] = None,
                                              additional_query: str = None):
    """
    Using for sync data additional conditions filter flatten analysis
    """
    logger.info(
        f"[Tasks][{self.request.id}][{client_id}][flat_sale_items_bulk_sync_additional_task]"
        f"[{type_flattens}]: Beginning ..."
    )

    for type_flatten in type_flattens:
        try:
            logger.info(
                f"[Tasks][{self.request.id}][{client_id}][handler_flatten_data_source_analysis_additional]: "
                f"Processing  {type_flatten} ..."
            )
            data_flatten_track = DataFlattenTrack.objects.tenant_db_for(client_id).get(client_id=client_id,
                                                                                       type=type_flatten)
            config = data_source_generator_config()[type_flatten]
            data_flatten_service = DataFlatten(
                client_id=client_id,
                type_flatten=type_flatten,
                **config,
                source=data_flatten_track.source,
                batch_size=data_flatten_track.batch_size,
                additional_query=additional_query
            )
            data_flatten_service.update_flatten_table()

            data_flatten_track.last_rows_synced = data_flatten_service.total_rows_synced
            data_flatten_track.save(update_fields=["last_rows_synced"])
        except Exception as ex:
            logger.error(
                f"[Tasks][{self.request.id}][{client_id}][handler_flatten_data_source_analysis_additional]: "
                f"Error {ex}"
            )


@current_app.task(bind=True)
def flat_ds_calculate(self, client_id: str, type_flatten: str):
    logger.info(
        f"[Tasks][{self.request.id}][{client_id}][flat_ds_calculate][{type_flatten}]: Beginning ..."
    )
    try:
        data_flatten_track = DataFlattenTrack.objects.tenant_db_for(client_id).get(client_id=client_id,
                                                                                   type=type_flatten)
        config = data_source_generator_config()[type_flatten]
        data_flatten_service = DataFlatten(
            client_id=client_id,
            type_flatten=type_flatten,
            **config,
            source=data_flatten_track.source,
            batch_size=data_flatten_track.batch_size,
            last_run_synced=data_flatten_track.last_run,
            last_rows_synced=data_flatten_track.last_rows_synced
        )
        data_flatten_service.do_flatten()

        data_flatten_track.last_rows_synced = data_flatten_service.total_rows_synced
        data_flatten_track.last_run = data_flatten_service.time_starting
        data_flatten_track.save(update_fields=["last_run", "last_rows_synced"])
    except Exception as ex:
        logger.error(
            f"[Tasks][{client_id}][{self.request.id}][handler_flatten_data_source_calculated][{type_flatten}]: "
            f"Error {ex}"
        )


@current_app.task(bind=True)
def handler_clean_log_live_feed_flatten(self, client_id):
    logger.info(
        f"[Tasks][{self.request.id}][{client_id}][handler_clean_log_live_feed_flatten]: Beginning ..."
    )
    DataFlattenTrack.objects.tenant_db_for(client_id).filter(live_feed=True, client__active=True).update(
        log_feed=dict(), log_event=dict())
