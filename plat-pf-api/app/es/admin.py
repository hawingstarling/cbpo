from django.contrib import admin

from .models import ESConfig, ESClientConfig


@admin.register(ESConfig)
class ESConfigAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'url', 'created', 'modified']
    search_fields = ['name']


@admin.register(ESClientConfig)
class ESClientConfigAdmin(admin.ModelAdmin):
    list_display = ['id', 'client', 'es', 'created', 'modified']