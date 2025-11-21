import copy
from datetime import datetime, timedelta, timezone
import logging
from auditlog.models import LogEntry
from django.db import transaction
from django.db.models import Q
from django_bulk_update.helper import bulk_update
from app.core.services.audit_logs.base import AuditLogCoreManager
from app.core.services.audit_logs.config import SYSTEM_COG
from app.core.utils import round_currency
from app.extensiv.models import COGSConflict
from app.extensiv.utils import init_cog_conflict
from app.extensiv.variables import PF_COG_SOURCE
from app.financial.jobs.data_flatten import flat_sale_items_bulks_sync_task
from app.financial.models import SaleItem, ItemCog, LogClientEntry
from app.financial.services.sale_item_mapping.abstract import MappingSaleItemAbstract, MappingCogMethod
from app.financial.variable.sale_item import COG_TYPE_CALCULATED_KEY
from app.financial.variable.sale_status_static_variable import SALE_PARTIALLY_REFUNDED_STATUS

logger = logging.getLogger(__name__)


class MappingSaleItemCog(MappingSaleItemAbstract, MappingCogMethod):

    def __init__(self, client_id: str, *args, **kwargs):
        super().__init__(client_id, *args, **kwargs)
        self._cog_use_pf = self.client_setting.cog_use_pf
        self._fields_updated = self._get_fields_updated()
        self._priority_source_number = self.setting_cog_priority_source.get(
            PF_COG_SOURCE) or 0

    def _get_fields_updated(self):
        fields = ["cog", "unit_cog", "cog_source", "used_cog_priority",
                  "dirty", "financial_dirty", "modified"]
        return fields

    def _base_condition(self):
        base_cond = {"sale__date__isnull": False}

        if self.client_id is not None:
            base_cond.update({"client__id": self.client_id})

        if self._affected_sale_item_ids:
            base_cond.update({"id__in": self._affected_sale_item_ids})
        else:
            base_cond.update({"type_cog": COG_TYPE_CALCULATED_KEY})

        logger.info(
            f"[{self.__class__.__name__}][{self.client_id}] Base condition: {base_cond}"
        )

        return base_cond

    def _get_mapping_condition(self):
        if not self._is_override_mode:
            if bool(self._priority_source_number):
                cond_priority = (
                    Q(used_cog_priority__isnull=True)
                    | (Q(used_cog_priority__gt=self._priority_source_number) & ~Q(cog_source=PF_COG_SOURCE)))
            else:
                cond_priority = Q(cog_source__isnull=True) & Q(
                    Q(cog__isnull=True) | Q(cog=0))
        else:
            cond_priority = Q()
        logger.info(
            f"[{self.__class__.__name__}][{self.client_id}] Mapping condition: {cond_priority}"
        )
        return cond_priority

    def _query_sale_items(self):
        """
        query sale items
        :return:
        """
        if not self._cog_use_pf:
            # return SaleItem.objects.tenant_db_for(self.client_id).none()
            raise Exception(
                f"the COGs setting {PF_COG_SOURCE} is not enabled")
        base_cond = self._base_condition()
        mapping_cond = self._get_mapping_condition()

        return SaleItem.objects \
            .tenant_db_for(self.client_id) \
            .filter(**base_cond) \
            .filter(mapping_cond) \
            .order_by("-created") \
            .values("id", "client_id", "sku", "sale_date", "sale_status__value", "quantity", "refunded_quantity") \
            .iterator(chunk_size=self._chunk_size)

    def _query_objects_ref_mapping(self):
        return ItemCog.objects.tenant_db_for(self.client_id).filter(item__client__id=self.client_id,
                                                                    item__sku__in=self._list_sku) \
            .order_by("-created") \
            .values("item__client__id",
                    "item__sku",
                    "cog",
                    "effect_start_date",
                    "effect_end_date")

    def _exec_mission(self):
        being_update_models = {}
        look_up_item_cog_bucket = self._query_objects_ref_mapping()  # sorted by created
        if len(look_up_item_cog_bucket) == 0:
            return
        for sale_item in self._sub_mission_being_calculate:
            sku_look_up_item_cog_bucket = [item for item in look_up_item_cog_bucket
                                           if item["item__sku"] == sale_item["sku"]
                                           and item["item__client__id"] == sale_item["client_id"]]
            if len(sku_look_up_item_cog_bucket) == 0:
                continue
            refunded_quantity = sale_item.get("refunded_quantity", 0) \
                if sale_item.get("sale_status__value", None) == SALE_PARTIALLY_REFUNDED_STATUS else 0
            if refunded_quantity is None:
                refunded_quantity = 0
            quantity = sale_item.get("quantity") - refunded_quantity
            cog_val = self._mapping_appropriate_cog(
                sale_date=sale_item["sale_date"],
                ref_cogs=sku_look_up_item_cog_bucket,
                quantity=quantity
            )
            if cog_val is not None:
                being_update_models.update({str(sale_item["id"]): cog_val})

        if being_update_models == {}:
            return

        log_entries = []
        cogs_conflicts = []

        with transaction.atomic():
            mapping_cond = self._get_mapping_condition()
            list_of_models = SaleItem.objects.tenant_db_for(self.client_id) \
                .filter(id__in=being_update_models.keys()).filter(mapping_cond)
            for item in list_of_models:
                item_original = copy.deepcopy(item)
                cog = round_currency(being_update_models.get(str(item.id)))
                unit_cog = cog / item.quantity
                unit_cog = round_currency(unit_cog)
                changes = {
                    "cog": [item.cog, cog],
                    "unit_cog": [item.unit_cog, unit_cog]
                }
                if item.cog_source != PF_COG_SOURCE:
                    changes["cog_source"] = [item.cog_source, PF_COG_SOURCE]
                item.cog = cog
                item.unit_cog = unit_cog
                # Write to COG Conflict
                _item_cog_priority_number = item.used_cog_priority or self._priority_source_number
                if self._priority_source_number < _item_cog_priority_number \
                        and item.cog_source != PF_COG_SOURCE:
                    obj = init_cog_conflict(
                        item=item_original,
                        configured_priority_source=PF_COG_SOURCE,
                        old_value=item_original.cog,
                        new_value=cog
                    )
                    if obj:
                        cogs_conflicts.append(obj)
                item.cog_source = PF_COG_SOURCE
                item.used_cog_priority = self._priority_source_number
                item.dirty = True
                item.financial_dirty = True
                item.modified = self.time_now
                # Make auditlog
                log_entry = AuditLogCoreManager(client_id=self.client_id) \
                    .set_actor_name(SYSTEM_COG) \
                    .create_log_entry_from_compared_changes(item, changes, action=LogEntry.Action.UPDATE)
                log_entries.append(log_entry)

            bulk_update(list_of_models, batch_size=self._chunk_size, update_fields=self._fields_updated,
                        using=self.client_db)
            LogClientEntry.objects.tenant_db_for(self.client_id).bulk_create(
                log_entries, ignore_conflicts=True)
            # Bulk create COGSConflict
            COGSConflict.objects.tenant_db_for(self.client_id).bulk_create(
                cogs_conflicts, ignore_conflicts=True)

        # sync to flatten table
        transaction.on_commit(
            lambda: flat_sale_items_bulks_sync_task(self.client_id),
            using=self.client_db
        )


class MappingSaleItemCog12HRecentOnly(MappingSaleItemCog):

    def _base_condition(self):
        cond = super()._base_condition()

        time_delta_12h = datetime.now(tz=timezone.utc) - timedelta(hours=12)
        cond.update({"modified__gte": time_delta_12h})
        return cond
