from django.contrib import admin
from django.contrib import messages
from django.utils.translation import ngettext
from django_better_admin_arrayfield.admin.mixins import DynamicArrayMixin

from app.app_setting import forms as app_setting_forms
from app.app_setting import models
from app.app_setting.tasks import (
    task_run_send_lwa_credential_setting_to_service,
    task_run_notify_an_expired_lwa_credential_setting,
)
from app.app_setting.models import TrackingURLCallback


# Register your models here.
class TrackingURLCallbackInline(admin.TabularInline):
    model = TrackingURLCallback
    readonly_fields = ("url", "created", "modified", "log")


class LWACredentialClientSettingAdmin(admin.ModelAdmin, DynamicArrayMixin):
    form = app_setting_forms.LWACredentialClientSettingForm

    list_display = (
        "app_name",
        "app_id",
        "lwa_client_id",
        "date_expired",
        "lwa_secret_key_encrypted",
    )
    list_filter = ("is_active",)
    search_fields = (
        "app_id",
        "lwa_client_id",
    )
    actions = ["notify_expired", "send_to_services"]
    inlines = [
        TrackingURLCallbackInline,
    ]

    def save_model(self, request, obj, form, change):
        if change:
            # administrator updates model setting
            input_secret_key = form.cleaned_data["lwa_secret_key"]
            if input_secret_key != obj.plain_text_lwa_secret_key:
                # administrator update new secret key
                lwa_secret_key_encrypted = form.cleaned_data["lwa_secret_key_encrypted"]
                setattr(obj, "lwa_secret_key_encrypted", lwa_secret_key_encrypted)

        else:
            # administrator add new model setting
            lwa_secret_key_encrypted = form.cleaned_data["lwa_secret_key_encrypted"]
            setattr(obj, "lwa_secret_key_encrypted", lwa_secret_key_encrypted)

        return super().save_model(request, obj, form, change)

    def notify_expired(self, request, queryset):
        for ele in queryset:
            task_run_notify_an_expired_lwa_credential_setting.apply_async(
                kwargs={"app_id": ele.app_id}
            )

        self.message_user(
            request,
            ngettext(
                "%d lwa setting was successfully notified.",
                "%d lwa settings were successfully notified.",
                len(queryset),
            )
            % len(queryset),
            messages.SUCCESS,
        )

    def send_to_services(self, request, queryset):
        for ele in queryset:
            for service_url in ele.url_callbacks:
                task_run_send_lwa_credential_setting_to_service.apply_async(
                    kwargs={"app_id": ele.app_id, "service_url": service_url},
                )

        self.message_user(
            request,
            ngettext(
                "%d lwa setting was successfully sent.",
                "%d lwa settings were successfully sent.",
                len(queryset),
            )
            % len(queryset),
            messages.SUCCESS,
        )


admin.site.register(models.LWACredentialClientSetting, LWACredentialClientSettingAdmin)
