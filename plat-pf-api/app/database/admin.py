from django.contrib import admin

from app.database.models import DatabaseConfig, DatabaseClientConfig


@admin.register(DatabaseConfig)
class DatabaseConfigAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'url', 'created', 'modified']
    search_fields = ['name']


@admin.register(DatabaseClientConfig)
class DatabaseClientConfigAdmin(admin.ModelAdmin):
    list_display = ['id', 'client', 'database', 'created', 'modified']
