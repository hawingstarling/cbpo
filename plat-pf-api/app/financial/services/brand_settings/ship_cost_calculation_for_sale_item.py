import json
from datetime import datetime, timezone
from bulk_update.helper import bulk_update
from django.db import transaction
from django.db.models import Q, Sum
from plat_import_lib_api.models import DataImportTemporary, PROCESSED
from app.core.logger import logger
from app.financial.jobs.data_flatten import flat_sale_items_bulks_sync_task
from app.financial.models import BrandSetting, SaleItem
from app.financial.services.brand_settings.ship_cost_calculation_adapter import ShipCostCalculationAdapter
from app.database.helper import get_connection_workspace
from app.financial.services.shipping_cost.shipping_cost_from_brand_settings import (
    EVALUATED_SHIPPING_COST_ACCURACY_SPECIFIC_BRAND)
from app.financial.utils.shipping_cost_helper import separate_shipping_cost_by_accuracy
from app.financial.variable.shipping_cost_source import BRAND_SETTING_SOURCE_KEY


class IBeingUpdateSaleItemShippingCost:
    update: bool
    sale_item: SaleItem
    message: str

    def __init__(self, update: bool, sale_item: SaleItem, message):
        self.update = update
        self.sale_item = sale_item
        self.message = message


class BrandSettingUpdateSaleItem:

    def __init__(self, client_id: str, brand_setting: BrandSetting, is_recalculate: bool,
                 from_date, to_date, bulk_progress_id: str = None, chunk_size=1000):
        self.__brand_setting = brand_setting
        self._client_id = client_id
        self._client_db = get_connection_workspace(self._client_id)

        self.__is_recalculate = is_recalculate
        self.__chunk_size = chunk_size
        self.__from_date = from_date
        self.__to_date = to_date

        self.__sub_update_mission = []

        self.__part_bulk_update_index = 0
        self.__being_update_queue = []
        self.__size_bulk_update = 50

        self.__base_cond = Q()
        self.__base_cond.add(Q(client_id=self._client_id,
                               sale__channel__id=self.__brand_setting.channel_id,
                               brand__id=self.__brand_setting.brand_id,
                               shipping_cost_accuracy__lte=EVALUATED_SHIPPING_COST_ACCURACY_SPECIFIC_BRAND), Q.AND)
        if self.__is_recalculate is False:
            self.__base_cond.add(Q(Q(shipping_cost__isnull=True) | Q(shipping_cost=0)), Q.AND)

        self.__cond = Q(sale_date__gte=self.__from_date, sale_date__lte=self.__to_date)

        self.__total_rows = 0
        self.__bulk_progress_id = bulk_progress_id

    @property
    def __sale_item_query_set(self):
        return SaleItem.objects \
            .tenant_db_for(self._client_id) \
            .filter(self.__base_cond) \
            .filter(self.__cond) \
            .order_by('sale') \
            .iterator(chunk_size=self.__chunk_size)

    def sale_item_query_set_count(self):
        return SaleItem.objects \
            .tenant_db_for(self._client_id) \
            .filter(self.__base_cond) \
            .filter(self.__cond) \
            .count()

    def get_sale_item_query_set(self):
        return SaleItem.objects \
            .tenant_db_for(self._client_id) \
            .filter(self.__base_cond) \
            .filter(self.__cond) \
            .values_list('id', flat=True)

    def update(self):
        self.__total_rows = self.sale_item_query_set_count()
        logger.info(f'[{self.__class__.__name__}] calculate ship cost for {self.__total_rows} sale items')
        for idx, sale_item in enumerate(self.__sale_item_query_set):
            self.__sub_update_mission.append(sale_item)

            if (idx + 1) % self.__chunk_size == 0:
                self.__exec_sub_mission()
                self.__sub_update_mission.clear()

        if len(self.__sub_update_mission):
            self.__exec_sub_mission()

    def __exec_sub_mission(self):
        sale_item_ids = [item.id for item in self.__sub_update_mission]
        sale_stats = SaleItem.objects.tenant_db_for(self._client_id).filter(id__in=sale_item_ids) \
            .values("sale_id", "brand_id").annotate(sum_sku_quantity=Sum('quantity'))
        for idx, sale_item in enumerate(self.__sub_update_mission):
            ship_cost, message_shipping_cost = self.__calc_sale_item_ship_cost(sale_item, sale_stats)

            if ship_cost is not None:
                sale_item, changes = separate_shipping_cost_by_accuracy(self._client_id, sale_item, ship_cost,
                                                            EVALUATED_SHIPPING_COST_ACCURACY_SPECIFIC_BRAND,
                                                            BRAND_SETTING_SOURCE_KEY)
                if changes:
                    sale_item.dirty = True
                    sale_item.financial_dirty = True
                    self.__being_update_queue.append(IBeingUpdateSaleItemShippingCost(True, sale_item, None))
            else:
                self.__being_update_queue.append(
                    IBeingUpdateSaleItemShippingCost(False, sale_item, message_shipping_cost))

            if (idx + 1) % self.__size_bulk_update == 0:
                self.__bulk_update()
                self.__being_update_queue.clear()

        if len(self.__being_update_queue):
            self.__bulk_update()

    def __calc_sale_item_ship_cost(self, sale_item, sale_stats):
        """
        :param sale_item:
        :param sale_stats:
        :return: shipping_cost, message_shipping_cost
        """
        shipping_cost = None
        try:
            if sale_item.fulfillment_type.name == 'FBA' and sale_item.shipping_cost_accuracy != 100:
                shipping_cost = ShipCostCalculationAdapter.calc_for_fba(self.__brand_setting, sale_item)
            if sale_item.fulfillment_type.name == 'MFN':
                shipping_cost = ShipCostCalculationAdapter.calc_for_mfn(self.__brand_setting, sale_item, sale_stats)
            # unknown fulfillment method
            if shipping_cost is None:
                return None, f'unknown sale item fulfillment method'
            return shipping_cost, None
        except Exception as error:
            logger.error(f'[{self.__class__.__name__}][__update_sale_item_ship_cost] {error}')
            return None, f'unknown sale item fulfillment method'

    def __bulk_update(self):
        self.__part_bulk_update_index += 1
        logger.info(f'[{self.__class__.__name__}][bulk update] part {self.__part_bulk_update_index}')
        if self.__total_rows <= self.__size_bulk_update:
            progress = 100
        else:
            progress = (self.__part_bulk_update_index / (self.__total_rows / self.__size_bulk_update)) * 100

        invalid_update_queue = list(filter(lambda ele: ele.update is False, self.__being_update_queue))
        if len(invalid_update_queue):
            self.__signal_for_progress(progress, False, invalid_update_queue, None)
        try:
            with transaction.atomic():
                being_update_queue = list(filter(lambda ele: ele.update is True, self.__being_update_queue))
                bulk_update([_queue_item.sale_item for _queue_item in being_update_queue],
                            batch_size=self.__size_bulk_update,
                            update_fields=['dirty', 'financial_dirty', 'shipping_cost', 'actual_shipping_cost',
                                           'estimated_shipping_cost', 'shipping_cost_accuracy', 'shipping_cost_source'],
                            using=self._client_db)
            transaction.on_commit(
                lambda: flat_sale_items_bulks_sync_task(self._client_id),
                using=self._client_db
            )
            self.__signal_for_progress(progress, True, being_update_queue, None)
        except Exception as err:
            logger.error(f'{err}')
            self.__signal_for_progress(progress, False, being_update_queue, err)

    def __signal_for_progress(self, progress: float, is_success: bool, _queue: [IBeingUpdateSaleItemShippingCost],
                              error_message=None):
        logger.info(f'[{self.__class__.__name__}][__signal_for_progress]')
        try:
            data_import_lib = DataImportTemporary.objects.db_manager(using=self._client_db).get(
                id=self.__bulk_progress_id)
        except DataImportTemporary.DoesNotExist:
            return

        count_errors = data_import_lib.info_import_file['summary']['error']
        count_success = data_import_lib.info_import_file['summary']['success']

        if is_success is True:
            data_import_lib.info_import_file['summary']['success'] = count_success + len(_queue)
            json_last_cache = json.loads(data_import_lib.json_data_last_cache)
            new_json_last_cache = [{"id": str(_queue_item.sale_item.id), "_meta": {
                "command": "shipping_cost_calculation",
                "valid": is_success,
                "complete": is_success,
                "processing_errors": []
            }} for _queue_item in _queue]
            json_last_cache.extend(new_json_last_cache)
            data_import_lib.json_data_last_cache = json.dumps(json_last_cache)

        else:
            data_import_lib.info_import_file['summary']['error'] = count_errors + len(_queue)
            json_last_cache = json.loads(data_import_lib.json_data_last_cache)
            new_json_last_cache = [{"id": str(_queue_item.sale_item.id), "_meta": {
                "command": "shipping_cost_calculation",
                "valid": is_success,
                "complete": is_success,
                "processing_errors": [_queue_item.message if error_message is None else f'{error_message}']
            }} for _queue_item in _queue]
            json_last_cache.extend(new_json_last_cache)
            data_import_lib.json_data_last_cache = json.dumps(json_last_cache)

        if progress >= 100:
            progress = 100
            data_import_lib.status = PROCESSED
            data_import_lib.process_completed = datetime.now(tz=timezone.utc)

        data_import_lib.progress = progress
        data_import_lib.save()
