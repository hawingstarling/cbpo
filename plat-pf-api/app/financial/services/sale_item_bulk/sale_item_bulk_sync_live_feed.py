import json
import logging
from app.core.variable.marketplace import CHANNEL_DEFAULT
from app.financial.models import DataFlattenTrack
from app.financial.services.imports import ImportDataModuleService
from app.financial.variable.job_status import BULK_SYNC_LIVE_FEED_JOB
from app.financial.services.integrations.live_feed import SaleItemsLiveFeedManager

logger = logging.getLogger(__name__)


class SaleItemBulkSyncLiveFeed(SaleItemsLiveFeedManager):
    JOB_TYPE = BULK_SYNC_LIVE_FEED_JOB

    def __init__(self, client_id: str, flatten: DataFlattenTrack = None, marketplace: str = CHANNEL_DEFAULT, **kwargs):
        super().__init__(client_id, flatten, marketplace, **kwargs)
        # ac_is_forced
        self.ac_is_forced = kwargs.get('ac_is_forced', False)
        #
        self.channel_sale_ids = kwargs.get('channel_sale_ids', [])
        self.list_sku = kwargs.get('list_sku', [])

        # override init object import manage to add user_id
        user_id = kwargs.get('user_id', None)
        self.import_manage = ImportDataModuleService(client_id=self.client_id, user_id=user_id, marketplace=marketplace)

    def _write_log_to_flatten(self):
        try:
            #
            self._refresh_flatten_track()
            # self.set_last_run_flatten_track()
            self.flatten_track.log_feed = json.dumps(self.log_feed)
            # self.flatten_track.save()
            DataFlattenTrack.objects.tenant_db_for(self.client_id).bulk_update([self.flatten_track],
                                                                               fields=['log_feed'])
        except Exception as ex:
            pass

    def _write_errors_request(self, status_code, content):

        content = f"[ACManager][{BULK_SYNC_LIVE_FEED_JOB}] __handler_result error: {content}"
        self.log_feed.get('errors').update({'{}'.format(self.time_tracking): content})
        self._write_log_to_flatten()

    def _add_log_to_flatten(self, page: int = 1):
        pass

    def _get_data_request(self, page: int = 1):
        try:
            channel_sale_ids = list(set(self.channel_sale_ids))
            query_params = {'page': page, 'limit': self.limit_size_request, 'marketplace': self.marketplace,
                            'channel_sale_id': channel_sale_ids}
            if self.is_replacement_order is not None:
                query_params.update({'is_replacement_order': self.is_replacement_order})
            if self.ac_is_forced:
                query_params.pop('page')
                query_params.pop('limit')
                rs = self.ac_manager.get_sale_items_immediately(sc_method=self.sc_method, **query_params)
            else:
                rs = self.ac_manager.get_sale_items(sc_method=self.sc_method, **query_params)
            data = self._handler_result(rs)
            data['items'] = [item for item in data['items'] if item['sku'] in self.list_sku]
            return data
        except Exception as ex:
            logger.error('[_get_data_request] {}'.format(ex))
            return {}

    def progress(self):
        if self.ac_is_forced:
            #
            data = self._get_data_request()
            if not data:
                return

            # save last run
            self._write_log_to_flatten()

            items = data.get('items')
            self._processing(items)

            self.bulk_process()

            self.import_manage.complete_process()
            #
            if len(self.import_manage.SALE_IDS) > 0:
                # clean sale id duplicate
                sale_ids = list(set(self.import_manage.SALE_IDS))
                self.reopen_fedex_by_sale_status(sale_ids)

            self._write_log_to_flatten()
        else:
            return super().progress()
