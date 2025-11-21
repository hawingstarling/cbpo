import json
import logging
import sys
from django.db import transaction
from typing import Union
from auditlog.models import LogEntry
from django.db.models import Q
from django.utils import timezone

from app.core.services.integrations.base import BULK_INDEXES_KEY, BULK_INSERTS_KEY, BULK_UPDATES_KEY
from app.core.variable.marketplace import CHANNEL_DEFAULT
from app.financial.jobs.data_flatten import flat_sale_items_bulks_sync_task
from app.financial.models import DataFlattenTrack, SaleItem, SaleItemFinancial, SaleStatus
from app.financial.services.integrations.base import IntegrationFinancialBase
from app.financial.services.transaction.calculate.sale_item_shipped import CalculateTransSaleItemsShippedManage
from app.financial.variable.data_flatten_variable import FLATTEN_SALE_ITEM_FINANCIAL_KEY
from app.financial.variable.job_status import SALE_ITEM_FINANCIAL_JOB
from app.core.variable.pf_trust_ac import TIME_CONTROL_LOG_TYPE
from app.financial.variable.sale_status_static_variable import SALE_REFUNDED_STATUS, SALE_PARTIALLY_REFUNDED_STATUS, \
    RETURN_REVERSED_STATUS
from app.financial.variable.transaction.config import RefundEvent, ShipmentEvent
from app.core.services.audit_logs.base import AuditLogCoreManager
from app.financial.services.transaction.calculate.sale_item_returned import CalculateTransSaleItemsReturnedManage
from app.core.services.audit_logs.base import SALE_ITEM_FINANCIAL_LEVEL as AUDIT_LOG_SALE_ITEM_FINANCIAL_LEVEL

logger = logging.getLogger(__name__)

SALE_ITEM_FINANCIAL_LEVEL = 'SALE_ITEM_FINANCIAL_LEVEL'
LOG_ENTRY = 'LOG_ENTRY'

SALE_STATUS_ACCEPT_SPLIT_FINANCIAL = [SALE_REFUNDED_STATUS, SALE_PARTIALLY_REFUNDED_STATUS, RETURN_REVERSED_STATUS]


class SaleItemFinancialIntegration(IntegrationFinancialBase):
    MINUTES = 60
    JOB_TYPE = SALE_ITEM_FINANCIAL_JOB

    def __init__(self, client_id: str, flatten: DataFlattenTrack = None, marketplace: str = CHANNEL_DEFAULT, **kwargs):
        super().__init__(client_id=client_id, flatten=flatten, marketplace=marketplace, **kwargs)

        # log event
        self.log_event = self._init_log()

        # bulk config upsert transaction
        self.BULK_OBJ = {}
        self.init_bulk_config()

        self.now = timezone.now()
        self.time_now = self.now.strftime(self.DT_FILTER_FORMAT)
        self.sale_items = []

    def init_bulk_config(self):
        self.BULK_OBJ = {
            SALE_ITEM_FINANCIAL_LEVEL: {
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

        logger.info(
            f"[{self.client_id}][{self.marketplace}][{self.JOB_TYPE}][{self.time_tracking}]"
            f"[size memory] {sys.getsizeof(self.BULK_OBJ)}"
        )

        if len(self._success) > 0:
            self.log_event.get('success').update({f'[{self.time_tracking}]': self._success})
        if len(self._errors) > 0:
            self.log_event.get('errors').update({f'[{self.time_tracking}]': self._errors})

    def add_obj_to_bulk(self, sender: Union[SALE_ITEM_FINANCIAL_LEVEL, LOG_ENTRY],
                        obj: Union[SaleItemFinancial, LogEntry], created: bool = True):

        if sender == LOG_ENTRY:
            self.BULK_OBJ[LOG_ENTRY].append(obj)
            return
        index = obj.pk
        if index and index not in self.BULK_OBJ[sender][BULK_INDEXES_KEY]:
            obj_type = BULK_INSERTS_KEY if created else BULK_UPDATES_KEY
            #
            self.BULK_OBJ[sender][BULK_INDEXES_KEY].append(index)
            self.BULK_OBJ[sender][obj_type].append(obj)

    @property
    def cond_base(self):
        cond = Q(financial_dirty=True)
        return cond

    @property
    def sale_item_ids(self):
        return self.kwargs.get('sale_item_ids', [])

    @property
    def amazon_order_ids(self):
        return self.kwargs.get('amazon_order_ids', [])

    def _get_data_request(self):
        if len(self.sale_item_ids) > 0:
            # logger.info(f"[{self.__class__.__name__}][queryset_financial_dirty][sale_item_ids] : {self.sale_item_ids}")
            cond = self.cond_base & Q(id__in=self.sale_item_ids)
        elif len(self.amazon_order_ids) > 0:
            # logger.info(f"[{self.__class__.__name__}][queryset_financial_dirty][amazon_order_ids] : {self.amazon_order_ids}")
            cond = self.cond_base & Q(sale__channel=self.channel, sale__channel_sale_id__in=self.amazon_order_ids)
        else:
            cond = self.cond_base & Q(sale__channel=self.channel, modified__lte=self.now)

        queryset = SaleItem.all_objects.tenant_db_for(self.client_id).filter(cond).order_by('-sale_date')
        return queryset

    def __process_data_page(self):

        for item in self.sale_items:
            self.__process_item(item)
            #
            item.financial_dirty = False
            item.modified = self.now

    @property
    def fields_sale_item(self):
        return [i.name for i in SaleItem._meta.fields if i.name not in ['pk', 'id', 'financial_dirty']]

    def make_financial_object(self, financial: SaleItemFinancial, is_filter_sale_status: bool = True,
                              sale_status_filter: list = []):
        created = True
        # find object in SaleItemFinancial
        try:
            cond = Q(sale=financial.sale, sale_item=financial.sale_item, sku=financial.sku)
            #
            if is_filter_sale_status:
                cond = cond & Q(sale_status__value__in=sale_status_filter)
            else:
                cond = cond & ~Q(sale_status__value__in=SALE_STATUS_ACCEPT_SPLIT_FINANCIAL)

            instance = SaleItemFinancial.all_objects.tenant_db_for(self.client_id).get(cond)
            #
            financial.pk = instance.pk
            # make log entry
            log_entry = AuditLogCoreManager(client_id=self.client_id).create_log_entry_instance(
                level=AUDIT_LOG_SALE_ITEM_FINANCIAL_LEVEL,
                origin=instance, target=financial,
                action=LogEntry.Action.UPDATE)
            created = False
        except SaleItemFinancial.DoesNotExist:
            # make log entry
            log_entry = AuditLogCoreManager(client_id=self.client_id).create_log_entry_instance(
                level=AUDIT_LOG_SALE_ITEM_FINANCIAL_LEVEL,
                origin=None, target=financial,
                action=LogEntry.Action.CREATE)
        except Exception as ex:
            logger.error(
                f"[{self.__class__.__name__}][{self.client_id}][make_financial_object]"
                f"[{financial.sale_item_id}] : {ex}"
            )
            log_entry = None
        return financial, log_entry, created

    def clone_sale_item_to_financial(self, item: SaleItem):
        SaleItemFinancial.objects.tenant_db_for(self.client_id)
        financial = SaleItemFinancial()
        financial.sale_item = item

        # all field of sale items
        for field in self.fields_sale_item:
            setattr(financial, field, getattr(item, f"{field}"))
        return financial

    def make_sale_status(self, value):
        return SaleStatus.objects.tenant_db_for(self.client_id).get(value=value)

    def __calculated_field_returned(self, financial_refunded: SaleItemFinancial):
        # update field calculate from trans by event
        cal_sale_item = CalculateTransSaleItemsReturnedManage(client_id=self.client_id, job_action=self.JOB_TYPE,
                                                              instance=financial_refunded,
                                                              event=RefundEvent)
        trans_event_data = cal_sale_item.process()
        # print(f"[__calculated_field_returned]: {trans_event_data}")
        for attr, value in trans_event_data.items():
            if attr in self.fields_sale_item:
                setattr(financial_refunded, attr, value)

    def __calculated_field_shipped(self, financial_shipped: SaleItemFinancial):
        # update field calculate from trans by event
        cal_sale_item = CalculateTransSaleItemsShippedManage(client_id=self.client_id, job_action=self.JOB_TYPE,
                                                             instance=financial_shipped,
                                                             event=ShipmentEvent)
        trans_event_data = cal_sale_item.process()
        # print(f"[__calculated_field_shipped]: {trans_event_data}")
        for attr, value in trans_event_data.items():
            if attr in self.fields_sale_item:
                setattr(financial_shipped, attr, value)

    def __process_financial_refunded(self, item: SaleItem):
        assert item.sale_status.value in SALE_STATUS_ACCEPT_SPLIT_FINANCIAL, "Sale status item not refunded"
        # CLONE SHIPPED
        financial_shipped = self.clone_sale_item_to_financial(item)
        self.__calculated_field_shipped(financial_shipped)
        self.__process_financial_to_bulk_list(item=financial_shipped, is_filter_sale_status=False)

        # CLONE REFUNDED
        financial_refunded = self.clone_sale_item_to_financial(item)
        # update field calculate from trans by event
        self.__calculated_field_returned(financial_refunded)
        #
        self.__process_financial_to_bulk_list(item=financial_refunded,
                                              sale_status_filter=SALE_STATUS_ACCEPT_SPLIT_FINANCIAL)

    def set_field_numeric(self, financial_refunded: SaleItemFinancial, field: str, value: any):
        setattr(financial_refunded, field, value)

    def __process_financial_to_bulk_list(self, item: SaleItemFinancial, is_filter_sale_status: bool = True,
                                         sale_status_filter: list = []):
        financial, log_entry, created = self.make_financial_object(item, is_filter_sale_status, sale_status_filter)

        if log_entry:
            financial.dirty = True
            self.add_obj_to_bulk(SALE_ITEM_FINANCIAL_LEVEL, financial, created)
            # self.add_obj_to_bulk(LOG_ENTRY, log_entry)

    def __process_item(self, item: SaleItem):
        # split record refunded
        if item.sale_status.value in SALE_STATUS_ACCEPT_SPLIT_FINANCIAL:
            self.__process_financial_refunded(item)
        else:
            financial = self.clone_sale_item_to_financial(item)
            self.__process_financial_to_bulk_list(financial, is_filter_sale_status=False)

    def progress(self):
        qs_financial = self._get_data_request()
        total_count = qs_financial.count()
        logger.info(
            f"[{self.client_id}][{self.marketplace}][{self.JOB_TYPE}][{self.time_tracking}] "
            f"Total count : {total_count}"
        )

        page = 1
        while True:
            if not qs_financial.exists():
                break

            self.sale_items = list(qs_financial[:self.LIMIT_SIZE])

            self.__process_data_page()

            self.bulk_process()

            logger.info(
                f"[{self.client_id}][{self.marketplace}][{self.JOB_TYPE}][{self.time_tracking}] "
                f"Exec page {page} completed"
            )
            page += 1

        self.complete_process()

        # complete write log to event
        # self._write_log_process()

    def complete_bulk_process(self):
        def map_set_object(x):
            x.financial_dirty = False
            x.modified = timezone.now()
            return x

        SaleItem.all_objects.tenant_db_for(self.client_id).bulk_update(self.sale_items,
                                                                       fields=['financial_dirty', 'modified'])

    def complete_process(self):
        count_dirty = SaleItemFinancial.all_objects.tenant_db_for(self.client_id).filter(dirty=True).count()
        if count_dirty > 0:
            transaction.on_commit(
                lambda: flat_sale_items_bulks_sync_task(client_id=self.client_id,
                                                        type_flatten=FLATTEN_SALE_ITEM_FINANCIAL_KEY),
                using=self.client_db
            )

    def bulk_process(self):
        try:
            SaleItemFinancial.all_objects.tenant_db_for(self.client_id).bulk_create(
                self.BULK_OBJ[SALE_ITEM_FINANCIAL_LEVEL][BULK_INSERTS_KEY], ignore_conflicts=True)

            fields_update = [i.name for i in SaleItemFinancial._meta.fields if i.name not in ['pk', 'id']]
            SaleItemFinancial.all_objects.tenant_db_for(self.client_id).bulk_update(
                self.BULK_OBJ[SALE_ITEM_FINANCIAL_LEVEL][BULK_UPDATES_KEY], fields=fields_update)

            # Log entry of sale level
            # LogClientEntry.objects.tenant_db_for(self.client_id).bulk_create(self.BULK_OBJ[LOG_ENTRY])

            self.complete_bulk_process()

        except Exception as ex:
            logger.error(
                f"[{self.client_id}][{self.marketplace}][{self.JOB_TYPE}][{self.time_tracking}][bulk_process] : {ex}"
            )
            errors = {
                'key': 'bulk_process_update_trans_event_to_sale',
                'msg': str(ex)
            }
            self._errors.append(errors)

        self._add_log_to_flatten()

        # reset config bulk
        self.init_bulk_config()
