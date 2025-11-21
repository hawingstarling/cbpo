from app.financial.models import ShippingInvoice
from app.database.sub_serializers.tenant_db_for_serializer import TenantDBForSerializer


class ShippingInvoiceSerializer(TenantDBForSerializer):
    class Meta:
        model = ShippingInvoice
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data.update(instance.agg_trans)
        source_files = instance.source_files
        data.update(source_files=source_files)
        return data


# LOG INFO
class ShippingInvoiceLogSerializer(ShippingInvoiceSerializer):
    class Meta(ShippingInvoiceSerializer.Meta):
        fields = ['invoice_number', 'invoice_date', 'payee_account_id', 'payer_account_id']

    @property
    def log_data(self):
        if self.instance:
            data = self.data
        else:
            data = {field: None for field in self.fields}
        rs = {key: str(data[key]) if data[key] is not None else None for key in sorted(data.keys())}
        return rs
