import json
import logging
import sys
from typing import Union
import maya
from auditlog.models import LogEntry
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from app.core.services.integrations.base import BULK_INDEXES_KEY, BULK_INSERTS_KEY, BULK_UPDATES_KEY
from app.core.utils import hashlib_content
from app.core.variable.marketplace import CHANNEL_DEFAULT
from app.financial.jobs.data_flatten import flat_sale_items_bulks_sync_task
from app.financial.models import DataFlattenTrack, Sale, SaleItem, SaleItemTransaction, LogClientEntry
from app.financial.services.integrations.base import IntegrationFinancialBase
from app.financial.variable.job_status import TRANS_DATA_EVENT_JOB
from app.financial.sub_serializers.client_serializer import ClientSaleSerializer, ClientSaleItemSerializer
from app.core.variable.pf_trust_ac import TIME_CONTROL_LOG_TYPE
from app.financial.services.fedex_shipment.config import REOPEN_BY_AMZ_EVENT
from app.job.utils.helper import register
from app.job.utils.variable import SYNC_ANALYSIS_CATEGORY, MODE_RUN_SEQUENTIALLY

logger = logging.getLogger(__name__)

SALE_LEVEL_KEY = 'SALE_LEVEL'
SALE_ITEM_LEVEL_KEY = 'SALE_ITEM_LEVEL'
LOG_ENTRY = 'LOG_ENTRY'


class SaleIntegrationTransEvent(IntegrationFinancialBase):
    MINUTES = 60
    JOB_TYPE = TRANS_DATA_EVENT_JOB

    def __init__(self, client_id: str, flatten: DataFlattenTrack = None, marketplace: str = CHANNEL_DEFAULT, **kwargs):
        super().__init__(client_id=client_id, flatten=flatten, marketplace=marketplace, **kwargs)

        # log event
        self.log_event = self._init_log()

        # bulk config upsert transaction
        self.BULK_OBJ = {}
        self.init_bulk_config()

        self.time_now = timezone.now()

    def init_bulk_config(self):
        self.BULK_OBJ = {
            SALE_LEVEL_KEY: {
                BULK_INDEXES_KEY: [],
                BULK_INSERTS_KEY: [],
                BULK_UPDATES_KEY: [],
            },
            SALE_ITEM_LEVEL_KEY: {
                BULK_INDEXES_KEY: [],
                BULK_INSERTS_KEY: [],
                BULK_UPDATES_KEY: [],
            },
            LOG_ENTRY: []
        }

    def _write_log_process(self):
        if self.log_type == TIME_CONTROL_LOG_TYPE:
            self._write_log_to_time_control(log_data=self.log_event)
        else:
            self._write_log_to_flatten()

    def _write_log_to_flatten(self):
        try:
            #
            self._refresh_flatten_track()
            self.flatten_track.log_event = json.dumps(self.log_event)
            # self.flatten_track.save()
            DataFlattenTrack.objects.tenant_db_for(self.client_id).bulk_update([self.flatten_track],
                                                                               fields=['log_event'])
        except Exception as ex:
            logger.error(f"[{self.__class__.__name__}][{self.client_id}][_write_log_to_flatten] {ex}")

    def _write_errors_request(self, status_code, content):
        content = f"[TransEventToSaleLevel] __handler_result error: {content}"
        self.log_event.get('errors').update({'{}'.format(self.time_tracking): content})
        self._write_log_process()

    def _add_log_to_flatten(self):

        track_logs = self.kwargs.get('track_logs', True)

        if not track_logs:
            return

        logger.info(f"[{self.client_id}][{self.marketplace}][{self.JOB_TYPE}]"
                    f"[{self.time_tracking}][size memory] {sys.getsizeof(self.BULK_OBJ)}")

        if len(self._success) > 0:
            self.log_event.get('success').update({f'[{self.time_tracking}]': self._success})
        if len(self._errors) > 0:
            self.log_event.get('errors').update({f'[{self.time_tracking}]': self._errors})

    def add_obj_to_bulk(self, sender: Union[SALE_LEVEL_KEY, SALE_ITEM_LEVEL_KEY, LOG_ENTRY],
                        obj: Union[Sale, SaleItem, LogEntry], created: bool = True):

        if sender == LOG_ENTRY:
            self.BULK_OBJ[LOG_ENTRY].append(obj)
            return
        index = str(obj.pk)
        if index and index not in self.BULK_OBJ[sender][BULK_INDEXES_KEY]:
            obj_type = BULK_INSERTS_KEY if created else BULK_UPDATES_KEY

            self.BULK_OBJ[sender][BULK_INDEXES_KEY].append(index)
            self.BULK_OBJ[sender][obj_type].append(obj)

            if sender == SALE_LEVEL_KEY:
                self._success.append(obj.channel_sale_id)

    @property
    def amazon_order_ids(self):
        return self.kwargs.get('amazon_order_ids', [])

    def _get_data_request(self):
        # get all sale info

        from_date = self.kwargs.get('from_date', None)
        to_date = self.kwargs.get('to_date', None)

        filter_sale_channel = Q(client=self.client, channel=self.channel, modified__lte=self.time_now)

        if self.amazon_order_ids:

            channel_sale_id__in = Q(channel_sale_id__in=self.amazon_order_ids)

            cond_trans = filter_sale_channel & channel_sale_id__in

        elif from_date and to_date:
            _from_date = maya.parse(from_date).datetime()
            _to_date = maya.parse(to_date).datetime()

            filter_date_time = Q(date__gte=_from_date, date__lte=_to_date, dirty=True)

            cond_trans = filter_sale_channel & filter_date_time
        else:
            filter_dirty = Q(dirty=True)

            cond_trans = filter_sale_channel & filter_dirty

        # get list channel sale ids of channel
        queryset = SaleItemTransaction.objects.tenant_db_for(self.client_id) \
            .filter(cond_trans).values_list('channel_sale_id', flat=True).distinct()

        return queryset

    def __process_data_page(self, sales):

        for sale in sales:
            self.__update_sale_data_level(sale)

            self.__process_items_of_sale(sale)

    def __update_sale_data_level(self, sale: Sale):
        # origin sale status of sale level
        validated_data = {'sale_status': sale.sale_status}
        obj, log_entry = ClientSaleSerializer(context=self._context_serializer).update(sale, validated_data)

        if log_entry:
            self.add_obj_to_bulk(SALE_LEVEL_KEY, obj, False)
            self.add_obj_to_bulk(LOG_ENTRY, log_entry)

    def __process_items_of_sale(self, sale: Sale):

        sale_items = sale.saleitem_set.tenant_db_for(sale.client_id).all()

        for sale_item in sale_items.iterator():
            # sale status origin of sale item level
            validated_data = {'sale_status': sale_item.sale_status}
            item_obj, item_log_entry = ClientSaleItemSerializer(context=self._context_serializer).update(sale_item,
                                                                                                         validated_data)

            if item_log_entry:
                self.add_obj_to_bulk(SALE_ITEM_LEVEL_KEY, item_obj, False)
                self.add_obj_to_bulk(LOG_ENTRY, item_log_entry)

    def progress(self):

        queryset_trans_event = self._get_data_request()

        total_count = queryset_trans_event.count()
        logger.info(f"[{self.client_id}][{self.marketplace}][{self.JOB_TYPE}][{self.time_tracking}] "
                    f"Total count : {total_count}")

        page = 1
        while True:
            if not queryset_trans_event.exists():
                break
            #
            channel_sale_ids = list(queryset_trans_event[:self.LIMIT_SIZE])
            sales = Sale.objects.tenant_db_for(self.client_id) \
                .filter(client=self.client, channel=self.channel, channel_sale_id__in=channel_sale_ids)

            self.__process_data_page(sales)

            self.bulk_process()

            def map_set_object(x):
                x.dirty = False
                x.modified = timezone.now()
                return x

            channel_sale_events = SaleItemTransaction.objects.tenant_db_for(self.client_id) \
                .filter(client_id=self.client_id, channel_id=self.channel.id, channel_sale_id__in=channel_sale_ids)
            chunk_event = list(map(map_set_object, channel_sale_events))

            SaleItemTransaction.objects.tenant_db_for(self.client_id) \
                .bulk_update(chunk_event, fields=['dirty', 'modified'])

            logger.info(f"[{self.client_id}][{self.marketplace}][{self.JOB_TYPE}][{self.time_tracking}] "
                        f"Exec page {page} completed")
            page += 1

        self.complete_process()

        # complete write log to event
        self._write_log_process()

    def complete_process(self):
        # handle set sale status of Sale Obj
        exists_dirty = SaleItem.all_objects.tenant_db_for(self.client_id).filter(dirty=True).exists()
        if exists_dirty:
            # register job for split financial flatten
            meta = dict(client_id=self.client_id, marketplace=self.marketplace)
            job_data = dict(
                name=f"split_sale_item_financial_ws_{self.marketplace}",
                job_name="app.financial.jobs.sale_financial.handler_trigger_split_sale_item_financial_ws",
                module="app.financial.jobs.sale_financial",
                method="handler_trigger_split_sale_item_financial_ws",
                meta=meta
            )
            transaction.on_commit(
                lambda: {
                    flat_sale_items_bulks_sync_task(self.client_id),
                    register(category=SYNC_ANALYSIS_CATEGORY, client_id=self.client_id, **job_data,
                             mode_run=MODE_RUN_SEQUENTIALLY)
                },
                using=self.client_db
            )

            logger.info(f"[{self.__class__.__name__}][{self.client_id}][{self.marketplace}][complete_process] "
                        f"Register split sale item financial job")

    @transaction.atomic
    def bulk_process(self):
        try:

            fields_update = [i.name for i in Sale._meta.fields if i.name not in ['pk', 'id']]
            Sale.all_objects.tenant_db_for(self.client_id).bulk_update(self.BULK_OBJ[SALE_LEVEL_KEY][BULK_UPDATES_KEY],
                                                                       fields=fields_update)

            fields_update = [i.name for i in SaleItem._meta.fields if i.name not in ['pk', 'id']]
            SaleItem.all_objects.tenant_db_for(self.client_id).bulk_update(
                self.BULK_OBJ[SALE_ITEM_LEVEL_KEY][BULK_UPDATES_KEY],
                fields=fields_update)

            # Log entry of sale level
            LogClientEntry.objects.tenant_db_for(self.client_id).bulk_create(self.BULK_OBJ[LOG_ENTRY],
                                                                             ignore_conflicts=True)

            # trigger check & reset shipping cost priority
            if len(self.BULK_OBJ[SALE_ITEM_LEVEL_KEY][BULK_INDEXES_KEY]) > 0:
                # reopen fedex by sale status
                meta = dict(client_id=self.client_id, marketplace=self.marketplace,
                            reopen_action=REOPEN_BY_AMZ_EVENT,
                            obj_ids=self.BULK_OBJ[SALE_ITEM_LEVEL_KEY][BULK_INDEXES_KEY])
                hash_content = hashlib_content(meta)
                data = dict(
                    name=f"reopen_fedex_by_sale_status_{hash_content}",
                    job_name="app.financial.jobs.fedex_shipment.sale_item_reopen_fedex_shipment_job",
                    module="app.financial.jobs.fedex_shipment",
                    method="sale_item_reopen_fedex_shipment_job",
                    meta=meta
                )
                register(category=SYNC_ANALYSIS_CATEGORY, client_id=self.client_id, **data)

        except Exception as ex:
            logger.error(
                f"[{self.client_id}][{self.marketplace}][{self.JOB_TYPE}]"
                f"[{self.time_tracking}][bulk_process] : {ex}"
            )
            errors = {
                'key': 'bulk_process_update_trans_event_to_sale',
                'msg': str(ex)
            }
            self._errors.append(errors)

        self._add_log_to_flatten()

        # reset config bulk
        self.init_bulk_config()
