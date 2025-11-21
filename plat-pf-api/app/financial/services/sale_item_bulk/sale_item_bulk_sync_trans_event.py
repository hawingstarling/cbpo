import logging
from rest_framework import status
from app.core.variable.marketplace import CHANNEL_DEFAULT
from app.financial.models import DataFlattenTrack
from app.financial.jobs.sale_event import handler_trans_event_data_to_sale_level
from app.financial.services.sale_item_bulk.sale_item_bulk_sync_trans_data_event import SaleItemBulkSyncTransDataEvent
from app.financial.variable.job_status import BULK_SYNC_TRANS_EVENT_JOB
from app.financial.services.integrations.trans_event import TransactionSaleItemEvent

logger = logging.getLogger(__name__)


class SaleItemBulkSyncTransEvent(TransactionSaleItemEvent):
    JOB_TYPE = BULK_SYNC_TRANS_EVENT_JOB

    def __init__(self, client_id: str, flatten: DataFlattenTrack = None, marketplace: str = CHANNEL_DEFAULT, **kwargs):
        # ac_is_forced
        super().__init__(client_id, flatten, marketplace, **kwargs)
        self.ac_is_forced = kwargs.get('ac_is_forced', False)

    def _get_data_request(self, page: int = 1) -> dict:
        try:
            query_params = {"marketplace": self.marketplace, "page": page, "limit": self.LIMIT_SIZE}

            self.prefetch_query_params(query_params)

            if self.ac_is_forced:
                query_params.pop('page')
                query_params.pop('limit')
                rs = self.ac_manager.get_financial_events_immediately(sc_method=self.sc_method, **query_params)
            else:
                rs = self.ac_manager.get_financial_events(sc_method=self.sc_method, **query_params)
            data = self._handler_result(rs)
            return data
        except Exception as ex:
            content = str(ex)
            self._write_errors_request(status.HTTP_400_BAD_REQUEST, content)
            return {}

    def progress(self):
        if self.ac_is_forced:
            data = self._get_data_request()
            if not data:
                return

            # save last run
            self._write_log_to_flatten()

            items = data.get('items')
            self.process_page_data(items)

            self.bulk_process()

            self._write_log_to_flatten()
        else:
            super().progress()

        # sync trans data event to sale, sale items
        self.completed_bulk_sync()

    def completed_bulk_sync(self):
        logger.info(f"[{self.client_id}][{self.marketplace}][{self.JOB_TYPE}][{self.sc_method}]:"
                    f" Completed bulk sync trans event data")
        # Sync transaction events data to Sale, SaleItem Model
        handler_trans_event_data_to_sale_level(client_id=self.client_id, marketplace=self.marketplace,
                                               class_trigger=SaleItemBulkSyncTransDataEvent, **self.kwargs)
