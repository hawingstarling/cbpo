from rest_framework import serializers

from app.financial.models import User
from app.database.sub_serializers.tenant_db_for_serializer import TenantDBForSerializer


class UserSerializer(TenantDBForSerializer):
    fullname_search = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = '__all__'

    @staticmethod
    def get_fullname_search(ins: User):
        vals = []
        if ins.first_name:
            vals.append(ins.first_name.lower())
        if ins.last_name:
            vals.append(ins.last_name.lower())
        return ' '.join(vals)
