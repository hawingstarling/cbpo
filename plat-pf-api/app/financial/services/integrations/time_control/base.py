import json, logging, time

from django.db import transaction
from httplib2 import Response
from rest_framework import status
from app.core.services.ac_service import ACManager
from app.financial.models import DataStatus
from app.core.services.utils import get_sc_method, get_marketplace_type
from app.core.variable.pf_trust_ac import ERROR_STATUS, PROCESS_STATUS, READY_STATUS, DONE_STATUS, IGNORE_STATUS

logger = logging.getLogger(__name__)


class BaseTimeControl(object):
    JOB_TYPE = None
    DATE_FILTER_FORMAT = '%Y-%m-%d'
    BEGIN_TIME = '00:00:00'
    END_TIME = '23:59:59'

    def __init__(self, data_tracking: DataStatus, **kwargs):

        self.data_tracking = data_tracking

        self.data_tracking_id = str(self.data_tracking.pk)

        self.client = self.data_tracking.client

        self.client_id = str(self.client.id)

        #

        self.ac_manager = ACManager(client_id=self.client_id)

        self.channel = self.data_tracking.channel

        self.marketplace = self.channel.name

        self.marketplace_type = get_marketplace_type(self.marketplace)

        self.sc_method = get_sc_method(self.marketplace_type)

        self.date = self.data_tracking.date.strftime(self.DATE_FILTER_FORMAT)

        self.kwargs = kwargs

        self.time_started = time.time()

        self.is_valid_job_type()

    def is_valid_job_type(self):
        if not self.JOB_TYPE:
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

    def _get_data_request(self):
        raise NotImplementedError

    def _write_log_to_data_tracking(self, status_tracking: str, content: str = None, reset_log=False):
        self.data_tracking.refresh_from_db()
        if reset_log:
            log = {}
        else:
            try:
                log = json.loads(self.data_tracking.log)
            except Exception as ex:
                log = {}
        if content:
            log.update({'status': content})
            if status_tracking == DONE_STATUS:
                time_exec = time.time() - self.time_started
                log.update({'time_exec': str(time_exec)})
                self.data_tracking.only_purchased_date = True
                self.data_tracking.is_checking_prime = False
            self.data_tracking.log = json.dumps(log)
        self.data_tracking.status = status_tracking
        self.data_tracking.save()

    def _write_errors_request(self, status_code, content):
        content = f"[ACManager][{self.JOB_TYPE}][status_code={status_code}] __handler_result error: {content}"
        status_tracking = ERROR_STATUS
        if status.HTTP_401_UNAUTHORIZED <= status_code <= status.HTTP_407_PROXY_AUTHENTICATION_REQUIRED:
            status_tracking = IGNORE_STATUS
        self._write_log_to_data_tracking(status_tracking=status_tracking, content=content)

    def _add_log_to_flatten(self, *args, **kwargs):
        pass

    @property
    def prefetch_status(self):
        self.data_tracking.refresh_from_db()
        return self.data_tracking.status

    def is_valid_content(self, data):
        raise NotImplementedError

    @property
    def is_ready(self):
        if self.prefetch_status in [READY_STATUS]:
            self._write_log_to_data_tracking(status_tracking=PROCESS_STATUS, reset_log=True)
            return True
        return False

    def handler_is_ready_event(self):
        # check data is ready
        data = self._get_data_request()

        # error request to get financial event status
        if not data:
            logger.error(
                f'[{self.client_id}][{self.channel.name}][{self.JOB_TYPE}][{self.date}]: request fail , pls check log')
            return

        errors = self.is_valid_content(data)

        if errors:
            msg = f'response is not valid : {errors}'
            content = f'[{self.client_id}][{self.channel.name}][{self.JOB_TYPE}][{self.date}]: {msg}'
            logger.error(content)
            self._write_log_to_data_tracking(status_tracking=IGNORE_STATUS, content=msg)
            return

        is_ready = data['ready']

        if not is_ready:
            # write log error
            msg = 'Data status is not ready'
            content = f'[{self.client_id}][{self.channel.name}][{self.JOB_TYPE}][{self.date}]: {msg}'
            logger.error(content)
            self._write_log_to_data_tracking(status_tracking=ERROR_STATUS, content=msg)
            return

        self._write_log_to_data_tracking(status_tracking=READY_STATUS)

    @transaction.atomic
    def progress(self):
        raise NotImplementedError
