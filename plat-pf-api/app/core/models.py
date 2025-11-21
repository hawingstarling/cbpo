import uuid

from django.db import models
from model_utils.models import TimeStampedModel

from app.database.db.objects_manage import MultiDbTableManagerBase


class WhileList(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    domain = models.CharField(max_length=255)
    ip_addr = models.CharField(max_length=50, unique=True)
    enabled = models.BooleanField(default=True)

    #
    objects = MultiDbTableManagerBase()
    all_objects = MultiDbTableManagerBase()

    def __str__(self):
        return f"{self.domain} - {self.id} - {self.enabled}"
