import logging
from datetime import timedelta
from django.utils import timezone
from celery import current_app
from app.edi.configs.status import EDI_INVOICE_PROCESS, EDI_INVOICE_PENDING
from app.edi.models import EdiInvoiceSource
from app.edi.services.fetch_source import EDISourceManage
from app.edi.sources.ftp import FTPConnect
from app.financial.models import DataFlattenTrack
from app.financial.variable.data_flatten_variable import FLATTEN_SALE_ITEM_KEY

logger = logging.getLogger(__name__)


@current_app.task(bind=True)
def handler_prefetch_edi_invoice_source(self, client_id):
    try:
        flatten = DataFlattenTrack.objects.tenant_db_for(client_id).get(client_id=client_id, live_feed=True,
                                                                        type=FLATTEN_SALE_ITEM_KEY)
        logger.info(f"[handler_prefetch_edi_invoice_source][{self.request.id}][{flatten.client}] processing ...")
        ftp_connect = EDISourceManage(client=flatten.client, source=FTPConnect())
        ftp_connect.processing()
    except Exception as ex:
        logger.error(f"[{client_id}][handler_prefetch_edi_invoice_source] {ex}")


@current_app.task(bind=True)
def handler_reopen_edi_invoice_source(self, client_id):
    logger.info(f"[handler_reopen_edi_invoice_source][{self.request.id}][{client_id}] processing ...")
    expired = timezone.now() - timedelta(hours=2)
    EdiInvoiceSource.objects.tenant_db_for(client_id) \
        .filter(client_id=client_id, modified__lte=expired, status=EDI_INVOICE_PROCESS) \
        .update(status=EDI_INVOICE_PENDING, modified=timezone.now())


@current_app.task(bind=True)
def handler_clean_edi_invoice_tracking(self, client_id):
    logger.info(f"[clean_edi_invoice_tracking][{self.request.id}][{client_id}] processing ...")
    EDISourceManage.clean_source(client_id)
