from datetime import datetime
import copy
import decimal
import json
import logging
import re
import maya
from auditlog.models import LogEntry
from django.db import transaction
from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from app.core.utils import hashlib_content
from app.financial.import_template.validation.sale_item import default_error_messages, get_label
from app.financial.models import ClientPortal, SaleItem, DataFlattenTrack, SaleItemTransaction, Channel, \
    SKUVaultPrimeTrack, ClientSettings, LogClientEntry
from app.financial.models import Sale, SaleStatus, ProfitStatus, UserPermission, Brand, Variant, \
    SaleChargeAndCost, FulfillmentChannel, SaleItemFinancial
from app.core.services.audit_logs.base import AuditLogCoreManager, SALE_ITEM_LEVEL, SALE_LEVEL
from app.financial.services.highchart_mapping import HighChartMappingService
from app.database.sub_serializers.tenant_db_for_serializer import TenantDBForSerializer
from app.financial.utils.shipping_cost_helper import separate_shipping_cost_by_data
from app.financial.variable.fulfillment_type import FULFILLMENT_MFN_DS, FULFILLMENT_MFN_RA
from app.financial.variable.job_status import LIVE_FEED_JOB, TRANS_DATA_EVENT_JOB, JOB_ACTION, \
    BULK_SYNC_LIVE_FEED_JOB, SKU_VAULT_JOB, CART_ROVER_JOB, BULK_SYNC_TRANS_DATA_EVENT_JOB
from app.financial.services.transaction.calculate.sale_item import CalculateTransSaleItemsManage
from app.financial.services.utils.common import round_currency
from app.financial.variable.profit_status_static_variable import PROFIT_STATUS_ENUM
from app.financial.variable.sale_item import SINGLE_EDIT_JOB, BULK_EDIT_JOB
from app.financial.variable.sale_status_static_variable import SALE_STATUS_ENUM, SALE_PARTIALLY_REFUNDED_STATUS
from app.financial.services.transaction.calculate.sale import CalculateTransSaleManage
from app.financial.variable.data_flatten_variable import FLATTEN_SALE_ITEM_FINANCIAL_KEY, FLATTEN_PG_SOURCE, \
    FLATTEN_ES_SOURCE
from app.job.utils.helper import register_list
from app.job.utils.variable import SYNC_ANALYSIS_CATEGORY, MODE_RUN_PARALLEL

logger = logging.getLogger(__name__)


class CreateSyncClientSerializer(serializers.Serializer):
    client_id = serializers.CharField(max_length=36, required=False)
    user_id = serializers.CharField(max_length=36, required=False)


class ClientPortalSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)

    class Meta:
        model = ClientPortal
        fields = (
            'id', 'name', 'active', 'logo', 'dashboard_button_color', 'account_manager', 'special_project_manager',)


class ClientSaleSerializer(TenantDBForSerializer):
    channel = serializers.CharField(max_length=100)

    class Meta:
        model = Sale
        fields = '__all__'
        read_only_fields = ['id', 'created', 'updated', 'client', 'sale_status', 'profit_status']

    def process_import(self, validated_data):
        client = validated_data.get('client')
        channel_sale_id = validated_data.get('channel_sale_id')
        channel = validated_data.get('channel')
        validated_data.update({'client': client, 'is_removed': False})
        try:
            created = False
            obj = Sale.all_objects.tenant_db_for(client.id).get(client=client, channel_sale_id=channel_sale_id,
                                                                channel=channel)
            # remove all item is None if action is live feed
            self.excluding_none_value_validated_data(validated_data)
            sale, log_entry = self.update(obj, validated_data)
            if log_entry:
                sale.save()
        except Sale.DoesNotExist:
            created = True
            sale, log_entry = self.create(validated_data)
        return sale, log_entry, created

    def init_data_sale(self, validated_data):
        sale_status = SaleStatus.objects.tenant_db_for(self.client_id).order_by('order').first()
        validated_data['sale_status'] = sale_status

        # profit status
        profit_status = ProfitStatus.objects.tenant_db_for(self.client_id).order_by('order').first()
        validated_data['profit_status'] = profit_status

    def create(self, validated_data):
        self.init_data_sale(validated_data)
        # Mapping state_key, county_key to validated sale data
        HighChartMappingService().map_high_chart_sale(sale_data=validated_data)
        #
        obj = Sale(**validated_data)
        obj.id = Sale.generate_id(self.client_id)
        Sale.objects.tenant_db_for(self.client_id).bulk_create([obj])
        # make log entry
        log_entry = AuditLogCoreManager(client_id=self.client_id).set_actor_name(self.job_type_action) \
            .create_log_entry_instance(level=SALE_LEVEL,
                                       origin=None,
                                       target=obj,
                                       action=LogEntry.Action.CREATE)
        return obj, log_entry

    @property
    def job_type_action(self):
        return self.context.get('kwargs', {}).get(JOB_ACTION, None)

    def __field_calculate_by_trans_event_data(self, instance: Sale, validated_data: dict = {}):
        if not instance:
            return

        # check sale status calculate by trans event when live feed
        if self.job_type_action in [LIVE_FEED_JOB, TRANS_DATA_EVENT_JOB, BULK_SYNC_LIVE_FEED_JOB,
                                    BULK_SYNC_TRANS_DATA_EVENT_JOB]:
            trans_event_data = CalculateTransSaleManage(client_id=self.client_id, job_action=self.job_type_action,
                                                        instance=instance).process()
            if trans_event_data:
                validated_data.update(trans_event_data)

    def __remove_field_validated_data(self, validated_data, field):
        try:
            del validated_data[field]
        except Exception as ex:
            logger.debug(f"[{self.__class__.__name__}][{self.client_id}][__remove_field_validated_data]: {ex}")

    def __clean_data_by_accurate(self, instance: Sale, validated_data: dict):

        if self.job_type_action not in [SKU_VAULT_JOB, CART_ROVER_JOB]:
            # clean prime if exist in SKUVaultPrimeTrack
            try:
                SKUVaultPrimeTrack.objects.tenant_db_for(self.client_id).get(client_id=instance.client_id,
                                                                             channel_id=instance.channel_id,
                                                                             channel_sale_id=instance.channel_sale_id)
                self.__remove_field_validated_data(validated_data, 'is_prime')
            except Exception as ex:
                logger.debug(f"[{self.__class__.__name__}][{self.client_id}][__clean_data_by_accurate]: {ex}")

    @classmethod
    def excluding_none_value_validated_data(cls, validated_data):
        data = copy.deepcopy(validated_data)
        for key in data.keys():
            try:
                if validated_data[key] is None:
                    del validated_data[key]
            except Exception as ex:
                logger.debug(f"[ClientSaleSerializer][excluding_none_value_validated_data] {ex}")

    def update(self, instance, validated_data):
        validated_data['is_removed'] = False
        obj = copy.deepcopy(instance)
        # Mapping state_key, county_key to validated sale data
        HighChartMappingService().map_high_chart_sale(sale_data=validated_data, sale_instance=obj)

        self.__field_calculate_by_trans_event_data(instance, validated_data)
        #
        self.__clean_data_by_accurate(instance, validated_data)

        for attr, value in validated_data.items():
            setattr(obj, attr, value)
        # make log entry
        log_entry = AuditLogCoreManager(client_id=self.client_id) \
            .set_actor_name(self.job_type_action) \
            .create_log_entry_instance(level=SALE_LEVEL, origin=instance, target=obj, action=LogEntry.Action.UPDATE)
        return obj, log_entry


class ClientSaleChargeAndCostSerializer(TenantDBForSerializer):
    class Meta:
        model = SaleChargeAndCost
        fields = '__all__'
        read_only_fields = ['id', 'created', 'updated']

    def process_import(self, validated_data: dict = None):
        sale = validated_data.get('sale')
        try:
            created = False
            obj = SaleChargeAndCost.all_objects.tenant_db_for(self.client_id).get(sale=sale)
            sale, log_entry = self.update(obj, validated_data)
        except SaleChargeAndCost.DoesNotExist:
            created = True
            sale, log_entry = self.create(validated_data)
        return sale, log_entry, created

    def create(self, validated_data):
        sale = validated_data.get('sale')
        obj = SaleChargeAndCost(**validated_data)
        obj.pk = sale.pk
        # make log entry
        log_entry = {}
        return obj, log_entry

    def update(self, instance, validated_data):
        obj = copy.deepcopy(instance)
        validated_data.update({'is_removed': False})
        for attr, value in validated_data.items():
            setattr(obj, attr, value)
        # make log entry
        log_entry = {}
        return obj, log_entry


class ClientSaleItemSerializer(TenantDBForSerializer):
    # sale
    customer_name = serializers.CharField(max_length=100, required=False, allow_null=True, allow_blank=True,
                                          error_messages=default_error_messages['customer_name'])
    recipient_name = serializers.CharField(max_length=100, required=False, allow_null=True, allow_blank=True,
                                           error_messages=default_error_messages['recipient_name'])
    state = serializers.CharField(max_length=45, required=False, allow_null=True, allow_blank=True, write_only=True,
                                  error_messages=default_error_messages['state'])
    city = serializers.CharField(max_length=100, required=False, allow_null=True, allow_blank=True)
    country = serializers.CharField(max_length=100, required=False, allow_null=True, allow_blank=True)
    postal_code = serializers.CharField(max_length=100, required=False, allow_null=True, allow_blank=True)
    is_prime = serializers.BooleanField(required=False, allow_null=True, write_only=True, help_text='Boolean',
                                        error_messages=default_error_messages['is_prime'], label=get_label('is_prime'))

    # sale item
    brand = serializers.CharField(max_length=100, required=False, allow_null=True, allow_blank=True, write_only=True)
    sale_date = serializers.DateTimeField(allow_null=False, write_only=True)
    profit_status = serializers.ChoiceField(choices=PROFIT_STATUS_ENUM, required=False, write_only=True)
    sale_status = serializers.ChoiceField(choices=SALE_STATUS_ENUM, required=False, write_only=True)
    quantity = serializers.IntegerField(allow_null=True, required=False, max_value=100,
                                        error_messages=default_error_messages['quantity'], write_only=True,
                                        help_text="Number")
    size_variant = serializers.CharField(max_length=200, allow_blank=True, required=False, write_only=True,
                                         error_messages=default_error_messages['size'])
    style_variant = serializers.CharField(max_length=200, allow_blank=True, required=False, write_only=True,
                                          error_messages=default_error_messages['style'])
    notes = serializers.CharField(allow_blank=True, required=False)
    title = serializers.CharField(max_length=255, required=False, allow_null=False, allow_blank=False,
                                  error_messages=default_error_messages['title'])
    fulfillment_type = serializers.CharField(max_length=45, required=False, allow_null=True, allow_blank=True,
                                             error_messages=default_error_messages['fulfillment_type'], write_only=True,
                                             help_text=f"{', '.join(['RA', 'FBA', 'MFN'])}")

    class Meta:
        model = SaleItem
        fields = "__all__"
        read_only_fields = [
            "id", "is_removed", "sale", "dirty", "client", "created", "modified", "sku"
        ]

    @property
    def allow_sale_data_update_from(self):
        try:
            return ClientSettings.objects.tenant_db_for(self.client_id).get(
                client_id=self.client_id).allow_sale_data_update_from
        except ClientSettings.DoesNotExist:
            return None

    @property
    def fields_sale_item_accept(self):
        return [i.name for i in SaleItem._meta.fields if i.name not in ['pk', 'id']]

    @property
    def fields_sale_accept(self):
        return [i.name for i in Sale._meta.fields if i.name not in ['pk', 'id']]

    def validate_size_variant(self, value):
        if not value:
            return None
        value, _ = Variant.objects.tenant_db_for(self.client_id).get_or_create(value=value, type='Size',
                                                                               defaults={'name': value})
        return value

    def validate_style_variant(self, value):
        if not value:
            return None
        value, _ = Variant.objects.tenant_db_for(self.client_id).get_or_create(value=value, type='Style',
                                                                               defaults={'name': value})
        return value

    def bulk_update(self, validated_data):
        with transaction.atomic():
            #
            _change_is_prime = True if 'is_prime' in validated_data and validated_data['is_prime'] is True else False
            fulfillment_mfn_prime = FulfillmentChannel.objects.tenant_db_for(self.client_id).get(name='MFN-Prime')
            self.context.update({'changed_is_prime': _change_is_prime, 'fulfillment_mfn_prime': fulfillment_mfn_prime})
            #
            sale_item_ids = self.context.get('sale_item_ids', [])
            sale_items = SaleItem.objects.tenant_db_for(self.client_id).filter(pk__in=sale_item_ids,
                                                                               client_id=self.client_id)
            sale_item_bulk = []
            log_entry_bulk = []
            for sale_item in sale_items.iterator():
                _validated_data = copy.deepcopy(validated_data)
                sale_item, log_entry = self.update(sale_item, _validated_data)
                if log_entry:
                    sale_item_bulk.append(sale_item)
                    log_entry_bulk.append(log_entry)
            #
            SaleItem.objects.tenant_db_for(self.client_id).bulk_update(sale_item_bulk,
                                                                       fields=self.fields_sale_item_accept)
            #
            LogClientEntry.objects.tenant_db_for(self.client_id).bulk_create(log_entry_bulk,
                                                                             ignore_conflicts=True)

            # update sale data level
            _validated_data = copy.deepcopy(validated_data)
            self.update_and_reset_data_sale(_validated_data)
            #
            meta_split_financial = dict(client_id=self.client_id, sale_item_ids=sale_item_ids)
            hash_content = hashlib_content(meta_split_financial)
            data = [
                dict(
                    client_id=self.client_id,
                    name=f"sync_data_source_standard",
                    job_name="app.financial.jobs.data_flatten.flat_sale_items_bulks_sync_task",
                    module="app.financial.jobs.data_flatten",
                    method="flat_sale_items_bulks_sync_task",
                    meta=dict(client_id=self.client_id)
                ),
                dict(
                    client_id=self.client_id,
                    name=f"split_sale_item_financial_ws_{hash_content}",
                    job_name="app.financial.jobs.sale_financial.handler_trigger_split_sale_item_financial_ws",
                    module="app.financial.jobs.sale_financial",
                    method="handler_trigger_split_sale_item_financial_ws",
                    meta=meta_split_financial
                )
            ]
            #
            transaction.on_commit(lambda: register_list(SYNC_ANALYSIS_CATEGORY, data, mode_run=MODE_RUN_PARALLEL),
                                  using=self.client_db)

    def process_import(self, validated_data: dict = {}):
        client = validated_data.get('client')
        sale = validated_data.get('sale')
        sku = validated_data.get('sku')
        try:
            obj = self.Meta.model.all_objects.tenant_db_for(self.client_id).get(sale=sale, client=client, sku=sku)
            created = False
            # remove all item is None if action is live feed
            self.excluding_none_value_validated_data(validated_data)
            instance, log_entry = self.update(obj, validated_data)
        except SaleItem.DoesNotExist:
            created = True
            instance, log_entry = self.create(validated_data)
        return instance, log_entry, created

    def __is_changed_to_mfn_prime(self, instance: SaleItem, validated_data: dict):
        # On fulfillment-type change, reset dropship free column if it is not MFN-DS
        try:
            _changed_is_prime = self.context.get('changed_is_prime', False)
            if not instance.sale.is_prime and _changed_is_prime is True:
                #
                validated_data.update({'warehouse_processing_fee': 0, 'warehouse_processing_fee_accuracy': 0})
                #
                _fulfillment_mfn_prime = self.context.get('fulfillment_mfn_prime', None)
                if _fulfillment_mfn_prime is not None:
                    validated_data.update({'fulfillment_type': _fulfillment_mfn_prime})
        except Exception as ex:
            logger.debug(f"[{self.__class__.__name__}][__reset_warehouse_processing_fee]"
                         f"[fulfilment_type_brand_settings]: {ex}")

    def __remove_field_validated_data(self, validated_data, field):
        try:
            del validated_data[field]
        except Exception as ex:
            logger.debug(f"[{self.__class__.__name__}][__remove_field_validated_data] {ex}")

    def __clean_data_by_brand_setting(self, instance: SaleItem, validated_data: dict):
        # not change fulfilment_type setting by brand settings
        if self.job_type_action in [LIVE_FEED_JOB, BULK_SYNC_LIVE_FEED_JOB]:
            try:
                fulfillment_type = validated_data['fulfillment_type']
                if instance.fulfillment_type.name.startswith('MFN-') and fulfillment_type.name in ['MFN']:
                    self.__remove_field_validated_data(validated_data, 'fulfillment_type')
            except Exception as ex:
                logger.debug(f"[{self.__class__.__name__}][__clean_data_by_brand_setting]"
                             f"[fulfilment_type_brand_settings]: {ex}")
        # change to MFN-DS , MFN-RA set zero to freight_cost
        try:
            if validated_data['fulfillment_type'].name in [FULFILLMENT_MFN_RA, FULFILLMENT_MFN_DS]:
                validated_data.update({'inbound_freight_cost': 0, 'outbound_freight_cost': 0, 'user_provided_cost': 0})
        except Exception as ex:
            logger.debug(f"[{self.__class__.__name__}][__clean_data_by_brand_setting]"
                         f"[set zero to freight_cost]: {ex}")

    def __clean_data_by_accurate(self, instance: SaleItem, validated_data: dict):
        fields = [
            dict(
                field="sale_charged",
                jobs=[LIVE_FEED_JOB, TRANS_DATA_EVENT_JOB, BULK_SYNC_LIVE_FEED_JOB, BULK_SYNC_TRANS_DATA_EVENT_JOB]
            ),
            dict(
                field="channel_listing_fee",
                jobs=[LIVE_FEED_JOB, TRANS_DATA_EVENT_JOB, BULK_SYNC_LIVE_FEED_JOB, BULK_SYNC_TRANS_DATA_EVENT_JOB]
            ),
            dict(
                field="fulfillment_type",
                jobs=[SKU_VAULT_JOB, CART_ROVER_JOB]
            ),
            dict(
                field="inbound_freight_cost",
                jobs=[]
            ),
            dict(
                field="outbound_freight_cost",
                jobs=[]
            ),
            dict(
                field="channel_tax_withheld",
                jobs=[LIVE_FEED_JOB, TRANS_DATA_EVENT_JOB, BULK_SYNC_LIVE_FEED_JOB, BULK_SYNC_TRANS_DATA_EVENT_JOB]
            )
        ]
        for item in fields:
            try:
                accuracy_field = item.get("field_accuracy", f"{item['field']}_accuracy")
                assert getattr(instance, accuracy_field, 0) == 100 and self.job_type_action not in item["jobs"], \
                    f"Invalid conditions for remove {item['field']}"
                self.__remove_field_validated_data(validated_data, item["field"])
            except Exception as ex:
                logger.debug(f'[{self.__class__.__name__}][{self.client_id}][__clean_data_by_accurate]: {ex}')

    def __clean_estimated_shipping_cost_accurate(self, instance: SaleItem, validated_data: dict):
        try:
            has_estimated_field = "estimated_shipping_cost" in validated_data and \
                                  "shipping_cost_accuracy" in validated_data
            assert has_estimated_field is True \
                   and validated_data["shipping_cost_accuracy"] < (instance.shipping_cost_accuracy or 0) < 100 \
                   and self.job_type_action in [LIVE_FEED_JOB, TRANS_DATA_EVENT_JOB, BULK_SYNC_LIVE_FEED_JOB,
                                                BULK_SYNC_TRANS_DATA_EVENT_JOB], \
                f"Invalid conditions for remove estimated_shipping_cost"
            self.__remove_field_validated_data(validated_data, "estimated_shipping_cost")
            self.__remove_field_validated_data(validated_data, "shipping_cost_accuracy")
        except Exception as ex:
            logger.debug(f"[{self.__class__.__name__}][__clean_estimated_shipping_cost_accurate] {ex}")

    def __has_mapping_accurate_data(self, instance: SaleItem, validated_data: dict):
        self.__clean_data_by_accurate(instance, validated_data)
        self.__clean_estimated_shipping_cost_accurate(instance, validated_data)
        # check trans_event exist
        filters = {
            'client': instance.client,
            'channel_sale_id': instance.sale.channel_sale_id,
            'channel': instance.sale.channel,
            'sku': instance.sku,
        }
        trans_exist = SaleItemTransaction.has_transaction_event(self.client_id, filters)
        # del fields ignore override
        if trans_exist:
            # field ignore if trans event data of sale item exist
            fields_ignore = ['tax_charged', 'channel_listing_fee', 'other_channel_fees']
            for field in fields_ignore:
                self.__remove_field_validated_data(validated_data, field)

    def __field_calculate_cogs(self, instance: SaleItem, validated_data: dict = {}):
        try:
            # check action
            if self.job_type_action in [SINGLE_EDIT_JOB, BULK_EDIT_JOB]:
                if 'cog' in validated_data:
                    cog = validated_data['cog']
                    quantity = validated_data.get('quantity', instance.quantity)
                    unit_cog = cog / quantity
                    unit_cog = round_currency(unit_cog)
                    validated_data.update({'unit_cog': unit_cog})
                elif validated_data['sale_status'].value == SALE_PARTIALLY_REFUNDED_STATUS \
                        and validated_data['sale_status'] != instance.sale_status \
                        and self.context["is_remove_cogs_refunded"] is True:
                    refunded_quantity = validated_data.get('refunded_quantity', instance.refunded_quantity)
                    quantity = validated_data.get('quantity', instance.quantity) - refunded_quantity
                    cog = validated_data.get('unit_cog', instance.unit_cog) * quantity
                    assert cog >= 0, "cog not allow less than 0"
                    validated_data.update({'cog': cog})
                else:
                    pass
        except Exception as ex:
            logger.debug(f'[{self.__class__.__name__}][__field_calculate_cogs]: {ex}')

    def __field_calculate_by_trans_event_data(self, instance: SaleItem, validated_data: dict = {}):
        if not instance:
            return

        self.__has_mapping_accurate_data(instance=instance, validated_data=validated_data)

        # job in [LIVE_FEED_JOB, TRANS_DATA_EVENT_JOB, BULK_SYNC_LIVE_FEED_JOB] check field calculate from trans event
        if self.job_type_action in [LIVE_FEED_JOB, TRANS_DATA_EVENT_JOB, BULK_SYNC_LIVE_FEED_JOB,
                                    BULK_SYNC_TRANS_DATA_EVENT_JOB]:

            data = copy.deepcopy(validated_data)

            cal_sale_item = CalculateTransSaleItemsManage(
                client_id=self.client_id, job_action=self.job_type_action,
                instance=instance,
                validated_data=data,
                is_remove_cogs_refunded=self.context.get("is_remove_cogs_refunded", False)
            )
            trans_event_data = cal_sale_item.process()
            if trans_event_data:
                validated_data.update(trans_event_data)

    def init_data_sale_item(self, validated_data):
        # sale status
        sale_status = validated_data.get('sale_status', None)
        if not sale_status:
            sale_status = SaleStatus.objects.tenant_db_for(self.client_id).order_by('order').first()  # set lowest
            validated_data['sale_status'] = sale_status

        # profit status
        profit_status = validated_data.get('profit_status', None)
        if not profit_status:
            profit_status = ProfitStatus.objects.tenant_db_for(self.client_id).order_by('order').first()  # set lowest
            validated_data['profit_status'] = profit_status

    def create(self, validated_data):
        self.init_data_sale_item(validated_data)

        client = validated_data.pop('client')
        sale = validated_data.pop('sale')
        sku = validated_data.get('sku')

        # init instance
        obj = SaleItem(client=client, sale=sale, sku=sku)

        if 'size_variant' in validated_data:
            size = validated_data.pop('size_variant')
            validated_data.update({'size': size})
        if 'style_variant' in validated_data:
            style = validated_data.pop('style_variant', None)
            validated_data.update({'style': style})

        quantity = validated_data.get('quantity', None)
        if not quantity:
            validated_data.update({'quantity': 1})

        self.__field_calculate_by_trans_event_data(instance=obj, validated_data=validated_data)
        separate_shipping_cost_by_data(self.client_id, obj, validated_data, self.job_type_action)

        for attr, value in validated_data.items():
            if attr in self.fields_sale_item_accept:
                setattr(obj, attr, value)

        # make log entry
        log_entry = AuditLogCoreManager(client_id=self.client_id) \
            .set_actor_name(self.job_type_action) \
            .create_log_entry_instance(level=SALE_ITEM_LEVEL, origin=None, target=obj, action=LogEntry.Action.CREATE)
        return obj, log_entry

    @classmethod
    def excluding_none_value_validated_data(cls, validated_data):
        data = copy.deepcopy(validated_data)
        for key in data.keys():
            try:
                if validated_data[key] is None:
                    del validated_data[key]
            except Exception as ex:
                logger.debug(f"[ClientSaleItemSerializer][excluding_none_value_validated_data] {ex}")

    def update(self, instance, validated_data):

        if not validated_data:
            return instance, None

        validated_data.update({'is_removed': False, 'dirty': True, 'financial_dirty': True, 'modified': timezone.now()})
        #
        if 'size_variant' in validated_data:
            size = validated_data.pop('size_variant')
            validated_data.update({'size': size})
        if 'style_variant' in validated_data:
            style = validated_data.pop('style_variant', None)
            validated_data.update({'style': style})

        quantity = validated_data.get('quantity', None)
        if not quantity and 'quantity' in validated_data:
            del validated_data['quantity']

        #
        obj = copy.deepcopy(instance)

        #
        self.__clean_data_by_brand_setting(instance=obj, validated_data=validated_data)

        # field calculate unit cog
        self.__field_calculate_cogs(instance=obj, validated_data=validated_data)

        # field cal by trans event data
        self.__field_calculate_by_trans_event_data(instance=obj, validated_data=validated_data)
        separate_shipping_cost_by_data(self.client_id, obj, validated_data, self.job_type_action)
        #
        self.__is_changed_to_mfn_prime(instance=obj, validated_data=validated_data)

        # all field of sale items
        for attr, value in validated_data.items():
            if attr in self.fields_sale_item_accept:
                setattr(obj, attr, value)

        # make log entry
        log_entry = AuditLogCoreManager(client_id=self.client_id) \
            .set_actor_name(self.job_type_action) \
            .create_log_entry_instance(level=SALE_ITEM_LEVEL, origin=instance, target=obj,
                                       action=LogEntry.Action.UPDATE)
        return obj, log_entry

    @property
    def job_type_action(self):
        return self.context.get('kwargs', {}).get(JOB_ACTION, None)

    def bulk_delete(self):
        with transaction.atomic():
            sale_item_ids = self.context.get('sale_item_ids', [])

            # soft deleted is_removed = True , enabled dirty for decrease item in query delete
            SaleItem.objects.tenant_db_for(self.client_id).filter(pk__in=sale_item_ids).update(
                is_removed=True, dirty=True)
            # clean in sale financial event
            SaleItemFinancial.objects.tenant_db_for(self.client_id).filter(sale_item_id__in=sale_item_ids).update(
                is_removed=True, dirty=True)
            #
            timestamp = int(timezone.now().timestamp())
            data = [
                dict(
                    client_id=self.client_id,
                    name=f"sync_data_source_standard",
                    job_name="app.financial.jobs.data_flatten.flat_sale_items_bulks_sync_task",
                    module="app.financial.jobs.data_flatten",
                    method="flat_sale_items_bulks_sync_task",
                    meta=dict(client_id=self.client_id)
                ),
                dict(
                    client_id=self.client_id,
                    name=f"sync_data_source_financial",
                    job_name="app.financial.jobs.data_flatten.flat_sale_items_bulks_sync_task",
                    module="app.financial.jobs.data_flatten",
                    method="flat_sale_items_bulks_sync_task",
                    meta=dict(client_id=self.client_id, type_flatten=FLATTEN_SALE_ITEM_FINANCIAL_KEY)
                ),
            ]
            transaction.on_commit(lambda: register_list(SYNC_ANALYSIS_CATEGORY, data, mode_run=MODE_RUN_PARALLEL),
                                  using=self.client_db)

    def map_form_sale_data(self, sale, validated_data):
        # Mapping state_key, county_key to validated sale data
        HighChartMappingService().map_high_chart_sale(sale_data=validated_data, sale_instance=sale)

        for field in self.fields_sale_accept:
            try:
                val = validated_data[field]
                setattr(sale, field, val)
            except Exception as ex:
                logger.debug(f"[{self.__class__.__name__}][map_form_sale_data] {ex}")

    def update_and_reset_data_sale(self, validated_data: dict = {}):
        sale_item_ids = self.context.get('sale_item_ids', [])
        sale_ids = SaleItem.objects.tenant_db_for(self.client_id).filter(pk__in=sale_item_ids) \
            .values_list('sale_id', flat=True).distinct('sale')
        sales = Sale.objects.tenant_db_for(self.client_id).filter(pk__in=sale_ids)
        # state
        sale_objs_update = []
        sale_log_entry_bulk = []
        for sale in sales:
            origin = copy.deepcopy(sale)

            # update state
            self.map_form_sale_data(sale, validated_data)
            # sale status
            item_sale_status = sale.saleitem_set.tenant_db_for(self.client_id).all().order_by(
                'sale_status__order').first()
            if item_sale_status:
                sale.sale_status = item_sale_status.sale_status
            # sale profit
            item_profit_status = sale.saleitem_set.tenant_db_for(self.client_id).all().order_by(
                'profit_status__order').first()
            if item_profit_status:
                sale.profit_status = item_profit_status.profit_status
            # sale date
            item_sale_date = sale.saleitem_set.tenant_db_for(self.client_id).all().order_by('sale_date').first()
            if item_sale_date:
                sale.date = item_sale_date.sale_date

            log_sale_entry = AuditLogCoreManager(client_id=self.client_id) \
                .create_log_entry_instance(level=SALE_LEVEL, origin=origin, target=sale, action=LogEntry.Action.UPDATE)
            if log_sale_entry:
                # set all item of sale if sale already change value
                sale.saleitem_set.tenant_db_for(self.client_id).all().update(dirty=True)
                sale_objs_update.append(sale)
                sale_log_entry_bulk.append(log_sale_entry)
        # update from form view edit
        Sale.objects.tenant_db_for(self.client_id).bulk_update(sale_objs_update, fields=self.fields_sale_accept)
        # create log entry
        LogClientEntry.objects.tenant_db_for(self.client_id).bulk_create(sale_log_entry_bulk, ignore_conflicts=True)

    def validate_fulfillment_type(self, value):
        if not value:
            return None
        errors = []
        try:
            value = FulfillmentChannel.objects.tenant_db_for(self.client_id).get(name=value)
        except FulfillmentChannel.DoesNotExist:
            errors.append("Fulfillment Type is invalid")
        if errors:
            raise ValidationError(errors, code="fulfillment_type")
        return value

    def validate_brand(self, value):
        if not value:
            return None
        errors = []
        # find brand in system
        try:
            value = Brand.objects.tenant_db_for(self.client_id).get(name=value, client_id=self.client_id)
        except Brand.DoesNotExist:
            errors.append('"{}" brand does not exist'.format(value))
        if errors:
            raise ValidationError(errors, code="brand")
        return value

    def validate_sale_status(self, value):
        errors = []
        # find brand in system
        if value:
            try:
                value = SaleStatus.objects.tenant_db_for(self.client_id).get(value=value)
            except SaleStatus.DoesNotExist:
                errors.append('Sale Status is invalid')
        if errors:
            raise ValidationError(errors, code="sale_status")
        return value

    def validate_profit_status(self, value):
        errors = []
        # find brand in system
        if value:
            try:
                value = ProfitStatus.objects.tenant_db_for(self.client_id).get(value=value)
            except ProfitStatus.DoesNotExist:
                errors.append('Profit Status is invalid')
        if errors:
            raise ValidationError(errors, code="profit_status")
        return value

    def is_valid_number_field_negative(self, value=None, errors: list = [], name: str = "Field"):
        if (isinstance(value, int) or isinstance(value, float) or isinstance(value, decimal.Decimal)) and value < 0:
            errors.append("{} does not accept negative number".format(name))
        if value and isinstance(value, str):
            errors.append("{} does not accept string".format(name))

    def is_valid_number_field_equal_zero(self, value=None, errors: list = [], name: str = "Field"):
        self.is_valid_number_field_negative(value, errors, name)
        if (isinstance(value, int) or isinstance(value, float) or isinstance(value, decimal.Decimal)) and value == 0:
            errors.append("{} must greater than 0".format(name))

    def validate_upc(self, value):
        errors = []
        if value:
            regex = re.compile('[@_!#$%^&*()<>?/\|}{~:]')
            if regex.search(value) is not None:
                errors.append("UPC/EAN contains character special")
            is_numeric = value.isnumeric()
            if not is_numeric:
                errors.append("UPC/EAN must is numeric")
            len_value = len(value)
            is_len_valid = True if (len_value == 12 or len_value == 13) else False
            if not is_len_valid:
                errors.append("UPC/EAN is invalid")
        if errors:
            raise ValidationError(errors, code="upc")
        return value

    def validate_asin(self, value):
        errors = []
        # validate charater special
        if value:
            regex = re.compile('[@_!#$%^&*()<>?/\|}{~:]')
            if regex.search(value) is not None:
                errors.append("ASIN contains character special")
            # validate len == 10
            len_value = len(value)
            if len_value != 10:
                errors.append("ASIN is invalid")
        if errors:
            raise ValidationError(errors, code="asin")
        return value

    def validate_quantity(self, value):
        errors = []
        self.is_valid_number_field_negative(value, errors, "Quantity")
        if errors:
            raise ValidationError(errors, code="quantity")
        return value

    def validate_cog(self, value):
        errors = []
        self.is_valid_number_field_negative(value, errors, "COG")
        if errors:
            raise ValidationError(errors, code="cog")
        return value

    def validate_shipping_cost(self, value):
        errors = []
        self.is_valid_number_field_negative(value, errors, "Shipping Cost")
        if errors:
            raise ValidationError(errors, code="shipping_cost")
        return value

    def validate_actual_shipping_cost(self, value):
        errors = []
        self.is_valid_number_field_negative(value, errors, "Actual Shipping Cost")
        if errors:
            raise ValidationError(errors, code="actual_shipping_cost")
        return value

    def validate_estimated_shipping_cost(self, value):
        errors = []
        self.is_valid_number_field_negative(value, errors, "Estimated Shipping Cost")
        if errors:
            raise ValidationError(errors, code="estimated_shipping_cost")
        return value

    def validate_tax_cost(self, value):
        errors = []
        self.is_valid_number_field_negative(value, errors, "Tax Cost")
        if errors:
            raise ValidationError(errors, code="tax_cost")
        return value

    def validate_sale_charged(self, value):
        errors = []
        self.is_valid_number_field_negative(value, errors, "Sale Charged")
        if errors:
            raise ValidationError(errors, code="sale_charged")
        return value

    def validate_shipping_charged(self, value):
        errors = []
        self.is_valid_number_field_negative(value, errors, "Shipping Charged")
        if errors:
            raise ValidationError(errors, code="shipping_charged")
        return value

    def validate_tax_charged(self, value):
        errors = []
        self.is_valid_number_field_negative(value, errors, "Tax Charged")
        if errors:
            raise ValidationError(errors, code="tax_charged")
        return value

    # validate datetime
    def validate_datetime_field(self, errors, value, name):
        if not isinstance(value, str):
            return
        try:
            maya.parse(value)
        except Exception as ex:
            errors.append("{} datetime has wrong format".format(value))

    def validate_sale_date(self, value):
        errors = []
        self.validate_datetime_field(errors, value, "Sale Date")
        if errors:
            raise ValidationError(errors, code="sale_date")
        if self.allow_sale_data_update_from \
                and value and datetime.date(value) < self.allow_sale_data_update_from:
            raise ValidationError(
                f"Do not allow to update data before {self.allow_sale_data_update_from.strftime('%m/%d/%Y')}",
                code="sale_date")
        return value

    def validate_ship_date(self, value):
        errors = []
        self.validate_datetime_field(errors, value, "Ship Date")
        if errors:
            raise ValidationError(errors, code="sale_date")
        return value


class DataFlattenTrackSerializer(TenantDBForSerializer):
    class Meta:
        model = DataFlattenTrack
        exclude = ['log_feed', 'log_event']


class DataSourceConnectionSerializer(serializers.Serializer):
    data_source_id = serializers.SerializerMethodField()
    client_id = serializers.CharField()
    type = serializers.CharField()
    created = serializers.DateTimeField()
    modified = serializers.DateTimeField()

    def get_data_source_id(self, instance):
        if instance.source == FLATTEN_PG_SOURCE:
            return instance.data_source_id
        elif instance.source == FLATTEN_ES_SOURCE:
            return instance.data_source_es_id
        else:
            return None

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class SaleItemAuditLogSerializer(TenantDBForSerializer):
    changes = serializers.SerializerMethodField()
    action = serializers.SerializerMethodField()
    model_name = serializers.SerializerMethodField()

    class Meta:
        model = LogEntry
        fields = '__all__'

    def get_changes(self, obj):
        res = json.loads(obj.changes) if obj.changes else None
        return res

    def get_action(self, obj):
        choices = (
            (0, "create"),
            (1, "update"),
            (2, "delete"),
        )
        return str(choices[obj.action][1])

    def get_model_name(self, obj):
        return obj.content_type.model


class UserPermissionSerializer(TenantDBForSerializer):
    class Meta:
        model = UserPermission
        fields = ('client_id', 'user_id', 'role', 'module_enabled', 'permissions')

    def to_representation(self, instance):
        res = super().to_representation(instance)
        try:
            res["permissions"].update({"PF_CLIENT_IS": instance.client.is_oe})
        except Exception as ex:
            logger.debug(f"[{self.__class__.__name__}][to_representation] {ex}")
        return res


class ChannelSerializer(TenantDBForSerializer):
    class Meta:
        model = Channel
        fields = '__all__'
