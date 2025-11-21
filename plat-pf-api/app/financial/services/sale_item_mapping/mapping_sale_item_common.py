from datetime import datetime, timezone, timedelta

from auditlog.models import LogEntry
from django.db import transaction
from django.db.models import Q
from django_bulk_update.helper import bulk_update

from app.financial.jobs.data_flatten import flat_sale_items_bulks_sync_task
from app.financial.models import SaleItem, Item, LogClientEntry
from app.core.services.audit_logs.base import AuditLogCoreManager
from app.core.services.audit_logs.config import SYSTEM_COMMON
from app.financial.services.sale_item_mapping.abstract import MappingSaleItemAbstract

VALID_SALE_ITEM_COMMON_FIELDS = [
    'asin', 'title', 'upc', 'size', 'style', 'brand', 'product_number', 'product_type',
    'parent_asin'
]


class MappingSaleItemCommon(MappingSaleItemAbstract):

    def __init__(self, client_id: str, *args, **kwargs):
        super().__init__(client_id, *args, **kwargs)
        self._fields_mapping = []
        self._fields_mapping_with_foreign_key = []
        self._get_fields_mapping()

    def _get_fields_mapping(self):
        assert len(self.kwargs["fields_mapping"]) > 0, 'fields_mapping is not empty'
        for field in self.kwargs["fields_mapping"]:
            assert field in VALID_SALE_ITEM_COMMON_FIELDS, '{} is  invalid'.format(field)
            _field = ''
            if field in ['brand', 'size', 'style']:
                _field = f'{field}_id'
            else:
                _field = field
            self._fields_mapping_with_foreign_key.append(_field)
            self._fields_mapping.append(field)

    def _base_condition(self):
        base_cond = {}
        if self.client_id is not None:
            base_cond.update({'client__id': self.client_id})

        if self._affected_sale_item_ids:
            base_cond.update({'id__in': self._affected_sale_item_ids})
        return base_cond

    def _query_sale_items(self):
        """
        query sale items which are null values or empty at VALID_SALE_ITEM_COMMON_FIELDS based on 2 options:
        :return:
        """
        base_cond = self._base_condition()
        fields = ['id', 'client_id', 'sku'] + self._fields_mapping

        if self._is_override_mode:
            return SaleItem.objects \
                .tenant_db_for(self.client_id) \
                .filter(**base_cond) \
                .order_by('-created') \
                .values(*fields) \
                .iterator(chunk_size=self._chunk_size)

        cond_mapping_field = Q()
        for field in self._fields_mapping_with_foreign_key:
            cond_mapping_field.add(Q(**{f'{field}__isnull': True}), Q.OR)
            if '_id' not in field:
                cond_mapping_field.add(Q(**{f'{field}': ""}), Q.OR)

        return SaleItem.objects \
            .tenant_db_for(self.client_id) \
            .filter(**base_cond) \
            .filter(cond_mapping_field) \
            .order_by('-created') \
            .values(*fields) \
            .iterator(chunk_size=self._chunk_size)

    def _query_objects_ref_mapping(self):
        return Item.objects.tenant_db_for(self.client_id) \
            .filter(client_id=self.client_id, sku__in=self._list_sku) \
            .order_by('-created')

    def _exec_mission(self):
        look_up_item_bucket = self._query_objects_ref_mapping()  # sorted by created
        if len(look_up_item_bucket) == 0:
            return

        being_update_models = {}

        for sale_item in self._sub_mission_being_calculate:
            sku_look_up_item = filter(
                lambda ele: getattr(ele, 'client_id') == sale_item['client_id'] and getattr(ele, 'sku') == sale_item[
                    'sku'],
                look_up_item_bucket)
            try:
                find_one = next(sku_look_up_item)
                del sku_look_up_item
                res_mapping = self.__mapping_appropriate_fields(sale_item, find_one)
                if res_mapping == {}:
                    continue
                being_update_models.update(
                    {str(sale_item['id']): res_mapping})

            except StopIteration:
                continue

        if being_update_models == {}:
            return

        log_entries = []
        list_of_models = SaleItem.objects.tenant_db_for(self.client_id) \
            .filter(id__in=being_update_models.keys())

        for item in list_of_models:
            mapping_ref = being_update_models.get(str(item.id))
            changes = {}
            for key_mapping in mapping_ref:
                old_value, new_value, new_changes = self.__handle_changes(key_mapping, item, mapping_ref)
                changes.update({key_mapping: [old_value, new_value]})
                setattr(item, key_mapping, new_changes)

            if changes == {}:
                continue
            setattr(item, 'dirty', True)
            setattr(item, 'financial_dirty', True)

            log_entry = AuditLogCoreManager(client_id=self.client_id).set_actor_name(SYSTEM_COMMON) \
                .create_log_entry_from_compared_changes(item, changes, action=LogEntry.Action.UPDATE)
            log_entries.append(log_entry)

        with transaction.atomic():
            update_fields = self._fields_mapping + ['dirty', 'financial_dirty']
            bulk_update(list_of_models, batch_size=self._chunk_size, update_fields=update_fields, using=self.client_db)
            LogClientEntry.objects.tenant_db_for(self.client_id).bulk_create(log_entries, ignore_conflicts=True)

        # sync to flatten table
        transaction.on_commit(
            lambda: flat_sale_items_bulks_sync_task(self.client_id),
            using=self.client_db
        )
        #
        self._mapping_warehouse_processing_fee_by_brand_settings(from_mapping="sale_item_common",
                                                                 sale_item_ids=list(being_update_models.keys()))

    def __mapping_appropriate_fields(self, sale_item, object_ref):
        res_mapping_fields = {}
        if self._is_override_mode:
            for field in self._fields_mapping:
                if not hasattr(object_ref, field):
                    continue
                new_value = getattr(object_ref, field)
                if new_value not in [None, "", 0]:
                    res_mapping_fields.update({field: new_value})
        else:
            for field in self._fields_mapping:
                if not hasattr(object_ref, field):
                    continue
                new_value = getattr(object_ref, field)
                if new_value not in [None, "", 0] and sale_item[field] in [None, "", 0]:
                    res_mapping_fields.update({field: new_value})

        return res_mapping_fields

    @classmethod
    def __handle_changes(cls, key_mapping: str, item: SaleItem, mapping_ref):
        if key_mapping == 'brand':
            brand_ins = mapping_ref.get(key_mapping)
            old_value = item.brand.name if item.brand else None
            new_value = brand_ins.name
            new_changes = brand_ins
        elif key_mapping == 'size':
            size_ins = mapping_ref.get(key_mapping)
            old_value = item.size.value if item.size else None
            new_value = size_ins.value
            new_changes = size_ins
        elif key_mapping == 'style':
            style_ins = mapping_ref.get(key_mapping)
            old_value = item.style.value if item.style else None
            new_value = style_ins.value
            new_changes = style_ins
        else:
            old_value = getattr(item, key_mapping)
            new_value = mapping_ref.get(key_mapping)
            new_changes = mapping_ref.get(key_mapping)

        return old_value, new_value, new_changes


class MappingSaleItemCommon12HRecentOnly(MappingSaleItemCommon):

    def _base_condition(self):
        cond = super()._base_condition()

        time_delta_12h = datetime.now(tz=timezone.utc) - timedelta(hours=12)
        cond.update({'modified__gte': time_delta_12h})
        return cond
