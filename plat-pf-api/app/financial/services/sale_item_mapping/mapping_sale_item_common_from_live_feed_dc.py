import json
import time
from datetime import datetime, timezone, timedelta
from itertools import groupby
from auditlog.models import LogEntry
from django.conf import settings
from django.db import transaction
from django.db.models import Q
from django_bulk_update.helper import bulk_update
from httplib2 import Response
from rest_framework import status
from app.core.exceptions import ACServiceError
from app.core.logger import logger
from app.core.services.dc_service import DCManager
from app.core.sub_serializers.base_serializer import CostInputSerializer
from app.core.utils import round_currency
from app.extensiv.models import COGSConflict
from app.extensiv.utils import init_cog_conflict
from app.extensiv.variables import DC_COG_SOURCE
from app.financial.jobs.data_flatten import flat_sale_items_bulks_sync_task
from app.financial.models import SaleItem, Brand, BrandMissing, BrandSetting, LogClientEntry
from app.core.services.audit_logs.base import AuditLogCoreManager
from app.core.services.audit_logs.config import SYSTEM_DC
from app.financial.services.sale_item_mapping.abstract import MappingSaleItemAbstract
from app.financial.services.utils.common import is_the_same_currency
from app.financial.variable.brand_setting import EVALUATED_FREIGHT_COST_ACCURACY_SPECIFIC_BRAND, \
    PO_DROPSHIP_PERCENT_METHOD
from app.financial.variable.fulfillment_type import FULFILLMENT_MFN, FULFILLMENT_FBA, FULFILLMENT_MFN_PRIME, \
    FULFILLMENT_MFN_RA, FULFILLMENT_MFN_DS

VALID_SALE_ITEM_COMMON_FIELDS_LIVE_FEED_DC = [
    "upc", "unit_cog", "cog", "brand", "channel_brand"]


class MappingSaleItemCommonFromLiveFeedDC(MappingSaleItemAbstract):
    COMMON_FIELDS_ACCEPT = VALID_SALE_ITEM_COMMON_FIELDS_LIVE_FEED_DC
    """
    inherits form MappingSaleItemAbstract
    """

    def __init__(self, client_id: str, *args, **kwargs):
        super().__init__(client_id, *args, **kwargs)
        self._cog_use_dc = self.client_setting.cog_use_dc
        #
        self._fields_mapping = []
        self._fields_mapping_with_foreign_key = []
        self._get_fields_mapping()
        self._others_mapping = self._get_fields_others_mapping()
        self._is_only_cog_fields = self.check_is_only_cog_fields()
        #
        self._brand_names = set()
        self._load_config_service()
        #
        self.config_brand_setting = self.prefetch_field_by_brand_setting()

        self._priority_source_number = self.setting_cog_priority_source.get(
            DC_COG_SOURCE) or 0

    def _load_config_service(self):
        self.__dc_manager = DCManager(
            client_id=self.client_id, read_timeout=60)
        self._limit_items = settings.DC_SERVICE_LIMIT_ITEM
        self._actor_name = SYSTEM_DC

    def check_is_only_cog_fields(self) -> bool:
        required = {"cog", "unit_cog"}
        return set(self._fields_mapping) == required

    def _get_fields_mapping(self):
        assert len(self.kwargs["fields_mapping"]
                   ) > 0, "fields_mapping is not empty"
        for field in self.kwargs["fields_mapping"]:
            assert field in self.COMMON_FIELDS_ACCEPT, f"`{field}` is invalid"
            # PF-3370: Should be applies by the setting COGs Source
            if field in ["cog", "unit_cog"] and not self.client_setting.cog_use_dc:
                continue
            _field = ""
            if field in ["brand"]:
                _field = f"{field}_id"
            else:
                _field = field
            self._fields_mapping_with_foreign_key.append(_field)
            self._fields_mapping.append(field)

    def _get_fields_others_mapping(self):
        _others_mapping = []
        if "brand" in self._fields_mapping:
            _others_mapping += [
                "segment", "inbound_freight_cost", "inbound_freight_cost_accuracy",
                "outbound_freight_cost", "outbound_freight_cost_accuracy",
                "user_provided_cost"
            ]
        if "cog" in self._fields_mapping:
            _others_mapping += ["cog_source", "used_cog_priority"]
        logger.info(
            f"[{self.__class__.__name__}][{self.client_id}] _others_mapping: {_others_mapping}"
        )
        return _others_mapping

    def _base_condition(self):
        base_cond = {}
        if self.client_id is not None:
            base_cond.update({"client__id": self.client_id})
        if self._affected_sale_item_ids is not None:
            base_cond.update({"id__in": self._affected_sale_item_ids})
        logger.info(
            f"[{self.__class__.__name__}][{self.client_id}] Base condition: {base_cond}"
        )
        return base_cond

    def _get_mapping_condition(self):
        cond_mapping = Q()
        if not self._is_override_mode:
            for field in self._fields_mapping_with_foreign_key:
                cond_mapping.add(Q(**{f"{field}__isnull": True}), Q.OR)
                if "_id" not in field:
                    cond_mapping.add(Q(**{f"{field}": 0}), Q.OR)
                    cond_mapping.add(Q(**{f"{field}": "0"}), Q.OR)
        logger.info(
            f"[{self.__class__.__name__}][{self.client_id}] Mapping condition: {cond_mapping}"
        )
        return cond_mapping

    def _query_sale_items(self):
        base_cond = self._base_condition()
        fields = ["id", "client_id", "asin", "sku", "sale__channel__name",
                  "sku", "quantity"] + self._fields_mapping + self._others_mapping

        if self._is_override_mode:
            return SaleItem.objects \
                .tenant_db_for(self.client_id) \
                .filter(**base_cond) \
                .select_related("sale__channel") \
                .order_by("sale__channel__name") \
                .values(*fields) \
                .iterator(chunk_size=self._chunk_size)

        mapping_cond = self._get_mapping_condition()

        return SaleItem.objects \
            .tenant_db_for(self.client_id) \
            .filter(**base_cond) \
            .filter(mapping_cond) \
            .select_related("sale__channel") \
            .order_by("sale__channel__name") \
            .values(*fields) \
            .iterator(chunk_size=self._chunk_size)

    def _query_objects_ref_mapping(self, domain: str, item_type: str, list_value: [str]):
        assert item_type in ["ASIN", "SKU"], "item_type query DC is invalid"
        data = {"item_type": item_type,
                "item_ids": list_value, "domain": domain.lower()}
        logger.info(
            f"[{self.__class__.__name__}][{self.client_id}] getting data from DC")
        response = self.__dc_manager.get_upc(data)
        return self._handler_result(response)

    def _exec_mission(self):
        being_update_models = {}

        #  sorted by channel name
        sub_mission_being_calculate = [(item["sale__channel__name"], item)
                                       for item in self._sub_mission_being_calculate]

        for group_key, group_items in groupby(sub_mission_being_calculate, lambda x: x[0]):
            #  group by channel name
            logger.info(
                f"[{self.__class__.__name__}][{self.client_id}] process group channel name {group_key}...")
            sale_items = []
            set_asin = set()
            set_sku = set()

            for index, item in enumerate(group_items):
                item_content = item[1]
                sale_items.append(item_content)

                set_asin.add(item_content["asin"])
                set_sku.add(item_content["sku"])

                if len(set_sku) % self._limit_items == 0 or len(set_asin) % self._limit_items == 0:
                    # Fetch and update models per DC_SERVICE_LIMIT_ITEM sku or asin value
                    updated_models = self.__update_models(group_key=group_key, list_sku=list(set_sku),
                                                          list_asin=list(set_asin), sale_items=sale_items)
                    being_update_models.update(updated_models)
                    sale_items.clear()
                    set_sku.clear()
                    set_asin.clear()

                    time.sleep(2)

            if len(set_sku) or len(set_asin):
                # Fetch and update models for remaining asin value
                updated_models = self.__update_models(group_key=group_key, list_sku=list(set_sku),
                                                      list_asin=list(set_asin), sale_items=sale_items)
                being_update_models.update(updated_models)

        if being_update_models == {}:
            return

        logger.info(
            f"[{self.__class__.__name__}][{self.client_id}] sale items mapping, logging changes...")

        # TODO: Add cond_mapping to the query to avoid the issue of the cog field is not updated
        mapping_cond = self._get_mapping_condition()
        list_of_models = SaleItem.objects.tenant_db_for(self.client_id) \
            .filter(id__in=being_update_models.keys()).filter(mapping_cond).select_related("brand")
        if list_of_models.count() == 0:
            logger.info(
                f"[{self.__class__.__name__}][{self.client_id}] Rerun mapping conditions "
                f"no sale items found to update"
            )
            return
        log_entries = []
        cogs_conflicts = []

        brand_dict_query_set = {
            f"{_brand.client_id}-{_brand.name}": _brand
            for _brand in Brand.objects.tenant_db_for(self.client_id).filter(
                name__in=self._brand_names, client_id=self.client_id
            )
        }
        brand_missing_dict_query_set = {
            f"{_brand.client_id}-{_brand.name}": _brand
            for _brand in BrandMissing.objects.tenant_db_for(self.client_id).filter(
                name__in=self._brand_names, client_id=self.client_id
            )
        }
        self._brand_names.clear()

        # print(f"Query : {list_of_models.query}")
        for item in list_of_models:
            # print(
            #     f"Query : {item.cog} | {item.unit_cog} | {item.used_cog_priority} | {item.cog_source}")
            mapping_ref = being_update_models.get(str(item.id))
            changes = {}
            is_reset_brand = False
            for key_mapping in mapping_ref:
                if key_mapping == "brand":
                    old_value, new_value, new_changes, is_reset_brand = self.__handle_brand(
                        item=item,
                        brand_name=mapping_ref.get(key_mapping),
                        brand_dict_query_set=brand_dict_query_set,
                        brand_missing_dict_query_set=brand_missing_dict_query_set)
                else:
                    old_value = getattr(item, key_mapping)
                    new_value = mapping_ref.get(key_mapping)
                    new_changes = new_value

                _item_cog_priority_number = item.used_cog_priority or self._priority_source_number
                if (new_changes is None and (key_mapping not in ["brand"] or not is_reset_brand)) or \
                        (is_the_same_currency(old_value, new_value) is True
                         and (key_mapping not in ["cog",
                                                  "unit_cog"] or self._priority_source_number >= _item_cog_priority_number)):
                    continue

                changes.update({key_mapping: [old_value, new_value]})
                setattr(item, key_mapping, new_changes)
                # PF-3307
                if key_mapping == "cog":
                    if self._priority_source_number < _item_cog_priority_number \
                            and item.cog_source != DC_COG_SOURCE:
                        obj = init_cog_conflict(
                            item=item,
                            configured_priority_source=DC_COG_SOURCE,
                            old_value=old_value,
                            new_value=new_value
                        )
                        if obj:
                            cogs_conflicts.append(obj)
                    if item.cog_source != DC_COG_SOURCE:
                        changes.update(
                            {"cog_source": [item.cog_source, DC_COG_SOURCE]}
                        )
                        item.cog_source = DC_COG_SOURCE
                    item.used_cog_priority = self._priority_source_number

            if "brand" in self._fields_mapping:
                # mapping segment
                self.mapping_segment_by_brand_settings(item, changes)
                # mapping freight cost
                self.mapping_freight_cost_by_brand_settings(item, changes)
                # mapping user provided cost
                self.mapping_user_provided_cost_by_brand_settings(
                    item, changes)

            if changes == {}:
                continue
            setattr(item, "dirty", True)
            setattr(item, "financial_dirty", True)
            setattr(item, "modified", self.time_now)

            log_entry = AuditLogCoreManager(client_id=self.client_id).set_actor_name(self._actor_name) \
                .create_log_entry_from_compared_changes(item, changes, action=LogEntry.Action.UPDATE)
            log_entries.append(log_entry)

        with transaction.atomic():
            update_fields = self._fields_mapping + self._others_mapping + \
                            ["dirty", "financial_dirty", "modified"]
            logger.info(
                f"[{self.__class__.__name__}][{self.client_id}] bulk update for mapping missing Sale Item data with fields: {update_fields}"
            )
            bulk_update(list_of_models, batch_size=self._chunk_size,
                        update_fields=update_fields, using=self.client_db)
            logger.info(
                f"[{self.__class__.__name__}][{self.client_id}] bulk create auditlog for Sale Item")
            LogClientEntry.objects.tenant_db_for(self.client_id).bulk_create(
                log_entries, ignore_conflicts=True)
            # Bulk create COGSConflict
            COGSConflict.objects.tenant_db_for(self.client_id).bulk_create(
                cogs_conflicts, ignore_conflicts=True)

        # sync to flatten table
        logger.info(
            f"[{self.__class__.__name__}][{self.client_id}] sync to flatten table")
        transaction.on_commit(
            lambda: flat_sale_items_bulks_sync_task(self.client_id),
            using=self.client_db
        )
        #
        self._mapping_warehouse_processing_fee_by_brand_settings(from_mapping="live_feed_dc",
                                                                 sale_item_ids=list(being_update_models.keys()))

    def prefetch_field_by_brand_setting(self):
        cond = Q(client_id=self.client_id, channel__is_pull_data=True, brand__isnull=False) \
               & (
                       Q(segment__isnull=False) | Q(est_unit_inbound_freight_cost__isnull=False,
                                                    est_unit_inbound_freight_cost__gt=0)
                       | Q(est_unit_outbound_freight_cost__isnull=False, est_unit_outbound_freight_cost__gt=0)
                       | Q(add_user_provided_cost__isnull=False, add_user_provided_cost__gt=0)
               )
        brand_segment_queryset = BrandSetting.objects.tenant_db_for(self.client_id).filter(cond) \
            .values("client_id", "channel_id", "brand_id", "segment", "est_unit_inbound_freight_cost",
                    "est_unit_outbound_freight_cost", "add_user_provided_cost", "add_user_provided_method")
        config_field = {
            f"{item['client_id']}-{item['channel_id']}-{item['brand_id']}": {
                'segment': item['segment'],
                'est_unit_inbound_freight_cost': item['est_unit_inbound_freight_cost'],
                'est_unit_outbound_freight_cost': item['est_unit_outbound_freight_cost'],
                'add_user_provided_method': item['add_user_provided_method'],
                'add_user_provided_cost': item['add_user_provided_cost']
            } for item in brand_segment_queryset
        }
        return config_field

    def mapping_segment_by_brand_settings(self, item: SaleItem, changes: dict):
        try:
            assert item.brand_id is not None, "Brand item is not empty"
            old_value = item.segment
            new_value = self.config_brand_setting[f"{item.client_id}-{item.sale.channel_id}-{item.brand_id}"]["segment"]
            if not new_value or is_the_same_currency(old_value, new_value):
                return
            changes.update({"segment": [old_value, new_value]})
            setattr(item, "segment", new_value)
        except Exception as ex:
            logger.debug(f"[{self.__class__.__name__}][{self.client_id}][mapping_segment_by_brand_settings]: "
                         f"Item Pk {item.pk} {ex}")

    def mapping_freight_cost_by_brand_settings(self, item: SaleItem, changes: dict):
        logger.debug(f"[{self.__class__.__name__}][{self.client_id}][mapping_freight_cost_by_brand_settings]: "
                     f"Calculating inbound freight cost ...")
        self.mapping_inbound_outbound_freight_cost_by_brand_settings(item, changes, "inbound_freight_cost",
                                                                     "est_unit_inbound_freight_cost")
        logger.debug(f"[{self.__class__.__name__}][{self.client_id}][mapping_freight_cost_by_brand_settings]: "
                     f"Calculating outbound freight cost ...")
        self.mapping_inbound_outbound_freight_cost_by_brand_settings(item, changes, "outbound_freight_cost",
                                                                     "est_unit_outbound_freight_cost")

    def mapping_inbound_outbound_freight_cost_by_brand_settings(self, item: SaleItem, changes: dict, field_update: str,
                                                                key_getting: str):
        try:
            assert item.brand_id is not None, "Brand item is not empty"
            assert item.fulfillment_type.name not in [FULFILLMENT_MFN_RA, FULFILLMENT_MFN_DS], \
                f"The fulfillment type is not supported"
            old_value = getattr(item, field_update)
            key = f"{item.client_id}-{item.sale.channel_id}-{item.brand_id}"
            new_value = self.config_brand_setting[key][key_getting] * \
                        item.quantity
            assert new_value != 0 and not is_the_same_currency(old_value, new_value), \
                "The new value is the same as old value or zero"
            cost_serializer = CostInputSerializer(data=dict(value=new_value))
            cost_serializer.is_valid(raise_exception=True)
            changes.update({
                field_update: [old_value, new_value],
                f"{field_update}_accuracy": [None, f"{EVALUATED_FREIGHT_COST_ACCURACY_SPECIFIC_BRAND}%"]}
            )
            setattr(item, field_update, new_value)
            setattr(item, f"{field_update}_accuracy",
                    EVALUATED_FREIGHT_COST_ACCURACY_SPECIFIC_BRAND)
        except Exception as ex:
            logger.debug(
                f"[{self.__class__.__name__}][{self.client_id}]"
                f"[mapping_inbound_outbound_freight_cost_by_brand_settings]: Item Pk {item.pk} {ex}"
            )

    def mapping_user_provided_cost_by_brand_settings(self, item: SaleItem, changes: dict):
        try:
            assert item.brand_id is not None, "Brand item is not empty"
            user_provided_method = \
                self.config_brand_setting[f"{item.client_id}-{item.sale.channel_id}-{item.brand_id}"][
                    "add_user_provided_method"]
            add_user_provided_cost = \
                self.config_brand_setting[f"{item.client_id}-{item.sale.channel_id}-{item.brand_id}"][
                    "add_user_provided_cost"]
            old_value = item.user_provided_cost
            if user_provided_method == PO_DROPSHIP_PERCENT_METHOD:
                assert 0 <= add_user_provided_cost <= 100, "User-Provided Percentage must have range in [0, 100]"
                new_value = (item.sale_charged * add_user_provided_cost) / 100
                new_value = round_currency(new_value)
            else:
                new_value = add_user_provided_cost * item.quantity
            if item.fulfillment_type.name not in [FULFILLMENT_MFN, FULFILLMENT_MFN_PRIME, FULFILLMENT_FBA] \
                    or new_value == 0 or is_the_same_currency(old_value, new_value):
                return
            cost_serializer = CostInputSerializer(data=dict(value=new_value))
            cost_serializer.is_valid(raise_exception=True)
            changes.update({"user_provided_cost": [old_value, new_value]})
            setattr(item, "user_provided_cost", new_value)
        except Exception as ex:
            logger.debug(f"[{self.__class__.__name__}][{self.client_id}][mapping_freight_cost_by_brand_settings]: "
                         f"Item Pk {item.pk} {ex}")

    @classmethod
    def _handler_result(cls, response: Response):
        try:
            status_code = response.status_code
            content = response.content.decode("utf-8")
            content = json.loads(content)
        except Exception as err:
            logger.error("[{}] request error {}".format(
                cls.__class__.__name__, err))
            return []
        if status_code == status.HTTP_200_OK:
            return content["items"]
        logger.error("[{}] request error {}".format(
            cls.__class__.__name__, content))
        if status_code >= 500:
            raise ACServiceError()
        return []

    @classmethod
    def diff_field_name(cls, _field_name):
        """
        field names in response from DC are different
        :param _field_name:
        :return:
        """
        if _field_name in ["cog", "unit_cog"]:
            # Map field "cost" from DC"s response to "cog" in SaleItem
            return "cost"
        if _field_name == "channel_brand":
            # Map field "aws_brand" from DC"s response to "channel_brand" in SaleItem
            return "aws_brand"

        return _field_name

    def __mapping_appropriate_fields(self, sale_item, object_ref):
        res_mapping_fields = {}
        if self._is_override_mode:
            for field in self._fields_mapping:
                object_ref_field = self.diff_field_name(field)
                if object_ref.get(object_ref_field) not in [None, "", 0]:
                    if object_ref_field == "brand":
                        self._brand_names.add(object_ref.get(object_ref_field))
                    if field in ["cog", "unit_cog"]:
                        amount = object_ref.get(object_ref_field)
                        if field == "cog":
                            amount = round_currency(
                                amount * sale_item["quantity"])
                        res_mapping_fields.update({field: amount})
                    else:
                        res_mapping_fields.update(
                            {field: object_ref.get(object_ref_field)})
        else:
            _item_cog_priority_number = sale_item.get(
                "used_cog_priority") or self._priority_source_number
            for field in self._fields_mapping:
                object_ref_field = self.diff_field_name(field)
                if object_ref.get(object_ref_field) not in [None, "", 0] and \
                        (sale_item.get(field) in [None, 0, ""]
                         or (field in ["cog", "unit_cog"]
                             and self._priority_source_number < _item_cog_priority_number)):
                    if object_ref_field == "brand":
                        self._brand_names.add(object_ref.get(object_ref_field))
                    if field in ["cog", "unit_cog"]:
                        amount = object_ref.get(object_ref_field)
                        if field == "cog":
                            amount = round_currency(
                                amount * sale_item["quantity"])
                        res_mapping_fields.update({field: amount})
                    else:
                        res_mapping_fields.update(
                            {field: object_ref.get(object_ref_field)})

        return res_mapping_fields

    def __update_models(self, group_key, list_sku, list_asin, sale_items):
        being_update_models = {}

        try:
            bucket_ref = self._query_objects_ref_mapping(
                domain=group_key, item_type="SKU", list_value=list_sku)
            if not len(bucket_ref):
                time.sleep(2)
            bucket_ref.extend(self._query_objects_ref_mapping(
                domain=group_key, item_type="ASIN", list_value=list_asin))
        except Exception as err:
            logger.error("[{}] request error {}".format(
                self.__class__.__name__, err))
            bucket_ref = []

        if not len(bucket_ref):
            time.sleep(2)
            return being_update_models

        logger.info(
            f"[{self.__class__.__name__}][{self.client_id}] look up items for mapping...")

        for sale_item in sale_items:
            look_up_item = filter(
                lambda ele: ele["sku"] == sale_item["sku"], bucket_ref)
            try:
                find_one = next(look_up_item)
                del look_up_item
                res_mapping = self.__mapping_appropriate_fields(
                    sale_item, find_one)
                if res_mapping != {}:
                    being_update_models.update(
                        {str(sale_item["id"]): res_mapping})
                    continue
            except StopIteration:
                pass

            look_up_item = filter(lambda ele: ele.get(
                "asin") == sale_item["asin"], bucket_ref)
            try:
                find_one = next(look_up_item)
                del look_up_item
                res_mapping = self.__mapping_appropriate_fields(
                    sale_item, find_one)
                if res_mapping != {}:
                    being_update_models.update(
                        {str(sale_item["id"]): res_mapping})
            except StopIteration:
                pass

        return being_update_models

    @classmethod
    def __create_missing_brand(cls, client_id: str, missing_brand_name: str):
        try:
            if missing_brand_name not in ["", 0, None]:
                BrandMissing.all_objects.update_or_create(client_id=client_id, name=missing_brand_name,
                                                          defaults={"mapped_brand": None, "is_removed": False})
        except Exception as _err:
            logger.error(f"{_err}")

    def __handle_brand(self, item: SaleItem, brand_name: str,
                       brand_dict_query_set: dict,
                       brand_missing_dict_query_set: dict):
        brand_ins = brand_dict_query_set.get(
            f"{item.client_id}-{brand_name}", None)
        is_reset = False
        new_changes = None
        if brand_ins is None:
            missing_brand = brand_missing_dict_query_set.get(
                f"{item.client_id}-{brand_name}", None)
            if missing_brand is None:
                self.__create_missing_brand(str(item.client_id), brand_name)
            else:
                brand_ins = missing_brand.mapped_brand
        if brand_ins is None:
            old_value = item.brand.name if item.brand else None
            if self._is_override_mode:
                brand_name = None
                is_reset = True
            return old_value, brand_name, new_changes, is_reset
        else:
            old_value = item.brand.name if item.brand else None
            new_value = brand_ins.name
            new_changes = brand_ins
            return old_value, new_value, new_changes, is_reset

    def validate_sale_item(self):
        """
        validate sale item "sale_date" -> must be large than settings "allow_sale_data_update_from"
        """
        pass


class MappingSaleItemCommonFromLive12HRecentOnlyFeedDC(MappingSaleItemCommonFromLiveFeedDC):
    """
    inherits form MappingSaleItemCommonFromLiveFeedDC
    """

    def _get_mapping_condition(self):
        if self._is_only_cog_fields:
            if bool(self._priority_source_number):
                cond_mapping = (Q(used_cog_priority__isnull=True)
                                | (Q(used_cog_priority__gt=self._priority_source_number) & ~Q(
                            cog_source=DC_COG_SOURCE)))
            else:
                cond_mapping = Q(cog_source__isnull=True) & Q(
                    Q(cog__isnull=True) | Q(cog=0))
            logger.info(
                f"[{self.__class__.__name__}][{self.client_id}] Is only cog fields: {cond_mapping}"
            )
            return cond_mapping
        return super()._get_mapping_condition()

    def _base_condition(self):
        time_delta_12h = datetime.now(tz=timezone.utc) - timedelta(hours=12)
        base_cond = {"modified__gte": time_delta_12h}

        if self.client_id is not None:
            base_cond.update({"client__id": self.client_id})
        if self._affected_sale_item_ids is not None:
            base_cond.update({"id__in": self._affected_sale_item_ids})
        return base_cond


class MappingSaleItemCommonFromSaleDateLiveFeedDC(MappingSaleItemCommonFromLiveFeedDC):
    """
    inherits form MappingSaleItemCommonFromLiveFeedDC
    """

    def __init__(self, client_id: str, *args, **kwargs):
        super().__init__(client_id, *args, **kwargs)

        self.from_date = self.kwargs["from_date"]
        self.to_date = self.kwargs["to_date"]

    def _base_condition(self):
        base_cond = Q(client_id=self.client_id, sale_date__gte=self.from_date, sale_date__lte=self.to_date,
                      sale__channel__name=self.marketplace)

        extra_cond = Q(upc__isnull=True) | Q(unit_cog__isnull=True) | Q(cog__isnull=True) | Q(brand__isnull=True) | Q(
            channel_brand__isnull=True)

        item_ids_cond = base_cond & extra_cond

        self._affected_sale_item_ids = SaleItem.objects.tenant_db_for(self.client_id) \
            .filter(item_ids_cond).values_list("id", flat=True)

        return super()._base_condition()
