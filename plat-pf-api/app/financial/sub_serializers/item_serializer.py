from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from app.core.logger import logger
from app.financial.models import Item, Brand, Variant, ItemCog, FulfillmentChannel, Channel
from app.financial.sub_serializers.default_message_serializer import default_error_message
from app.database.sub_serializers.tenant_db_for_serializer import TenantDBForSerializer


class ItemReferenceValidation(TenantDBForSerializer):
    class Meta:
        model = Item
        fields = '__all__'

    def validate_brand(self, value):
        try:
            return Brand.objects.tenant_db_for(self.client_id).get(name=value, client_id=self.client_id)
        except Brand.DoesNotExist:
            raise ValidationError('{} brand does not exist in the system'.format(value), code="brand")

    def validate_channel(self, value):
        try:
            return Channel.objects.tenant_db_for(self.client_id).get(name=value)
        except Channel.DoesNotExist:
            raise ValidationError(f'{value} channel does not exist in the system', code='channel')

    def validate_size(self, value):
        if not value:
            return None
        size_obj, _ = Variant.objects.tenant_db_for(self.client_id).get_or_create(type="Size", name=value, value=value)
        return size_obj

    def validate_style(self, value):
        if not value:
            return None
        style_obj, _ = Variant.objects.tenant_db_for(self.client_id).get_or_create(type="Style", name=value,
                                                                                   value=value)
        return style_obj

    def validate_fulfillment_type(self, value):
        errors = []
        if value:
            try:
                value = FulfillmentChannel.objects.tenant_db_for(self.client_id).get(name=value)
            except FulfillmentChannel.DoesNotExist:
                errors.append("Fulfillment Type is invalid")
        else:
            errors.append("Fulfillment Type is required")

        if len(errors):
            raise ValidationError(errors, code="fulfillment_type")
        return value


class ItemImportSerializer(ItemReferenceValidation):
    #  using base validation from django models
    #  provide serializer field for reference fields only

    brand = serializers.CharField(max_length=50, write_only=True, error_messages=default_error_message('Brand', 50))
    channel = serializers.CharField(max_length=50, write_only=True, error_messages=default_error_message('Channel', 50))

    size = serializers.CharField(max_length=50, allow_blank=True, allow_null=True, required=False,
                                 write_only=True)
    style = serializers.CharField(max_length=50, allow_blank=True, allow_null=True, required=False,
                                  write_only=True)

    cog = serializers.DecimalField(max_digits=6, decimal_places=2, write_only=True, label="COG",
                                   error_messages=default_error_message('Cost of Good'))

    effective_start_date = serializers.DateTimeField(required=False, allow_null=True, write_only=True,
                                                     label="Effective Start Date",
                                                     error_messages=default_error_message("Effective Start Date"))
    effective_end_date = serializers.DateTimeField(required=False, allow_null=True, write_only=True,
                                                   label="Effective End Date",
                                                   error_messages=default_error_message("Effective End Date"))
    fulfillment_type = serializers.CharField(max_length=45, label="Fulfillment Type", write_only=True,
                                             error_messages=default_error_message("Fulfillment Type"))

    estimated_shipping_cost = serializers.DecimalField(max_digits=6, decimal_places=2, write_only=True,
                                                       error_messages=default_error_message('Estimated Shipping Cost'))

    estimated_dropship_cost = serializers.DecimalField(max_digits=6, decimal_places=2, write_only=True,
                                                       error_messages=default_error_message(
                                                           'Estimated Drop Shipping Cost'))

    class Meta:
        model = Item
        fields = ['sku', 'upc', 'asin', 'cog', 'title', 'fulfillment_type', 'brand', 'channel', 'size',
                  'style', 'estimated_shipping_cost', 'estimated_dropship_cost', 'effective_start_date',
                  'effective_end_date', 'description', 'product_number', 'product_type', 'parent_asin']

        read_only_fields = ['id']

        extra_kwargs = {
            'sku': {
                "error_messages": default_error_message('SKU')
            },
            'upc': {
                "error_messages": default_error_message('UPC', 45)
            },
            'asin': {
                "error_messages": default_error_message('ASIN', 45)
            },
            'title': {
                "error_messages": default_error_message('Title', 256)
            }
        }

    def validate(self, data):
        start_date = data.get('effective_start_date')
        end_date = data.get('effective_end_date')
        if start_date and end_date:
            if start_date > end_date:
                raise serializers.ValidationError('Effective Start Date must be less than Effective End Date')
        return data

    def create(self, validated_data):
        cog = validated_data.pop('cog')
        effect_start_date = validated_data.pop('effective_start_date', None)
        effect_end_date = validated_data.pop('effective_end_date', None)

        est_shipping_cost = validated_data.pop('estimated_shipping_cost', None)
        est_drop_ship_cost = validated_data.pop('estimated_dropship_cost', None)

        validated_data.update({"est_shipping_cost": est_shipping_cost,
                               "est_drop_ship_cost": est_drop_ship_cost})

        sku = validated_data.pop('sku')
        client_id = self.client_id

        validated_data.update({'is_removed': False})

        # create Table Item
        instance, _ = Item.all_objects.update_or_create(client_id=client_id, sku=sku, defaults=validated_data)
        # update Table Item Cog
        ItemCog.all_objects.update_or_create(item=instance, **{"cog": cog,
                                                               "effect_start_date": effect_start_date,
                                                               "effect_end_date": effect_end_date,
                                                               "is_removed": False})
        return instance

    def update(self, instance, validated_data):
        cog = validated_data.pop('cog')
        effect_start_date = validated_data.pop('effective_start_date', None)
        effect_end_date = validated_data.pop('effective_end_date', None)

        est_shipping_cost = validated_data.pop('estimated_shipping_cost', None)
        est_drop_ship_cost = validated_data.pop('estimated_dropship_cost', None)

        validated_data.update({"est_shipping_cost": est_shipping_cost,
                               "est_drop_ship_cost": est_drop_ship_cost})

        # update Table Item
        ins = super().update(instance, validated_data)
        # update Table Item Cog
        ItemCog.all_objects.tenant_db_for(self.client_id).update_or_create(
            item=instance,
            **{"cog": cog,
               "effect_start_date": effect_start_date,
               "effect_end_date": effect_end_date,
               "is_removed": False})
        return ins


class ItemSerializer(ItemReferenceValidation):
    brand = serializers.CharField(max_length=50, write_only=True, error_messages=default_error_message('Brand', 50))
    channel = serializers.CharField(max_length=50, write_only=True, error_messages=default_error_message('Channel', 50))

    size = serializers.CharField(max_length=50, allow_blank=True, allow_null=True, required=False,
                                 write_only=True)
    style = serializers.CharField(max_length=50, allow_blank=True, allow_null=True, required=False,
                                  write_only=True)
    fulfillment_type = serializers.CharField(max_length=45, required=False, allow_null=True, allow_blank=True,
                                             label="Fulfillment Type", write_only=True)

    class Meta:
        model = Item
        fields = ['id', 'sku', 'upc', 'asin', 'title', 'description', 'est_shipping_cost', 'est_drop_ship_cost',
                  'brand', 'channel', 'size', 'style', 'fulfillment_type', 'product_number', 'product_type',
                  'parent_asin']
        read_only_fields = ['id']

    def create(self, validated_data):
        sku = validated_data.pop('sku')
        validated_data.update({'is_removed': False})

        instance, _ = Item.all_objects.tenant_db_for(self.client_id).update_or_create(client_id=self.client_id, sku=sku,
                                                                                      defaults=validated_data)
        return instance


class ItemLargeImportSerializer(TenantDBForSerializer):
    brand = serializers.CharField(max_length=50, write_only=True, error_messages=default_error_message('Brand', 50))

    class Meta:
        model = Item
        fields = ['sku', 'asin', 'brand']

    def validate_brand(self, value):
        brand_bucket = self.context['brand_bucket']
        brand = brand_bucket.get(value)
        if brand is None:
            raise ValidationError('{} brand does not exist in the system'.format(value), code="brand")
        return brand


class ItemDetailSerializer(TenantDBForSerializer):
    cogs = serializers.SerializerMethodField()
    size = serializers.SerializerMethodField()
    style = serializers.SerializerMethodField()
    brand = serializers.SerializerMethodField()
    channel = serializers.SerializerMethodField()
    fulfillment_type = serializers.SerializerMethodField()

    class Meta:
        model = Item
        exclude = ['is_removed', 'client']

    def get_cogs(self, instance):
        cogs = ItemCog.objects.tenant_db_for(self.client_id).filter(item=instance)
        serializer = ItemCogSerializer(cogs, many=True, context=self.context)
        return serializer.data

    @classmethod
    def get_size(cls, instance):
        try:
            return instance.size.value
        except AttributeError:
            return None

    @classmethod
    def get_style(cls, instance):
        try:
            return instance.style.value
        except AttributeError:
            return None

    @classmethod
    def get_brand(cls, instance):
        try:
            return instance.brand.name
        except AttributeError:
            return None

    @classmethod
    def get_channel(cls, instance):
        try:
            return instance.channel.name
        except AttributeError:
            return None

    @classmethod
    def get_fulfillment_type(cls, instance):
        try:
            return instance.fulfillment_type.name
        except AttributeError:
            return None


class ItemCogSerializer(TenantDBForSerializer):
    class Meta:
        model = ItemCog
        exclude = ['is_removed', 'item']

    def create(self, validated_data):
        try:
            item_id = self.context['item_id']
            item = Item.objects.tenant_db_for(self.client_id).get(pk=item_id)
            validated_data.update({'item': item})
            return super().create(validated_data)
        except Item.DoesNotExist:
            raise ValidationError('Item does not exist')

    def validate(self, data):
        start_date = data.get('effect_start_date')
        end_date = data.get('effect_end_date')
        if start_date and end_date:
            if start_date > end_date:
                raise serializers.ValidationError('Effective Start Date must be less than Effective End Date')
        return data


class ItemBulkActionSerializer(ItemSerializer):
    class Meta(ItemSerializer.Meta):
        fields = [update_field for update_field in ItemSerializer.Meta.fields
                  if update_field not in ['upc', 'sku', 'asin']]

    def bulk_update(self, object_ids: [str]):
        self.validated_data.update({'is_removed': False})
        Item.objects.tenant_db_for(self.client_id).filter(id__in=object_ids, client_id=self.client_id).update(
            **self.validated_data)

    def bulk_delete(self, object_ids):
        ItemCog.objects.tenant_db_for(self.client_id).filter(item__id__in=object_ids).delete()
        Item.objects.tenant_db_for(self.client_id).filter(id__in=object_ids, client_id=self.client_id).delete()

    def validate_object_ids(self, object_ids):
        for item_id in object_ids:
            try:
                Item.objects.tenant_db_for(self.client_id).get(pk=item_id)
            except Item.DoesNotExist:
                raise ValidationError('Item {} does not exist'.format(item_id))
            except Exception as err:
                logger.error('[ItemImportSerializer] {}'.format(err))
                raise err
        return object_ids
