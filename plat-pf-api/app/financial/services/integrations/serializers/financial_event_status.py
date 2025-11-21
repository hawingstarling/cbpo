from rest_framework import serializers

from app.core.sub_serializers.base_serializer import BaseSerializer


class FinancialEventDataStatusSerializer(BaseSerializer):
    marketplace = serializers.CharField(max_length=50, required=True)
    posted_date = serializers.DateField(required=True, format='%Y-%m-%d')
    ready = serializers.BooleanField(required=True)


class OrderEventDataStatusSerializer(BaseSerializer):
    marketplace = serializers.CharField(max_length=50, required=True)
    modified_date = serializers.DateField(required=True, format='%Y-%m-%d')
    ready = serializers.BooleanField(required=True)

class InformedReportDataStatusSerializer(BaseSerializer):
    posted_date = serializers.DateField(required=True, format='%Y-%m-%d')
    report_type = serializers.CharField(max_length=50, required=True)
    ready = serializers.BooleanField(required=True)
