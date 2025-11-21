import copy
import json
import logging
import sys
from time import sleep
from rest_framework import status
from app.core.utils import hashlib_content
from app.core.variable.marketplace import CHANNEL_DEFAULT
from app.financial.import_template.validation.sale_item import decimal_fields, fields as fields_sale_items
from app.financial.models import DataFlattenTrack
from app.financial.services.imports import ImportDataModuleService, SALE_ITEM_KEY, INDEXES
from app.financial.services.integrations.base import IntegrationFinancialBase
from app.financial.variable.job_status import LIVE_FEED_JOB, POSTED_FILTER_MODE
from app.financial.services.utils.common import round_currency
from app.financial.sub_serializers.sale_item_import_serializer import SaleItemsImportLiveFeedSerializer
from app.core.variable.pf_trust_ac import TIME_CONTROL_LOG_TYPE
from app.financial.services.fedex_shipment.config import REOPEN_BY_SALE_STATUS
from app.financial.variable.shipping_cost_source import SHIPPING_COST_ACCURACY_BY_SOURCE, AMZ_SELLER_CENTRAL_SOURCE_KEY
from app.job.utils.helper import register
from app.job.utils.variable import SYNC_ANALYSIS_CATEGORY

logger = logging.getLogger(__name__)


class SaleItemsLiveFeedManager(IntegrationFinancialBase):
    JOB_TYPE = LIVE_FEED_JOB

    def __init__(self, client_id: str, flatten: DataFlattenTrack = None, marketplace: str = CHANNEL_DEFAULT, **kwargs):
        super().__init__(client_id=client_id, flatten=flatten,
                         marketplace=marketplace, **kwargs)
        # init object import manage
        self.import_manage = ImportDataModuleService(client_id=self.client_id, marketplace=marketplace)
        #
        self.log_feed = self._init_log()
        self.limit_size_request = self.get_limit_size()

    def get_limit_size(self):
        return self.LIMIT_SIZE

    def validated_data(self, data):
        context = {"kwargs": {"client_id": self.client_id}}
        serializer = SaleItemsImportLiveFeedSerializer(
            context=context, data=data)
        serializer.is_valid()
        errors = serializer.errors
        return serializer.validated_data, errors

    def normalize_data_item(self, item):
        # Map product_info to item
        product_info = item.get("product_info", {})
        if product_info is not None:
            # Map Brand to item
            # if product_info.get("brand") is not None:
            #     item["brand"] = product_info.get("brand")
            # Map UPC to item -> upc or ean value if exists
            if product_info.get("upc") is not None:
                item["upc"] = product_info.get("upc")
            elif product_info.get("ean") is not None:
                item["upc"] = product_info.get("ean")
            # Map Color to item
            if product_info.get("color") is not None:
                item["style"] = product_info.get("color")
            # Map Size to item
            if product_info.get("size") is not None:
                item["size"] = product_info.get("size")

        # get info address lines

        address_line = item.get("address_line", {})
        if address_line:
            if isinstance(address_line, str):
                item["address_line_1"] = address_line
            else:
                positions = [1, 2, 3]
                for position in positions:
                    column = f"address_line_{position}"
                    try:
                        val = address_line[column]
                        item[column] = val
                    except KeyError:
                        continue

        # packages
        try:
            packages = item.get("packages", [])
            if packages:
                tracking_fedex_ids = set()
                ship_carriers = set()
                for package in packages:
                    tracking_fedex_ids.add(package["tracking_id"])
                    ship_carriers.add(package["ship_carrier"])
                #
                tracking_fedex_id = " , ".join(
                    sorted(filter(None, tracking_fedex_ids)))
                ship_carrier = " , ".join(sorted(filter(None, ship_carriers)))
                #
                item.update({"tracking_fedex_id": tracking_fedex_id})
                item.update({"ship_carrier": ship_carrier})
        except Exception as ex:
            logger.debug(f"[{self.__class__.__name__}] {ex}")

        #
        for field in fields_sale_items:
            if field not in item:
                continue
            # round currency
            if field in decimal_fields:
                try:
                    val = item[field]
                    item[field] = round_currency(val)
                except TypeError:
                    pass

        item = self.calculate_sale_charged(item)
        item = self.calculate_shipping_cost(item)
        item = self.calculate_parent_asins(item)
        return item

    @classmethod
    def calculate_parent_asins(cls, item):
        try:
            assert "parent_asins" in item, f"The parent_asins is in item"

            parent_asins = copy.deepcopy(item["parent_asins"])
            del item["parent_asins"]

            assert isinstance(parent_asins, list), f"The parent_asins is list"
            parent_asins = set(parent_asins)
            parent_asins = " , ".join(sorted(filter(None, parent_asins)))
            item.update({"parent_asin": parent_asins})
        except Exception as ex:
            logger.debug(f"[{cls.__class__.__name__}][calculate_parent_asins] : {ex}")
        return item

    @classmethod
    def calculate_shipping_cost(cls, item):
        try:
            shipping_cost = item.get("shipping_cost")
            if shipping_cost is not None:
                item["estimated_shipping_cost"] = shipping_cost
                item["shipping_cost_accuracy"] = SHIPPING_COST_ACCURACY_BY_SOURCE[AMZ_SELLER_CENTRAL_SOURCE_KEY]
                del item["shipping_cost"]
        except Exception as ex:
            logger.debug(f"[{cls.__class__.__name__}][calculate_shipping_cost] : {ex}")
        return item

    @classmethod
    def calculate_sale_charged(cls, item):
        try:
            sale_charged = item.get("sale_charged", 0)
            if sale_charged is None:
                sale_charged = 0
            if sale_charged > 0:
                item["sale_charged_accuracy"] = 100
                return item
            sale_charged_est = item.get("sale_charged_est", 0)
            if sale_charged_est is None:
                sale_charged_est = 0
            sale_charged_est = round_currency(sale_charged_est)
            if not sale_charged and sale_charged_est > 0:
                item["sale_charged"] = sale_charged_est
                item["sale_charged_accuracy"] = 80
        except Exception as ex:
            logger.debug(f"[{cls.__class__.__name__}][calculate_shipping_cost] : {ex}")
        return item

    def _write_log_process(self):
        if self.log_type == TIME_CONTROL_LOG_TYPE:
            self._write_log_to_time_control(log_data=self.log_feed)
        else:
            self._write_log_to_flatten()

    def _write_log_to_flatten(self):
        try:
            track_logs = self.kwargs.get("track_logs", False)
            if not track_logs:
                return
            #
            self._refresh_flatten_track()
            self.set_last_run_flatten_track()
            self.flatten_track.log_feed = json.dumps(self.log_feed)
            # self.flatten_track.save()
            DataFlattenTrack.objects.tenant_db_for(self.client_id).bulk_update([self.flatten_track],
                                                                               fields=["last_run", "log_feed"])
        except Exception as ex:
            logger.debug(f"[{self.__class__.__name__}][{self.client_id}][_write_log_to_flatten] : {ex}")

    def _write_errors_request(self, status_code, content):

        track_logs = self.kwargs.get("track_logs", False)

        if not track_logs:
            return

        content = f"[ACManager] __handler_result error: {content}"
        self.log_feed.get("errors").update(
            {"{}".format(self.time_tracking): content})
        self._write_log_process()

    def _add_log_to_flatten(self, page: int = 1):

        track_logs = self.kwargs.get("track_logs", False)

        if not track_logs:
            return

        logger.info(
            f"[{self.client_id}][{self.marketplace}][{self.JOB_TYPE}][{self.filter_mode}][{self.time_tracking}]"
            f"[size memory][page: {page}] {sys.getsizeof(self.import_manage.BULK_OBJ)}"
        )

        ids = self.import_manage.BULK_OBJ[SALE_ITEM_KEY][INDEXES]
        #
        if len(ids) > 0:
            self.log_feed.get("success").update(
                {f"{self.time_tracking} - [page:{page}]": ids})
        if len(self._errors) > 0:
            self.log_feed.get("errors").update(
                {f"{self.time_tracking} - [page:{page}]": self._errors})

    def _get_data_request(self, page: int = 1):
        try:
            query_params = {
                "marketplace": self.marketplace,
                "page": page,
                "limit": self.limit_size_request
            }
            if self.is_replacement_order is not None:
                query_params.update({"is_replacement_order": self.is_replacement_order})
            self.prefetch_query_params(query_params)
            rs = self.ac_manager.get_sale_items(
                sc_method=self.sc_method, **query_params)
            data = self._handler_result(rs)
            return data
        except Exception as ex:
            content = str(ex)
            self._write_errors_request(status.HTTP_400_BAD_REQUEST, content)
            return {}

    @property
    def amazon_order_ids(self):
        return self.kwargs.get("amazon_order_ids", [])

    def prefetch_query_params(self, query_params: dict):
        if self.amazon_order_ids:
            query_params.update({"channel_sale_id": self.amazon_order_ids})
        #
        else:
            # check mode filter date ranges
            if self.filter_mode == POSTED_FILTER_MODE:
                query_params.update(
                    {"purchase_date_from": self.from_date, "purchase_date_to": self.to_date})
            else:
                query_params.update(
                    {"from": self.from_date, "to": self.to_date})

    def progress(self):
        page_info = self._get_data_request()

        if not page_info:
            return
        kwargs_info = [self.client_id, self.marketplace, self.JOB_TYPE, self.filter_mode, self.time_tracking]
        if self.is_replacement_order:
            kwargs_info.append("replacement_order")
        # save last run
        self._write_log_process()

        page_info.pop("items")
        logger.info(f"[{']['.join(kwargs_info)}] : Page count info : {page_info}")

        page_count = page_info.get("page_count")

        if page_count == 0:
            return

        for i in range(page_count):

            page = i + 1

            data = {}

            # connect timeout and read timeout limit
            while not data:
                sleep(2)
                logger.info(f"[{']['.join(kwargs_info)}][{page_count}] Retry get data page {page} ...")
                data = self._get_data_request(page=page)

            items = data.get("items")
            self._processing(items)

            self.bulk_process(page=page)

            logger.info(f"[{']['.join(kwargs_info)}][{page_count}] Exec page {page} completed")
        #
        self.import_manage.complete_process()
        #
        if len(self.import_manage.SALE_IDS) > 0:
            # clean sale id duplicate
            sale_ids = list(set(self.import_manage.SALE_IDS))
            self.reopen_fedex_by_sale_status(sale_ids)

        self._write_log_process()

        #
        # self.complete_process()

    def complete_process(self):
        pass

    def reopen_fedex_by_sale_status(self, sale_ids: [int]):
        # reopen fedex by sale status
        meta = dict(client_id=self.client_id, marketplace=self.marketplace, reopen_action=REOPEN_BY_SALE_STATUS,
                    obj_ids=sale_ids)
        hash_content = hashlib_content(meta)
        data = dict(
            name=f"reopen_fedex_by_sale_status_{hash_content}",
            job_name="app.financial.jobs.fedex_shipment.sale_item_reopen_fedex_shipment_job",
            module="app.financial.jobs.fedex_shipment",
            method="sale_item_reopen_fedex_shipment_job",
            meta=meta
        )
        register(category=SYNC_ANALYSIS_CATEGORY, client_id=self.client_id, **data)

    def bulk_process(self, page: int = 1):
        try:
            self._add_log_to_flatten(page)
            self.import_manage.bulk_process(ignore_conflicts=True)
        except Exception as ex:
            logger.error(
                f"[{self.client_id}][{self.marketplace}][{self.JOB_TYPE}][{self.filter_mode}]"
                f"[{self.time_tracking}][bulk_process] : {ex}"
            )
            errors = {
                "key": "bulk_process_live_feed",
                "msg": str(ex)
            }
            self._errors.append(errors)

    def _processing(self, data):
        if self.is_replacement_order is True:
            self._processing_replacement_items(data)
        else:
            self._processing_items(data)

    def _processing_items(self, data):
        for item in data:
            #
            normalize_data = self.normalize_data_item(copy.deepcopy(item))
            try:
                assert len(normalize_data) > 0, f"[{item['channel_sale_id']}] normalize data item invalid"
                validated_data, errors = self.validated_data(normalize_data)
                if errors:
                    msg = self.import_manage.get_processing_errors(errors)
                    info = {
                        "job_type": self.JOB_TYPE,
                        "key": normalize_data.get("channel_sale_id"),
                        "marketplace": self.marketplace,
                        "errors": msg
                    }
                    self._errors.append(info)
                    continue

                kwargs = self._context_serializer["kwargs"]

                self.import_manage.import_data_sale_item_module(validated_data=validated_data, **kwargs)
            except Exception as ex:
                logger.debug(
                    f"[{self.client_id}][{self.marketplace}][{self.JOB_TYPE}][{self.filter_mode}]"
                    f"[{self.time_tracking}][_processing_items] : {ex}"
                )
                info = {
                    "job_type": self.JOB_TYPE,
                    "key": normalize_data.get("channel_sale_id"),
                    "marketplace": self.marketplace,
                    "errors": str(ex)
                }
                self._errors.append(info)
                continue

    def _processing_replacement_items(self, data):
        kwargs = self._context_serializer["kwargs"]
        channel_sale_ids = [item["replaced_order_id"] for item in data if "replaced_order_id" in item]
        logger.debug(
            f"[{self.client_id}][{self.marketplace}][{self.JOB_TYPE}][{self.filter_mode}][{self.time_tracking}]"
            f"[_processing_replacement_items] channel_sale_ids = {channel_sale_ids}"
        )
        self.import_manage.handler_replacement_sales_replacement(channel_sale_ids=channel_sale_ids, **kwargs)
