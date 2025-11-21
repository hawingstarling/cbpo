from rest_framework.validators import UniqueTogetherValidator

from app.core.context import AppContext
from app.database.sub_serializers.tenant_db_for_serializer import TenantDBForSerializer
from rest_framework import serializers
from app.financial.models import TopClientASINs, Channel
from app.financial.sub_serializers.default_message_serializer import default_error_message
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError


class TopASINsSerializer(TenantDBForSerializer):
    channel = serializers.CharField(max_length=50, error_messages=default_error_message('Channel', 50))

    def validate_channel(self, value):
        try:
            return Channel.objects.tenant_db_for(self.client_id).get(name=value)
        except Channel.DoesNotExist:
            raise ValidationError('{} channel does not exist in the system'.format(value), code="channel")

    class Meta:
        model = TopClientASINs
        fields = "__all__"
        validators = [
            UniqueTogetherValidator(
                queryset=TopClientASINs.objects.tenant_db_for(AppContext.instance().client_id).all(),
                fields=['client', 'channel', 'parent_asin', 'child_asin'],
                message=_('Channel, Parent/Child ASINs must be unique')
            )
        ]


# class TopASINsBulkActionSerializer(TopASINsSerializer):
#     class Meta(TopASINsSerializer.Meta):
#         fields = [update_field for update_field in TopASINsSerializer.Meta.fields
#                   if update_field not in ['parent_asin', 'child_asin', 'sku']]


class TopASINsImportSerializer(TopASINsSerializer):
    class Meta:
        model = TopClientASINs
        fields = ["channel", "parent_asin", "child_asin", "segment"]
        extra_kwargs = {
            "channel": {
                "error_messages": default_error_message("Channel"),
                "label": 'Channel'
            },
            "parent_asin": {
                "error_messages": default_error_message("Parent ASIN"),
                "label": "Parent ASIN"
            },
            "child_asin": {
                "error_messages": default_error_message("Child ASIN"),
                "label": "Child ASIN"
            },
            "segment": {
                "required": False,
                "error_messages": default_error_message("Segment"),
                "label": "Segment",
                "allow_null": True
            }
        }
