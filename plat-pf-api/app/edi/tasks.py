from django.db.utils import DEFAULT_DB_ALIAS
from .jobs.invoice_source import *
from .jobs.fedex_shipment import *
from celery.utils.log import get_task_logger
from app.financial.models import ClientPortal
from app.job.utils.helper import register_clients_method
from app.job.utils.variable import MODE_RUN_PARALLEL, DATA_SOURCE_CALCULATION_CATEGORY

logger = get_task_logger(__name__)


def get_client_ids_active():
    return ClientPortal.objects.tenant_db_for(DEFAULT_DB_ALIAS).filter(active=True).values_list('pk', flat=True)


# select_clients_for_sale_items_flatten
@current_app.task(bind=True)
def prefetch_edi_invoice_source(self):
    client_ids = get_client_ids_active()
    data = dict(
        name="prefetch_edi_invoice_source",
        job_name="app.edi.jobs.invoice_source.handler_prefetch_edi_invoice_source",
        module="app.edi.jobs.invoice_source",
        method="handler_prefetch_edi_invoice_source"
    )
    register_clients_method(DATA_SOURCE_CALCULATION_CATEGORY, client_ids, data, mode_run=MODE_RUN_PARALLEL)
    logger.info(f"[Scheduler][{self.request.id}][prefetch_edi_invoice_source] beat job for {len(client_ids)} clients")


# select_clients_for_sale_items_flatten
@current_app.task(bind=True)
def up_edi_to_fedex_shipment(self):
    client_ids = get_client_ids_active()
    data = dict(
        name="up_edi_to_fedex_shipment",
        job_name="app.edi.jobs.fedex_shipment.handler_up_edi_to_fedex_shipment",
        module="app.edi.jobs.fedex_shipment",
        method="handler_up_edi_to_fedex_shipment"
    )
    register_clients_method(DATA_SOURCE_CALCULATION_CATEGORY, client_ids, data, mode_run=MODE_RUN_PARALLEL)
    logger.info(f"[Scheduler][{self.request.id}][up_edi_to_fedex_shipment] beat job for {len(client_ids)} clients")


#
@current_app.task(bind=True)
def reopen_edi_invoice_source(self):
    client_ids = get_client_ids_active()
    data = dict(
        name="reopen_edi_invoice_source",
        job_name="app.edi.jobs.invoice_source.handler_reopen_edi_invoice_source",
        module="app.edi.jobs.invoice_source",
        method="handler_reopen_edi_invoice_source"
    )
    register_clients_method(DATA_SOURCE_CALCULATION_CATEGORY, client_ids, data, mode_run=MODE_RUN_PARALLEL)
    logger.info(f"[Scheduler][{self.request.id}][reopen_edi_invoice_source] beat job for {len(client_ids)} clients")


# Execute on the first day of every month.
@current_app.task(bind=True)
def clean_edi_invoice_tracking(self):
    client_ids = get_client_ids_active()
    data = dict(
        name="clean_edi_invoice_tracking",
        job_name="app.edi.jobs.invoice_source.handler_clean_edi_invoice_tracking",
        module="app.edi.jobs.invoice_source",
        method="handler_clean_edi_invoice_tracking"
    )
    register_clients_method(DATA_SOURCE_CALCULATION_CATEGORY, client_ids, data, mode_run=MODE_RUN_PARALLEL)
    logger.info(f"[Scheduler][{self.request.id}][clean_edi_invoice_tracking] beat job for {len(client_ids)} clients")
