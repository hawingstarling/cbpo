import uuid

from django.db import models
from model_utils.models import TimeStampedModel

from app.database.db.objects_manage import MultiDbTableManagerBase
from app.financial.models import ClientPortal


class Account3PLCentral(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(ClientPortal, on_delete=models.CASCADE)
    client_auth_id = models.CharField(max_length=50)
    client_auth_secret = models.CharField(max_length=100)
    user_login = models.CharField(max_length=100)
    enabled = models.BooleanField(default=True)
    synced = models.BooleanField(default=False)
    #
    objects = MultiDbTableManagerBase()
    all_objects = MultiDbTableManagerBase()

    class Meta:
        unique_together = ["client", "client_auth_id", "user_login"]

    def __str__(self):
        return f"{self.client} - {self.client_auth_id} - {self.user_login}"
