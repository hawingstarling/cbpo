import uuid
from django.db import models
from model_utils.models import TimeStampedModel
from app.database.db.objects_manage import MultiDbTableManagerBase
from app.financial.models import ClientPortal


class DatabaseConfig(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)  # name of config
    url = models.CharField(max_length=500, null=False)

    #
    objects = MultiDbTableManagerBase()
    all_objects = MultiDbTableManagerBase()

    def __str__(self):
        return f"{self.id} - {self.url}"

    class Meta:
        ordering = ['created']
        unique_together = ['name', 'url']


class DatabaseClientConfig(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(ClientPortal, on_delete=models.CASCADE)
    database = models.ForeignKey(DatabaseConfig, on_delete=models.CASCADE)

    #
    objects = MultiDbTableManagerBase()
    all_objects = MultiDbTableManagerBase()

    def __str__(self):
        return f"{self.id} - {self.client} - {self.database}"

    class Meta:
        ordering = ['created']
        unique_together = ['client', 'database']
