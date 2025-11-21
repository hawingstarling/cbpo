import copy
import csv
import logging
import os
import time
import uuid
import pytz
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db import DatabaseError
from plat_import_lib_api.static_variable.raw_data_import import RAW_IGNORED_TYPE
from psycopg2 import OperationalError
from app.financial.models import CustomReport
from app.financial.services.exports.schema import ExportSchema
from app.financial.services.sale_item_bulk import SaleItemBulkEditModuleService
from app.financial.variable.report import REPORTED
from config.settings.common import DS_TZ_CALCULATE
from plat_import_lib_api.static_variable.config import plat_import_setting
from django_bulk_update.helper import bulk_update

logger = logging.getLogger(__name__)

REPORT_TIMEZONE = DS_TZ_CALCULATE if DS_TZ_CALCULATE is not None else "UTC"


class BaseCustomReportModuleService(SaleItemBulkEditModuleService):
    module = None
    serializer_class = None
    model = None

    def __init__(self, bulk_id: str = None, jwt_token: str = None, user_id: str = None, client_id: str = None):
        super().__init__(bulk_id=bulk_id, jwt_token=jwt_token,
                         user_id=user_id, client_id=client_id)
        #
        self.columns_as_type = {}
        #
        self.custom_report = self._get_custom_report()
        self.custom_report_columns = self.get_columns_export()
        self.custom_report_columns_mapping = list(
            self.custom_report_columns.keys())
        self.custom_report_file_temp = self.get_custom_report_temp()
        #
        self.export_schema = ExportSchema(client_id=self.client_id, columns=self.custom_report_columns, queryset=None,
                                          category='custom_report', df_mode='a', header=False,
                                          file_path=self.custom_report_file_temp, index=False,
                                          storage_env=plat_import_setting.storage_location)

        self.custom_report_tz = self.bulk.meta.get(
            'query', {}).get('timezone', REPORT_TIMEZONE)
        self.timezone = pytz.timezone(self.custom_report_tz)

        self.instance_ids = []

    def _get_custom_report(self):
        return CustomReport.objects.tenant_db_for(self.client_id).get(pk=self.bulk.id)

    def get_columns_export(self):
        raise NotImplementedError

    def _update_meta_custom_report(self, data: list = []):
        try:
            assert len(data) > 0, "Data meta custom report is not empty"
            self.custom_report.meta_data = data
            self.custom_report.save()
        except Exception as ex:
            logger.debug(
                f"[{self.__class__.__name__}][{self.client_id}][_update_meta_custom_report] {ex}")

    def get_custom_report_temp(self):
        file_path = self.bulk.meta.get('custom_report_temp')
        if not file_path:
            file_path = self.init_file_csv()
        return file_path

    def _generate_file_storage(self):
        custom_report_name = self.custom_report.name.replace(' ', '-')
        d, m, y = self.time_now.strftime(
            '%d'), self.time_now.strftime('%m'), self.time_now.year
        timestamp = int(self.time_now.timestamp())
        file_path = f"{plat_import_setting.storage_folder}/reports/{self.client_id}/{y}/{m}/{d}/" \
                    f"{custom_report_name}-{timestamp}.csv"
        file_storage = os.path.join(settings.MEDIA_ROOT, file_path)
        file_storage = default_storage.save(file_storage, ContentFile(''))
        return file_storage

    def init_file_csv(self):
        file_storage = self._generate_file_storage()
        with open(file_storage, 'w', newline='') as f:
            w = csv.writer(f)
            w.writerow(list(self.custom_report_columns.values()))
        self.bulk.meta['custom_report_file_temp'] = file_storage
        self.bulk.save()
        return file_storage

    def _get_instances(self, ids, **kwargs):
        self.instance_ids = ids
        return self.model.objects.tenant_db_for(self.client_id) \
            .filter(id__in=self.instance_ids, client__id=self.client_id).order_by('-id')

    def _process(self):
        if self.bulk.status == REPORTED:
            return
        start_time = time.time()
        try:
            while True:
                if not self.query_set_processing.exists():
                    url = self.export_schema.up_to_service(
                        self.custom_report_file_temp)
                    self._update_report_info(
                        data={"status": REPORTED, "download_url": url, "progress": self.progress})
                    #
                    self._update_bulk_info()
                    break

                bulk_data = self.query_set_processing.order_by(
                    'index')[:self.bulk_data_chunk_size]
                self.items_chunk_map = {
                    uuid.UUID(item.key_map): item for item in bulk_data}
                ids = list(self.items_chunk_map.keys())

                logger.debug(f"[{self.__class__.__name__}][_process][{self.client_id}][{self.command}][{self.bulk.pk}] "
                             f"Items to processed: {len(ids)}")

                instances = self._get_instances(ids)
                try:
                    # Start bulk_edit process for items in each page
                    self._process_data(instances=instances)
                except OperationalError or DatabaseError as ex:
                    logger.debug(f"[{self.__class__.__name__}][_process][{self.client_id}][{self.command}]"
                                 f"[{self.bulk.pk}][OperationalError|DatabaseError] {ex}")
                    continue
                except Exception as ex:
                    self._update_error_summary(self.command, message=str(ex))
                    logger.debug(f"[{self.__class__.__name__}][_process][{self.client_id}][{self.command}]"
                                 f"[{self.bulk.pk}][Exception] {ex}")

                # Update bulk_info
                self._update_bulk_info()
                #
                # Stop process if job is `cancelled`
                if self.bulk.status in [REPORTED]:
                    break
        except Exception as ex:
            logger.error(f"[{self.__class__.__name__}][_process][{self.client_id}][{self.command}][{self.bulk.pk}] "
                         f"Error {ex}")
        end_time = time.time()
        logger.debug(f"[{self.__class__.__name__}][_process][{self.client_id}][{self.bulk.pk}][{self.command}] "
                     f"Execution time: {end_time - start_time}")
        # update file to storage
        if self.bulk.status == REPORTED:
            url = self.export_schema.up_to_service(
                self.custom_report_file_temp)
            self._update_report_info(
                data={"status": REPORTED, "download_url": url})

    @property
    def _status_complete(self):
        return REPORTED

    def _update_bulk_info(self):
        super()._update_bulk_info()
        # update to custom reports
        self._update_report_info(data={"progress": self.bulk.progress})

    def _update_report_info(self, data):
        CustomReport.objects.tenant_db_for(
            self.client_id).filter(pk=self.bulk.id).update(**data)

    def _process_data_item(self, instance, validated_data, export_data, **kwargs):
        raise NotImplementedError

    def _validate_data_context(self, instance, raw_ins):
        context_data = dict(instance=instance, bulk_edit=True)
        serializer, list_error, dict_error = self._validate_update_data(
            **context_data)
        if not serializer.is_valid():
            raw_ins.status = self._status_complete
            raw_ins.is_valid = False
            raw_ins.is_complete = False
            raw_ins.type = RAW_IGNORED_TYPE
            raw_ins.processing_errors += list_error
            self.items_chunk_map[instance.pk] = raw_ins
            return False, {}
        return True, serializer.validated_data

    def _process_data(self, instances):
        export_data = []
        for index, instance in enumerate(instances):
            item_id = instance.pk
            raw_ins = self.items_chunk_map[item_id]
            raw_ins.meta_addition = {
                'command': self.command, 'processing_errors': []}
            raw_ins.modified = self.time_now
            # Item to be cached
            try:
                valid, validated_data = self._validate_data_context(
                    instance, raw_ins)
                if not valid:
                    continue
                validated_data_copy = copy.deepcopy(validated_data)
                self._process_data_item(
                    instance, validated_data_copy, export_data)
                #
                raw_ins.status = self._status_complete
                raw_ins.is_valid = True
                raw_ins.is_complete = True
                self.items_chunk_map[item_id] = raw_ins
            except OperationalError or DatabaseError as ex:
                logger.debug(f"[{self.__class__.__name__}][{self.client_id}][_process_data]"
                             f"[OperationalError|DatabaseError] {ex}")
                raise ex
            except Exception as ex:
                raw_ins.status = self._status_complete
                raw_ins.is_valid = False
                raw_ins.is_complete = False
                raw_ins.type = RAW_IGNORED_TYPE
                raw_ins.processing_errors += [
                    {'code': 'system', 'message': str(ex)}]
                self.items_chunk_map[item_id] = raw_ins
                logger.debug(
                    f"[{self.__class__.__name__}][{self.client_id}][_process_data][Exception] {ex}")
        #
        self._bulk_update()
        if export_data:
            self.export_schema.processing_data_frame(data=export_data)

    def _bulk_update(self):
        try:
            if self.items_chunk_map:
                bulk_update(self.items_chunk_map.values(), update_fields=self.fields_raw_import_accept,
                            using=self.client_db)
            # Update bulk_info
            self._update_bulk_info()
            logger.info(f"""[{self.__class__.__name__}] Bulk exported successfully:
                bulk_id: {self.bulk.pk}
                items_chunk_map: {len(self.items_chunk_map)} item(s) """)
        except Exception as ex:
            logger.error(f"""[{self.__class__.__name__}] Failed to process bulk exported: {ex} 
                bulk_id: {self.bulk.pk} 
                items_chunk_map: {self.items_chunk_map[:9]} item(s)""")
        self.sale_item_bulk, self.sale_bulk, self.log_entry_bulk, self.items_chunk_map = [], [], [], {}
