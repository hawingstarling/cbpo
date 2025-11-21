import logging
from django.db.models import Sum, Q
from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from app.core.utils import get_nested_attr
from app.financial.models import SaleItemTransaction, CacheSaleItemTransaction
from app.core.services.audit_logs.base import AuditLogCoreManager, SALE_ITEM_TRANS_LEVEL
from app.financial.services.utils.common import round_currency
from app.database.sub_serializers.tenant_db_for_serializer import TenantDBForSerializer
from app.financial.variable.sale_status_static_variable import SALE_REFUNDED_STATUS
from app.financial.variable.shipping_cost_source import SHIP_CARRIER_FEDEX
from app.financial.variable.transaction.config import TransTypeConfig
from app.financial.variable.transaction.generic import TRANS_COLUMN_EXIST_ADJUSTMENT_EVENT, POSTAGE_BILLING_TYPES, \
    RETURN_POSTAGE_BILLING_TYPES
from auditlog.models import LogEntry

logger = logging.getLogger(__name__)


class SaleItemTransEventSerializer(TenantDBForSerializer):
    type_trans = serializers.SerializerMethodField()
    item_amount = serializers.SerializerMethodField()
    total_sale_item = serializers.SerializerMethodField()

    class Meta:
        model = SaleItemTransaction
        fields = '__all__'
        read_only_fields = ['id', 'client', 'content_type', 'channel', 'is_removed', 'created', 'modified']

    def get_total_sale_item(self, instance):
        sale_item = self.context['instance']
        sale = sale_item.sale
        return sale.saleitem_set.tenant_db_for(sale.client_id).count()

    def validate_amount(self, value):
        errors = []
        if value == 0:
            errors.append("Amount can't pass with zero")
        if errors:
            raise ValidationError(errors, code="amount")
        return value

    def process_trans_event(self, validated_data: dict):
        """
        :param validated_data:
        :return:
        """
        client = validated_data.pop('client')
        channel_sale_id = validated_data.pop('channel_sale_id')
        channel = validated_data.pop('channel')
        sku = validated_data.pop('sku')
        trans_type = validated_data.pop('type')
        category = validated_data.pop('category')
        event = validated_data.pop('event')
        content_type = validated_data.pop('content_type')
        seq = validated_data.pop('seq')

        created = True
        action = LogEntry.Action.CREATE
        origin = None
        #
        unique = dict(content_type=content_type, sku=sku, type=trans_type, category=category, event=event)
        queryset = SaleItemTransaction.all_objects.tenant_db_for(self.client_id) \
            .filter(client=client, channel=channel, channel_sale_id=channel_sale_id)
        obj = SaleItemTransaction(client=client, channel=channel, channel_sale_id=channel_sale_id, **unique, seq=seq)
        try:
            if seq == 1:
                origin = queryset.filter(**unique, seq__isnull=True).first()
            if not origin:
                origin = queryset.get(**unique, seq=seq)
            obj.id = origin.id
            created = False
            action = LogEntry.Action.UPDATE
        except Exception as ex:
            pass
        #
        obj.is_removed = False
        obj.seq = seq
        obj.modified = timezone.now()
        for attr, value in validated_data.items():
            setattr(obj, attr, value)
        # make log entry
        log_entry = AuditLogCoreManager(client_id=client.pk).create_log_entry_instance(level=SALE_ITEM_TRANS_LEVEL,
                                                                                       origin=origin, target=obj,
                                                                                       action=action)
        return obj, created, log_entry

    def get_type_trans(self, instance):
        return dict(TransTypeConfig).get(instance.type)

    def get_item_amount(self, instance):
        # get info from serializer context
        request = self.context['request']
        column = request.query_params.get('column', None)

        sale_item = self.context['instance']

        type_breakdown = POSTAGE_BILLING_TYPES + RETURN_POSTAGE_BILLING_TYPES

        if not column or column not in TRANS_COLUMN_EXIST_ADJUSTMENT_EVENT \
                or sale_item.sale.saleitem_set.tenant_db_for(
            sale_item.sale.client_id).count() == 1 or instance.type not in type_breakdown:
            return instance.amount
        return self.split_amount_breakdown(column, instance, sale_item)

    def split_amount_breakdown(self, column, instance, sale_item):
        amount = instance.amount
        try:
            sale = sale_item.sale
            fulfillment_type = sale_item.fulfillment_type
            queryset = sale.saleitem_set.tenant_db_for(sale.client_id).all()

            multiple = 1
            if column == 'shipping_cost' and fulfillment_type.name.startswith('MFN') and \
                    instance.type in POSTAGE_BILLING_TYPES:
                cond_mfn = Q(fulfillment_type__name__startswith='MFN') & ~Q(ship_carrier=SHIP_CARRIER_FEDEX)
                queryset = queryset.filter(cond_mfn)
                #
                if sale_item.sale_status.value in [SALE_REFUNDED_STATUS]:
                    multiple = 2

            total_quantity = queryset.aggregate(total=Sum('quantity'))
            amount_base_quantity = amount / total_quantity['total']
            amount = amount_base_quantity * sale_item.quantity * multiple

            return round_currency(amount)

        except Exception as ex:
            logger.error(f'[{self.__class__.__name__}][split_amount_breakdown] : {ex}')
        return amount


class SaleItemTransEventLogSerializer(SaleItemTransEventSerializer):
    class Meta:
        model = SaleItemTransaction
        fields = ['client', 'content_type', 'type', 'category', 'event', 'channel_sale_id', 'channel', 'sku', 'seq',
                  'amount', 'currency', 'quantity', 'date', 'type', 'category', 'event', 'is_removed']

    @property
    def log_data(self):
        if self.instance:
            data = self.data
        else:
            data = self.data
            data['client'] = None
            data['channel'] = None
            data['content_type'] = None
        rs = {key: str(data[key]) if data[key] else None for key in sorted(data.keys())}
        return rs

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['client'] = get_nested_attr(instance, 'client.id')
        data['channel'] = get_nested_attr(instance, 'channel.name')
        data['content_type'] = get_nested_attr(instance, 'content_type.id')
        return data


class SaleItemCacheTransEventSerializer(TenantDBForSerializer):
    class Meta:
        model = CacheSaleItemTransaction
        fields = '__all__'
        read_only_fields = ['id', 'client', 'content_type', 'channel', 'is_removed', 'created', 'modified']

    def process_trans_event(self, validated_data: dict):
        """
        :param validated_data:
        :return:
        """
        client = validated_data.pop('client')
        channel_sale_id = validated_data.pop('channel_sale_id')
        channel = validated_data.pop('channel')
        content_type = validated_data.pop('content_type')

        unique = dict(client=client, content_type=content_type, channel_sale_id=channel_sale_id, channel=channel)
        obj = CacheSaleItemTransaction(**unique)

        created = True

        try:
            origin = CacheSaleItemTransaction.all_objects.tenant_db_for(self.client_id).get(**unique)
            obj.id = origin.id
            created = False
        except Exception as ex:
            pass
        #
        obj.is_removed = False
        obj.modified = timezone.now()
        for attr, value in validated_data.items():
            setattr(obj, attr, value)
        return obj, created
