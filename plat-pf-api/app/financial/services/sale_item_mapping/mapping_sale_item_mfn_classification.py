from datetime import datetime, timezone, timedelta
from decimal import Decimal
from itertools import groupby

from auditlog.models import LogEntry
from django.db import transaction
from django.db.models import Value, CharField
from django.db.models.functions import Concat, Cast
from django_bulk_update.helper import bulk_update
from app.core.logger import logger
from app.financial.jobs.data_flatten import flat_sale_items_bulks_sync_task
from app.financial.models import SaleItem, FulfillmentChannel, BrandSetting, LogClientEntry
from app.core.services.audit_logs.base import AuditLogCoreManager
from app.core.services.audit_logs.config import SYSTEM_FULFILLMENT_MFN_CLASSIFICATION
from app.financial.services.sale_item_mapping.abstract import MappingSaleItemAbstract
from app.financial.variable.fulfillment_type import (
    FULFILLMENT_MFN, FULFILLMENT_MFN_PRIME, FULFILLMENT_MFN_RA, FULFILLMENT_MFN_DS,
    FULFILLMENT_MFN_PRIME_ACCURACY_DEFAULT)
from app.financial.variable.brand_setting import EVALUATED_SHIPPING_COST_ACCURACY_SPECIFIC_BRAND_MFN_DS, \
    EVALUATED_SHIPPING_COST_ACCURACY_SPECIFIC_BRAND_MFN_PRIME, MFN_RAPID_ACCESS, MFN_DROP_SHIP, MFN_STANDARD
from app.financial.variable.shipping_cost_source import BRAND_SETTING_SOURCE_KEY


class MappingSaleItemMFNClassification(MappingSaleItemAbstract):

    def __init__(self, client_id: str, *args, **kwargs):
        super().__init__(client_id, *args, **kwargs)
        self._actor_name = SYSTEM_FULFILLMENT_MFN_CLASSIFICATION
        self._standard_formula_key_config = self.get_standard_formula_key_config()
        try:
            self.__mfn_prime = FulfillmentChannel.objects.tenant_db_for(self.client_id).get(
                name=FULFILLMENT_MFN_PRIME)
            self.__mfn_ds = FulfillmentChannel.objects.tenant_db_for(self.client_id).get(name=FULFILLMENT_MFN_DS)
            self.__mfn_ra = FulfillmentChannel.objects.tenant_db_for(self.client_id).get(name=FULFILLMENT_MFN_RA)
            self.__mfn = FulfillmentChannel.objects.tenant_db_for(self.client_id).get(name=FULFILLMENT_MFN)
        except BaseException as err:
            logger.error(f'New Fulfillment Types for MFN are not created')
            logger.error(f'{err}')
            raise err

    @property
    def update_fields(self):
        return [
            'fulfillment_type', 'fulfillment_type_accuracy', 'shipping_cost_accuracy', 'warehouse_processing_fee',
            'warehouse_processing_fee_accuracy', 'inbound_freight_cost', 'inbound_freight_cost_accuracy',
            'outbound_freight_cost', 'outbound_freight_cost_accuracy', 'user_provided_cost', 'dirty', 'financial_dirty'
        ]

    def get_standard_formula_key_config(self):
        base_cond = self._base_condition()
        client_ids = SaleItem.objects.tenant_db_for(self.client_id).filter(**base_cond).distinct().values_list(
            'client_id', flat=True)
        key_mapping_configs = BrandSetting.objects.tenant_db_for(self.client_id).filter(client_id__in=client_ids,
                                                                                        mfn_formula=MFN_STANDARD,
                                                                                        brand__isnull=False) \
            .annotate(
            key_mapping=Cast(Concat('client_id', Value('-'), 'channel_id', Value('-'), 'brand_id'), CharField())) \
            .distinct().values_list('key_mapping', flat=True)
        return list(key_mapping_configs)

    def _base_condition(self):
        base_cond = {}
        if self.client_id is not None:
            base_cond.update({'client__id': self.client_id})
        if self._affected_sale_item_ids is not None:
            base_cond.update({'id__in': self._affected_sale_item_ids})

        if self._is_override_mode:
            base_cond.update(
                {'fulfillment_type_accuracy__isnull': True, 'fulfillment_type__name__startswith': FULFILLMENT_MFN})
        else:
            base_cond.update({'fulfillment_type__name': FULFILLMENT_MFN})
        return base_cond

    def _query_sale_items(self):
        base_cond = self._base_condition()
        fields = ['id', 'client_id', 'sale__channel__name', 'sku', 'brand_id']
        queryset = SaleItem.objects \
            .tenant_db_for(self.client_id) \
            .filter(**base_cond)

        #
        if len(self._standard_formula_key_config) > 0:
            # Exclude sale item have brand channel setting MFN Standard formula
            queryset = queryset.annotate(
                key_mapping=Cast(Concat('client_id', Value('-'), 'sale__channel_id', Value('-'), 'brand_id'),
                                 CharField())).exclude(key_mapping__in=self._standard_formula_key_config)

        return queryset.select_related('sale', 'sale__channel') \
            .order_by('sale__channel', '-sale_date') \
            .values(*fields) \
            .iterator(chunk_size=self._chunk_size)

    def _query_objects_ref_mapping(self, set_brands_id: set):
        return BrandSetting.objects.tenant_db_for(self.client_id).filter(brand_id__in=set_brands_id)

    def _exec_mission(self):
        #  sorted by channel name
        sub_mission_being_calculate = [(item['sale__channel__name'], item)
                                       for item in self._sub_mission_being_calculate]

        for group_key, group_items in groupby(sub_mission_being_calculate, lambda x: x[0]):
            #  group by channel name
            sale_item_ids = []
            set_brands_id = set()
            logger.info(
                f"[{self.__class__.__name__}][{self.client_id}] process group channel name {group_key}...")
            for index, item in enumerate(group_items):
                sale_item = item[1]
                sale_item_ids.append(sale_item['id'])
                set_brands_id.add(sale_item['brand_id'])

                if len(sale_item_ids) % self._chunk_size == 0:
                    brand_settings = self._query_objects_ref_mapping(set_brands_id=set_brands_id)
                    self.__mapping(sale_item_ids=sale_item_ids, brand_settings=brand_settings)
                    set_brands_id.clear()
                    sale_item_ids.clear()

            if len(sale_item_ids):
                brand_settings = self._query_objects_ref_mapping(set_brands_id=set_brands_id)
                self.__mapping(sale_item_ids=sale_item_ids, brand_settings=brand_settings)

        # sync to flatten table
        transaction.on_commit(
            lambda: flat_sale_items_bulks_sync_task(self.client_id),
            using=self.client_db
        )

    def __classify(self, sale_item: SaleItem, brand_settings):
        # classify by is prime from sale
        if sale_item.sale.is_prime is True:
            sale_item.fulfillment_type = self.__mfn_prime
            sale_item.fulfillment_type_accuracy = FULFILLMENT_MFN_PRIME_ACCURACY_DEFAULT
            return sale_item, self.__mfn_prime.name
        # classify by brand setting
        brand_setting_find_one = filter(lambda ele:
                                        ele.channel_id == sale_item.sale.channel_id and
                                        ele.brand_id == sale_item.brand_id, brand_settings)
        try:
            brand_setting_find_one = next(brand_setting_find_one)
        except StopIteration:
            brand_setting_find_one = None

        if brand_setting_find_one and brand_setting_find_one.mfn_formula == MFN_RAPID_ACCESS:
            sale_item.fulfillment_type = self.__mfn_ra
            return sale_item, self.__mfn_ra.name

        if brand_setting_find_one and brand_setting_find_one.mfn_formula == MFN_STANDARD:
            sale_item.fulfillment_type = self.__mfn
            return sale_item, self.__mfn.name

        if brand_setting_find_one and brand_setting_find_one.mfn_formula == MFN_DROP_SHIP:
            sale_item.fulfillment_type = self.__mfn_ds
            return sale_item, self.__mfn_ds.name

        return None, None

    def reset_fields_cost_to_zero(self, sale_item: SaleItem, changes: dict):
        # Reset MFN_RA, MFN_DS freight cost zero
        if sale_item.inbound_freight_cost is not None and sale_item.inbound_freight_cost > 0:
            changes.update({'inbound_freight_cost': [Decimal(format(sale_item.inbound_freight_cost, '.2f')), '0']})
            sale_item.inbound_freight_cost = 0
        if sale_item.inbound_freight_cost_accuracy is not None and sale_item.inbound_freight_cost_accuracy > 0:
            changes.update({'inbound_freight_cost_accuracy': [f'{sale_item.inbound_freight_cost_accuracy}%', '0%']})
            sale_item.inbound_freight_cost_accuracy = 0
        if sale_item.outbound_freight_cost is not None and sale_item.outbound_freight_cost > 0:
            changes.update({'outbound_freight_cost': [Decimal(format(sale_item.outbound_freight_cost, '.2f')), '0']})
            sale_item.outbound_freight_cost = 0
        if sale_item.outbound_freight_cost_accuracy is not None and sale_item.outbound_freight_cost_accuracy > 0:
            changes.update({'outbound_freight_cost_accuracy': [f'{sale_item.outbound_freight_cost_accuracy}%', '0%']})
            sale_item.outbound_freight_cost_accuracy = 0
        # Reset MFN_RA, MFN_DS user provided cost zero
        if sale_item.user_provided_cost is not None and sale_item.user_provided_cost > 0:
            changes.update(
                {'user_provided_cost': [Decimal(format(sale_item.user_provided_cost, '.2f')), '0']})
            sale_item.user_provided_cost = 0

    def __mapping(self, sale_item_ids: [str], brand_settings):
        bulk_update_queue = []
        log_entries = []

        sale_items = SaleItem.objects.tenant_db_for(self.client_id).filter(id__in=sale_item_ids)

        for sale_item in sale_items:
            changed, new_value_classified = self.__classify(sale_item, brand_settings)
            if changed:
                changed.dirty = True
                changed.financial_dirty = True
                bulk_update_queue.append(changed)
                changes = {
                    'fulfillment_type': [FULFILLMENT_MFN, new_value_classified]
                }
                # reset Warehouse Processing Fee if change to [MFN-Prime]
                if new_value_classified == FULFILLMENT_MFN_PRIME:
                    # TODO: continue verify this logic shipping_cost_accuracy = 100 if item AMZ is Prime and source = Brand Settings
                    if sale_item.shipping_cost is not None \
                            and sale_item.shipping_cost_source == BRAND_SETTING_SOURCE_KEY \
                            and sale_item.shipping_cost_accuracy < EVALUATED_SHIPPING_COST_ACCURACY_SPECIFIC_BRAND_MFN_PRIME:
                        changes.update({'shipping_cost_accuracy': [f'{sale_item.shipping_cost_accuracy}%',
                                                                   f'{EVALUATED_SHIPPING_COST_ACCURACY_SPECIFIC_BRAND_MFN_PRIME}%']})
                        sale_item.shipping_cost_accuracy = EVALUATED_SHIPPING_COST_ACCURACY_SPECIFIC_BRAND_MFN_PRIME
                    #
                    if sale_item.warehouse_processing_fee is not None and sale_item.warehouse_processing_fee > 0:
                        changes.update({'warehouse_processing_fee': [
                            Decimal(format(sale_item.warehouse_processing_fee, '.2f')), '0']})
                        sale_item.warehouse_processing_fee = 0
                    #
                    if sale_item.warehouse_processing_fee_accuracy is not None and sale_item.warehouse_processing_fee_accuracy > 0:
                        changes.update({'warehouse_processing_fee_accuracy': [
                            f'{sale_item.warehouse_processing_fee_accuracy}%', '0%']})
                        sale_item.warehouse_processing_fee_accuracy = 0
                elif new_value_classified == FULFILLMENT_MFN_DS:
                    # change accuracy MFN-DS
                    if sale_item.shipping_cost is not None \
                            and sale_item.shipping_cost_source == BRAND_SETTING_SOURCE_KEY \
                            and sale_item.shipping_cost_accuracy < EVALUATED_SHIPPING_COST_ACCURACY_SPECIFIC_BRAND_MFN_DS:
                        changes.update({
                            'shipping_cost_accuracy': [f'{sale_item.shipping_cost_accuracy}%',
                                                       f'{EVALUATED_SHIPPING_COST_ACCURACY_SPECIFIC_BRAND_MFN_DS}%']
                        })
                        sale_item.shipping_cost_accuracy = EVALUATED_SHIPPING_COST_ACCURACY_SPECIFIC_BRAND_MFN_DS
                    self.reset_fields_cost_to_zero(sale_item, changes)

                elif new_value_classified == FULFILLMENT_MFN_RA:
                    self.reset_fields_cost_to_zero(sale_item, changes)
                #
                log_entry = AuditLogCoreManager(client_id=self.client_id) \
                    .set_actor_name(self._actor_name) \
                    .create_log_entry_from_compared_changes(sale_item, changes, action=LogEntry.Action.UPDATE)
                log_entries.append(log_entry)

        if len(bulk_update_queue):
            with transaction.atomic():
                bulk_update(bulk_update_queue, update_fields=self.update_fields, batch_size=500, using=self.client_db)
                LogClientEntry.objects.tenant_db_for(self.client_id).bulk_create(log_entries,
                                                                                 ignore_conflicts=True)


class MappingSaleItemMFNClassification12HRecent(MappingSaleItemMFNClassification):

    def _base_condition(self):
        cond = super()._base_condition()

        time_delta_12h = datetime.now(tz=timezone.utc) - timedelta(hours=12)
        cond.update({'modified__gte': time_delta_12h})
        return cond
