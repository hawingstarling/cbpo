import logging
import json
from typing import Union
import sys

from app.core.services.integrations.base import BULK_INDEXES_KEY, BULK_INSERTS_KEY, BULK_UPDATES_KEY
from app.core.sub_serializers.base_serializer import CostInputSerializer
from app.core.variable.marketplace import CHANNEL_DEFAULT
from app.financial.services.integrations.base import IntegrationFinancialBase
from app.financial.services.utils.common import round_currency, is_the_same_currency
from app.financial.variable.brand_setting import EVALUATED_FREIGHT_COST_ACCURACY_SPECIFIC_BRAND
from app.financial.variable.fulfillment_type import FULFILLMENT_MFN_RA, FULFILLMENT_MFN_DS
from app.financial.variable.job_status import SALE_ITEM_FREIGHT_COST_JOB
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


class FreightCostCalculationFromBrandSetting(IntegrationFinancialBase):
    DT_FILTER_FORMAT = '%Y-%m-%d %H:%M:%S'
    JOB_TYPE = SALE_ITEM_FREIGHT_COST_JOB

    def __init__(self, client_id: str, flatten: DataFlattenTrack = None, marketplace: str = CHANNEL_DEFAULT, **kwargs):
        super().__init__(client_id=client_id, flatten=flatten, marketplace=marketplace, **kwargs)
        #
        # log event
        self.log_event = self._init_log()
        # bulk config upsert transaction
        self.BULK_OBJ = {}
        self.init_bulk_config()

        self.time_now = timezone.now()
        self.field_target = self.get_field_target()
        # last time filter
        self.filter_from = self.time_now - timedelta(minutes=60)
        #
        self.config_brand_est_unit_freight_cost = {}
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
    def markerplace(self):
        return self.kwargs.get('markerplace', CHANNEL_DEFAULT)

    @property
    def is_override(self):
        return self.kwargs.get('override', False)

    def get_field_target(self):
        val = self.kwargs.get("field_target_calculation", "all")
        assert val in ["all", "inbound",
                       "outbound"], "field_target_calculation must be in ['all', 'inbound', 'outbound']"
        return val

    def _get_data_request(self):
        if len(self.sale_item_ids) > 0:
            cond = self.base_cond & Q(pk__in=self.sale_item_ids)
        elif len(self.bulk_channel_sale_ids) > 0:
            cond = self.base_cond & Q(sale__channel_sale_id__in=self.bulk_channel_sale_ids)
        else:
            cond = self.base_cond & Q(sale__channel=self.channel, modified__gte=self.filter_from,
                                      modified__lte=self.time_now)
        if not self.is_override:
            if self.field_target == "all":
                cond = cond & (
                        Q(inbound_freight_cost_accuracy__lte=100) | Q(inbound_freight_cost_accuracy__isnull=True) |
                        Q(outbound_freight_cost_accuracy__lte=100) | Q(outbound_freight_cost_accuracy__isnull=True)
                )
            elif self.field_target == "inbound":
                cond = cond & (
                        Q(inbound_freight_cost_accuracy__lte=100) | Q(inbound_freight_cost_accuracy__isnull=True)
                )
            else:
                cond = cond & (
                        Q(outbound_freight_cost_accuracy__lte=100) | Q(outbound_freight_cost_accuracy__isnull=True)
                )
        #
        queryset = SaleItem.objects.tenant_db_for(self.client_id).filter(cond).order_by('-sale_date')
        #
        paging = Paginator(queryset, 1000)
        return paging

    def __prefetch_brand_setting_segment_config(self):
        cond = Q(client_id=self.client_id)
        if self.field_target == "all":
            cond = cond & (
                    Q(est_unit_inbound_freight_cost__isnull=False, est_unit_inbound_freight_cost__gt=0)
                    | Q(est_unit_outbound_freight_cost__isnull=False, est_unit_outbound_freight_cost__gt=0)
            )
        elif self.field_target == "inbound":
            cond = cond & Q(est_unit_inbound_freight_cost__isnull=False, est_unit_inbound_freight_cost__gt=0)
        else:
            cond = cond & Q(est_unit_outbound_freight_cost__isnull=False, est_unit_outbound_freight_cost__gt=0)
        brand_field_queryset = BrandSetting.objects.tenant_db_for(self.client_id).filter(cond) \
            .values("client_id", "channel__id", "brand__id", "est_unit_inbound_freight_cost",
                    "est_unit_outbound_freight_cost")
        for item in brand_field_queryset:
            self.config_brand_est_unit_freight_cost.update(
                {
                    f"{item['client_id']}-{item['channel__id']}-{item['brand__id']}": {
                        "inbound": item['est_unit_inbound_freight_cost'],
                        "outbound": item['est_unit_outbound_freight_cost']
                    }
                }
            )

    def mapping_freight_cost_by_brand_settings(self, sale_item: SaleItem, validated_data: dict, field_update: str,
                                               key_getting: str):
        try:
            assert sale_item.brand_id is not None, "Brand item is not empty"
            assert getattr(sale_item, f"{field_update}_accuracy") is None \
                   or getattr(sale_item, f"{field_update}_accuracy") < EVALUATED_FREIGHT_COST_ACCURACY_SPECIFIC_BRAND \
                   or self.is_override, f"{field_update} less than {EVALUATED_FREIGHT_COST_ACCURACY_SPECIFIC_BRAND}%"

            field_key = f"{sale_item.client_id}-{sale_item.sale.channel_id}-{sale_item.brand_id}"
            val_est = self.config_brand_est_unit_freight_cost.get(field_key, {}).get(key_getting, 0)

            val = round_currency(val_est * sale_item.quantity)
            val_accuracy = EVALUATED_FREIGHT_COST_ACCURACY_SPECIFIC_BRAND

            assert val != 0, f"{field_update} value is not empty"

            if sale_item.fulfillment_type.name in [FULFILLMENT_MFN_DS, FULFILLMENT_MFN_RA]:
                val = 0
                val_accuracy = 0

            cost_serializer = CostInputSerializer(data=dict(value=val))
            cost_serializer.is_valid(raise_exception=True)

            assert not is_the_same_currency(getattr(sale_item, field_update), val), \
                "The new value is the same as old value"

            validated_data.update(
                {
                    field_update: val,
                    f"{field_update}_accuracy": val_accuracy
                }
            )
        except Exception as ex:
            logger.debug(
                f"[{self.__class__.__name__}][{self.client_id}][mapping_freight_cost_by_brand_settings]: "
                f"Item Pk {sale_item.pk} {ex}"
            )

    def __process_data_page(self, sale_items: [SaleItem]):
        for sale_item in sale_items:
            try:
                validated_data = dict()
                if self.field_target == "all":
                    self.mapping_freight_cost_by_brand_settings(sale_item, validated_data, "inbound_freight_cost",
                                                                "inbound")
                    self.mapping_freight_cost_by_brand_settings(sale_item, validated_data, "outbound_freight_cost",
                                                                "outbound")
                else:
                    self.mapping_freight_cost_by_brand_settings(sale_item, validated_data,
                                                                f"{self.field_target}_freight_cost", self.field_target)

                item_obj, item_log_entry = ClientSaleItemSerializer(context=self._context_serializer) \
                    .update(sale_item, validated_data)
                if item_log_entry:
                    self.add_obj_to_bulk(SALE_ITEM_LEVEL_KEY, item_obj, False)
                    self.add_obj_to_bulk(LOG_ENTRY, item_log_entry)
            except Exception as ex:
                logger.debug(f"[{self.__class__.__name__}][__process_data_page][sale_item_pk={sale_item.pk}]: {ex}")

    def progress(self):
        pages = self._get_data_request()

        if not pages:
            logger.error(
                f"[{self.__class__.__name__}][{self.client_id}][{self.time_tracking}] "
                f"not found channel sale ids recalculate freight cost"
            )
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
            # fields_update = [i.name for i in SaleItem._meta.fields if i.name not in ['pk', 'id']]
            fields_update = [
                "dirty",
                "financial_dirty",
                "modified"
            ]
            if self.field_target == "all":
                fields_update.extend(
                    [
                        "inbound_freight_cost",
                        "outbound_freight_cost",
                        "inbound_freight_cost_accuracy",
                        "outbound_freight_cost_accuracy"
                    ]
                )
            else:
                fields_update.extend(
                    [
                        f"{self.field_target}_freight_cost",
                        f"{self.field_target}_freight_cost_accuracy"
                    ]
                )
            SaleItem.all_objects.tenant_db_for(self.client_id).bulk_update(
                self.BULK_OBJ[SALE_ITEM_LEVEL_KEY][BULK_UPDATES_KEY], fields=fields_update)
            # Log entry of sale level
            LogClientEntry.objects.tenant_db_for(self.client_id).bulk_create(self.BULK_OBJ[LOG_ENTRY],
                                                                             ignore_conflicts=True)
        except Exception as ex:
            logger.error(
                f"[{self.client_id}][{self.marketplace}][{self.JOB_TYPE}][{self.time_tracking}][bulk_process] : {ex}")
            errors = {
                'key': 'bulk_process_recalculate_freight_cost',
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
