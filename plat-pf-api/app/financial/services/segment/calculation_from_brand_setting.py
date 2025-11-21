import logging
import json
from typing import Union
import sys

from app.core.services.integrations.base import BULK_INDEXES_KEY, BULK_INSERTS_KEY, BULK_UPDATES_KEY
from app.core.variable.marketplace import CHANNEL_DEFAULT
from app.financial.services.integrations.base import IntegrationFinancialBase
from app.financial.variable.job_status import SALE_ITEM_SEGMENT_JOB
from app.financial.models import SaleItem, BrandSetting, DataFlattenTrack, LogClientEntry
from django.db.models import Q
from django.core.paginator import Paginator
from django.db import transaction
from auditlog.models import LogEntry
from app.financial.sub_serializers.client_serializer import ClientSaleItemSerializer
from app.financial.jobs.data_flatten import flat_sale_items_bulks_sync_task
from django.utils import timezone
from datetime import timedelta
from app.core.variable.pf_trust_ac import TIME_CONTROL_LOG_TYPE

logger = logging.getLogger(__name__)

SALE_ITEM_LEVEL_KEY = 'SALE_ITEM_LEVEL'
LOG_ENTRY = 'LOG_ENTRY'


class SegmentCalculationFromBrandSetting(IntegrationFinancialBase):
    DT_FILTER_FORMAT = '%Y-%m-%d %H:%M:%S'
    JOB_TYPE = SALE_ITEM_SEGMENT_JOB

    def __init__(self, client_id: str, flatten: DataFlattenTrack = None, marketplace: str = CHANNEL_DEFAULT, **kwargs):
        super().__init__(client_id=client_id, flatten=flatten, marketplace=marketplace, **kwargs)
        #
        # log event
        self.log_event = self._init_log()
        # bulk config upsert transaction
        self.BULK_OBJ = {}
        self.init_bulk_config()

        self.time_now = timezone.now()

        # last time filter
        self.filter_from = self.time_now - timedelta(minutes=60)
        #
        self.config_brand_segment = {}
        self.__prefetch_brand_setting_segment_config()

    @property
    def sale_item_ids(self):
        return self.kwargs.get('sale_item_ids', [])

    @property
    def bulk_channel_sale_ids(self):
        return self.kwargs.get('bulk_channel_sale_ids', [])

    @property
    def base_cond(self):
        cond = Q(client_id=self.client_id, brand__isnull=False)
        return cond

    @property
    def is_override(self):
        return self.kwargs.get('override', False)

    @property
    def markerplace(self):
        return self.kwargs.get('markerplace', CHANNEL_DEFAULT)

    def _get_data_request(self):
        if len(self.sale_item_ids) > 0:
            cond = self.base_cond & Q(pk__in=self.sale_item_ids)
        elif len(self.bulk_channel_sale_ids) > 0:
            cond = self.base_cond & Q(sale__channel_sale_id__in=self.bulk_channel_sale_ids)
        else:
            cond = self.base_cond & Q(sale__channel=self.channel, modified__gte=self.filter_from,
                                      modified__lte=self.time_now)
        if not self.is_override:
            cond = cond & Q(segment__isnull=True)
        #
        queryset = SaleItem.objects.tenant_db_for(self.client_id).filter(cond).order_by('-sale_date')
        #
        paging = Paginator(queryset, 1000)
        return paging

    def __prefetch_brand_setting_segment_config(self):
        brand_segment_queryset = BrandSetting.objects.tenant_db_for(self.client_id).filter(client_id=self.client_id,
                                                                                           channel__is_pull_data=True,
                                                                                           brand__isnull=False,
                                                                                           segment__isnull=False) \
            .values('client_id', 'channel__id', 'brand__id', 'segment')
        self.config_brand_segment = {f"{item['client_id']}-{item['channel__id']}-{item['brand__id']}": item['segment']
                                     for item in brand_segment_queryset}

    def __process_data_page(self, sale_items: [SaleItem]):
        for sale_item in sale_items:
            segment_key = f"{sale_item.client_id}-{sale_item.sale.channel_id}-{sale_item.brand_id}"
            segment = self.config_brand_segment.get(segment_key, None)
            if not segment:
                continue
            validated_data = dict(
                segment=segment
            )
            item_obj, item_log_entry = ClientSaleItemSerializer(context=self._context_serializer).update(sale_item,
                                                                                                         validated_data)
            if item_log_entry:
                self.add_obj_to_bulk(SALE_ITEM_LEVEL_KEY, item_obj, False)
                self.add_obj_to_bulk(LOG_ENTRY, item_log_entry)

    def progress(self):
        pages = self._get_data_request()

        if not pages:
            logger.error(
                f"[{self.__class__.__name__}][{self.client_id}][{self.time_tracking}] not found channel sale ids trans for update")
            return

        logger.info(f"[{self.__class__.__name__}][{self.client_id}][{self.time_tracking}] Total count : {pages.count}")

        if pages.count == 0:
            return

        num_pages = pages.num_pages

        for i in range(num_pages):
            page = i + 1

            items = pages.page(number=page).object_list

            self.__process_data_page(items)

            self.bulk_process()

            logger.info(
                f"[{self.__class__.__name__}][{self.client_id}][{self.time_tracking}] exec page {page} completed")

        self.complete_process()

        # complete write log to event
        # self._write_log_process()

    def complete_process(self):
        # handle set sale status of Sale Obj
        count_dirty = SaleItem.objects.tenant_db_for(self.client_id).filter(client_id=str(self.client.pk),
                                                                            dirty=True).count()
        if count_dirty > 0:
            transaction.on_commit(
                lambda: flat_sale_items_bulks_sync_task(self.client_id),
                using=self.client_db
            )

    def add_obj_to_bulk(self, sender: Union[SALE_ITEM_LEVEL_KEY, LOG_ENTRY],
                        obj: Union[SaleItem, LogEntry], created: bool = True):

        if sender == LOG_ENTRY:
            self.BULK_OBJ[LOG_ENTRY].append(obj)
            return
        index = obj.pk
        if index and index not in self.BULK_OBJ[sender][BULK_INDEXES_KEY]:
            obj_type = BULK_INSERTS_KEY if created else BULK_UPDATES_KEY

            self.BULK_OBJ[sender][BULK_INDEXES_KEY].append(index)
            self.BULK_OBJ[sender][obj_type].append(obj)

    @transaction.atomic
    def bulk_process(self):
        try:
            fields_update = [i.name for i in SaleItem._meta.fields if i.name not in ['pk', 'id']]
            SaleItem.all_objects.tenant_db_for(self.client_id).bulk_update(
                self.BULK_OBJ[SALE_ITEM_LEVEL_KEY][BULK_UPDATES_KEY],
                fields=fields_update)
            # Log entry of sale level
            LogClientEntry.objects.tenant_db_for(self.client_id).bulk_create(self.BULK_OBJ[LOG_ENTRY],
                                                                             ignore_conflicts=True)
        except Exception as ex:
            logger.error(
                f"[{self.client_id}][{self.marketplace}][{self.JOB_TYPE}][{self.time_tracking}][bulk_process] : {ex}")
            errors = {
                'key': 'bulk_process_update_trans_event_to_sale',
                'msg': str(ex)
            }

        self._add_log_to_flatten()

        # reset config bulk
        self.init_bulk_config()

    def init_bulk_config(self):
        self.BULK_OBJ = {
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
            pass

    def _write_errors_request(self, status_code, content):
        content = f"[TransEventToSaleLevel] __handler_result error: {content}"
        self.log_event.get('errors').update({'{}'.format(self.time_tracking): content})
        self._write_log_process()

    def _add_log_to_flatten(self):

        track_logs = self.kwargs.get('track_logs', False)

        if not track_logs:
            return

        logger.info(
            f"[{self.client_id}][{self.marketplace}][{self.JOB_TYPE}][{self.time_tracking}][size memory] {sys.getsizeof(self.BULK_OBJ)}")

        if len(self._success) > 0:
            self.log_event.get('success').update({f'[{self.time_tracking}]': self._success})
        if len(self._errors) > 0:
            self.log_event.get('errors').update({f'[{self.time_tracking}]': self._errors})
