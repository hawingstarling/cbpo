import logging
from celery.states import FAILURE
from django.db import transaction
from app.job.services.category.base.job_client import JobClientBase
from app.job.utils.variable import TIME_CONTROL_CATEGORY

logger = logging.getLogger(__name__)


class TimeControlJob(JobClientBase):
    category = TIME_CONTROL_CATEGORY

    def on_complete_acks_late_callback(self, item):
        try:
            assert item.status == FAILURE \
                   and item.job_name == 'app.financial.jobs.time_control.handler_time_control_process_type_is_ready_workspace', \
                "Callback not setup for this job name"
            from app.financial.models import DataStatus
            from app.core.variable.pf_trust_ac import ERROR_STATUS
            obj = DataStatus.objects.tenant_db_for(item.client_id).get(pk=item.meta['data_status_id'])
            assert obj.status not in [ERROR_STATUS], "Time control data status already update correct status"
            obj.status = ERROR_STATUS
            obj.log = "job already FAILURE in time control management"
            transaction.on_commit(lambda: obj.save())
        except Exception as ex:
            logger.error(f"[{self.__class__.__name__}][on_complete_acks_late_callback] {ex}")
