from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from app.core.context import AppContext
from app.financial.models import Alert
from django.utils.translation import gettext_lazy as _
from app.database.sub_serializers.tenant_db_for_serializer import TenantDBForSerializer


class AlertSerializer(TenantDBForSerializer):
    users = serializers.ListField(child=serializers.CharField(max_length=100), required=False)
    phones = serializers.ListField(child=serializers.CharField(max_length=50), required=False)
    emails = serializers.ListField(child=serializers.CharField(max_length=100), required=False)

    class Meta:
        model = Alert
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Alert.objects.tenant_db_for(AppContext.instance().client_id).all(),
                fields=['client', 'custom_view'],
                message=_('Custom view must be unique')
            )
        ]
