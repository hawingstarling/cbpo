from rest_framework import serializers
from app.financial.models import Activity, User
from app.database.sub_serializers.tenant_db_for_serializer import TenantDBForSerializer
from app.financial.sub_serializers.user_serializer import UserSerializer


class ActivitySerializer(TenantDBForSerializer):
    user_info = serializers.SerializerMethodField()

    class Meta:
        model = Activity
        fields = '__all__'

    def get_user_info(self, instance):
        try:
            user = User.objects.tenant_db_for(instance.client_id).get(user_id=instance.user_id)
            return UserSerializer(user).data
        except Exception as ex:
            return {}
