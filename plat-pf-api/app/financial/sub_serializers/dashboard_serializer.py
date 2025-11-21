from rest_framework import serializers
from app.financial.models import DashboardConfig, DivisionClientUserWidget, WidgetConfig, ClientDashboardWidget
from app.core.sub_serializers.base_serializer import BaseSerializer
from app.database.sub_serializers.tenant_db_for_serializer import TenantDBForSerializer
from app.financial.variable.dashboard import PROPORTION_CHOICE, DEFAULT_PROPORTION


class DashboardConfigSerializer(TenantDBForSerializer):
    class Meta:
        model = DashboardConfig
        fields = '__all__'


class WidgetConfigSerializer(TenantDBForSerializer):
    class Meta:
        model = WidgetConfig
        fields = ['id', 'key', 'value', 'icon_url']


class ClientDashboardWidgetSerializer(TenantDBForSerializer):
    widget = WidgetConfigSerializer(read_only=True)

    class Meta:
        model = ClientDashboardWidget
        fields = '__all__'


class ClientDashboardWidgetPayloadSerializer(BaseSerializer):
    widget = serializers.CharField(max_length=255)
    enabled = serializers.BooleanField(required=False)
    position = serializers.IntegerField(required=False)
    settings = serializers.JSONField(required=False)

    @classmethod
    def validate_setting(cls, value):
        if 'goal' not in value:
            raise serializers.ValidationError("JSON data must contain 'goal' key")
        return value

    def validate(self, attrs):
        if "settings" not in attrs and "enabled" not in attrs and "position" not in attrs:
            raise serializers.ValidationError("JSON data must contain 'setting', 'enabled' or 'position' key")
        return super().validate(attrs)


class BulkClientDashboardWidgetSerializer(BaseSerializer):
    data = serializers.ListField(child=ClientDashboardWidgetPayloadSerializer())


class DivisionClientUserWidgetSerializer(BaseSerializer):
    segment = serializers.CharField(max_length=255)
    enabled = serializers.BooleanField(default=True)


class BulkDivisionClientUserWidgetSerializer(BaseSerializer):
    data = serializers.ListField(child=DivisionClientUserWidgetSerializer())


class DivisionUserWidgetSettingSerializer(TenantDBForSerializer):
    class Meta:
        model = DivisionClientUserWidget
        exclude = ['id', 'client', 'category', 'created', 'modified']


class BulkDivisionUserWidgetSettingSerializer(BaseSerializer):
    data = serializers.ListField(child=DivisionUserWidgetSettingSerializer())
