import uuid
from datetime import timedelta

from auditlog.registry import auditlog
from cryptography.fernet import Fernet
from django.conf import settings
from django.db import models
from django_better_admin_arrayfield.models.fields import ArrayField
from model_utils.models import TimeStampedModel, SoftDeletableModel

from app.app_setting.config_static_variable import (
    LWA_CREDENTIAL_URL_STATUS,
    OPEN_STATUS_KEY,
)

# Create your models here.


class LWACredentialClientSetting(TimeStampedModel, SoftDeletableModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    #
    app_name = models.CharField(max_length=100, default=None, blank=None, null=True)
    app_id = models.CharField(max_length=100, unique=True)
    lwa_client_id = models.CharField(max_length=256)
    lwa_secret_key_encrypted = models.TextField(
        verbose_name="lwa secret key(encrypted)"
    )
    #
    is_active = models.BooleanField(default=True)
    date_expired = models.DateTimeField(verbose_name="Rotation Deadline")
    days_scheduled_notification = models.DurationField(default=timedelta(days=7))
    #
    emails = ArrayField(models.EmailField(), default=list)
    url_callbacks = ArrayField(models.URLField(), default=list)

    def __str__(self):
        return f"{self.app_name} - {self.id}"

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        if not self.lwa_secret_key_encrypted:
            raise ValueError("lwa_secret_key_encrypted is required")
        super().save(force_insert, force_update, using, update_fields)

    def delete(self, *args, **kwargs):
        self.tracking_lwa_client_setting.all().delete()
        super().delete(*args, **kwargs)

    @staticmethod
    def encrypt_secret_key(secret_key: str) -> str:
        fernet = Fernet(settings.FERNET_KEY.encode("utf-8"))
        encrypted_secret_key = fernet.encrypt(secret_key.encode()).decode("utf-8")
        return encrypted_secret_key

    @property
    def plain_text_lwa_secret_key(self) -> str:
        fernet = Fernet(settings.FERNET_KEY.encode("utf-8"))
        token = self.lwa_secret_key_encrypted.encode("utf-8")
        return fernet.decrypt(token).decode("utf-8")


class TrackingURLCallback(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lwa_setting = models.ForeignKey(
        LWACredentialClientSetting,
        on_delete=models.CASCADE,
        related_name="tracking_lwa_client_setting",
    )
    status = models.CharField(
        max_length=100, choices=LWA_CREDENTIAL_URL_STATUS, default=OPEN_STATUS_KEY
    )
    url = models.URLField(max_length=250)
    retry = models.SmallIntegerField(default=0)
    log = models.TextField(blank=True, null=True)

    def __str__(self):
        return f" Tracking: {self.status} - {self.url}"


auditlog.register(LWACredentialClientSetting)
