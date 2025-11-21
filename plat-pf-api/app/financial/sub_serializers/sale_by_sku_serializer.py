from app.financial.models import SaleBySKU
from app.database.sub_serializers.tenant_db_for_serializer import TenantDBForSerializer


class SaleBySKUSerializer(TenantDBForSerializer):
    class Meta:
        model = SaleBySKU
        fields = '__all__'
