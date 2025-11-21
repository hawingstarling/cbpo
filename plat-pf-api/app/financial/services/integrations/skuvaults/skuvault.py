import logging
import itertools
from django.utils import timezone
from typing import List, Union
import maya
from django.core.paginator import Paginator
from django.db.models import Q, Value, CharField, QuerySet
from django.db.models.functions import Cast, Concat
from rest_framework import status
from app.core.variable.marketplace import CHANNEL_DEFAULT
from app.financial.jobs.data_flatten import flat_sale_items_bulks_sync_task
from app.financial.utils.shipping_cost_helper import separate_shipping_cost_by_data
from app.financial.variable.brand_setting import EVALUATED_SHIPPING_COST_ACCURACY_SPECIFIC_BRAND_MFN_PRIME
from app.financial.variable.fulfillment_channel import FulfillmentChannelEnum
from app.financial.variable.fulfillment_type import FULFILLMENT_MFN_PRIME_ACCURACY_DEFAULT
from app.financial.variable.job_status import SKU_VAULT_JOB, CART_ROVER_JOB, CONNECT_3Pl_CENTRAL_JOB
from app.financial.services.integrations.live_feed import SaleItemsLiveFeedManager
from app.financial.models import SaleItem, DataFlattenTrack, SaleStatus, SKUVaultPrimeTrack, Sale, LogClientEntry, \
    FulfillmentChannel
from app.core.variable.sc_method import SKUVAULT_CONNECT_METHOD, CART_ROVER_CONNECT_METHOD, \
    THIRD_PARTY_LOGISTIC_CONNECT_METHOD
from app.financial.variable.shipping_cost_source import BRAND_SETTING_SOURCE_KEY
from app.financial.variable.sku_vault import SIMILAR_STATUS, DIFFERENT_STATUS, SKUVAULT_SOURCE, CART_ROVER_SOURCE, \
    THIRD_PARTY_LOGISTIC_SOURCE
from django.db import transaction

#
SKU_VAULT_PRIME_TYPE = "prime"
SKU_VAULT_CHANNEL_SALE_ID_TYPE = "channel_id"
SKU_VAULT_TYPE = "sku"
#
SALE_LEVEL_KEY = "SALE_LEVEL"
SALE_ITEM_LEVEL_KEY = "SALE_ITEM_LEVEL"
SKU_VAULT_PRIME_TRACK_LEVEL_KEY = "SKU_VAULT_PRIME_TRACK_LEVEL"
LOG_ENTRY = "LOG_ENTRY"
INDEXES = "INDEXES"
INSERT = "INSERT"
UPDATE = "UPDATE"

logger = logging.getLogger(__name__)


class SaleSKUVaultManager(SaleItemsLiveFeedManager):
    JOB_TYPE = SKU_VAULT_JOB

    def __init__(self, client_id: str, flatten: DataFlattenTrack = None, marketplace: str = CHANNEL_DEFAULT, **kwargs):
        super().__init__(client_id=client_id, flatten=flatten, marketplace=marketplace, **kwargs)
        self.fulfillment_channel_prime = FulfillmentChannel.objects.tenant_db_for(self.client_id) \
            .get(name=FulfillmentChannelEnum.MFN_PRIME.value)
        self.BULK_OBJ = {}
        self.init_bulk_config()
        self.time_now = timezone.now()

    def init_bulk_config(self):
        self.BULK_OBJ = {
            SALE_LEVEL_KEY: {
                INDEXES: [],
                UPDATE: []
            },
            SALE_ITEM_LEVEL_KEY: {
                INDEXES: [],
                UPDATE: []
            },
            SKU_VAULT_PRIME_TRACK_LEVEL_KEY: [],
            LOG_ENTRY: [],
        }

    def add_obj_to_bulk(
            self, sender: Union[SALE_LEVEL_KEY, SALE_ITEM_LEVEL_KEY, SKU_VAULT_PRIME_TRACK_LEVEL_KEY, LOG_ENTRY],
            obj: Union[Sale, SaleItem, SKUVaultPrimeTrack, LogClientEntry]
    ):
        if sender in [SKU_VAULT_PRIME_TRACK_LEVEL_KEY, LOG_ENTRY]:
            self.BULK_OBJ[sender].append(obj)
            return
        index = obj.pk
        if index and index not in self.BULK_OBJ[sender][INDEXES]:
            self.BULK_OBJ[sender][INDEXES].append(index)
            self.BULK_OBJ[sender][UPDATE].append(obj)

    @property
    def is_override(self):
        return self.kwargs.get('override', False)

    def _get_data_request(self, page: int = 1):
        try:
            query_params = {
                "marketplace": self.marketplace,
                "type": SKU_VAULT_PRIME_TYPE,
                "id_type": SKU_VAULT_CHANNEL_SALE_ID_TYPE,
                # "page": page, 
                # "limit": self.limit_size_request
            }

            #
            self.prefetch_query_params(query_params)
            #
            if self.JOB_TYPE == SKU_VAULT_JOB:
                sc_method = SKUVAULT_CONNECT_METHOD
            elif self.JOB_TYPE == CART_ROVER_JOB:
                sc_method = CART_ROVER_CONNECT_METHOD
            elif self.JOB_TYPE == CONNECT_3Pl_CENTRAL_JOB:
                sc_method = THIRD_PARTY_LOGISTIC_CONNECT_METHOD
            else:
                sc_method = None
            rs = self.ac_manager.get_prime_fulfillment_type_integration_method(sc_method=sc_method, **query_params)
            data = self._handler_result(rs)
            return data
        except Exception as ex:
            content = str(ex)
            kwargs_info = [self.client_id, self.marketplace, self.JOB_TYPE, self.filter_mode, self.time_tracking]
            logger.error(f"[{']['.join(kwargs_info)}]: {content}")
            self._write_errors_request(status.HTTP_400_BAD_REQUEST, content)
            return {}

    @property
    def channel_sale_ids(self):
        return self.kwargs.get('channel_sale_ids', [])

    @property
    def sale_item_ids(self):
        return self.kwargs.get('sale_item_ids', [])

    @property
    def sku_ids(self):
        return self.kwargs.get('sku_list', [])

    def prefetch_query_params(self, query_params: dict):
        # check has request channel sale ids
        query_params.update({"ids": self.channel_sale_ids})
        #
        if len(self.bulk_channel_sale_ids) == 0:
            query_params.update({"sale_date_from": self.from_date, "sale_date_to": self.to_date})

    def get_sale_status(self, name: str):
        return SaleStatus.objects.tenant_db_for(self.client_id).get(name=name)

    @property
    def base_condition(self):
        return Q(sale__channel=self.channel, fulfillment_type__name__startswith='MFN')

    def _get_queryset(self):
        #
        if not self.is_override:
            cond_verify_is_prime = ~Q(fulfillment_type_accuracy=100) \
                                   | Q(fulfillment_type_accuracy__isnull=True) \
                                   | Q(sale__is_prime=False)
        else:
            cond_verify_is_prime = Q()
        # is bulk sync data
        if len(self.sale_item_ids) > 0:
            logger.debug(f"[{self.__class__.__name__}][sale_item_ids]: {self.sale_item_ids}")
            cond_filter_ranges = Q(pk__in=self.sale_item_ids)
        elif len(self.bulk_channel_sale_ids) > 0:
            logger.debug(f"[{self.__class__.__name__}][bulk_channel_sale_ids]: {self.bulk_channel_sale_ids}")
            cond_filter_ranges = Q(sale__channel_sale_id__in=self.bulk_channel_sale_ids)
        else:
            cond_filter_ranges = Q(
                sale_date__gte=maya.parse(self.from_date).datetime(), sale_date__lte=maya.parse(self.to_date).datetime()
            )
        #
        cond = self.base_condition & cond_verify_is_prime & cond_filter_ranges
        queryset = SaleItem.objects.tenant_db_for(self.client_id).filter(cond)
        return queryset

    def set_ids_type_progress(self, objs: List[SaleItem]):
        channel_sale_ids = set()
        for obj in objs:
            channel_sale_ids.add(obj.sale.channel_sale_id)
        self.kwargs.update({"channel_sale_ids": list(channel_sale_ids)})

    @property
    def bulk_channel_sale_ids(self):
        return self.kwargs.get('bulk_channel_sale_ids', [])

    def progress(self):
        queryset = self._get_queryset()
        if queryset.count() == 0:
            logger.error(
                f"[{self.client_id}][{self.marketplace}][{self.JOB_TYPE}]"
                f"[{self.filter_mode}][{self.time_tracking}] "
                f"not found records sale status for update..."
            )
            return
        queryset = queryset.order_by("-sale_date")
        pages = Paginator(queryset, 100)
        num_pages = pages.num_pages
        logger.debug(
            f"[{self.client_id}][{self.marketplace}][{self.JOB_TYPE}][{self.filter_mode}][{self.time_tracking}]"
            f"[count: {pages.count}] [num_pages: {num_pages}]"
        )
        for i in range(num_pages):
            page = i + 1
            self.set_ids_type_progress(pages.page(number=page).object_list)
            #
            rs = self._get_data_request()
            if not rs or not rs.get("items"):
                logger.error(
                    f"[{self.client_id}][{self.marketplace}][{self.JOB_TYPE}]"
                    f"[{self.filter_mode}][{self.time_tracking}][{num_pages}] "
                    f"Not found items valid page {page}"
                )
                continue
            data = rs.get("items")
            sale_items, keys_mapping_items, sale_prime_ids, sale_brand_setting_source = self.__prefetch_items_mapping(
                data)
            if sale_items.count() == 0:
                logger.error(
                    f"[{self.client_id}][{self.marketplace}][{self.JOB_TYPE}]"
                    f"[{self.filter_mode}][{self.time_tracking}][{num_pages}] "
                    f"Not found keys mapping comparing page {page}"
                )
                continue

            self.__process_data_page(sale_items, keys_mapping_items, sale_prime_ids, sale_brand_setting_source)
            self.bulk_process(page=page)
            logger.info(
                f"[{self.client_id}][{self.marketplace}][{self.JOB_TYPE}]"
                f"[{self.filter_mode}][{self.time_tracking}][{num_pages}] "
                f"Exec page {page} completed"
            )

        self.process_complete()

    def _mapping_routing_info(self, sale_item: SaleItem, data: dict, validated_data: dict):
        try:
            assert sale_item.ship_carrier is None or not sale_item.tracking_fedex_id is None, \
                f"The sale item has enough routing info"
            routing_info = data.get("routing_info", {})
            assert len(routing_info) > 0, f"The routing info is empty"
            carrier = routing_info.get("carrier")
            tracking_number = routing_info.get("tracking_number")
            if sale_item.ship_carrier is None and carrier is not None:
                validated_data.update(dict(ship_carrier=carrier))
            if sale_item.tracking_fedex_id is None and tracking_number is not None:
                validated_data.update(dict(tracking_fedex_id=tracking_number))
        except Exception as ex:
            logger.debug(
                f"[{self.__class__.__name__}][_mapping_routing_info][{self.client_id}][{self.JOB_TYPE}]"
                f"[{sale_item.pk}] {ex}"
            )

    def _mapping_accuracy_of_esc(self, sale_item: SaleItem, key_mapping: str, sale_brand_setting_sources: list,
                                 validated_data: dict):
        if key_mapping in sale_brand_setting_sources \
                and sale_item.estimated_shipping_cost is not None \
                and sale_item.shipping_cost_accuracy is not None \
                and sale_item.shipping_cost_accuracy < 100 \
                and sale_item.shipping_cost_source in [BRAND_SETTING_SOURCE_KEY]:
            validated_data.update(
                {
                    "estimated_shipping_cost": sale_item.estimated_shipping_cost,
                    "shipping_cost_accuracy": EVALUATED_SHIPPING_COST_ACCURACY_SPECIFIC_BRAND_MFN_PRIME
                }
            )
            separate_shipping_cost_by_data(self.client_id, sale_item, validated_data, self.JOB_TYPE)

    def __process_data_page(self, sale_items: QuerySet, keys_mapping_items: dict, sale_prime_ids: list,
                            sale_brand_setting_sources: list):
        for sale_item in sale_items.order_by("sale_date"):
            try:
                channel_sale_id = sale_item.sale.channel_sale_id
                sku = sale_item.sku
                key_mapping = f"{channel_sale_id}_$_{sku}"
                rs_data = keys_mapping_items[f"{channel_sale_id}_$_{sku}"]
                #
                validated_data = dict(
                    is_prime=True,
                    fulfillment_type=self.fulfillment_channel_prime,
                    fulfillment_type_accuracy=FULFILLMENT_MFN_PRIME_ACCURACY_DEFAULT,
                    warehouse_processing_fee=0,
                    warehouse_processing_fee_accuracy=0
                )
                self._mapping_accuracy_of_esc(sale_item, key_mapping, sale_brand_setting_sources, validated_data)
                self._mapping_routing_info(sale_item, rs_data, validated_data)
                #
                sale = sale_item.sale
                fields_update = ["is_prime"]
                obj, obj_log = self._set_object_fields_change(sale, fields_update, validated_data)
                if obj_log:
                    self.add_obj_to_bulk(SALE_LEVEL_KEY, obj)
                    self.add_obj_to_bulk(LOG_ENTRY, obj_log)
                #
                fields_update = [
                    "fulfillment_type",
                    "fulfillment_type_accuracy",
                    "warehouse_processing_fee",
                    "warehouse_processing_fee_accuracy",
                    "shipping_cost_accuracy",
                    "ship_carrier",
                    "tracking_fedex_id"
                ]
                fields_properties = {
                    "fulfillment_type": {
                        "attribute": "name",
                        "default": None
                    }
                }
                obj, obj_log = self._set_object_fields_change(sale_item, fields_update, validated_data,
                                                              fields_properties)
                if obj_log:
                    self.add_obj_to_bulk(SALE_ITEM_LEVEL_KEY, obj)
                    self.add_obj_to_bulk(LOG_ENTRY, obj_log)
                #
                tracking_prime_status = SIMILAR_STATUS if channel_sale_id in sale_prime_ids else DIFFERENT_STATUS
                self.create_tracking_prime(channel_sale_id, tracking_prime_status)
            except Exception as ex:
                logger.debug(
                    f"[{self.__class__.__name__}][__process_data_page][{self.client_id}][{self.JOB_TYPE}]"
                    f"[{sale_item.pk}] {ex}"
                )

    def create_tracking_prime(self, channel_sale_id: str,
                              tracking_status: Union[SIMILAR_STATUS, DIFFERENT_STATUS] = DIFFERENT_STATUS):
        try:
            SKUVaultPrimeTrack.all_objects.tenant_db_for(self.client_id).get(channel_sale_id=channel_sale_id,
                                                                             channel_id=self.channel.pk,
                                                                             client_id=self.client_id)
        except SKUVaultPrimeTrack.DoesNotExist:
            obj = SKUVaultPrimeTrack(channel_sale_id=channel_sale_id, channel=self.channel, client=self.client,
                                     status=tracking_status)
            if self.JOB_TYPE == SKU_VAULT_JOB:
                obj.source = SKUVAULT_SOURCE
            elif self.JOB_TYPE == CART_ROVER_JOB:
                obj.source = CART_ROVER_SOURCE
            elif self.JOB_TYPE == CONNECT_3Pl_CENTRAL_JOB:
                obj.source = THIRD_PARTY_LOGISTIC_SOURCE
            else:
                pass
            self.add_obj_to_bulk(SKU_VAULT_PRIME_TRACK_LEVEL_KEY, obj)
        except Exception as ex:
            logger.debug(f"[{self.__class__.__name__}][create_tracking_prime][{channel_sale_id}] {ex}")

    def process_complete(self):
        count_dirty = (
            SaleItem.objects.tenant_db_for(self.client_id).filter(client_id=self.client_id, dirty=True).count()
        )
        if count_dirty > 0:
            transaction.on_commit(
                lambda: flat_sale_items_bulks_sync_task(self.client_id),
                using=self.client_db
            )

    def bulk_process(self, page: int = 1):
        with transaction.atomic():
            Sale.objects.tenant_db_for(self.client_id).bulk_update(
                self.BULK_OBJ[SALE_LEVEL_KEY][UPDATE], fields=["is_prime", "modified"]
            )
            SaleItem.all_objects.tenant_db_for(self.client_id).bulk_update(
                self.BULK_OBJ[SALE_ITEM_LEVEL_KEY][UPDATE],
                fields=["fulfillment_type", "fulfillment_type_accuracy", "warehouse_processing_fee",
                        "warehouse_processing_fee_accuracy", "shipping_cost_accuracy", "ship_carrier",
                        "tracking_fedex_id", "dirty", "financial_dirty", "modified"]
            )
            # Log entry of sale level
            LogClientEntry.objects.tenant_db_for(self.client_id).bulk_create(
                self.BULK_OBJ[LOG_ENTRY], ignore_conflicts=True
            )
            #
            SKUVaultPrimeTrack.objects.tenant_db_for(self.client_id).bulk_create(
                self.BULK_OBJ[SKU_VAULT_PRIME_TRACK_LEVEL_KEY], ignore_conflicts=True
            )
        # reset config bulk
        self.init_bulk_config()

    def __prefetch_items_mapping(self, data: List[dict]):
        channel_sale_ids = []
        sku_list = set()
        keys_mapping_items = dict()
        for key, groups in itertools.groupby(data, lambda x: x.get("channel_id")):
            try:
                assert key is not None, f"The channel sale id missing in res AC"
                channel_sale_ids.append(key)
                for k in groups:
                    keys_mapping_items.update({f"{key}_$_{k['sku']}": k})
                    sku_list.add(k["sku"])
            except Exception as ex:
                logger.error(f"[{self.__class__.__name__}][__prefetch_items_mapping][{key}][{groups}] {ex}")
        #
        sku_list = list(sku_list)
        cond = self.base_condition & Q(sale__channel_sale_id__in=channel_sale_ids, sku__in=sku_list)
        sale_items = SaleItem.objects.tenant_db_for(self.client_id).filter(cond)
        sale_prime_ids = self.prefetch_prime_channel_sale_ids(channel_sale_ids)
        sale_brand_setting_source = self.prefetch_sku_brand_setting_sources(channel_sale_ids, sku_list)
        return sale_items, keys_mapping_items, sale_prime_ids, sale_brand_setting_source

    def prefetch_prime_channel_sale_ids(self, channel_sale_ids: list):
        cond = Q(channel_sale_id__in=channel_sale_ids, channel=self.channel, is_prime=True)
        queryset = Sale.objects.tenant_db_for(self.client_id).filter(cond)
        return list(queryset.values_list("channel_sale_id", flat=True))

    def prefetch_sku_brand_setting_sources(self, channel_sale_ids: list, sku_list: list):
        cond = self.base_condition & Q(sale__channel_sale_id__in=channel_sale_ids, sku__in=sku_list,
                                       shipping_cost_source=BRAND_SETTING_SOURCE_KEY)
        queryset = SaleItem.objects.tenant_db_for(self.client_id).filter(cond) \
            .annotate(key_mapping=Cast(Concat("sale__channel_sale_id", Value("_$_"), "sku"), CharField()))
        return list(queryset.values_list("key_mapping", flat=True).distinct())
