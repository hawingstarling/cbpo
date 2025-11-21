import logging
from datetime import timedelta
from django.db.utils import DEFAULT_DB_ALIAS
from app.financial.models import Channel, ClientPortal
from django.utils import timezone

logger = logging.getLogger(__name__)


class StatReporter(object):

    def __init__(self, client_id: str, *args, **kwargs):
        #
        self.client_id = client_id
        self.client = ClientPortal.objects.tenant_db_for(DEFAULT_DB_ALIAS).get(pk=client_id)
        self.time_now = timezone.now()
        self.channels = self.get_channels_accept_report()
        self.args = args
        self.kwargs = kwargs

    @classmethod
    def _get_date_last_7_days(cls):
        _time_now = timezone.now()
        return [_time_now - timedelta(days=x + 1) for x in range(7)]

    @classmethod
    def _get_date_last_6_month(cls):
        _time_now = timezone.now() - timedelta(days=1)

        vals = [_time_now]

        for i in range(0, 5):
            _time_now = _time_now.replace(day=1)
            _time_now = _time_now - timedelta(days=1)
            vals.append(_time_now)

        return vals

    def get_channels_accept_report(self):
        channels = []
        try:
            channels = Channel.objects.tenant_db_for(self.client_id).filter(is_pull_data=True)
        except Exception as ex:
            logger.error(f"[{self.__class__.__name__}][get_channels_accept_report]: {ex}")
        return channels

    def validate(self):
        raise NotImplementedError

    def process(self):
        raise NotImplementedError

    def complete(self):
        raise NotImplementedError
