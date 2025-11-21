from typing import Union

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from app.financial.models import BrandSetting, Brand, Channel
from app.core.sub_serializers.base_serializer import BaseSerializer
from app.financial.sub_serializers.client_serializer import ChannelSerializer
from app.financial.sub_serializers.item_serializer import default_error_message
from app.financial.sub_serializers.brand_serializer import BrandSerializer
from app.database.sub_serializers.tenant_db_for_serializer import TenantDBForSerializer
from app.financial.variable.brand_setting import VALID_MFN_FORMULA, PO_DROPSHIP_METHOD_LIST, PO_DROPSHIP_PERCENT_METHOD


class BrandSettingSerializer(TenantDBForSerializer):
    channel = serializers.CharField(error_messages=default_error_message('Channel'))
    brand = serializers.CharField(allow_null=True, error_messages=default_error_message('Brand'))

    class Meta:
        model = BrandSetting
        exclude = ['is_removed', 'client', 'est_unit_freight_cost']

    def validate_brand(self, value):
        if value is not None:
            try:
                value = Brand.all_objects.tenant_db_for(self.client_id).get(name=value, client_id=self.client_id)
                if value.is_removed is True:
                    value.is_removed = False
                    value.save()
            except Brand.DoesNotExist:
                value = Brand.objects.tenant_db_for(self.client_id).create(name=value, client_id=self.client_id)
        return value

    def validate_segment(self, value):
        if value is not None:
            value = value.title()
        return value

    def validate_channel(self, value):
        try:
            return Channel.objects.tenant_db_for(self.client_id).get(name=value)
        except Channel.DoesNotExist:
            raise ValidationError('{} channel does not exist in the system'.format(value), code="channel")

    @classmethod
    def validate_mfn_formula(cls, value):
        if value in VALID_MFN_FORMULA:
            return value
        raise serializers.ValidationError(f'{value} is invalid.')

    @classmethod
    def validate_fields_method(cls, field: str, method: str, value: any):
        if method == PO_DROPSHIP_PERCENT_METHOD and value is not None:
            try:
                assert 0 <= int(value) <= 100, "PO dropship cost must have value in [0, 100]%"
            except Exception as ex:
                raise serializers.ValidationError(str(ex), field)

    def validate(self, attrs):
        po_dropship_method = attrs.get('po_dropship_method')
        po_dropship_cost = attrs.get('po_dropship_cost')
        self.validate_fields_method('po_dropship_cost', po_dropship_method, po_dropship_cost)
        add_user_provided_method = attrs.get('add_user_provided_method')
        add_user_provided_cost = attrs.get('add_user_provided_cost')
        self.validate_fields_method('add_user_provided_cost', add_user_provided_method, add_user_provided_cost)
        return attrs

    def create(self, validated_data):
        #
        view = self.context['view']
        client = view.get_client()
        channel = validated_data.pop('channel')
        brand = validated_data.pop('brand', None)
        ins, _ = BrandSetting.all_objects.tenant_db_for(self.client_id) \
            .update_or_create(client=client, channel=channel, brand=brand,
                              defaults={**validated_data, "is_removed": False})
        return ins

    def update(self, instance, validated_data):
        ins, _ = BrandSetting.all_objects.tenant_db_for(self.client_id) \
            .update_or_create(id=instance.id,
                              defaults={**validated_data, "is_removed": False})
        return ins

    def to_representation(self, instance):
        self.fields['brand'] = BrandSerializer()
        self.fields['channel'] = ChannelSerializer()
        return super().to_representation(instance)


class UpdateSaleSerializer(BaseSerializer):
    sale_date_from = serializers.DateTimeField()
    sale_date_to = serializers.DateTimeField()
    recalculate = serializers.BooleanField()


class CountUpdateSaleSerializerRes(BaseSerializer):
    count_sales = serializers.IntegerField()


class BrandSettingImportSerializer(BrandSettingSerializer):
    class Meta:
        model = BrandSetting
        exclude = BrandSettingSerializer.Meta.exclude + ['id', 'created', 'modified']

        extra_kwargs = {
            'est_first_item_shipcost': {
                "error_messages": default_error_message('Estimates first item ship cost')
            },
            'est_add_item_shipcost': {
                "error_messages": default_error_message('Estimates additional item ship cost')
            },
            'est_fba_fees': {
                "error_messages": default_error_message('Estimates FBA fees')
            },
            'est_unit_inbound_freight_cost': {
                "error_messages": default_error_message('Estimates Unit Inbound Freight Cost')
            },
            'est_unit_outbound_freight_cost': {
                "error_messages": default_error_message('Estimates Unit Outbound Freight Cost')
            },
            'po_dropship_method': {
                "error_messages": default_error_message('PO drop ship method'),
                "help_text": f"{', '.join(PO_DROPSHIP_METHOD_LIST)}"
            },
            'po_dropship_cost': {
                "error_messages": default_error_message('PO drop ship cost')
            },
            'add_user_provided_method': {
                "error_messages": default_error_message('Add. User-Provided method'),
                "help_text": f"{', '.join(PO_DROPSHIP_METHOD_LIST)}"
            },
            'add_user_provided_cost': {
                "error_messages": default_error_message('Add. User-Provided Cost')
            },
            'mfn_formula': {
                "error_messages": default_error_message('MFN Formula')
            },
            'auto_update_sales': {
                "error_messages": default_error_message('Auto Update Sales')
            }
        }
