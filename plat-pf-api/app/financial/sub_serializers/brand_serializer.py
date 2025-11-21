from rest_framework.validators import UniqueTogetherValidator
from app.core.context import AppContext
from app.financial.models import SaleItem
from app.financial.jobs.data_flatten import flat_sale_items_bulk_sync_additional_task
from app.financial.models import Brand
from app.financial.sub_serializers.default_message_serializer import default_error_message
from django.utils.translation import gettext_lazy as _
from app.database.sub_serializers.tenant_db_for_serializer import TenantDBForSerializer
from app.financial.variable.data_flatten_variable import FLATTEN_SALE_ITEM_KEY, FLATTEN_SALE_ITEM_FINANCIAL_KEY
from app.job.utils.helper import register_list
from app.job.utils.variable import BULK_CATEGORY
from plat_import_lib_api.static_variable.config import plat_import_setting


class BrandSerializer(TenantDBForSerializer):

    def update(self, instance, validated_data):
        try:
            is_change_name = instance.name != validated_data['name']
        except Exception as ex:
            is_change_name = False
        instance = super().update(instance, validated_data)
        # trigger sync to flatten
        if is_change_name:
            has_brand_items = SaleItem.objects.tenant_db_for(instance.client_id) \
                .filter(brand_id=instance.id).exists()
            if has_brand_items:
                additional_query = f"""
                AND _source_table_.brand_id = '{instance.id}'
                """
                if plat_import_setting.use_queue:
                    data = [
                        dict(
                            client_id=instance.client_id,
                            name="bulk_sync_additional_task",
                            job_name="app.financial.jobs.data_flatten.flat_sale_items_bulk_sync_additional_task",
                            module="app.financial.jobs.data_flatten",
                            method="flat_sale_items_bulk_sync_additional_task",
                            meta=dict(
                                client_id=str(instance.client_id),
                                type_flattens=[FLATTEN_SALE_ITEM_KEY, FLATTEN_SALE_ITEM_FINANCIAL_KEY],
                                additional_query=additional_query
                            )
                        )
                    ]
                    register_list(BULK_CATEGORY, data)
                else:
                    flat_sale_items_bulk_sync_additional_task(client_id=str(instance.client_id),
                                                              type_flattens=[FLATTEN_SALE_ITEM_KEY,
                                                                             FLATTEN_SALE_ITEM_FINANCIAL_KEY],
                                                              additional_query=additional_query)
        return instance

    class Meta:
        model = Brand
        fields = '__all__'
        write_only = []
        validators = [
            UniqueTogetherValidator(
                queryset=Brand.objects.tenant_db_for(AppContext.instance().client_id).all(),
                fields=['client', 'name'],
                message=_('Name must be unique')
            )
        ]


class BrandImportSerializer(TenantDBForSerializer):
    class Meta:
        model = Brand
        fields = ['name', 'supplier_name', 'is_obsolete', 'acquired_date']

        extra_kwargs = {
            'name': {
                "error_messages": default_error_message('Name'),
                "label": 'Name'
            },
            'supplier_name': {
                "error_messages": default_error_message('Supplier Name'),
                "label": 'Supplier Name'
            },
            'is_obsolete': {
                "required": False,
                "error_messages": default_error_message('Is Obsolete'),
                "label": "Is Obsolete",
                "allow_null": True
            },
            'acquired_date': {
                "error_messages": default_error_message('Acquired Date'),
                "label": 'Acquired Date'
            }
        }
