import logging
from rest_framework import status
from app.financial.jobs.event import handler_trigger_trans_event_sale_item_ws
from app.financial.jobs.sale_event import handler_trans_event_data_to_sale_level
from app.financial.services.integrations.serializers.financial_event_status import FinancialEventDataStatusSerializer
from app.financial.services.integrations.time_control.base import BaseTimeControl
from app.financial.services.integrations.trans_event import POSTED_FILTER_MODE
from app.financial.variable.job_status import MODIFIED_FILTER_MODE
from app.core.variable.pf_trust_ac import FINANCIAL_EVENT_TYPE, ERROR_STATUS, DONE_STATUS, TIME_CONTROL_LOG_TYPE, \
    PROCESS_STATUS

logger = logging.getLogger(__name__)


class FinancialEventTimeControl(BaseTimeControl):
    JOB_TYPE = FINANCIAL_EVENT_TYPE

    def _get_data_request(self):
        # check is ready data status of financial event
        try:
            # format posted_date : 'YYYY-MM-DD'
            query_params = {"marketplace": self.marketplace, "posted_date": self.date}
            rs = self.ac_manager.get_financial_events_status(sc_method=self.sc_method, **query_params)
            data = self._handler_result(rs)
            return data
        except Exception as ex:
            content = str(ex)
            self._write_errors_request(status.HTTP_400_BAD_REQUEST, content)
            return {}

    def is_valid_content(self, data):
        if 'marketplace' not in data:
            data.update(dict(marketplace=self.marketplace))
        serializer = FinancialEventDataStatusSerializer(data=data)
        serializer.is_valid()
        return serializer.errors

    def progress(self):
        self._write_log_to_data_tracking(status_tracking=PROCESS_STATUS, reset_log=True)
        try:
            track_logs = True
            from_date = f'{self.date} {self.BEGIN_TIME}'
            to_date = f'{self.date} {self.END_TIME}'
            kwargs_info = dict(
                client_id=self.client_id,
                marketplace=self.marketplace,
                from_date=from_date, to_date=to_date,
                track_logs=track_logs,
                log_type=TIME_CONTROL_LOG_TYPE,
                time_control_id=str(self.data_tracking.pk)
            )
            if self.data_tracking.only_purchased_date:
                handler_trigger_trans_event_sale_item_ws(**kwargs_info, filter_mode=POSTED_FILTER_MODE)
            else:
                # POSTED_FILTER_MODE
                handler_trigger_trans_event_sale_item_ws(**kwargs_info, filter_mode=POSTED_FILTER_MODE)
                # MODIFIED_FILTER_MODE
                handler_trigger_trans_event_sale_item_ws(**kwargs_info, filter_mode=MODIFIED_FILTER_MODE)

            # trans event to sale calculation
            handler_trans_event_data_to_sale_level(**kwargs_info)

            # make tracking time done
            self._write_log_to_data_tracking(status_tracking=DONE_STATUS, content='Success')
        except Exception as ex:
            content = str(ex)
            status_tracking = ERROR_STATUS
            self._write_log_to_data_tracking(status_tracking=status_tracking, content=content)
            raise ex
