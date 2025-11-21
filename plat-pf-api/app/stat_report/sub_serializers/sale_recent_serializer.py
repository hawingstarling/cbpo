from rest_framework import serializers
from app.database.sub_serializers.tenant_db_for_serializer import TenantDBForSerializer
from app.stat_report.models import StatSaleRecentReport, StatSaleRecentSummaryReport


class StatSaleRecentReportSerializer(TenantDBForSerializer):
    marketplace = serializers.SerializerMethodField()

    class Meta:
        model = StatSaleRecentReport
        fields = "__all__"

    @classmethod
    def get_marketplace(cls, ins):
        return ins.channel.name


class StatSaleRecentSummarySerializer(TenantDBForSerializer):
    class Meta:
        model = StatSaleRecentSummaryReport
        fields = "__all__"


class StatSaleMarketPlaceSerializer(StatSaleRecentSummarySerializer):
    marketplace = serializers.SerializerMethodField()

    class Meta:
        model = StatSaleRecentSummaryReport
        exclude = ["report_date", "channel"]

    @classmethod
    def get_marketplace(cls, ins):
        return ins.channel.name


class StatSaleRecentReportDateSerializer(StatSaleRecentSummarySerializer):
    class Meta:
        model = StatSaleRecentSummaryReport
        exclude = ["channel"]
