from app.financial.models import SaleItemTransaction, SaleStatus
from app.financial.variable.job_status import LIVE_FEED_JOB, BULK_SYNC_LIVE_FEED_JOB, TRANS_DATA_EVENT_JOB, \
    BULK_SYNC_TRANS_DATA_EVENT_JOB
from app.financial.services.transaction.calculate.base import TransBaseSaleCalculate, CalculateFieldManage


class SaleStatusCalculate(TransBaseSaleCalculate):
    field = 'sale_status'

    def _handler_popular_data(self):
        value = SaleItemTransaction.sale_status_of_sale_level(self.client_id, self.filters, **self.kwargs)
        if value:
            self._data[self.field] = SaleStatus.objects.tenant_db_for(self.client_id).get(value=value)


class CalculateTransSaleManage(CalculateFieldManage):
    JOB_ACCEPT = [LIVE_FEED_JOB, BULK_SYNC_LIVE_FEED_JOB, TRANS_DATA_EVENT_JOB, BULK_SYNC_TRANS_DATA_EVENT_JOB]
    CALCULATED_CONFIG = [SaleStatusCalculate]

    @property
    def filters(self):
        return {
            'client': self.instance.client,
            'channel': self.instance.channel,
            'channel_sale_id': self.instance.channel_sale_id
        }

    def process(self):

        for class_cal in self.CALCULATED_CONFIG:

            cal = class_cal(client_id=self.client_id, filters=self.filters, instance=self.instance, *self.args,
                            **self.kwargs)
            cal.calculate()
            data = cal.data
            # value is None
            if not data:
                continue
            self.data.update(data)

        return self.data
