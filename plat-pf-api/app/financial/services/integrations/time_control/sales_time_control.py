import logging, maya

from rest_framework import status

from app.financial.jobs.live_feed import handler_trigger_live_feed_sale_item_ws
from app.financial.variable.job_status import POSTED_FILTER_MODE, MODIFIED_FILTER_MODE
from app.financial.services.integrations.serializers.financial_event_status import OrderEventDataStatusSerializer
from app.financial.services.integrations.time_control.base import BaseTimeControl
from app.core.variable.pf_trust_ac import ERROR_STATUS, DONE_STATUS, SALE_EVENT_TYPE, TIME_CONTROL_LOG_TYPE, \
    PROCESS_STATUS, MARKETPLACE_AMZ_TYPE
from app.financial.services.sale_item_mapping.mapping_sale_item_common_from_live_feed_dc import \
    MappingSaleItemCommonFromSaleDateLiveFeedDC
from app.financial.models import DataStatus
from app.third_party_logistic.jobs.frequency import handler_getting_prime_3pl_central_ws

logger = logging.getLogger(__name__)


class SalesTimeControl(BaseTimeControl):
    JOB_TYPE = SALE_EVENT_TYPE

    def __init__(self, data_tracking: DataStatus, **kwargs):
        super().__init__(data_tracking, **kwargs)

        self.from_date = f'{self.date} {self.BEGIN_TIME}'
        self.to_date = f'{self.date} {self.END_TIME}'

    def _get_data_request(self):
        # check is ready data status of financial event
        try:
            # format posted_date : 'YYYY-MM-DD'
            query_params = {"modified_date": self.date}
            if self.marketplace_type == MARKETPLACE_AMZ_TYPE:
                query_params.update({"marketplace": self.marketplace})
            rs = self.ac_manager.get_orders_status(sc_method=self.sc_method, **query_params)
            data = self._handler_result(rs)
            return data
        except Exception as ex:
            content = str(ex)
            self._write_errors_request(status.HTTP_400_BAD_REQUEST, content)
            return {}

    def is_valid_content(self, data):
        if 'marketplace' not in data:
            data.update(dict(marketplace=self.marketplace))
        serializer = OrderEventDataStatusSerializer(data=data)
        serializer.is_valid()
        return serializer.errors

    def progress(self):
        self._write_log_to_data_tracking(status_tracking=PROCESS_STATUS, reset_log=True)
        try:
            track_logs = True

            kwarg_base = dict(
                client_id=self.client_id,
                marketplace=self.marketplace,
                from_date=self.from_date, to_date=self.to_date,
                track_logs=track_logs, log_type=TIME_CONTROL_LOG_TYPE,
                time_control_id=self.data_tracking_id
            )

            if self.data_tracking.only_purchased_date:
                # This case using when reopen any date and only get orders by purchase_date
                # POSTED_FILTER_MODE
                handler_trigger_live_feed_sale_item_ws(**kwarg_base, filter_mode=POSTED_FILTER_MODE)

                # REPLACEMENT POSTED_FILTER_MODE
                handler_trigger_live_feed_sale_item_ws(**kwarg_base, filter_mode=POSTED_FILTER_MODE,
                                                       is_replacement_order=True)
            else:
                # POSTED_FILTER_MODE
                handler_trigger_live_feed_sale_item_ws(**kwarg_base, filter_mode=POSTED_FILTER_MODE)
                # MODIFIED_FILTER_MODE
                handler_trigger_live_feed_sale_item_ws(**kwarg_base, filter_mode=MODIFIED_FILTER_MODE)

                # REPLACEMENT POSTED_FILTER_MODE
                handler_trigger_live_feed_sale_item_ws(**kwarg_base, filter_mode=POSTED_FILTER_MODE,
                                                       is_replacement_order=True)
                # REPLACEMENT POSTED_FILTER_MODE
                handler_trigger_live_feed_sale_item_ws(**kwarg_base, filter_mode=MODIFIED_FILTER_MODE,
                                                       is_replacement_order=True)

            if self.data_tracking.is_checking_prime:
                handler_getting_prime_3pl_central_ws(**kwarg_base, filter_mode=POSTED_FILTER_MODE)

            _from_date = maya.parse(self.from_date).datetime()
            _to_date = maya.parse(self.to_date).datetime()

            # mapping common DC fields
            if not self.client.is_oe:
                mapping = MappingSaleItemCommonFromSaleDateLiveFeedDC(
                    client_id=self.client_id,
                    limit_query_set_sale_item=1000,
                    fields_mapping=['upc', 'unit_cog', 'cog', 'brand', 'channel_brand'],
                    from_date=_from_date, to_date=_to_date,
                    marketplace=self.marketplace
                )
                mapping.exec()

            # make tracking time done
            self._write_log_to_data_tracking(status_tracking=DONE_STATUS, content='Success')
        except Exception as ex:
            content = str(ex)
            status_tracking = ERROR_STATUS
            self._write_log_to_data_tracking(status_tracking=status_tracking, content=content)
            raise ex
