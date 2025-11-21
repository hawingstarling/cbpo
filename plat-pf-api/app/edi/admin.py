from django.contrib import admin
from .models import EdiInvoiceSource
# from ..core.admin.client_active_simple_filter import ClientActiveFilter


@admin.register(EdiInvoiceSource)
class EdiInvoiceSourceAdmin(admin.ModelAdmin):
    list_display = ['id', 'client', 'source', 'date', 'status', 'file_path']
    search_fields = ['date']
    list_filter = ['client', 'source', 'status']
    ordering = ['-date']