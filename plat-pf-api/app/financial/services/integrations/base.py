import logging
import json
import datetime
from abc import ABC

from auditlog.models import LogEntry
from typing import Union, List, KeysView

from django.utils import timezone

from app.core.services.audit_logs.base import AuditLogCoreManager
from app.core.services.integrations.base import IntegrationCoreBase
from app.core.variable.marketplace import CHANNEL_DEFAULT
from app.financial.models import DataFlattenTrack, Channel, DataStatus, Sale, SaleItem
from app.core.services.utils import get_sc_method
from app.core.variable.pf_trust_ac import FLATTEN_TRACK_LOG_TYPE, TIME_CONTROL_LOG_TYPE
from app.financial.variable.job_status import LIVE_FEED_JOB, TRANS_EVENT_JOB, BULK_SYNC_LIVE_FEED_JOB, \
    SKU_VAULT_JOB, MODIFIED_FILTER_MODE, INFORMED_PROFILE_JOB, CART_ROVER_JOB, TRANS_DATA_EVENT_JOB

logger = logging.getLogger(__name__)


class IntegrationFinancialBase(IntegrationCoreBase, ABC):
    def __init__(self, client_id: str = None, flatten: DataFlattenTrack = None, marketplace: str = CHANNEL_DEFAULT,
                 **kwargs):
        super().__init__(client_id, flatten, marketplace, **kwargs)
        self.client = flatten.client
        #
        self.sc_method = get_sc_method(self.marketplace_type)
        # get channel info
        self.channel = Channel.objects.tenant_db_for(self.client_id).get(name__iexact=self.marketplace)
        self.log_type = self._log_type

    @property
    def filter_mode(self):
        return self.kwargs.get("filter_mode", MODIFIED_FILTER_MODE)

    @property
    def is_replacement_order(self):
        return self.kwargs.get("is_replacement_order", None)

    def _from_date(self):
        from_date = self.kwargs.get("from_date", None)
        if from_date:
            return from_date
        try:
            args = {
                LIVE_FEED_JOB: self.flatten_track.last_run,
                TRANS_EVENT_JOB: self.flatten_track.last_run_event,
                SKU_VAULT_JOB: self.flatten_track.last_run,
                CART_ROVER_JOB: self.flatten_track.last_run,
                INFORMED_PROFILE_JOB: self.flatten_track.last_run,
            }

            last_run = args.get(self.JOB_TYPE, None)
        except Exception as ex:
            logger.debug(f"[{self.__class__.__name__}][{self.client_id}][_from_date] {ex}")
            last_run = None

        if last_run is not None:
            # previous 1 hour
            from_date = last_run - datetime.timedelta(minutes=self.MINUTES)
            from_date = from_date.strftime(self.DT_FILTER_FORMAT)
        else:
            from_date = timezone.now() - datetime.timedelta(minutes=self.MINUTES)
            from_date = from_date.strftime(self.DT_FILTER_FORMAT)
        return from_date

    def _to_date(self):
        to_date = self.kwargs.get("to_date", None)
        if to_date:
            return to_date
        to_date = self.last_run + datetime.timedelta(minutes=self.MINUTES)
        return to_date.strftime(self.DT_FILTER_FORMAT)

    def _init_log(self):
        if self._log_type == TIME_CONTROL_LOG_TYPE:
            return self._update_log_schema(log={})

        args = {
            LIVE_FEED_JOB: self.flatten_track.log_feed,
            BULK_SYNC_LIVE_FEED_JOB: self.flatten_track.log_feed,
            TRANS_EVENT_JOB: self.flatten_track.log_event,
            TRANS_DATA_EVENT_JOB: self.flatten_track.log_event
        }

        log_data = args.get(self.JOB_TYPE, {})
        __log = self._convert_to_json_content(log_data)
        return self._update_log_schema(__log)

    @property
    def _log_type(self):
        return self.kwargs.get("log_type", FLATTEN_TRACK_LOG_TYPE)

    @property
    def time_control_id(self):
        return self.kwargs.get("time_control_id", None)

    def _write_log_to_time_control(self, log_data: dict):
        if not self.time_control_id:
            return
        try:
            time_control = DataStatus.objects.tenant_db_for(self.client_id).get(pk=self.time_control_id)

            __log = self._convert_to_json_content(time_control.log)

            __log.update({self.JOB_TYPE: log_data})

            time_control.log = json.dumps(__log)
            time_control.save()
        except Exception as ex:
            logger.error(
                f"[{self.__class__.__name__}][_write_log_to_time_control]: {ex}"
            )

    def _refresh_flatten_track(self):
        self.flatten_track.refresh_from_db()

    def set_last_run_flatten_track(self):
        if not self.kwargs.get("track_logs", True):
            return
        #
        try:
            args = {
                LIVE_FEED_JOB: self.flatten_track.last_run,
                TRANS_EVENT_JOB: self.flatten_track.last_run_event
            }

            last_run = args.get(self.JOB_TYPE)
            if not last_run or self.last_run > last_run:
                if self.JOB_TYPE == LIVE_FEED_JOB and self.marketplace == CHANNEL_DEFAULT:
                    self.flatten_track.last_run = self.last_run
                if self.JOB_TYPE == TRANS_EVENT_JOB and self.marketplace == CHANNEL_DEFAULT:
                    self.flatten_track.last_run_event = self.last_run
        except Exception as ex:
            logger.debug(f"[{self.__class__.__name__}][set_last_run_flatten_track] {ex}")

    def _set_object_fields_change(self, obj: Union[Sale, SaleItem], fields_update: Union[List, KeysView], validated_data: dict,
                                  fields_properties: dict = None):
        if fields_properties is None:
            fields_properties = {}
        changes = dict()
        obj_log = None
        for field in fields_update:
            if field not in validated_data:
                continue
            val_obj = getattr(obj, field)
            val_data = validated_data.pop(field)
            if val_data is None or val_obj == val_data:
                continue
            setattr(obj, field, val_data)
            field_properties = fields_properties.get(field, {})
            if field_properties:
                field_attribute = field_properties["attribute"]
                field_default = field_properties["default"]
                if not val_obj:
                    val_obj = field_default
                if not val_data:
                    val_data = field_default
                if field_attribute is not None:
                    try:
                        val_obj = getattr(val_obj, field_attribute, field_default)
                        val_data = getattr(val_data, field_attribute, field_default)
                    except Exception as ex:
                        logger.debug(f"[{self.__class__.__name__}][{self.client_id}][{self.JOB_TYPE}]"
                                     f"[{self.marketplace}][_set_object_fields_change] {ex}")
            changes.update({field: [str(val_obj), str(val_data)]})
        if changes:
            if hasattr(obj, "dirty"):
                setattr(obj, "dirty", True)
            if hasattr(obj, "financial_dirty"):
                setattr(obj, "financial_dirty", True)
            if hasattr(obj, "modified"):
                setattr(obj, "modified", self.last_run)
            obj_log = (
                AuditLogCoreManager(client_id=self.client_id)
                .set_actor_name(self.JOB_TYPE)
                .create_log_entry_from_compared_changes(obj, changes, action=LogEntry.Action.UPDATE)
            )
        return obj, obj_log
