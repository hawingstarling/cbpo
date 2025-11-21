import logging

from rest_framework import status

from app.financial.models import DataFlattenTrack, DataStatus
from app.financial.services.integrations.informed import InformedProfileManager
from app.financial.services.integrations.serializers.financial_event_status import InformedReportDataStatusSerializer
from app.financial.services.integrations.time_control.base import BaseTimeControl
from app.financial.variable.data_flatten_variable import FLATTEN_SALE_ITEM_KEY
from app.financial.variable.job_status import SUCCESS, POSTED_FILTER_MODE
from app.core.variable.pf_trust_ac import INFORMED_TYPE, ERROR_STATUS, DONE_STATUS, SALE_EVENT_TYPE, \
    PROCESS_STATUS, IGNORE_STATUS

logger = logging.getLogger(__name__)


class InformedTimeControl(BaseTimeControl):
    JOB_TYPE = INFORMED_TYPE

    def _get_data_request(self):
        # check is ready data status of financial event
        try:
            # format posted_date : 'YYYY-MM-DD'
            query_params = {
                "posted_date": self.date,
                "report_type": "All_Fields"
            }
            rs = self.ac_manager.get_informed_report_request_status(client_id=self.client_id, **query_params)
            data = self._handler_result(rs)
            return data
        except Exception as ex:
            content = str(ex)
            self._write_errors_request(status.HTTP_400_BAD_REQUEST, content)
            return {}

    def is_valid_content(self, data):
        serializer = InformedReportDataStatusSerializer(data=data)
        serializer.is_valid()
        return serializer.errors

    def is_get_orders_done(self):
        try:
            DataStatus.objects.tenant_db_for(self.client_id).get(client_id=self.client_id, channel=self.channel,
                                                                 date=self.date, type=SALE_EVENT_TYPE,
                                                                 status=DONE_STATUS)
            return True
        except Exception as ex:
            return False

    def progress(self):
        if not self.is_get_orders_done:
            self._write_log_to_data_tracking(status_tracking=ERROR_STATUS, content="Sale order is not sync done")
            return
        # make job get transactions event with time controls
        self._write_log_to_data_tracking(status_tracking=PROCESS_STATUS, reset_log=True)
        try:
            flatten = DataFlattenTrack.objects.tenant_db_for(self.client_id).get(client_id=self.client_id,
                                                                                 type=FLATTEN_SALE_ITEM_KEY,
                                                                                 status=SUCCESS)

            # Appeagle Profile
            is_override = True
            manage = InformedProfileManager(client_id=self.client_id, flatten=flatten, marketplace=self.marketplace,
                                            from_date=self.date,
                                            to_date=self.date, track_logs=True, filter_mode=POSTED_FILTER_MODE,
                                            time_control_id=str(self.data_tracking.pk), override=is_override)
            manage.progress()

            # TODO: Add service handler for report type ..

            # make tracking time done
            self._write_log_to_data_tracking(status_tracking=DONE_STATUS, content='Success')
        except Exception as ex:
            content = str(ex)
            status_tracking = ERROR_STATUS
            if "InformedMarketplace matching query does not exist" in content:
                status_tracking = IGNORE_STATUS
            self._write_log_to_data_tracking(status_tracking=status_tracking, content=content)
            raise ex
