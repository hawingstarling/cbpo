import logging
from datetime import timedelta
from django.db.models import Q
from django.utils import timezone
from plat_import_lib_api.models import PROCESSING, REPORTING, REVERTING, DataImportTemporary, RawDataTemporary
from celery import current_app
from app.financial.import_template.custom_report import SaleItemCustomReport
from app.financial.import_template.sale_item_bulk_edit import SaleItemBulkEdit
from app.financial.import_template.sale_item_bulk_sync import SaleItemBulkSync
from app.financial.jobs.bulk_process import processing_bulk_module_chunk
from app.database.helper import get_connection_workspace
from app.job.services.inspect import JobInspectManage
from app.job.utils.helper import register_list
from app.job.utils.variable import BULK_CATEGORY, MODE_RUN_IMMEDIATELY

logger = logging.getLogger(__name__)


@current_app.task(bind=True)
def handler_reopen_task_bulk_process(self, client_id):
    logger.info(f"[{client_id}][{self.request.id}][handler_reopen_task_bulk_process] begin processing ... ")
    date_created = timezone.now() - timedelta(minutes=10)
    # query with action bulk sync
    cond = Q(client_id=str(client_id), status__in=[PROCESSING, REVERTING, REPORTING],
             module__in=[SaleItemBulkSync.__NAME__, SaleItemBulkEdit.__NAME__, SaleItemCustomReport.__NAME__],
             modified__lt=date_created)

    query_set = DataImportTemporary.objects.db_manager(using=get_connection_workspace(client_id)) \
        .filter(cond).order_by('-modified')

    lib_import_ids = query_set.values_list('pk', flat=True)

    if len(lib_import_ids) == 0:
        logger.info(
            f"[Task][{client_id}][handler_reopen_task_bulk_process] not found lib import ids deactive ..........")
        return

    job_name = f"app.financial.jobs.bulk_process.{processing_bulk_module_chunk.__name__}"

    data_bulk_handler = []
    data_bulk_chunk = []

    job_control_manager = JobInspectManage()

    for item in query_set:
        is_active = job_control_manager.is_active_in_celery(item.pk, job_name, {"import_temp_id": item.pk})
        if is_active:
            logger.info(
                f"[Tasks][{client_id}][handler_reopen_task_bulk_process] Job {job_name} task: {item.pk} still running ...")
            continue
        logger.info(f"[Tasks][{client_id}][handler_reopen_task_bulk_process] Re-open {job_name} task: {item.pk}")
        # task id
        task_id = item.meta.get('task_id', str(item.pk))
        data_info = {
            'module': item.module,
            'import_temp_id': item.pk,
            'jwt_token': item.meta.get('jwt_token'),
            'client_id': item.meta.get('client_id'),
            'user_id': item.meta.get('user_id')
        }
        client_id = item.meta.get('client_id')
        client_db = get_connection_workspace(client_id)
        # check bulk data is not empty
        count = RawDataTemporary.objects.db_manager(client_db) \
            .filter(lib_import_id=data_info['import_temp_id']).count()
        if count == 0:
            data_bulk_handler.append(
                dict(
                    task_id=task_id,
                    client_id=client_id,
                    name=f"bulk_handler_{task_id}",
                    job_name="app.financial.jobs.bulk_process.bulk_handler",
                    module="app.financial.jobs.bulk_process",
                    method="bulk_handler",
                    meta=data_info
                )
            )
        else:
            data_bulk_chunk.append(
                dict(
                    task_id=task_id,
                    client_id=client_id,
                    name=f"bulk_chunk_{task_id}",
                    job_name="app.financial.jobs.bulk_process.processing_bulk_module_chunk",
                    module="app.financial.jobs.bulk_process",
                    method="processing_bulk_module_chunk",
                    meta=data_info
                )
            )
    register_list(category=BULK_CATEGORY, data=data_bulk_handler, mode_run=MODE_RUN_IMMEDIATELY)
    register_list(category=BULK_CATEGORY, data=data_bulk_chunk, mode_run=MODE_RUN_IMMEDIATELY)
