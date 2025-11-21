import hashlib, json, logging, sys
import itertools
from time import sleep
from typing import Union
from dictdiffer import diff
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from rest_framework import status
from app.core.services.integrations.base import BULK_INDEXES_KEY, BULK_UPDATES_KEY, BULK_INSERTS_KEY
from app.core.utils import hashlib_content
from app.core.variable.marketplace import CHANNEL_DEFAULT
from app.financial.models import DataFlattenTrack, SaleItem, CacheSaleItemTransaction, SaleItemTransaction
from app.financial.services.integrations.base import IntegrationFinancialBase
from app.financial.variable.job_status import TRANS_EVENT_JOB, POSTED_FILTER_MODE
from app.financial.services.integrations.events.adjustment import AdjustmentHandler
from app.financial.services.integrations.events.refund import RefundHandler
from app.financial.services.integrations.events.service_fee import ServiceFeeHandler
from app.financial.services.integrations.events.shipment import ShipmentHandler
from app.financial.sub_serializers.sale_item_trans_event_serializer import SaleItemTransEventSerializer, \
    SaleItemCacheTransEventSerializer
from app.core.variable.pf_trust_ac import TIME_CONTROL_LOG_TYPE
from app.job.utils.helper import register
from app.job.utils.variable import SYNC_ANALYSIS_CATEGORY, MODE_RUN_IMMEDIATELY

logger = logging.getLogger(__name__)

SALE_ITEM_TRAN_KEY = 'SALE_ITEM_TRAN'
SALE_ITEM_CACHE_TRAN_KEY = 'SALE_ITEM_CACHE_TRAN'


class TransactionSaleItemEvent(IntegrationFinancialBase):
    JOB_TYPE = TRANS_EVENT_JOB
    READ_TIMEOUT = 120.0

    def __init__(self, client_id: str, flatten: DataFlattenTrack = None, marketplace: str = CHANNEL_DEFAULT, **kwargs):
        super().__init__(client_id=client_id, flatten=flatten, marketplace=marketplace, **kwargs)

        # log event
        self.log_event = self._init_log()

        # bulk config upsert transaction
        self.BULK_OBJ = {}
        self.init_bulk_config()

        # sale item content type

        self.sale_item_content_type = ContentType.objects.db_manager(using=self.client_db).get_for_model(SaleItem)

        self.handler_event_item = {}

    @property
    def handler_event_config(self):
        return {
            'shipment_event': ShipmentHandler,
            'refund_event': RefundHandler,
            'adjustment_event': AdjustmentHandler,
            'service_fee_event': ServiceFeeHandler
        }

    def init_bulk_config(self):
        self.BULK_OBJ = {
            SALE_ITEM_TRAN_KEY: {
                BULK_INDEXES_KEY: [],
                BULK_INSERTS_KEY: [],
                BULK_UPDATES_KEY: [],
            },
            SALE_ITEM_CACHE_TRAN_KEY: {
                BULK_INDEXES_KEY: [],
                BULK_INSERTS_KEY: [],
                BULK_UPDATES_KEY: [],
            },
        }

    def _write_log_process(self):
        if self.log_type == TIME_CONTROL_LOG_TYPE:
            self._write_log_to_time_control(log_data=self.log_event)
        else:
            self._write_log_to_flatten()

    def _write_log_to_flatten(self):
        try:
            track_logs = self.kwargs.get('track_logs', True)
            if not track_logs:
                return
            #
            self._refresh_flatten_track()
            self.set_last_run_flatten_track()
            self.flatten_track.log_event = json.dumps(self.log_event)
            # self.flatten_track.save()
            DataFlattenTrack.objects.tenant_db_for(self.client_id).bulk_update([self.flatten_track],
                                                                               fields=['last_run_event', 'log_event'])
        except Exception as ex:
            logger.error(f"[{self.__class__.__name__}][{self.client_id}][_write_log_to_flatten] {ex}")

    def _write_errors_request(self, status_code, content):

        track_logs = self.kwargs.get('track_logs', True)

        if not track_logs:
            return

        content = f"[ACManager] __handler_result error: {content}"
        self.log_event.get('errors').update({'{}'.format(self.time_tracking): content})
        self._write_log_process()

    def _add_log_to_flatten(self):

        track_logs = self.kwargs.get('track_logs', True)

        if not track_logs:
            return

        logger.info(
            f"[{self.client_id}][{self.marketplace}][{self.JOB_TYPE}][{self.time_tracking}]"
            f"[size memory] {sys.getsizeof(self.BULK_OBJ)}"
        )

        # if len(self._success) > 0:
        #     self.log_event.get('success').update({'{}'.format(self.time_tracking): self._success})
        if len(self._errors) > 0:
            self.log_event.get('errors').update({f'[{self.time_tracking}]': self._errors})

    def _get_data_request(self, page: int = 1) -> dict:
        try:
            query_params = {"marketplace": self.marketplace, "page": page, "limit": self.LIMIT_SIZE}

            self.prefetch_query_params(query_params)

            rs = self.ac_manager.get_financial_events(sc_method=self.sc_method, **query_params)
            data = self._handler_result(rs)
            return data
        except Exception as ex:
            content = str(ex)
            self._write_errors_request(status.HTTP_400_BAD_REQUEST, content)
            return {}

    @property
    def amazon_order_ids(self):
        return self.kwargs.get('amazon_order_ids', [])

    def prefetch_query_params(self, query_params: dict):
        if self.amazon_order_ids:
            query_params.update({"amazon_order_id": self.amazon_order_ids})
        #
        else:
            # check mode filter date ranges
            if self.filter_mode == POSTED_FILTER_MODE:
                query_params.update({"posted_from": self.from_date, "posted_to": self.to_date})
            else:
                query_params.update({"modified_from": self.from_date, "modified_to": self.to_date})

    def progress(self):
        page_info = self._get_data_request()

        if not page_info:
            return

        # save last run
        self._write_log_process()

        page_info.pop('items')
        logger.info(f"[{self.client_id}][{self.marketplace}][{self.JOB_TYPE}]"
                    f"[{self.filter_mode}][{self.time_tracking}] Page count info : {page_info}")

        page_count = page_info.get('page_count')

        if page_count == 0:
            return

        for i in range(page_count):
            page = i + 1

            data = {}

            # connect timeout and read timeout limit
            while not data:
                sleep(2)
                data = self._get_data_request(page=page)  # i start with 0

            items = data.get('items')

            self.process_page_data(items)

            self.bulk_process()

            logger.info(f"[{self.client_id}][{self.marketplace}][{self.JOB_TYPE}]"
                        f"[{self.filter_mode}][{self.time_tracking}][{page_count}] exec page {page} completed")

        self.complete_process()

        # write log event
        self._write_log_process()

    def complete_process(self):
        trans_dirty_qs = SaleItemTransaction.objects.tenant_db_for(self.client_id) \
            .filter(client_id=self.client_id, channel=self.channel, dirty=True)
        if trans_dirty_qs.exists():
            # register job for split financial flatten
            meta = dict(client_id=self.client_id, marketplace=self.marketplace, **self.kwargs)
            data = dict(
                name=f"handler_trans_event_data_to_sale_level_{self.marketplace}_{hashlib_content(meta)}",
                job_name="app.financial.jobs.sale_event.handler_trans_event_data_to_sale_level",
                module="app.financial.jobs.sale_event",
                method="handler_trans_event_data_to_sale_level",
                meta=meta
            )
            register(category=SYNC_ANALYSIS_CATEGORY, client_id=self.client_id, **data, mode_run=MODE_RUN_IMMEDIATELY)
            logger.info(f"[{self.__class__.__name__}][{self.client_id}][{self.marketplace}][complete_process] "
                        f"register trans_event_data_to_sale_level job")

    def _processing_handler_config(self, channel_sale_id, channel, item):
        for key, handler_config in self.handler_event_item.items():
            handler = handler_config(self.client, channel_sale_id, channel, item)
            handler.process()
            data = handler.data
            self.__process_trans_item(channel_sale_id, data)

    def get_changed_handler(self, origin: dict = {}, target: dict = {}):
        self.handler_event_item = {}
        try:
            changes = diff(origin, target)
            event_keys = []
            for g_key, g_values in itertools.groupby(changes, lambda x: x[0]):
                assert g_key not in ["add"], "Event not in Add"
                for item in g_values:
                    if item[1][0] in event_keys:
                        continue
                    event_keys.append(item[1][0])
            assert len(event_keys) > 0, "Event keys must not empty"
            for key in event_keys:
                try:
                    self.handler_event_item.update({key: self.handler_event_config[key]})
                except Exception as ex:
                    # logger.error(f"[{self.__class__.__name__}][get_changed_handler] {ex}")
                    pass
            assert len(self.handler_event_item) > 0, "Handler event item must not empty"
        except Exception as ex:
            logger.debug(f"[{self.__class__.__name__}][{self.client_id}][get_changed_handler] {ex}")
            self.handler_event_item = self.handler_event_config

    def __has_content_changed(self, channel_sale_id: str, content: dict):
        # check content data update not changed
        is_changed = True
        origin_content = {}
        try:
            hash_data = hashlib.md5(json.dumps(content).encode('utf-8')).hexdigest()
            cache_ins = CacheSaleItemTransaction.objects.tenant_db_for(self.client_id) \
                .get(client_id=self.client_id,
                     channel_id=self.channel.id,
                     channel_sale_id=channel_sale_id)
            is_changed = cache_ins.hash != hash_data
            origin_content = cache_ins.content
        except Exception as ex:
            logger.debug(
                f"[{self.__class__.__name__}][{self.client_id}][{channel_sale_id}][__has_content_changed] {ex}"
            )
        if is_changed:
            self.get_changed_handler(origin_content, content)
        return is_changed

    def __cache_trans_event(self, channel_sale_id: str, content_type: ContentType, content: dict):
        hash_data = hashlib.md5(json.dumps(content).encode('utf-8')).hexdigest()
        data = {
            'client': self.client,
            'channel_sale_id': channel_sale_id,
            'channel': self.channel,
            'content_type': content_type,
            'content': content,
            'hash': hash_data,
            'is_removed': False
        }
        item_cache_event = SaleItemCacheTransEventSerializer()
        obj, created = item_cache_event.process_trans_event(data)
        self.add_obj_to_bulk(SALE_ITEM_CACHE_TRAN_KEY, obj, created)

    def process_page_data(self, data: list):
        #
        for item in data:
            channel_sale_id = item.get('amazon_order_id')
            if not channel_sale_id:
                continue

            if not self.__has_content_changed(channel_sale_id, item):
                logger.debug(
                    f"[{self.__class__.__name__}][{self.client_id}][{channel_sale_id}]"
                    f"[process_page_data] content not changed"
                )
                continue

            self._processing_handler_config(channel_sale_id, self.channel, item)

            # write cache
            self.__cache_trans_event(channel_sale_id, self.sale_item_content_type, item)

    @transaction.atomic
    def bulk_process(self):
        try:

            # Sale Item Trans Event
            SaleItemTransaction.all_objects.tenant_db_for(self.client_id).bulk_create(
                self.BULK_OBJ[SALE_ITEM_TRAN_KEY][BULK_INSERTS_KEY], ignore_conflicts=True)

            fields_update = [i.name for i in SaleItemTransaction._meta.fields if i.name not in ['pk', 'id']]
            SaleItemTransaction.all_objects.tenant_db_for(self.client_id).bulk_update(
                self.BULK_OBJ[SALE_ITEM_TRAN_KEY][BULK_UPDATES_KEY], fields=fields_update)

            # Sale Item Cache Trans Event
            CacheSaleItemTransaction.all_objects.tenant_db_for(self.client_id).bulk_create(
                self.BULK_OBJ[SALE_ITEM_CACHE_TRAN_KEY][BULK_INSERTS_KEY],
                ignore_conflicts=True)

            fields_update = [i.name for i in CacheSaleItemTransaction._meta.fields if i.name not in ['pk', 'id']]
            CacheSaleItemTransaction.all_objects.tenant_db_for(self.client_id).bulk_update(
                self.BULK_OBJ[SALE_ITEM_CACHE_TRAN_KEY][BULK_UPDATES_KEY],
                fields=fields_update)

        except Exception as ex:
            logger.error(
                f"[{self.client_id}][{self.marketplace}][{self.JOB_TYPE}][{self.filter_mode}][{self.time_tracking}]"
                f"[bulk_process] : {ex}"
            )
            errors = {
                'key': 'bulk_process_trans_event',
                'msg': str(ex)
            }
            self._errors.append(errors)

        self._add_log_to_flatten()

        # reset config bulk
        self.init_bulk_config()

    def add_obj_to_bulk(self, sender: str, obj: Union[SaleItemTransaction, CacheSaleItemTransaction],
                        created: bool = True):

        # index = self.hash_index_sender(sender, obj)
        index = obj.pk

        if index and index not in self.BULK_OBJ[sender][BULK_INDEXES_KEY]:
            obj_type = BULK_INSERTS_KEY if created else BULK_UPDATES_KEY
            self.BULK_OBJ[sender][obj_type].append(obj)

            # add record success
            self._success.append('{}'.format(str(obj.pk)))

    def __process_trans_item(self, channel_sale_id, data: list):
        for item in data:
            try:
                channel = item.pop('channel')
                content_type = item.pop('content_type')

                serializer_class = SaleItemTransEventSerializer(data=item)
                serializer_class.is_valid(raise_exception=True)
                validated_data = serializer_class.validated_data

                validated_data.update({'client': self.client, 'channel': channel, 'content_type': content_type,
                                       'is_removed': False})

                obj, created, log_entry = serializer_class.process_trans_event(validated_data)
                if log_entry:
                    obj.dirty = True
                    self.add_obj_to_bulk(SALE_ITEM_TRAN_KEY, obj, created)
            except Exception as ex:
                logger.debug(
                    f"[{self.client_id}][{self.marketplace}][{self.JOB_TYPE}][{self.filter_mode}][{self.time_tracking}]"
                    f"[__process_trans_item] : {ex}"
                )
                info = {
                    "key": channel_sale_id,
                    "marketplace": self.marketplace,
                    "errors": '[{}] __process_trans_item : {}'.format(self.__class__.__name__, ex)
                }
                self._errors.append(info)
