import requests
from django.utils import timezone
from django import forms
from durationwidget.widgets import TimeDurationWidget

from app.app_setting.models import (
    LWACredentialClientSetting,
    TrackingURLCallback,
)
from app.app_setting.config_static_variable import DONE_STATUS_KEY


class LWACredentialClientSettingForm(forms.ModelForm):
    lwa_secret_key = forms.CharField(max_length=256)
    days_scheduled_notification = forms.DurationField(
        widget=TimeDurationWidget(
            show_days=True, show_hours=False, show_minutes=False, show_seconds=False
        )
    )

    class Meta:
        model = LWACredentialClientSetting
        exclude = ("lwa_secret_key_encrypted", "is_removed")

    def __init__(self, *args, **kwargs):
        instance = kwargs.get("instance")
        initial = kwargs.get("initial", {})
        if instance:
            # get plain text secret key for user in case of editing an existing one
            initial["lwa_secret_key"] = instance.plain_text_lwa_secret_key
        kwargs["initial"] = initial
        super().__init__(*args, **kwargs)

    def clean_lwa_secret_key(self):
        try:
            lwa_secret_key = self.cleaned_data["lwa_secret_key"]
            lwa_secret_key_encrypted = LWACredentialClientSetting.encrypt_secret_key(
                lwa_secret_key
            )
            self.cleaned_data.update(
                {"lwa_secret_key_encrypted": lwa_secret_key_encrypted}
            )
        except Exception as error:
            raise forms.ValidationError(f"Invalid LWA secret key: {str(error)}")

    def clean_date_expired(self):
        value = self.cleaned_data.get("date_expired")
        if value < timezone.now():
            raise forms.ValidationError("Date and time must be in the future.")
        return value

    def clean_url_callbacks(self):
        value = self.cleaned_data.get("url_callbacks", [])

        try:
            for url in value:
                response = requests.get(url, timeout=(3, 5))
                if response.status_code == 404:
                    raise forms.ValidationError(f"URL not found (404) at {url}")
        except requests.exceptions.RequestException as request_error:
            raise forms.ValidationError(
                f"An error occurred while trying to connect to the URL: {str(request_error)}"
            )
        return value
