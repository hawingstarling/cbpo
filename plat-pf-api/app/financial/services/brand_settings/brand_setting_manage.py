import logging
from auditlog.models import LogEntry
from django.utils import timezone
from app.core.services.audit_logs.base import AuditLogCoreManager
from app.financial.models import SaleItem, Brand, BrandSetting, LogClientEntry

logger = logging.getLogger(__name__)


class BrandSettingManage:

    def __init__(self, client_id: str, brand_id: str, **kwargs):
        self.client_id = client_id
        self.brand_id = brand_id
        self.log_entries = []
        self.kwargs = kwargs
        self.limit_size = 1000

    @property
    def user_id(self):
        return self.kwargs.get('user_id')

    def reset_sale_items_relate_setting(self):
        queryset = SaleItem.objects.tenant_db_for(self.client_id).filter(brand_id=self.brand_id)

        def map_set_object(obj):
            changes = {}
            changes.update({'brand': [obj.brand.name, None]})
            obj.brand = None
            obj.modified = timezone.now()
            obj.resync = True
            obj.financial_dirty = True
            log_entry = AuditLogCoreManager(client_id=self.client_id, user_id=self.user_id) \
                .create_log_entry_from_compared_changes(obj, changes, action=LogEntry.Action.UPDATE)
            self.log_entries.append(log_entry)
            return obj

        page = 1
        #
        while True:
            if queryset.count() == 0:
                logger.info(
                    f"[{self.__class__.__name__}][{self.client_id}][reset_sale_items_relate_setting] "
                    f"No item relate with brand {self.brand_id}")
                break
            queryset_chunk = queryset[:self.limit_size]
            objs = list(map(map_set_object, queryset_chunk))
            SaleItem.objects.tenant_db_for(self.client_id) \
                .bulk_update(objs, fields=["brand", "resync", "financial_dirty", "modified"])
            LogClientEntry.objects.tenant_db_for(self.client_id).bulk_create(self.log_entries, ignore_conflicts=True)
            self.log_entries = []
            logger.info(
                f"[{self.__class__.__name__}][{self.client_id}][reset_sale_items_relate_setting] "
                f"Reset page {page} completed")
            page += 1

    def delete_settings(self):
        settings = BrandSetting.objects.tenant_db_for(self.client_id).filter(brand_id=self.brand_id)
        if settings.exists():
            settings.delete()

    def delete(self):
        brand = Brand.all_objects.tenant_db_for(self.client_id).get(id=self.brand_id)
        self.delete_settings()
        self.reset_sale_items_relate_setting()
        #
        if brand.is_removed is False:
            brand.is_removed = True
            brand.modified = timezone.now()
            brand.save()
