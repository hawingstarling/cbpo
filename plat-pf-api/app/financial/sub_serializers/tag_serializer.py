import logging

from rest_framework import serializers
from rest_framework.fields import empty
from rest_framework.validators import UniqueTogetherValidator

from app.core.context import AppContext
from app.financial.models import TagClient, CustomView, TagView
from app.database.sub_serializers.tenant_db_for_serializer import TenantDBForSerializer
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)


class TagSerializer(TenantDBForSerializer):
    custom_view_ids = serializers.ListField(required=False, child=serializers.UUIDField(), write_only=True)

    def __init__(self, instance=None, data=empty, **kwargs):
        super().__init__(instance, data, **kwargs)
        self.custom_view_ids = []

    class Meta:
        model = TagClient
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=TagClient.objects.tenant_db_for(AppContext.instance().client_id).all(),
                fields=['client', 'name'],
                message=_('Name must be unique')
            )
        ]

    def prefetch_bulk_custom_view(self, validated_data):
        try:
            self.custom_view_ids = validated_data.pop("custom_view_ids")
        except Exception as ex:
            pass

    def handler_bulk_custom_view(self, ins):
        try:
            assert len(self.custom_view_ids) > 0, "Custom view ids must larger 0"
            validated_data = dict(tag_ids=[str(ins.pk)], custom_view_ids=self.custom_view_ids)
            self.bulk_update(validated_data)
        except Exception as ex:
            logger.error(f"[{self.__class__.__name__}][handler_bulk_custom_view] {ex}")

    def bulk_update(self, validated_data):
        tag_ids = validated_data["tag_ids"]
        custom_view_ids = validated_data["custom_view_ids"]
        custom_view_queryset = CustomView.objects.tenant_db_for(self.client_id).filter(pk__in=custom_view_ids)
        tags_views = []
        for tag_id in tag_ids:
            for item in custom_view_queryset:
                tags_views.append(TagView(client_id=self.client_id, custom_view=item, tag_id=tag_id))
        TagView.objects.tenant_db_for(self.client_id).bulk_create(tags_views, ignore_conflicts=True)

    def create(self, validated_data):
        self.prefetch_bulk_custom_view(validated_data)
        ins = super().create(validated_data)
        self.handler_bulk_custom_view(ins)
        return ins

    def update(self, instance, validated_data):
        self.prefetch_bulk_custom_view(validated_data)
        ins = super().update(instance, validated_data)
        self.handler_bulk_custom_view(ins)
        return ins


class TagCreateSerializer(TagSerializer):
    class Meta(TagSerializer.Meta):
        fields = ["name", "color", "custom_view_ids"]


class TagCreateBulkSerializer(TagSerializer):
    tag_ids = serializers.ListField(required=True, child=serializers.UUIDField())
    custom_view_ids = serializers.ListField(required=True, child=serializers.UUIDField())

    class Meta(TagSerializer.Meta):
        fields = ['tag_ids', 'custom_view_ids']
        validators = []
