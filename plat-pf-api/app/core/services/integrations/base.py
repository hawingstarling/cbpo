import logging
import json
import datetime
from typing import Any

from django.utils import timezone
from httplib2 import Response
from rest_framework import status
from app.core.services.ac_service import ACManager
from app.database.helper import get_connection_workspace
from app.core.services.utils import get_marketplace_type
from app.financial.models import ClientSettings

logger = logging.getLogger(__name__)

JOB_ACTION = 'job_action'

BULK_INDEXES_KEY = 'INDEXES'
BULK_INSERTS_KEY = 'INSERTS'
BULK_UPDATES_KEY = 'UPDATES'


class IntegrationCoreBase(object):
    MINUTES = 30
    LIMIT_SIZE = 1000
    DT_FILTER_FORMAT = '%Y-%m-%d %H:%M:%S'
    JOB_TYPE = None
    CONNECT_TIMEOUT = 5.0
    READ_TIMEOUT = 30.0

    def __init__(self, client_id: str, flatten: Any, marketplace: str, **kwargs):
        self.client_id = client_id
        self.client_setting = ClientSettings.objects.tenant_db_for(self.client_id).get(client_id=self.client_id)
        self.flatten_track = flatten
        self.client_db = get_connection_workspace(self.client_id)
        self.kwargs = kwargs
        self.marketplace = marketplace
        self.marketplace_type = get_marketplace_type(self.marketplace)
        # validate job type define
        self.__validate_job_type()
        self.ac_manager = self.__instance_ac_service()
        self.last_run = timezone.now()
        #
        self._success = []
        self._errors = []
        self.from_date = self._from_date()
        self.to_date = self._to_date()
        self.time_tracking = '{} - {}'.format(self.from_date, self.to_date)

    def __instance_ac_service(self):
        return ACManager(client_id=self.client_id, connect_timeout=self.CONNECT_TIMEOUT, read_timeout=self.READ_TIMEOUT)

    @property
    def filter_mode(self):
        return self.kwargs.get('filter_mode', None)

    @property
    def _context_serializer(self) -> dict:
        return {
            "kwargs": {JOB_ACTION: self.JOB_TYPE, "client_id": self.client_id},
            "is_remove_cogs_refunded": getattr(self.client_setting, "is_remove_cogs_refunded", False)
        }

    def __validate_job_type(self):
        if not self.JOB_TYPE:
            raise NotImplementedError

    def _from_date(self):
        from_date = self.kwargs.get('from_date', None)
        return from_date

    def _to_date(self):
        to_date = self.kwargs.get('to_date', None)
        if to_date:
            return to_date
        to_date = self.last_run + datetime.timedelta(minutes=self.MINUTES)
        return to_date.strftime(self.DT_FILTER_FORMAT)

    def _init_log(self):
        pass

    def _update_log_schema(self, log: dict = {}):
        if 'success' not in log:
            log.update({'success': {}})
        if 'errors' not in log:
            log.update({'errors': {}})
        return log

    def _write_log_to_time_control(self, log_data: dict):
        pass

    def _convert_to_json_content(self, val):
        try:
            val = json.loads(val)
        except Exception as ex:
            val = {}
        return val

    def _get_data_request(self, *args, **kwargs):
        raise NotImplementedError

    def _write_log_process(self, *args, **kwargs):
        pass

    def _write_errors_request(self, *args, **kwargs):
        pass

    def _add_log_to_flatten(self, *args, **kwargs):
        pass

    def progress(self):
        raise NotImplementedError

    def _handler_result(self, rs: Response):
        status_code = rs.status_code
        if status_code in [status.HTTP_200_OK]:
            content = rs.content.decode('utf-8')
            return json.loads(content)
        if status.HTTP_400_BAD_REQUEST <= status_code <= status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED:
            content = rs.content.decode('utf-8')
            self._write_errors_request(status_code, content)
        return {}

    @staticmethod
    def chunks(lst, n) -> list:
        """Yield successive n-sized chunks from lst."""
        for i in range(0, len(lst), n):
            yield lst[i:i + n]
