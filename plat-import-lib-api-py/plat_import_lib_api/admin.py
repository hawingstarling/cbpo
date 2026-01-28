import logging
from django.contrib import admin
from .models import DataImportTemporary, Health, RawDataTemporary, Setting
from .services.common.healthy import HealthyModule

logger = logging.getLogger(__name__)


@admin.register(DataImportTemporary)
class DataImportTemporaryAdmin(admin.ModelAdmin):
    list_display = ['id', 'client_id', 'module', 'status', 'progress', 'created', 'modified']
    search_fields = ['id', 'module']
    list_filter = ['client_id', 'module', 'status']
    ordering = ['-created']


@admin.register(Health)
class HealthAdmin(admin.ModelAdmin):
    list_display = ['module_name', 'is_enabled', 'is_healthy', 'message', 'modified']
    search_fields = ['module_name']
    list_filter = ['is_enabled', 'is_healthy']
    actions = ['health_check']
    ordering = ['created']

    def health_check(self, request, queryset):
        for item in queryset:
            logger.info(f"[HealthAdmin][health_check] check health module {item.module_name}")
            healthy = HealthyModule(item.module_name)
            healthy.validate()
            healthy.process()
            healthy.complete()

    health_check.short_description = "Health check"


@admin.register(RawDataTemporary)
class RawDataTemporaryAdmin(admin.ModelAdmin):
    list_display = ['lib_import', 'index', 'status', 'is_valid', 'is_complete', 'created', 'modified']
    search_fields = ['lib_import__id', 'index', 'key_map', 'parent_key_map']
    list_filter = ['status', 'is_valid', 'is_complete']
    ordering = ['created']


@admin.register(Setting)
class SettingAdmin(admin.ModelAdmin):
    list_display = ['id', 'use_queue', 'bulk_process_size', 'storage_location', 'storage_folder', 'created', 'modified']
