from django.contrib import admin

from app.core.models import WhileList


@admin.register(WhileList)
class WhileListAdmin(admin.ModelAdmin):
    list_display = ["id", "domain", "ip_addr", "enabled", "created", "modified"]
    search_fields = ["domain", "ip_addr"]
    ordering = ["created"]
