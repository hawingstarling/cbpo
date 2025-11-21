import copy
import uuid

from django.db import DatabaseError
from psycopg2 import OperationalError
from typing import List
import logging
import time
from itertools import groupby
from plat_import_lib_api.models import PROCESSED
from app.financial.import_template.sale_item_bulk_sync import SaleItemBulkSync
from app.financial.models import SaleItem, DataFlattenTrack
from app.financial.services.freight_cost.calculation_from_brand_setting import FreightCostCalculationFromBrandSetting
# from app.financial.services.integrations.skuvaults.cart_rover import SaleCartRoverManager
from app.financial.services.integrations.skuvaults.connect_3pl_central import Connect3PLCentralManager
from app.financial.services.sale_item_bulk.sale_item_bulk_base import SaleItemBulkBaseModuleService
from app.financial.services.sale_item_bulk.sale_item_bulk_sync_live_feed import SaleItemBulkSyncLiveFeed
from app.financial.services.sale_item_bulk.sale_item_bulk_sync_trans_event import SaleItemBulkSyncTransEvent
# from app.financial.services.integrations.skuvault import SaleSKUVaultManager
from app.financial.services.sale_item_mapping.builder import MappingSaleItemBuilder
from app.financial.services.sale_item_mapping.mapping_sale_item_common_from_live_feed_dc import \
    VALID_SALE_ITEM_COMMON_FIELDS_LIVE_FEED_DC
from app.financial.services.shipping_cost.builder import ShippingCostBuilder
from app.financial.services.user_provided_cost.calculation_from_brand_setting import \
    UserProvidedCostCalculationFromBrandSetting
from app.financial.sub_serializers.sale_item_bulk_edit_serializer import ClientSaleItemBulkEditSerializer
from app.financial.variable.bulk_sync_datasource_variable import AMAZON_SELLER_CENTRAL, DATA_CENTRAL
from app.financial.variable.data_flatten_variable import FLATTEN_SALE_ITEM_KEY
from app.financial.variable.job_status import SUCCESS, BULK_SYNC_LIVE_FEED_JOB
from app.financial.services.segment.calculation_from_brand_setting import SegmentCalculationFromBrandSetting

logger = logging.getLogger(__name__)


class SaleItemBulkSyncModuleService(SaleItemBulkBaseModuleService):
    module = SaleItemBulkSync
    serializer_class = ClientSaleItemBulkEditSerializer

    def __init__(self, bulk_id: str = None, jwt_token: str = None, user_id: str = None, client_id: str = None):
        super().__init__(bulk_id=bulk_id, jwt_token=jwt_token, user_id=user_id, client_id=client_id)
        self.sources = self.bulk.meta.get('sources', [])
        self.dc_fields = self.bulk.meta.get('dc_fields', [])
        self.dc_is_override = self.bulk.meta.get('dc_is_override', [])
        self.ac_is_forced = self.bulk.meta.get('ac_is_forced', False)
        # self.pf_calculations = self.bulk.meta.get('pf_calculations', False)
        self.pf_calculation_recalculate_shipping_costs = self.bulk.meta.get('pf_calculation_recalculate_shipping_costs',
                                                                            False)
        self.pf_calculation_recalculate_cog = self.bulk.meta.get('pf_calculation_recalculate_cog', False)
        self.pf_calculation_recalculate_total_costs = self.bulk.meta.get('pf_calculation_recalculate_total_costs',
                                                                         False)
        self.pf_calculation_recalculate_segments = self.bulk.meta.get('pf_calculation_recalculate_segments', False)
        self.pf_calculation_recalculate_user_provided_cost = self.bulk.meta.get(
            'pf_calculation_recalculate_user_provided_cost', False)
        self.pf_calculation_recalculate_inbound_freight_cost = self.bulk.meta.get(
            'pf_calculation_recalculate_inbound_freight_cost', False)
        self.pf_calculation_recalculate_outbound_freight_cost = self.bulk.meta.get(
            'pf_calculation_recalculate_outbound_freight_cost', False)
        self.pf_calculation_recalculate_skuvault = self.bulk.meta.get('pf_calculation_recalculate_skuvault', False)
        self.pf_calculation_recalculate_cart_rover = self.bulk.meta.get('pf_calculation_recalculate_cart_rover',
                                                                        self.pf_calculation_recalculate_skuvault)
        self.pf_calculation_recalculate_3pl_central = self.bulk.meta.get('pf_calculation_recalculate_3pl_central',
                                                                         self.pf_calculation_recalculate_skuvault)
        self.pf_calculation_recalculate_ff = self.bulk.meta.get('pf_calculation_recalculate_ff', False)
        self.pf_calculation_is_override = self.bulk.meta.get('pf_calculation_is_override', False)
        self.flatten = self.__fetch_data_flatten_track()

    def __fetch_data_flatten_track(self):
        try:
            return DataFlattenTrack.objects.tenant_db_for(self.client_id).get(client_id=self.client_id,
                                                                              type=FLATTEN_SALE_ITEM_KEY,
                                                                              status=SUCCESS)
        except Exception as ex:
            logger.error(f"[{self.__class__.__name__}][{self.client_id}][__fetch_data_flatten_track] {ex}")
            return None

    def _process(self):
        try:
            while True:
                start_chunk = time.time()
                if not self.query_set_processing.exists():
                    break

                bulk_data = self.query_set_processing.order_by('index')[:self.bulk_data_chunk_size]
                self.items_chunk_map = {uuid.UUID(item.key_map): item for item in bulk_data}
                ids = list(self.items_chunk_map.keys())
                logger.info(
                    f'[{self.__class__.__name__}][process]{self.sources} {self.bulk.pk} - Items to processed: {len(ids)}')

                source_current = "system"
                try:
                    ids = self._process_allow_sale_data_update_from(ids, self.sources)
                    if len(ids) > 0:
                        if AMAZON_SELLER_CENTRAL in self.sources:
                            source_current = AMAZON_SELLER_CENTRAL
                            # Sync all sale/sale_item data and transaction event related to sale_item_ids
                            sale_items = SaleItem.objects.tenant_db_for(self.client_id) \
                                .filter(id__in=ids, client__id=self.client_id).order_by('-id')
                            self.__sync_from_seller_central(sale_items)

                        if DATA_CENTRAL in self.sources:
                            source_current = DATA_CENTRAL
                            # Sync sale_item `upc` and `cog`
                            self.__sync_from_data_central(ids)

                        if self.pf_calculation_recalculate_total_costs:
                            self.__recalculate_item_total_cost(ids)

                        if self.pf_calculation_recalculate_shipping_costs:
                            # shipping cost calculation
                            ShippingCostBuilder.instance() \
                                .tenant_db_for_only(self.client_id) \
                                .with_sale_item_ids(ids) \
                                .with_chunk_size(self.bulk_data_chunk_size) \
                                .with_is_recalculate(self.pf_calculation_is_override) \
                                .build_from_brand_settings() \
                                .update()
                            # drop ship fee calculation
                            ShippingCostBuilder.instance() \
                                .tenant_db_for_only(self.client_id) \
                                .with_sale_item_ids(ids) \
                                .with_action(BULK_SYNC_LIVE_FEED_JOB) \
                                .with_chunk_size(self.bulk_data_chunk_size) \
                                .with_is_recalculate(self.pf_calculation_is_override) \
                                .build_from_brand_settings_for_drop_ship_fee() \
                                .update()

                        if self.pf_calculation_recalculate_cog:
                            MappingSaleItemBuilder.instance() \
                                .tenant_db_for_only(self.client_id) \
                                .with_selected_sale_item_ids(ids) \
                                .with_override_mode(self.pf_calculation_is_override) \
                                .build_mapping_cog_from_item() \
                                .exec()

                        if self.pf_calculation_recalculate_segments:
                            SegmentCalculationFromBrandSetting(client_id=self.client_id, flatten=self.flatten,
                                                               sale_item_ids=ids,
                                                               override=self.pf_calculation_is_override).progress()

                        if self.pf_calculation_recalculate_user_provided_cost:
                            UserProvidedCostCalculationFromBrandSetting(client_id=self.client_id, flatten=self.flatten,
                                                                        sale_item_ids=ids,
                                                                        override=self.pf_calculation_is_override).progress()

                        if self.pf_calculation_recalculate_inbound_freight_cost \
                                and self.pf_calculation_recalculate_outbound_freight_cost:
                            field_target_calculation = "all"
                        elif self.pf_calculation_recalculate_inbound_freight_cost:
                            field_target_calculation = "inbound"
                        elif self.pf_calculation_recalculate_outbound_freight_cost:
                            field_target_calculation = "outbound"
                        else:
                            field_target_calculation = None
                        if field_target_calculation is not None:
                            FreightCostCalculationFromBrandSetting(
                                client_id=self.client_id, flatten=self.flatten,
                                sale_item_ids=ids,
                                override=self.pf_calculation_is_override,
                                field_target_calculation=field_target_calculation
                            ).progress()

                        if self.pf_calculation_recalculate_skuvault:
                            Connect3PLCentralManager(client_id=self.client_id, flatten=self.flatten, sale_item_ids=ids,
                                                     override=self.pf_calculation_is_override).progress()

                        if self.pf_calculation_recalculate_cart_rover:
                            Connect3PLCentralManager(client_id=self.client_id, flatten=self.flatten, sale_item_ids=ids,
                                                     override=self.pf_calculation_is_override).progress()

                        if self.pf_calculation_recalculate_3pl_central:
                            Connect3PLCentralManager(client_id=self.client_id, flatten=self.flatten, sale_item_ids=ids,
                                                     override=self.pf_calculation_is_override).progress()

                        if self.pf_calculation_recalculate_ff:
                            builder_dc = MappingSaleItemBuilder.instance() \
                                .with_override_mode(self.pf_calculation_is_override) \
                                .with_chunk_size_query_set_sale_item(self.bulk_data_chunk_size) \
                                .tenant_db_for_only(self.client_id) \
                                .with_selected_sale_item_ids(ids)
                            handler_dc = builder_dc.build_mapping_mfn_classification()
                            handler_dc.exec()

                    self._update_success_summary()
                except OperationalError or DatabaseError:
                    continue
                except Exception as ex:
                    self._update_error_summary(source_current, message=str(ex))
                    logger.error(f'[{self.__class__.__name__}][process]{self.sources} {self.bulk.pk} {ex}')

                # Update bulk_info
                self._update_bulk_info()

                # Sync edited sale_items to datasource
                self._sync_datasource(ids)

                end_chunk = time.time()
                logger.info(f'[{self.__class__.__name__}][process]{self.sources} {self.bulk.pk} '
                            f'Time executed bulk-sync sale item chunk: {end_chunk - start_chunk}')
                # Stop process if job is `cancelled`
                if self.bulk.status == PROCESSED:
                    break
        except Exception as ex:
            logger.error(f'[{self.__class__.__name__}]{self.sources} {self.bulk.pk} {ex}')
            raise ex

    def __sync_from_data_central(self, ids):
        assert not self.client.is_oe, "Action denied by workspace is oe"
        logger.info(f'[{self.__class__.__name__}]{self.sources} {self.bulk.pk} '
                    f'Sync `sale_item` [UPC, COG] data from live feed DC')

        fields_override = [_field for _field in self.dc_fields if _field in VALID_SALE_ITEM_COMMON_FIELDS_LIVE_FEED_DC]

        if 'cog' in fields_override and 'unit_cog' not in fields_override:
            fields_override.append('unit_cog')

        builder_dc = MappingSaleItemBuilder.instance() \
            .with_common_mapping_fields(fields_override) \
            .with_override_mode(self.dc_is_override) \
            .with_chunk_size_query_set_sale_item(self.bulk_data_chunk_size) \
            .tenant_db_for_only(self.client_id) \
            .with_selected_sale_item_ids(ids)
        handler_dc = builder_dc.build_mapping_from_live_feed_dc()
        handler_dc.exec()

    def __recalculate_item_total_cost(self, sale_item_ids: List[str]):
        SaleItem.objects.tenant_db_for(self.client_id).filter(id__in=sale_item_ids).update(dirty=True)

    def __sync_from_seller_central(self, sale_items):
        logger.info(f'[{self.__class__.__name__}]{self.sources} {self.bulk.pk} Sync `sale_item` from live feed AC')
        marketplace_sale_item_mapping = [(item.sale.channel.name, item) for item in sale_items]

        #  group by channel name
        for marketplace, marketplace_sale_items in groupby(marketplace_sale_item_mapping, lambda x: x[0]):
            logger.info(
                f'[{self.__class__.__name__}]{self.sources} {self.bulk.pk} process group channel name {marketplace}')

            total_channel_sale_ids, list_sku = [], []
            for item in marketplace_sale_items:
                total_channel_sale_ids.append(item[1].sale.channel_sale_id)
                list_sku.append(item[1].sku)

            chunk_channel_sale_ids = self.chunks(total_channel_sale_ids, 200)

            total = len(total_channel_sale_ids)

            kwargs_template_info = dict(
                client_id=self.client_id,
                user_id=self.user_id,
                flatten=self.flatten,
                marketplace=marketplace,
                track_logs=False,
                ac_is_forced=self.ac_is_forced
            )

            for channel_sale_ids in chunk_channel_sale_ids:
                kwargs_info = copy.deepcopy(kwargs_template_info)
                logger.info(
                    f'[{self.client_id}][__sync_from_seller_central][{total}] Process {len(channel_sale_ids)} channel sale ids items ...')
                # Sync sale/sale_item from SC
                live_feed_manager = SaleItemBulkSyncLiveFeed(**kwargs_info, list_sku=list_sku,
                                                             channel_sale_ids=channel_sale_ids)
                live_feed_manager.progress()

                # Sync sale/sale_item replacement from SC
                live_feed_manager = SaleItemBulkSyncLiveFeed(**kwargs_info, list_sku=list_sku,
                                                             channel_sale_ids=channel_sale_ids,
                                                             is_replacement_order=True)
                live_feed_manager.progress()

                # Sync transaction events from SC
                trans_event_manager = SaleItemBulkSyncTransEvent(**kwargs_info, amazon_order_ids=channel_sale_ids)
                trans_event_manager.progress()
