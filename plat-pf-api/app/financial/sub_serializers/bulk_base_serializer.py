import logging

from app.core.utils import hashlib_content
from app.financial.models import BulkData
from plat_import_lib_api.models import DataImportTemporary, STATUS_CHOICE, PROCESSING, RawDataTemporary
from plat_import_lib_api.sub_serializers.common_serializer import ColumnsMappingResponseSerializer, ColumnsSerializer
from rest_framework import serializers
from app.core.sub_serializers.base_serializer import BaseSerializer
from app.database.sub_serializers.tenant_db_for_serializer import TenantDBForSerializer
from app.financial.variable.bulk_sync_datasource_variable import AMAZON_SELLER_CENTRAL

logger = logging.getLogger(__name__)

TEXT_BASE_FIELDS = (serializers.CharField,)

NUMERIC_BASE_FIELDS = (serializers.DecimalField, serializers.FloatField, serializers.IntegerField)


class BulkCreateSerializer(BaseSerializer):
    query = serializers.JSONField(required=False)
    ids = serializers.ListField(required=False, child=serializers.UUIDField())


class BulkSummaryErrorSerializer(BaseSerializer):
    id = serializers.UUIDField(required=True)
    message = serializers.CharField(required=True)


class BulkSummarySerializer(BaseSerializer):
    total = serializers.IntegerField(required=True)
    error = serializers.IntegerField(default=0)
    success = serializers.IntegerField(default=0)
    errors = serializers.ListField(child=BulkSummaryErrorSerializer(), default=[])


class BulkInfoSerializer(BaseSerializer):
    summary = BulkSummarySerializer()
    cols_file = serializers.ListField(child=ColumnsSerializer(), default=[])
    map_cols_to_module = serializers.ListField(child=ColumnsMappingResponseSerializer())


class BulkDataSerializer(TenantDBForSerializer):
    class Meta:
        model = BulkData
        fields = '__all__'


class BulkBaseSerializer(TenantDBForSerializer):
    info_import_file = BulkInfoSerializer(write_only=True)
    summary = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = DataImportTemporary
        fields = ['id', 'module', 'status', 'progress', 'summary', 'meta', 'info_import_file', 'json_data_last_cache',
                  'created', 'modified', 'client_id']
        extra_kwargs = {
            'module': {'required': False, 'write_only': True},
            'status': {'choices': STATUS_CHOICE, 'default': PROCESSING},
            'json_data_last_cache': {'write_only': True, 'default': '[]'}
        }

    @classmethod
    def get_summary(cls, instance) -> dict:
        summary = RawDataTemporary.summary(instance.pk)
        total = summary.get('total', 0)
        success = summary.get('completed', 0)
        if instance.progress < 100:
            error = 0
        else:
            error = total - success
        return {
            'total': total,
            'success': success,
            'error': error
        }

    def validate(self, attrs):
        meta = attrs.get('meta', {})
        ac_is_forced = meta.get('ac_is_forced', False)
        sources = meta.get('sources', [])
        total = attrs.get('info_import_file', 0).get('summary', 0).get('total', 0)
        if ac_is_forced and AMAZON_SELLER_CENTRAL not in sources:
            raise serializers.ValidationError(
                f'ac_is_forced is only available for syncing from {AMAZON_SELLER_CENTRAL}')
        if ac_is_forced and total > 10:
            raise serializers.ValidationError('ac_is_forced is only available for syncing at most 10 records')
        return super(BulkBaseSerializer, self).validate(attrs)

    def create(self, validated_data):
        client_id = validated_data.get('client_id')
        module = validated_data.get('module')
        meta = validated_data.get('meta')
        meta_hash = hashlib_content(meta)
        try:
            ins = DataImportTemporary.objects.db_manager(using=self.client_db) \
                .filter(client_id=client_id,
                        module=module, meta_hash=meta_hash,
                        progress__lt=100) \
                .order_by('-created').first()
            assert ins is not None, "Ins not exist in lib import"
        except Exception as ex:
            logger.info(
                f"[{self.__class__.__name__}][{client_id}][{module}][{meta_hash}] {ex}")
            validated_data.update(dict(meta_hash=meta_hash))
            ins = DataImportTemporary.objects.db_manager(using=self.client_db).create(**validated_data)
        return ins

    def update(self, instance, validated_data):
        instance._state = self.client_db
        return super().update(instance, validated_data)


class BulkListItemSerializer(BulkBaseSerializer):
    pass


class BulkDetailSerializer(BulkBaseSerializer):
    pass
