from django.contrib import admin

from app.core.admins.channel_global_simple_filter import GlobalChannelListFilter
from app.core.admins.tenant_db_admin import TenantDBForModelAdmin
from app.extensiv.models import COGSConflict


@admin.register(COGSConflict)
class COGSConflictAdmin(TenantDBForModelAdmin):
    list_display = (
        'id',
        'sale_ids',
        'channel_sale_ids',
        'sku',
        'status',
        'used_cog',
        'extensiv_cog',
        'dc_cog',
        'pf_cog',
        'created',
        'short_note',
    )
    list_filter = (
        GlobalChannelListFilter,
        'client',
        'status',
        'used_cog',
        'created',
    )
    search_fields = (
        'sku',
        'sale_ids',
        'channel_sale_ids',
        'note',
    )
    readonly_fields = ('created', 'modified')

    fieldsets = (
        (None, {
            'fields': (
                'sku',
                'sale_ids',
                'channel_sale_ids',
                'status',
                'used_cog'
            )
        }),
        ('Costs', {
            'fields': (
                'extensiv_cog',
                'dc_cog',
                'pf_cog'
            )
        }),
        ('Timestamps', {
            'fields': (
                'created',
                'modified'
            )
        }),
        ('Notes', {
            'fields': ('note',)
        }),
    )

    def short_note(self, obj):
        return (obj.note[:40] + "...") if obj.note and len(obj.note) > 40 else obj.note or "-"

    short_note.short_description = "Note"
