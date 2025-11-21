import uuid

from model_utils.models import TimeStampedModel
from django.db import models
from app.edi.configs.status import EDI_INVOICE_CHOICE, EDI_INVOICE_PENDING
from app.database.db.objects_manage import MultiDbTableManagerBase
from app.financial.models import ClientPortal
from app.financial.services.fedex_shipment.config import FEDEX_SHIPMENT_SOURCE_FTP_EDI, FEDEX_SHIPMENT_SOURCE_CHOICE


class EdiInvoiceSource(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(ClientPortal, on_delete=models.CASCADE, null=True)
    source = models.CharField(max_length=50, choices=FEDEX_SHIPMENT_SOURCE_CHOICE,
                              default=FEDEX_SHIPMENT_SOURCE_FTP_EDI)
    date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=EDI_INVOICE_CHOICE, default=EDI_INVOICE_PENDING)
    file_path = models.CharField(max_length=500)
    log = models.TextField(default=None, null=True)

    #
    objects = MultiDbTableManagerBase()
    all_objects = MultiDbTableManagerBase()

    def __str__(self):
        return f"{self.id} - {self.date} - {self.status}"

    class Meta:
        ordering = ['-created']
        unique_together = ['client', 'source', 'date', 'file_path']
        indexes = [
            models.Index(fields=['client', 'date', 'file_path', 'status'])
        ]
