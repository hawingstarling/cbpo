import copy
import logging
import time
from datetime import datetime
from typing import List

from auditlog.models import LogEntry
from django.db import transaction
from django.utils import timezone
from plat_import_lib_api.models import DataImportTemporary, RawDataTemporary, PROCESSING, PROCESSED
from plat_import_lib_api.services.utils.temp_data import DataTempService
from plat_import_lib_api.services.utils.utils import load_lib_module
from app.core.context import AppContext
from app.core.utils import hashlib_content
from app.financial.jobs.data_flatten import flat_sale_items_bulks_sync_task
from app.financial.models import Sale, SaleItem, ClientPortal, SaleChargeAndCost, LogClientEntry, Channel
from app.core.services.audit_logs.base import AuditLogCoreManager, SALE_LEVEL
from app.database.helper import get_connection_workspace
from app.financial.sub_serializers.client_serializer import (
    ClientSaleSerializer, ClientSaleChargeAndCostSerializer, ClientSaleItemSerializer)
from app.financial.sub_serializers.sale_item_import_serializer import ClientSaleItemsImportSerializer
from plat_import_lib_api.static_variable.config import plat_import_setting
from plat_import_lib_api.static_variable.raw_data_import import RAW_UPDATED_TYPE, RAW_IGNORED_TYPE

from app.financial.variable.job_status import IMPORT_JOB
from app.job.utils.helper import register
from app.job.utils.variable import SYNC_ANALYSIS_CATEGORY, MODE_RUN_IMMEDIATELY

logger = logging.getLogger(__name__)

SALE_KEY = "SALE"
SALE_CHARGE_AND_COST_KEY = "SALE_CHARGE_AND_COST"
SALE_ITEM_KEY = "SALE_ITEM"
INDEXES = "INDEXES"
INSERT = "INSERT"
UPDATE = "UPDATE"
LOG_ENTRY = "LOG_ENTRY"


class ImportDataModuleService:
    ACTION_MERGE = "merge"
    ACTION_OVERRIDE = "override"

    # sale_item_ids = []

    def __init__(self, jwt_token: str = None, user_id: str = None, client_id: str = None, import_file_id: str = None,
                 mode: str = "merge", **kwargs):
        self.jwt_token = jwt_token
        self.client_id = str(client_id)
        self.client_db = get_connection_workspace(self.client_id)
        self.client = self.get_client_portal(client_id)
        self.user_id = user_id
        self.lib_import_id = import_file_id
        self.lib_import = self.get_lib_import()
        self.mode = mode
        self.kwargs = kwargs
        # info import files
        self.map_config = self.get_map_config()
        self.lib_module = self.get_lib_module()
        #
        self.load_queue_environment()
        #
        self.BULK_OBJ = {}
        self.SALE_OBJS = []
        self.SALE_IDS = []
        self.init_bulk_config()

        # sale field imports
        # field "sale_status", "profit_status" of sale update by sale items so ignore it
        self.sale_fields_accept = [i.name for i in Sale._meta.fields if
                                   i.name not in ["pk", "id", "sale_status", "profit_status", "created", "updated"]]

        self.sale_charge_cost_accept = [i.name for i in SaleChargeAndCost._meta.fields if i.name not in ["pk", "id"]]
        self.sale_items_fields_accept = [i.name for i in SaleItem._meta.fields if i.name not in ["pk", "id"]]
        self.raws_import_fields_accept = [i.name for i in RawDataTemporary._meta.fields if i.name not in ["pk", "id"]]
        #
        self.raws_import_process_queryset = self._get_raws_process_action_queryset()
        self.total_records = self._get_total_raw_records()
        self.number_process = self._get_number_process()

    @property
    def marketplace(self):
        return self.kwargs.get("marketplace", None)

    def get_channel_marketplace(self):
        try:
            return Channel.objects.tenant_db_for(self.client_id).get(name=self.marketplace)
        except Exception as ex:
            return None

    def get_lib_import(self):
        try:
            return DataImportTemporary.objects.get(pk=self.lib_import_id)
        except Exception as ex:
            return None

    def get_map_config(self):
        try:
            return {_item["target_col"]: _item["upload_col"] for _item in
                    self.lib_import.info_import_file.get("map_cols_to_module", [])}
        except Exception as ex:
            return {}

    def get_lib_module(self):
        try:
            return load_lib_module(name=self.lib_import.module)
        except Exception as ex:
            return None

    def _get_raws_process_action_queryset(self):
        try:
            queryset = RawDataTemporary.objects.filter(lib_import_id=self.lib_import_id, status=PROCESSING)
            if queryset.filter(is_valid=False).count() > 0:
                queryset.filter(is_valid=False).update(status=PROCESSED, is_complete=False, modified=timezone.now())
            return queryset.order_by("index")
        except Exception as ex:
            return None

    def _get_total_raw_records(self):
        try:
            return RawDataTemporary.objects.filter(lib_import_id=self.lib_import_id, is_valid=True).count()
        except Exception as ex:
            return 0

    def _get_number_process(self):
        try:
            return RawDataTemporary.objects.filter(lib_import_id=self.lib_import_id, status=PROCESSED, is_complete=True) \
                .count()
        except Exception as ex:
            return 0

    @property
    def auto_prefetch_shipping_cost(self):
        return self.kwargs.get("auto_prefetch_shipping_cost", True)

    def init_bulk_config(self):
        self.BULK_OBJ = {
            SALE_KEY: {
                INDEXES: [],
                INSERT: [],
                UPDATE: [],
            },
            SALE_CHARGE_AND_COST_KEY: {
                INDEXES: [],
                INSERT: [],
                UPDATE: [],
            },
            SALE_ITEM_KEY: {
                INDEXES: [],
                INSERT: [],
                UPDATE: []
            },
            LOG_ENTRY: []
        }

    def get_client_portal(self, client_id):
        return ClientPortal.objects.tenant_db_for(client_id).get(pk=client_id)

    def load_queue_environment(self):
        if plat_import_setting.use_queue:
            AppContext.instance().clean()
            context = AppContext.instance()
            context.user_id = self.user_id
            context.client_id = str(self.client.pk)
            context.jwt_token = self.jwt_token

    def validate_sale_item_import(self, data_map_config: dict = {}, raw_instance: RawDataTemporary = None):
        context = {"kwargs": {"client_id": self.client_id}}
        serializer = ClientSaleItemsImportSerializer(context=context, data=data_map_config)
        serializer.is_valid()
        errors = serializer.errors
        if errors:
            errors = self.get_processing_errors(errors)
            raw_instance.processing_errors = errors
            raw_instance.is_complete = False
            return data_map_config, {}
        return data_map_config, serializer.validated_data

    def fetch_rows_is_valid(self):
        if self.total_records == 0:
            update = dict(progress=100, status=PROCESSED, total_process=0, time_exc=0)
            DataTempService.update_import(lib_import_id=self.lib_import_id, **update)
            return False
        return True

    def get_processing_errors(self, errors: dict = {}):
        rs = []
        for key in errors:
            item = {
                "code": key,
                "message": errors[key]
            }
            rs.append(item)
        return rs

    def process_file_import(self):
        """
        Implement raw files import
        :return:
        """
        #
        raws_process = []
        # get record valid
        has_rows_valid = self.fetch_rows_is_valid()
        if not has_rows_valid:
            return
        start_time = time.time()
        #
        for raw_instance in self.raws_import_process_queryset:
            logger.info(f"processing index raw : {raw_instance.index}")
            # import sale model and sales item model
            try:
                # validate data import with serializer_class
                raw, validated_data = self.validate_sale_item_import(data_map_config=raw_instance.data_map_config,
                                                                     raw_instance=raw_instance)
                if not validated_data:
                    self.number_process += 1
                    raws_process.append(raw_instance)
                    continue
                info = self.import_data_sale_item_module(validated_data=validated_data, client_id=self.client_id,
                                                         job_action=IMPORT_JOB)
                if info["process_ignored"]:
                    raw_instance.type = RAW_IGNORED_TYPE
                elif not info["sale_item_created"]:
                    raw_instance.type = RAW_UPDATED_TYPE
                raw_instance.processing_errors = []
                raw_instance.is_complete = True
            except Exception as ex:
                logger.error(f"[{self.__class__.__name__}]: {ex}")
                error = [
                    {
                        "code": "system",
                        "message": [str(ex)]
                    }
                ]
                raw_instance.processing_errors = error
                raw_instance.is_complete = False
            raw_instance.status = PROCESSED
            raw_instance.modified = timezone.now()
            self.number_process += 1
            raws_process.append(raw_instance)
            if len(raws_process) % plat_import_setting.bulk_process_size == 0:
                self.update_lib_import_process(raws_process)
                raws_process = []

        if len(raws_process) > 0:
            self.update_lib_import_process(raws_process)

        self.complete_process()
        time_exc = str(time.time() - start_time)
        DataTempService.update_import(lib_import_id=self.lib_import_id, time_exc=time_exc,
                                      process_completed=datetime.utcnow())

    def update_lib_import_process(self, raws_process):
        #
        self.bulk_process(ignore_conflicts=True)
        #
        RawDataTemporary.objects.bulk_update(objs=raws_process, fields=self.raws_import_fields_accept)
        #
        progress = float(self.number_process / self.total_records * 100)
        status = PROCESSED if progress == 100 else PROCESSING
        #
        update = dict(progress=progress, status=status, total_process=self.number_process)
        DataTempService.update_import(lib_import_id=self.lib_import_id, **update)

    def complete_process(self):
        # handle set sale status of Sale Obj
        self.reset_data_of_sale()
        count_dirty = SaleItem.all_objects.tenant_db_for(self.client_id).filter(dirty=True).count()
        if count_dirty > 0:
            flat_sale_items_bulks_sync_task(self.client_id)

            # Split sale item financial
            self.split_sale_item_financial_ws(marketplace=self.marketplace)
        #
        # if self.auto_prefetch_shipping_cost:
        #     ShippingCostBuilder.instance() \
        #         .with_sale_item_ids(self.sale_item_ids) \
        #         .with_chunk_size(5000) \
        #         .build_from_brand_settings() \
        #         .update()

    def reset_data_of_sale(self):
        """
        Reset sale status of sale eq min(sale status of sale item)
        :return:
        """
        sale_bulk = []
        log_entry_bulk = []
        sales = list(set(self.SALE_OBJS))
        for sale in sales:
            origin = copy.deepcopy(sale)
            # sale status
            item_sale_status_min = (sale.saleitem_set.tenant_db_for(sale.client_id).all()
                                    .order_by("sale_status__order").first())
            if item_sale_status_min:
                sale.sale_status = item_sale_status_min.sale_status
            # profit status
            item_sale_profit_min = (sale.saleitem_set.tenant_db_for(sale.client_id).all()
                                    .order_by("profit_status__order").first())
            if item_sale_profit_min:
                sale.profit_status = item_sale_profit_min.profit_status
            # sale date
            sale_item_min = sale.saleitem_set.tenant_db_for(sale.client_id).all().order_by("sale_date").first()
            if sale_item_min:
                sale.date = sale_item_min.sale_date
            #
            log_entry = (AuditLogCoreManager(client_id=self.client_id)
                         .create_log_entry_instance(level=SALE_LEVEL, origin=origin, target=sale,
                                                    action=LogEntry.Action.UPDATE))
            if log_entry:
                self.SALE_IDS.append(sale.pk)
                sale_bulk.append(sale)
        Sale.objects.tenant_db_for(self.client_id).bulk_update(sale_bulk, ["sale_status", "profit_status", "date"])
        LogClientEntry.objects.tenant_db_for(self.client_id).bulk_create(log_entry_bulk, ignore_conflicts=True)

    def add_bulk(self, sender: str = None, obj: any = None, created: bool = False, log_entry: dict = {}):
        if sender == LOG_ENTRY:
            index = obj.object_pk
        else:
            index = obj.pk
        if index and index not in self.BULK_OBJ[sender][INDEXES]:
            obj_type = INSERT if created else UPDATE
            self.BULK_OBJ[sender][INDEXES].append(index)
            self.BULK_OBJ[sender][obj_type].append(obj)
            if log_entry:
                self.BULK_OBJ[LOG_ENTRY].append(log_entry)

    def add_sale_objs_reset(self):
        sale_chunk_ids = self.BULK_OBJ[SALE_KEY][INSERT] + self.BULK_OBJ[SALE_KEY][UPDATE]
        self.SALE_OBJS += sale_chunk_ids

    def bulk_process(self, ignore_conflicts: bool = False):
        with transaction.atomic():
            self.add_sale_objs_reset()
            # insert sale
            # Sale.objects.tenant_db_for(self.client_id).bulk_create(self.BULK_OBJ[SALE_KEY][INSERT])
            #
            # fields_update = [i.name for i in Sale._meta.fields if i.name not in ["pk", "id"]]
            # print(fields_update)
            # Sale.objects.tenant_db_for(self.client_id).bulk_update(self.BULK_OBJ[SALE_KEY][INSERT], fields=fields_update)

            # sale charge and cost
            if len(self.BULK_OBJ[SALE_CHARGE_AND_COST_KEY][INSERT]) > 0:
                SaleChargeAndCost.all_objects.tenant_db_for(self.client_id).bulk_create(
                    self.BULK_OBJ[SALE_CHARGE_AND_COST_KEY][INSERT], ignore_conflicts=ignore_conflicts)
            #
            if len(self.BULK_OBJ[SALE_CHARGE_AND_COST_KEY][UPDATE]) > 0:
                fields_update = [i.name for i in SaleChargeAndCost._meta.fields if i.name not in ["pk", "id"]]
                SaleChargeAndCost.all_objects.tenant_db_for(self.client_id).bulk_update(
                    self.BULK_OBJ[SALE_CHARGE_AND_COST_KEY][UPDATE], fields=fields_update)

            # sale item
            if len(self.BULK_OBJ[SALE_ITEM_KEY][INSERT]) > 0:
                SaleItem.all_objects.tenant_db_for(self.client_id).bulk_create(self.BULK_OBJ[SALE_ITEM_KEY][INSERT],
                                                                               ignore_conflicts=ignore_conflicts)
            if len(self.BULK_OBJ[SALE_ITEM_KEY][UPDATE]) > 0:
                SaleItem.all_objects.tenant_db_for(self.client_id).bulk_update(self.BULK_OBJ[SALE_ITEM_KEY][UPDATE],
                                                                               fields=self.sale_items_fields_accept)

            # insert log entry
            if len(self.BULK_OBJ[LOG_ENTRY]) > 0:
                LogClientEntry.objects.tenant_db_for(self.client_id).bulk_create(self.BULK_OBJ[LOG_ENTRY],
                                                                                 ignore_conflicts=ignore_conflicts)

        # split financial event
        # @TODO: using split sale item financial by sale_item_ids
        # self.split_sale_item_financial_ws(sale_item_ids=self.BULK_OBJ[SALE_ITEM_KEY][INDEXES])
        #
        self.init_bulk_config()

    def split_sale_item_financial_ws(self, marketplace: str = None, sale_item_ids: List[str] = None):
        try:
            if not bool(sale_item_ids):
                sale_item_ids = []

            meta = dict(client_id=self.client_id, sale_item_ids=sale_item_ids)

            if bool(sale_item_ids):
                hash_content = hashlib_content(meta)
                name = f"split_sale_item_financial_ws_{hash_content}"
            else:
                meta.update(
                    dict(
                        marketplace=marketplace
                    )
                )
                name = f"split_sale_item_financial_ws_{self.marketplace}"

            data = dict(
                name=name,
                job_name="app.financial.jobs.sale_financial.handler_trigger_split_sale_item_financial_ws",
                module="app.financial.jobs.sale_financial",
                method="handler_trigger_split_sale_item_financial_ws",
                meta=meta
            )
            register(category=SYNC_ANALYSIS_CATEGORY, client_id=self.client_id, **data, mode_run=MODE_RUN_IMMEDIATELY)
        except Exception as ex:
            logger.error(
                f"[{self.__class__.__name__}][{self.marketplace}][split_sale_item_financial_ws]: {ex}"
            )

    def get_pop_validated_data(self, validated_data: dict, field: str):
        try:
            return validated_data.pop(field)
        except Exception as ex:
            return None

    def has_change_sale_status_item(self, sale_status_origin, sale_status_target):
        if sale_status_origin is not None and sale_status_target is not None and \
                sale_status_origin != sale_status_target:
            return True
        return False

    def import_data_sale_item_module(self, validated_data: dict = {}, **kwargs):
        with transaction.atomic():
            #
            sale_status_origin = validated_data.get("sale_status", None)
            #
            sale_data = {
                "client": self.client
            }
            for field in self.sale_fields_accept:
                try:
                    val = validated_data.pop(field)
                    sale_data.update({field: val})
                except Exception as ex:
                    continue

            context = {"kwargs": kwargs}

            #
            sale, sale_log, is_sale_created = ClientSaleSerializer(context=context).process_import(sale_data)

            #
            sale_cost_data = {
                "sale": sale
            }
            sale_cost, sale_cost_log, is_sale_cost_created = ClientSaleChargeAndCostSerializer(
                context=context).process_import(sale_cost_data)

            #
            validated_data.update({"sale": sale, "client": self.client})
            sale_item, sale_item_log, is_sale_item_created = ClientSaleItemSerializer(context=context).process_import(
                validated_data=validated_data)

            self.add_bulk(SALE_CHARGE_AND_COST_KEY, sale_cost, is_sale_cost_created, sale_cost_log)

            if sale_item_log:
                self.add_bulk(SALE_ITEM_KEY, sale_item, is_sale_item_created, sale_item_log)
                #
                if self.has_change_sale_status_item(sale_status_origin, sale_item.sale_status):
                    # check sale status item has change for reset sale orders
                    self.add_bulk(SALE_KEY, sale, False, {})

            # add log and bulk when process import complete
            if sale_log:
                sale.saleitem_set.tenant_db_for(sale.client_id).all().update(dirty=True)
                self.add_bulk(SALE_KEY, sale, is_sale_created, sale_log)

            # make flag for tracking created or updated in import file
            is_no_changes = [sale_log == {} or sale_log is None, sale_cost_log == {} or sale_cost_log is None,
                             sale_item_log == {} or sale_item_log is None]

            info = {
                "sale_item_created": is_sale_item_created,
                "process_ignored": all(is_no_changes)
            }
            return info

    def handler_replacement_sales_replacement(self, channel_sale_ids: list = [], **kwargs):
        try:
            assert len(channel_sale_ids) > 0, "Channel Sale IDs removed is not empty"
            #
            channel_marketplace = self.get_channel_marketplace()
            logger.debug(
                f"[{self.__class__.__name__}][{self.marketplace}][handler_replacement_sales_replacement]"
                f"[{channel_marketplace}]: Channel Sale IDs = {channel_sale_ids}"
            )
            sale_items_queryset = SaleItem.all_objects.tenant_db_for(self.client_id) \
                .filter(sale__channel=channel_marketplace, sale__channel_sale_id__in=channel_sale_ids, is_removed=False)
            #
            if sale_items_queryset.count() > 0:
                sale_item_ids = list(sale_items_queryset.values_list("pk", flat=True))
                logger.debug(
                    f"[{self.__class__.__name__}][{self.marketplace}][handler_replacement_sales_replacement]: "
                    f"sale_item_ids = {sale_item_ids}"
                )
                sale_items_queryset.update(is_removed=True, dirty=True, financial_dirty=True, modified=timezone.now())
                # split financial event
                self.split_sale_item_financial_ws(sale_item_ids=sale_item_ids)
            #
            sale_queryset = Sale.all_objects.tenant_db_for(self.client_id) \
                .filter(channel=channel_marketplace, channel_sale_id__in=channel_sale_ids, is_removed=False)
            if sale_queryset.count() > 0:
                sale_queryset.update(is_removed=True, modified=timezone.now())
        except Exception as ex:
            logger.error(
                f"[{self.__class__.__name__}][{self.marketplace}][handler_replacement_sales_replacement]: {ex}"
            )
