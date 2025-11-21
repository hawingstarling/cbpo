from django.contrib import admin, messages
from app.core.admins.tenant_db_admin import TenantDBForModelAdmin
from app.third_party_logistic.models import Account3PLCentral
from app.third_party_logistic.tasks import sync_account_3pl_central


@admin.register(Account3PLCentral)
class Account3PLCentralAdmin(TenantDBForModelAdmin):
    list_display = ["id", "client", "client_auth_id", "client_auth_secret", "user_login", "enabled", "synced",
                    "created", "modified"]
    list_filter = ["client", "enabled", "synced"]
    actions = ["sync_account", "reopen_sync_status"]

    def sync_account(self, request, queryset):
        errors = []
        # client_ids = queryset.filter(synced=False).values_list("client_id", flat=True)
        for obj in queryset:
            try:
                sync_account_3pl_central(client_id=obj.client_id, obj_id=obj.pk)
            except Exception as ex:
                errors.append(f"{obj.client_id}: {ex}")
        if errors:
            msg = f" , ".join(errors)
            messages.error(request, msg)
        else:
            messages.success(request, f"{queryset.count()} synced successfully")

    def reopen_sync_status(self, request, queryset):
        errors = []
        client_ids = queryset.values_list("client_id", flat=True)
        try:
            queryset.update(synced=False)
        except Exception as ex:
            errors.append(f"{client_ids}: {ex}")
        if errors:
            msg = f" , ".join(errors)
            messages.error(request, msg)
        else:
            messages.success(request, f"{queryset.count()} reopen sync status successfully")

    sync_account.short_description = "Sync Accounts"
    reopen_sync_status.short_description = "ReOpen Sync Status"
