from rest_framework import serializers

from app.financial.services.sale_item_mapping.mapping_sale_item_common_from_live_feed_dc import \
    VALID_SALE_ITEM_COMMON_FIELDS_LIVE_FEED_DC
from app.financial.sub_serializers.bulk_base_serializer import BulkCreateSerializer
from app.financial.variable.bulk_sync_datasource_variable import BULK_SYNC_DATASOURCE_LIST, AMAZON_SELLER_CENTRAL


class SaleItemBulkSyncCreateSerializer(BulkCreateSerializer):
    sources = serializers.ListField(required=False, allow_empty=True,
                                    child=serializers.ChoiceField(BULK_SYNC_DATASOURCE_LIST))
    dc_fields = serializers.ListField(required=False, child=serializers.CharField())
    dc_is_override = serializers.BooleanField(required=False, default=False)
    ac_is_forced = serializers.BooleanField(required=False, default=False)
    # pf_calculations = serializers.BooleanField(required=False, default=False)
    pf_calculation_recalculate_shipping_costs = serializers.BooleanField(required=False, default=False)
    pf_calculation_recalculate_cog = serializers.BooleanField(required=False, default=False)
    pf_calculation_recalculate_total_costs = serializers.BooleanField(required=False, default=False)
    pf_calculation_recalculate_segments = serializers.BooleanField(required=False, default=False)
    pf_calculation_recalculate_user_provided_cost = serializers.BooleanField(required=False, default=False)
    pf_calculation_recalculate_inbound_freight_cost = serializers.BooleanField(required=False, default=False)
    pf_calculation_recalculate_outbound_freight_cost = serializers.BooleanField(required=False, default=False)
    pf_calculation_recalculate_skuvault = serializers.BooleanField(required=False, default=False)
    pf_calculation_recalculate_cart_rover = serializers.BooleanField(required=False, default=False)
    pf_calculation_recalculate_ff = serializers.BooleanField(required=False, default=False)
    pf_calculation_is_override = serializers.BooleanField(required=False, default=False)

    @classmethod
    def validate_dc_fields(cls, value):
        if not value:
            return VALID_SALE_ITEM_COMMON_FIELDS_LIVE_FEED_DC
        for item in value:
            if item not in VALID_SALE_ITEM_COMMON_FIELDS_LIVE_FEED_DC:
                raise serializers.ValidationError(f'{item} field is invalid')
        return value

    def validate(self, attrs):
        ac_is_forced = attrs.get('ac_is_forced', False)
        sources = attrs.get('sources', [])
        ids = attrs.get('ids', [])
        if ac_is_forced and AMAZON_SELLER_CENTRAL not in sources:
            raise serializers.ValidationError(
                f'ac_is_forced is only available for syncing from {AMAZON_SELLER_CENTRAL}')
        if ac_is_forced and len(ids) > 10:
            raise serializers.ValidationError('ac_is_forced is only available for syncing at most 10 records')
        return super(SaleItemBulkSyncCreateSerializer, self).validate(attrs)
