import logging
from datetime import datetime
import maya
import pytz
from django.conf import settings
from app.financial.services.integrations.live_feed import SaleItemsLiveFeedManager

logger = logging.getLogger(__name__)


class ITDepartmentSaleItemsLiveFeedManager(SaleItemsLiveFeedManager):

    def get_limit_size(self):
        return self.client.clientsettings.it_department_orders_limit

    def _from_date(self):
        if self.time_control_id is not None:
            start_date = maya.parse(self.kwargs["from_date"], timezone=settings.DS_TZ_CALCULATE) \
                .datetime().strftime("%Y-%m-%d %H:%M:%S")
        else:
            tz_info = pytz.timezone(settings.DS_TZ_CALCULATE)
            start_date = datetime.combine(datetime.now(tz_info).date(), datetime.min.time(), tzinfo=tz_info)
            start_date = start_date.astimezone(pytz.UTC).strftime("%Y-%m-%d %H:%M:%S")
        return start_date

    def _to_date(self):
        if self.time_control_id is not None:
            end_date = maya.parse(self.kwargs["to_date"], timezone=settings.DS_TZ_CALCULATE) \
                .datetime().strftime("%Y-%m-%d %H:%M:%S")
        else:
            tz_info = pytz.timezone(settings.DS_TZ_CALCULATE)
            end_date = datetime.combine(datetime.now(tz_info).date(), datetime.max.time(), tzinfo=tz_info)
            end_date = end_date.astimezone(pytz.UTC).strftime("%Y-%m-%d %H:%M:%S")
        return end_date

    def prefetch_query_params(self, query_params: dict):
        if self.amazon_order_ids:
            query_params.update({"channel_sale_id": self.amazon_order_ids})
        #
        else:
            query_params.update(
                {
                    "purchase_date_from": self.from_date,
                    "purchase_date_to": self.to_date
                }
            )

    def _get_data_request(self, page: int = 1):
        data = super()._get_data_request(page)
        try:
            assert "page_count" in data and "total" in data, f"The data request is empty"
            data.update(dict(
                page_count=1,
                total=self.limit_size_request
            ))
        except Exception as ex:
            logger.debug(f"[{self.__class__.__name__}][{self.client_id}][_get_data_request] : {ex}")
        return data
