import copy
from decimal import Decimal, ROUND_DOWN
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import empty
from app.financial.models import Sale
from app.core.services.audit_logs.base import AuditLogCoreManager, SALE_LEVEL, LogEntry
from app.core.sub_serializers.base_serializer import BaseSerializer
from app.financial.sub_serializers.bulk_base_serializer import BulkCreateSerializer
from app.financial.sub_serializers.client_serializer import ClientSaleItemSerializer
from app.financial.variable.bulk_edit_action_variable import BULK_EDIT_ACTION_CHOICE, BULK_EDIT_NUMERIC_ACTION_LIST, \
    BULK_EDIT_TEXT_ACTION_LIST, CHANGE_TO, ADD, SUBTRACT, MULTIPLY_BY, DIVIDE_BY, PERCENT_INCREASE, PERCENT_DECREASE, \
    UNDO_PERCENT_INCREASE, UNDO_PERCENT_DECREASE, APPEND, PREPEND

TEXT_BASE_FIELDS = (serializers.CharField,)

NUMERIC_BASE_FIELDS = (serializers.DecimalField, serializers.FloatField, serializers.IntegerField)


class ValueField(serializers.Field):
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        return data


class SaleItemBulkEditOperationSerializer(BaseSerializer):
    column = serializers.CharField(required=True)
    action = serializers.ChoiceField(required=True, choices=BULK_EDIT_ACTION_CHOICE)
    value = ValueField(required=True)


class SaleItemBulkEditCreateSerializer(BulkCreateSerializer):
    updates = serializers.ListField(required=True, child=SaleItemBulkEditOperationSerializer(), allow_empty=False)

    def validate_updates(self, data):
        errors = []
        for item in data:
            fields = ClientSaleItemBulkEditSerializer(context=self.context).get_fields()
            column = item['column']
            if not fields.get(column):
                errors.append('Column<{column}> not exists'.format(column=column))
                continue
            action = item['action']
            value = item['value']
            column_type = fields.get(column)
            type_name = column_type.__class__.__name__
            # Validate action on column
            if (action in BULK_EDIT_TEXT_ACTION_LIST and not isinstance(column_type, TEXT_BASE_FIELDS)) or (
                    action in BULK_EDIT_NUMERIC_ACTION_LIST and not isinstance(column_type, NUMERIC_BASE_FIELDS)):
                error_detail = f'Cannot apply action<{action}> to column<{column}> - type<{type_name}>'
                errors.append(error_detail)
            # Validate value to be applied on column
            try:
                column_type.run_validation(data=value)
            except ValidationError:
                error_detail = f'Invalid value<{value}> for editing column<{column}> - type<{type_name}>'
                errors.append(error_detail)
        if errors:
            raise ValidationError(detail=errors)
        return data


class ClientSaleItemBulkEditSerializer(ClientSaleItemSerializer):
    sale_date = serializers.DateTimeField(required=False, allow_null=True, write_only=True)

    @property
    def fields_sale_bulk_accept(self):
        return [i.name for i in Sale._meta.fields if
                i.name not in ['pk', 'id', 'created', 'modified', 'is_removed', 'channel_sale_id', 'channel', 'client']]

    def __init__(self, instance=None, data=empty, **kwargs):
        calculated_data = copy.deepcopy(data)
        if instance and data and kwargs.get('bulk_edit'):
            calculated_data = {}
            for (key, operation) in data.items():
                if key in self.fields_sale_bulk_accept:
                    origin_value = getattr(instance.sale, key)
                else:
                    if key == 'size_variant':
                        origin_value = getattr(instance, 'size')
                    elif key == 'style_variant':
                        origin_value = getattr(instance, 'style')
                    else:
                        origin_value = getattr(instance, key)
                action = operation.get('action', '')
                value = operation.get('value', '')
                calculated_value = self.bulk_edit_calculate(origin_value=origin_value, action=action, value=value)
                if action in BULK_EDIT_NUMERIC_ACTION_LIST:
                    calculated_value = calculated_value.quantize(Decimal('.01'), rounding=ROUND_DOWN)
                calculated_data[key] = calculated_value
        if 'bulk_edit' in kwargs:
            del kwargs['bulk_edit']
        super().__init__(instance=instance, data=calculated_data, **kwargs)

    @staticmethod
    def bulk_edit_calculate(origin_value, action, value):
        if action == CHANGE_TO:
            return value
        # Applied for numeric columns
        elif action == ADD:
            return Decimal(origin_value) + Decimal(value)
        elif action == SUBTRACT:
            return Decimal(origin_value) - Decimal(value)
        elif action == MULTIPLY_BY:
            return Decimal(origin_value) * Decimal(value)
        elif action == DIVIDE_BY:
            return Decimal(origin_value) / Decimal(value)
        elif action == PERCENT_INCREASE:
            return Decimal(origin_value) * (1 + Decimal(value) / 100)
        elif action == PERCENT_DECREASE:
            return Decimal(origin_value) * (1 - Decimal(value) / 100)
        elif action == UNDO_PERCENT_INCREASE:
            return Decimal(origin_value) / (1 + Decimal(value) / 100)
        elif action == UNDO_PERCENT_DECREASE:
            return Decimal(origin_value) / (1 - Decimal(value) / 100)
        # Text column only
        elif action == APPEND:
            origin_value = origin_value if origin_value is not None else ''
            return f'{origin_value}{value}'
        elif action == PREPEND:
            origin_value = origin_value if origin_value is not None else ''
            return f'{value}{origin_value}'
        else:
            return origin_value

    def update_single_data_sale(self, sale, validated_data):
        origin = copy.deepcopy(sale)

        # update state
        self.map_form_sale_data(sale, validated_data)

        log_entry = AuditLogCoreManager(client_id=self.client_id) \
            .create_log_entry_instance(
            level=SALE_LEVEL,
            origin=origin,
            target=sale,
            action=LogEntry.Action.UPDATE
        )
        return sale, log_entry
