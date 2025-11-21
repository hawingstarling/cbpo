import copy
import logging
import json
from typing import List, Union
import sys

from rest_framework import status

from app.core.utils import round_currency
from app.core.variable.marketplace import CHANNEL_DEFAULT
from app.extensiv.integration.parser import build_product_lookup
from app.extensiv.integration.product import ExtensivProductService
from app.extensiv.models import COGSConflict
from app.extensiv.utils import init_cog_conflict
from app.extensiv.variables import EXTENSIV_COG_SOURCE
from app.financial.services.integrations.base import IntegrationFinancialBase
from app.financial.variable.job_status import EXTENSIV_COG_CALCULATION_JOB
from app.financial.models import SaleItem, DataFlattenTrack, LogClientEntry
from django.db.models import Q
from django.core.paginator import Paginator
from django.db import transaction
from app.financial.jobs.data_flatten import flat_sale_items_bulks_sync_task
from django.utils import timezone
from datetime import timedelta
from app.core.variable.pf_trust_ac import TIME_CONTROL_LOG_TYPE

logger = logging.getLogger(__name__)

SALE_LEVEL_KEY = "SALE_LEVEL"
SALE_ITEM_LEVEL_KEY = "SALE_ITEM_LEVEL"
COGS_CONFLICT_LEVEL_KEY = "COGS_CONFLICT_LEVEL_KEY"
LOG_ENTRY = "LOG_ENTRY"
INDEXES = "INDEXES"
INSERT = "INSERT"
UPDATE = "UPDATE"


class ExtensivCogCalculation(IntegrationFinancialBase):
    DT_FILTER_FORMAT = "%Y-%m-%d %H:%M:%S"
    JOB_TYPE = EXTENSIV_COG_CALCULATION_JOB
    # Extensiv Products API limit cannot exceed 100
    LIMIT_SIZE = 100

    def __init__(self, client_id: str, flatten: DataFlattenTrack = None, marketplace: str = CHANNEL_DEFAULT, **kwargs):
        super().__init__(client_id=client_id, flatten=flatten,
                         marketplace=marketplace, **kwargs)
        #
        # log event
        self.log_event = self._init_log()
        # bulk config upsert transaction
        self.BULK_OBJ = {}
        self.init_bulk_config()

        self.time_now = timezone.now()

        # last time filter
        self.filter_from = self.time_now - timedelta(hours=12)
        #
        self.config_brand_user_provided_cost = {}

        self.products_service = ExtensivProductService(
            access_token=self.client_setting.cog_extensiv_token
        )
        self.setting_cog_priority_source = self.client_setting.cog_priority_source
        self._priority_source_number = self.setting_cog_priority_source.get(
            EXTENSIV_COG_SOURCE) or 0
        self._fields_updated = self.get_fields_updated()

        self.log_format_info = f"[{self.__class__.__name__}][{self.client_id}][{self.marketplace}]"\
            f"[{self.JOB_TYPE}][{self.filter_mode}][{self.time_tracking}]"

    @property
    def sale_item_ids(self):
        return self.kwargs.get("sale_item_ids", [])

    @property
    def bulk_channel_sale_ids(self):
        return self.kwargs.get("bulk_channel_sale_ids", [])

    def get_fields_updated(self):
        fields = ["cog", "unit_cog", "cog_source", "used_cog_priority",
                  "dirty", "financial_dirty", "modified"]
        return fields

    def _base_condition(self):
        cond = Q(client_id=self.client_id)
        logger.info(
            f"{self.log_format_info} Base condition: {cond}"
        )
        return cond

    @property
    def is_override(self):
        return self.kwargs.get("override", False)

    def _get_priority_condition(self):
        if len(self.sale_item_ids) > 0:
            cond = Q(pk__in=self.sale_item_ids)
        elif len(self.bulk_channel_sale_ids) > 0:
            cond = Q(
                sale__channel_sale_id__in=self.bulk_channel_sale_ids)
        else:
            cond = Q(sale__channel=self.channel, modified__gte=self.filter_from,
                     modified__lte=self.time_now)
        logger.info(
            f"{self.log_format_info} Priority condition: {cond}"
        )
        return cond

    def _get_mapping_condition(self):
        cond = Q()
        if not self.is_override:
            if bool(self._priority_source_number):
                cond = cond & (Q(used_cog_priority__isnull=True)
                               | Q(used_cog_priority__gt=self._priority_source_number))
            else:
                cond = cond & Q(cog_source__isnull=True) & (
                    Q(cog__isnull=True) | Q(cog=0))
        logger.info(
            f"{self.log_format_info} Mapping condition: {cond}"
        )
        return cond

    def _get_data_request(self):
        if not self.client_setting.cog_use_extensiv:
            # return Paginator([], 0)
            raise Exception(
                f"the COGs setting {EXTENSIV_COG_SOURCE} is not enabled")
        base_cond = self._base_condition()
        queryset = SaleItem.objects.tenant_db_for(
            self.client_id).filter(base_cond)
        priority_cond = self._get_priority_condition()
        if priority_cond:
            queryset = queryset.filter(priority_cond)
        mapping_cond = self._get_mapping_condition()
        if mapping_cond:
            queryset = queryset.filter(mapping_cond)
        return queryset.order_by("-sale_date")

    def _get_products_cost(self, objs: List[SaleItem]):
        try:
            list_sku = [obj.sku for obj in objs]
            logger.debug(
                f"{self.log_format_info}[_get_products_cost] {list_sku}"
            )
            rs = self.products_service.get_vendor_cost_by_sku(
                list_sku=list_sku)
            return rs
        except Exception as ex:
            content = str(ex)
            kwargs_info = [self.client_id, self.marketplace,
                           self.JOB_TYPE, self.filter_mode, self.time_tracking]
            logger.error(f"[{']['.join(kwargs_info)}]: {content}")
            self._write_errors_request(status.HTTP_400_BAD_REQUEST, content)
            return {}

    def __process_data_page(self, sale_items: List[SaleItem]):
        result = self._get_products_cost(objs=sale_items)
        logger.debug(
            f"{self.log_format_info}[__process_data_page][_get_products_cost] {result}")
        products_lookup = build_product_lookup(result, fields=["vendorCost"])
        if not products_lookup:
            return
        logger.debug(
            f"{self.log_format_info}[__process_data_page][products_lookup] {products_lookup}"
        )
        sale_items_ids = [str(sale_item.pk) for sale_item in sale_items]
        mapping_cond = self._get_mapping_condition()
        sale_items_found = SaleItem.objects.tenant_db_for(self.client_id).filter(
            pk__in=sale_items_ids, sku__in=list(products_lookup.keys())).filter(mapping_cond)
        found_ids = []
        for sale_item in sale_items_found:
            sku = sale_item.sku
            product = products_lookup.get(sku)
            logger.debug(
                f"{self.log_format_info}[__process_data_page][product][{sku}] {product}"
            )
            if not product or not product.get("vendorCost") or not product["vendorCost"].get("amount"):
                logger.debug(
                    f"{self.log_format_info}[__process_data_page][product][{sku}] "
                    f"Product={product}"
                )
                logger.info(
                    f"{self.log_format_info}[__process_data_page][product][{sku}] "
                    f"Not found vendorCost"
                )
                continue
            found_ids.append(str(sale_item.pk))
            try:
                sale_item_original = copy.deepcopy(sale_item)
                unit_cog = round_currency(
                    float(product["vendorCost"]["amount"]))
                refunded_qty = sale_item.refunded_quantity or 0
                cog = round_currency(
                    unit_cog * (sale_item.quantity - refunded_qty))
                validated_data = dict(
                    cog=cog,
                    unit_cog=unit_cog,
                    cog_source=EXTENSIV_COG_SOURCE
                )
                # Tracking COGs Conflicts
                _item_cog_priority_number = sale_item_original.used_cog_priority or self._priority_source_number
                if self._priority_source_number < _item_cog_priority_number\
                        and sale_item_original.cog_source != EXTENSIV_COG_SOURCE:
                    conflict = init_cog_conflict(
                        item=sale_item_original,
                        configured_priority_source=EXTENSIV_COG_SOURCE,
                        old_value=sale_item_original.cog,
                        new_value=cog
                    )
                    self.add_obj_to_bulk(COGS_CONFLICT_LEVEL_KEY, conflict)
                #
                fields_update = list(validated_data.keys())
                obj, obj_log = self._set_object_fields_change(
                    sale_item, fields_update, validated_data)
                obj.used_cog_priority = self._priority_source_number
                if obj_log:
                    self.add_obj_to_bulk(SALE_ITEM_LEVEL_KEY, obj)
                    self.add_obj_to_bulk(LOG_ENTRY, obj_log)
            except Exception as ex:
                logger.error(
                    f"{self.log_format_info}[__process_data_page][sale_item_pk={sale_item.pk}] {ex}"
                )
        not_found_ids = set(sale_items_ids) - set(found_ids)
        logger.debug(
            f"{self.log_format_info}[__process_data_page][products_lookup] "
            f"Sale IDs not found: {not_found_ids}"
        )
        SaleItem.objects.tenant_db_for(self.client_id).filter(
            pk__in=list(not_found_ids)).update(modified=timezone.now())

    def progress(self):
        queryset = self._get_data_request()
        total_count = queryset.count()
        logger.info(
            f"{self.log_format_info} Total count : {total_count}"
        )

        if total_count == 0:
            logger.error(
                f"{self.log_format_info} not found channel sale ids trans for update"
            )
            return

        page = 1
        while True:
            if not queryset.exists():
                break

            items = list(queryset[:self.LIMIT_SIZE])

            self.__process_data_page(items)

            self.bulk_process()

            logger.info(
                f"{self.log_format_info} exec page {page} completed"
            )

            page += 1

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

    def add_obj_to_bulk(
            self, sender: Union[SALE_ITEM_LEVEL_KEY, COGS_CONFLICT_LEVEL_KEY, LOG_ENTRY],
            obj: Union[SaleItem, COGSConflict, LogClientEntry]
    ):

        if sender in [COGS_CONFLICT_LEVEL_KEY, LOG_ENTRY]:
            self.BULK_OBJ[sender].append(obj)
            return
        index = obj.pk
        if index and index not in self.BULK_OBJ[sender][INDEXES]:
            self.BULK_OBJ[sender][INDEXES].append(index)
            self.BULK_OBJ[sender][UPDATE].append(obj)

    @transaction.atomic
    def bulk_process(self):
        try:
            SaleItem.all_objects.tenant_db_for(self.client_id) \
                .bulk_update(self.BULK_OBJ[SALE_ITEM_LEVEL_KEY][UPDATE], fields=self._fields_updated)
            # Log entry of sale level
            LogClientEntry.objects.tenant_db_for(self.client_id) \
                .bulk_create(self.BULK_OBJ[LOG_ENTRY], ignore_conflicts=True)
            # COGs Conflict
            COGSConflict.objects.tenant_db_for(self.client_id) \
                .bulk_create(self.BULK_OBJ[COGS_CONFLICT_LEVEL_KEY], ignore_conflicts=True)
        except Exception as ex:
            logger.error(
                f"{self.log_format_info}[{self.time_tracking}][bulk_process] : {ex}"
            )

        self._add_log_to_flatten()
        # reset config bulk
        self.init_bulk_config()

    def init_bulk_config(self):
        self.BULK_OBJ = {
            SALE_ITEM_LEVEL_KEY: {
                INDEXES: [],
                UPDATE: []
            },
            COGS_CONFLICT_LEVEL_KEY: [],
            LOG_ENTRY: [],
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
            DataFlattenTrack.objects.tenant_db_for(self.client_id) \
                .bulk_update([self.flatten_track], fields=["log_event"])
        except Exception as ex:
            logger.error(
                f"{self.log_format_info}[_write_log_to_flatten] : {ex}"
            )

    def _write_errors_request(self, status_code, content):
        content = f"{self.log_format_info} __handler_result error: {content}"
        self.log_event.get("errors").update(
            {"{}".format(self.time_tracking): content})
        self._write_log_process()

    def _add_log_to_flatten(self):

        track_logs = self.kwargs.get("track_logs", False)

        if not track_logs:
            return

        logger.info(
            f"[{self.client_id}][{self.marketplace}][{self.JOB_TYPE}][{self.time_tracking}]"
            f"[size memory] {sys.getsizeof(self.BULK_OBJ)}"
        )
        if len(self._success) > 0:
            self.log_event.get("success").update(
                {f"[{self.time_tracking}]": self._success})
        if len(self._errors) > 0:
            self.log_event.get("errors").update(
                {f"[{self.time_tracking}]": self._errors})
