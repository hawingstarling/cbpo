from rest_framework import serializers


class BaseSerializer(serializers.Serializer):
    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class ExportResponseSerializer(BaseSerializer):
    file_url = serializers.CharField(max_length=500)


class CostInputSerializer(BaseSerializer):
    value = serializers.DecimalField(max_digits=6, decimal_places=2, allow_null=False, required=True)
