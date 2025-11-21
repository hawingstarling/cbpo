import copy
import hashlib
from django.conf import settings
from django.utils import timezone
from plat_import_lib_api.static_variable.raw_data_import import RAW_UPDATED_TYPE, RAW_IGNORED_TYPE
from app.core.utils import hashlib_content
from app.database.helper import get_connection_workspace
from app.financial.jobs.data_flatten import flat_sale_items_bulks_sync_task
from app.financial.services.utils.common import chunks_size_list, get_id_data_source_3rd_party, get_flatten_source_name
from app.financial.variable.bulk_sync_datasource_variable import DATA_CENTRAL
import json
import logging
from abc import abstractmethod
from auditlog.models import LogEntry
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import QuerySet
from django_bulk_update.helper import bulk_update
from app.job.utils.helper import register
from app.job.utils.variable import BULK_CATEGORY, MODE_RUN_IMMEDIATELY
from plat_import_lib_api.models import DataImportTemporary, PROCESSED, REVERTING, REVERTED, PROCESSING, RawDataTemporary
from plat_import_lib_api.services.modules.base import BaseModule
from app.core.context import AppContext
from app.financial.exceptions import CustomObjNotFoundException
from app.financial.models import ClientSettings, SaleItem, Sale, SaleStatus, ProfitStatus, LogClientEntry, \
    DataFlattenTrack, ClientPortal
from app.core.services.audit_logs.base import AuditLogCoreManager
from app.financial.sub_serializers.client_serializer import ClientSaleItemSerializer
#
from app.financial.services.api_data_source_centre import ApiCentreContainer
from app.financial.services.data_source import DataSource
from app.financial.variable.data_flatten_variable import FLATTEN_SALE_ITEM_KEY
import math
import time

logger = logging.getLogger(__name__)


class SaleItemBulkBaseModuleService:
    module: BaseModule = None
    serializer_class: ClientSaleItemSerializer = None
    query_set: QuerySet = None
    query_set_processing: QuerySet = None
    paginator: Paginator = None

    def __init__(self, bulk_id: str = None, jwt_token: str = None, user_id: str = None, client_id: str = None):
        # authentication info
        self.client_id = client_id
        self.client = ClientPortal.objects.tenant_db_for(self.client_id).get(pk=self.client_id)
        self.client_db = get_connection_workspace(self.client_id)
        self.user_id = user_id
        self.jwt_token = jwt_token
        try:
            self.bulk = DataImportTemporary.objects.db_manager(using=self.client_db).get(pk=bulk_id,
                                                                                         module=self.module.__NAME__)
        except DataImportTemporary.DoesNotExist:
            raise CustomObjNotFoundException(
                message='[%s] Cannot find %s<%s>' % (self.__class__.__name__, self.module.__NAME__, bulk_id),
                verbose=True)
        # use dictionary of items to ignore duplicated values
        self._items_chunk_map = {}
        # bulk-edit meta-data
        self.command = self.bulk.meta['command']  # edit/delete/sync
        # use set of ids to ignore duplicated values
        self.ids = set(self.bulk.meta.get('ids', []))
        self.sale_item_query = self.bulk.meta.get('query', {})
        # bulk-edit process summary
        self.progress = self.bulk.progress
        self.total = 0
        #
        # items to be bulk-updated
        self.sale_item_bulk, self.sale_bulk, self.log_entry_bulk = [], [], []
        #
        self.fields_sale_accept = [i.name for i in Sale._meta.fields if i.name not in ['pk', 'id']]
        self.fields_sale_item_accept = [i.name for i in SaleItem._meta.fields if i.name not in ['pk', 'id']]
        self.fields_raw_import_accept = [i.name for i in RawDataTemporary._meta.fields if i.name not in ['pk', 'id']]
        #
        self._sale_ids_affected = set()  # for sale status and profit status
        self.bulk_data_chunk_size = 1000
        self.client_setting = self.__get_client_setting()
        self.allow_sale_data_update_from = getattr(self.client_setting, 'allow_sale_data_update_from', None)
        self.time_now = timezone.now()

    def __get_client_setting(self):
        try:
            return ClientSettings.objects.tenant_db_for(self.client_id).get(client_id=self.client_id)
        except ClientSettings.DoesNotExist:
            return None

    @property
    def number_process(self):
        try:
            return self.query_set.filter(status=self._status_complete).count()
        except Exception as ex:
            return 0

    @property
    def items_chunk_map(self):
        return self._items_chunk_map

    @items_chunk_map.setter
    def items_chunk_map(self, value):
        self._items_chunk_map = value

    @property
    def bulk_data_status(self):
        return self._bulk_data_status

    @bulk_data_status.setter
    def bulk_data_status(self, value):
        self._bulk_data_status = value

    @property
    def _is_reverting_empty_last_values(self):
        try:
            find = RawDataTemporary.objects.db_manager(self.client_db).filter(lib_import_id=self.bulk.pk,
                                                                              status=self.bulk.status)
            if self.bulk.status == REVERTING and find.count() == 0:
                self._update_bulk_info()
                return True
        except Exception as ex:
            pass
        return False

    def create_bulk_revert_chunks(self):
        RawDataTemporary.objects.db_manager(self.client_db).filter(lib_import_id=self.bulk.pk) \
            .update(status=self.bulk.status, is_valid=None, is_complete=None, modified=self.time_now)

    def get_total_ids(self):
        total_ids = self.bulk.meta.get('ids', [])
        if '__all__' in total_ids:
            total_ids = SaleItem.objects.tenant_db_for(self.client_id) \
                .order_by('sale_date') \
                .values_list('id', flat=True)
        elif 'filter' in self.sale_item_query:
            logger.info(f"[{self.__class__.__name__}] begin create bulk process chunks")
            total_ids += self.get_ids_from_query(query=self.sale_item_query)

        total_ids = list(set(total_ids))
        return total_ids

    def create_bulk_process_chunks(self):
        if self.bulk.status == REVERTING:
            self.create_bulk_revert_chunks()
        else:
            bulk_data = []
            total_ids = self.get_total_ids()
            if len(total_ids) > 0:
                index = 1
                for chunk_ids in chunks_size_list(total_ids, 1000):
                    for obj_id in chunk_ids:
                        obj = RawDataTemporary(
                            lib_import_id=self.bulk.pk,
                            index=index,
                            data=dict(id=obj_id),
                            data_map_config=dict(id=obj_id),
                            type=RAW_UPDATED_TYPE,
                            status=self.bulk.status,
                            key_map=obj_id,
                            hash_data=hashlib.md5(json.dumps(dict(id=obj_id)).encode('utf-8')).hexdigest()
                        )
                        bulk_data.append(obj)
                        index += 1
                    RawDataTemporary.objects.db_manager(using=self.client_db).bulk_create(bulk_data,
                                                                                          ignore_conflicts=True)
                    bulk_data = []
            # Update total items
            self.total = len(set(total_ids))
            self._update_bulk_info()
            # move all item ids to bulkdata done, so we need set empty make decrease memory cache queryset load
            bulk_ids = self.bulk.meta.get('ids', [])
            if len(bulk_ids) > 50:
                self.bulk.meta.update({'ids': bulk_ids[:50]})
            self.bulk.save()

    def start_processing(self):
        self._load_queue_environment()
        if self._is_reverting_empty_last_values:
            logger.error(
                f"[{self.__class__.__name__}][_is_reverting_empty_last_values] {self.bulk.pk} not found last values for reverting ...")
            return
        self._load_query_set()
        self._process()

    def get_ids_from_query(self, query: dict):
        sale_item_ids = set()
        if 'filter' in self.sale_item_query and query.get('filter') == {}:
            return []
        # update sort query
        query.update({
            'orders': [{"column": "sale_date", "direction": "asc"}],
            'group': {
                'columns': [],
                'aggregations': []
            },
        })
        logger.info(f"[{self.__class__.__name__}][get_ids_from_query] query origin={query}")
        data_source_tracking = DataFlattenTrack.objects.tenant_db_for(self.client_id).get(client_id=self.client_id,
                                                                                          type=FLATTEN_SALE_ITEM_KEY)
        tabel_name = get_flatten_source_name(client_id=self.client_id, type_flatten=FLATTEN_SALE_ITEM_KEY)
        data_source_service = DataSource(client_id=self.client_id, type_flatten=FLATTEN_SALE_ITEM_KEY,
                                         table=tabel_name, access_token=settings.DS_TOKEN,
                                         api_centre=ApiCentreContainer.data_source_central(),
                                         source=data_source_tracking.source, token_type='DS_TOKEN')
        external_id = get_id_data_source_3rd_party(source=data_source_tracking.source, client_id=self.client_id,
                                                   type_flatten=FLATTEN_SALE_ITEM_KEY)
        fields = [
            {
                "name": "sale_item_id",
                "alias": "sale_item_id"
            }
        ]
        count_result = data_source_service.call_query(external_id=external_id, fields=fields, query_type='count',
                                                      **query)
        limit = 10000
        current = 1
        page_count = math.ceil(int(count_result['count']) / limit)
        while current <= page_count:
            try:
                logger.info(f"[{self.__class__.__name__}][{external_id}][get_ids_from_query] "
                            f"limit={limit}, current={current}, page_count={page_count}")
                query['paging'] = {'limit': limit, 'current': current}
                fields = [
                    {
                        "name": "sale_item_id",
                        "alias": "sale_item_id"
                    }
                ]
                query_result = data_source_service.call_query(external_id=external_id, fields=fields, **query)
                for row in query_result['rows']:
                    sale_item_ids.add(row[0])
                current += 1
            except Exception as ex:
                logger.error(f"[{self.__class__.__name__}][get_ids_from_query] {ex}")
            time.sleep(0.5)
        logger.info(f"[{self.__class__.__name__}][get_ids_from_query] "
                    f"sale_item_ids={len(sale_item_ids)}, count_result={count_result['count']}")
        return list(sale_item_ids)

    @abstractmethod
    def _process(self):
        pass

    def _load_queue_environment(self):
        try:
            AppContext.instance().clean()
            context = AppContext.instance()
            context.user_id = self.user_id
            context.client_id = self.client_id
            context.jwt_token = self.jwt_token
        except Exception as ex:
            logger.error(
                f'''[{self.__class__.__name__}][load_queue_environment] {self.command} - {self.bulk.pk} {ex}''')
            raise ex

    def _load_query_set(self):
        try:
            self.query_set = RawDataTemporary.objects.db_manager(self.client_db).filter(lib_import_id=self.bulk.pk)
            self.total = self.query_set.count()
            self.query_set_processing = self.query_set.filter(status=self.bulk.status)
        except Exception as ex:
            logger.error(
                f'''[{self.__class__.__name__}][load_query_set] {self.command} - {self.bulk.pk} {ex}''')
            raise ex

    def _bulk_update(self):
        try:
            # with transaction.atomic():
            if self.sale_item_bulk:
                SaleItem.objects.tenant_db_for(self.client_id) \
                    .bulk_update(self.sale_item_bulk, fields=self.fields_sale_item_accept)
            if self.sale_bulk:
                Sale.objects.tenant_db_for(self.client_id) \
                    .bulk_update(self.sale_bulk, fields=self.fields_sale_accept)
            if self.log_entry_bulk:
                LogClientEntry.objects.tenant_db_for(self.client_id).bulk_create(objs=self.log_entry_bulk,
                                                                                 ignore_conflicts=True)
            if self.items_chunk_map:
                bulk_update(self.items_chunk_map.values(), update_fields=self.fields_raw_import_accept,
                            using=self.client_db)
            # Update bulk_info
            self._update_bulk_info()
            logger.info(f'''[{self.__class__.__name__}] Bulk_update successfully:
                bulk_id: {self.bulk.pk}
                sale_item_bulk: {len(self.sale_item_bulk)} item(s)
                sale_bulk: {len(self.sale_bulk)} item(s)
                log_entry_bulk: {len(self.log_entry_bulk)} item(s)            
            ''')
            self._process_and_bulk_update_sale_affected()
        except Exception as ex:
            logger.error(f'''[{self.__class__.__name__}] Failed to process bulk_update: {ex}
                bulk_id: {self.bulk.pk}
                sale_item_bulk: {self.sale_item_bulk[:9]}
                sale_bulk: {self.sale_bulk[:9]}
                log_entry_bulk: {self.log_entry_bulk[:9]}            
            ''')
            # self.errors.append({'code': 'bulk_update_error', 'message': ex})
        self.sale_item_bulk, self.sale_bulk, self.log_entry_bulk, self.items_chunk_map = [], [], [], {}

    def _update_bulk_info(self):
        self.progress = round((self.number_process / self.total) * 100, 2) if self.total > 0 else 100
        self.bulk.progress = self.progress
        if self.progress == 100:
            self.bulk.status = self._status_complete
            self.bulk.process_completed = timezone.now()
        self.bulk.save()

    @property
    def _status_complete(self):
        if self.bulk.status in [REVERTING, REVERTED]:
            return REVERTED
        elif self.bulk.status in [PROCESSING, PROCESSED]:
            return PROCESSED
        else:
            return self.bulk.status

    def _sync_datasource(self, ids: []):
        ids = list(ids)
        count_dirty = SaleItem.all_objects.tenant_db_for(self.client_id).filter(pk__in=ids, client_id=self.client_id,
                                                                                dirty=True).count()
        if count_dirty > 0:
            # financial split records
            meta = dict(client_id=self.client_id, sale_item_ids=ids)
            hash_content = hashlib_content(meta)
            job_data = dict(
                name=f"split_sale_item_financial_ws_{hash_content}",
                job_name="app.financial.jobs.sale_financial.handler_trigger_split_sale_item_financial_ws",
                module="app.financial.jobs.sale_financial",
                method="handler_trigger_split_sale_item_financial_ws",
                meta=meta
            )
            transaction.on_commit(
                lambda: {
                    flat_sale_items_bulks_sync_task(self.client_id),
                    register(BULK_CATEGORY, client_id=self.client_id, **job_data, mode_run=MODE_RUN_IMMEDIATELY)
                },
                using=self.client_db)

    @staticmethod
    def chunks(lst, n) -> list:
        """Yield successive n-sized chunks from lst."""
        for i in range(0, len(lst), n):
            yield lst[i:i + n]

    def _process_and_bulk_update_sale_affected(self):
        # sale status and profit status of sale are affected by sale item's sale status and profit status
        if not len(self._sale_ids_affected):
            return
        sale_being_bulk_update = {}
        sale_log_being_create = []
        sale_query_set = Sale.objects.tenant_db_for(self.client_id).filter(id__in=self._sale_ids_affected)
        for sale in sale_query_set:
            new_sale_status_id = sale.saleitem_set.tenant_db_for(self.client_id) \
                .all() \
                .order_by('sale_status__order') \
                .values_list('sale_status', flat=True) \
                .first()
            new_profit_status_id = sale.saleitem_set.tenant_db_for(self.client_id) \
                .all() \
                .order_by('profit_status__order') \
                .values_list('profit_status', flat=True) \
                .first()
            new_sale_date = sale.saleitem_set.tenant_db_for(self.client_id) \
                .all() \
                .order_by('sale_date') \
                .values_list('sale_date', flat=True) \
                .first()

            changes = {}

            if new_sale_status_id and sale.sale_status_id != new_sale_status_id:
                new_value = SaleStatus.objects.tenant_db_for(self.client_id).get(id=new_sale_status_id).value
                changes.update({'sale_status': [sale.sale_status.value, new_value]})
                sale.sale_status_id = new_sale_status_id
                sale_being_bulk_update.update({str(sale.id): sale})
            if new_profit_status_id and sale.profit_status_id != new_profit_status_id:
                new_value = ProfitStatus.objects.tenant_db_for(self.client_id).get(id=new_profit_status_id).value
                changes.update({'profit_status': [sale.profit_status.value, new_value]})
                sale.profit_status_id = new_profit_status_id
                sale_being_bulk_update.update({str(sale.id): sale})
            if new_sale_date and sale.date != new_sale_date:
                changes.update({'date': [sale.date, new_sale_date]})
                sale.date = new_sale_date
                sale_being_bulk_update.update({str(sale.id): sale})

            if changes != {}:
                log_entry = AuditLogCoreManager(client_id=self.client_id).set_actor_name('Bulk_Edit_Affect_Sale') \
                    .create_log_entry_from_compared_changes(sale, changes, action=LogEntry.Action.UPDATE)
                sale_log_being_create.append(log_entry)

        sale_being_bulk_update = list(sale_being_bulk_update.values())
        if len(sale_being_bulk_update):
            try:
                with transaction.atomic():
                    bulk_update(sale_being_bulk_update, update_fields=['sale_status', 'profit_status', 'date'],
                                using=self.client_db)
                    LogClientEntry.objects.tenant_db_for(self.client_id).bulk_create(sale_log_being_create,
                                                                                     ignore_conflicts=True)
            except Exception as error:
                logger.error(f'[{self.__class__.__name__}][_process_and_bulk_update_sale_affected] {error}')
        # make flat for generate to data source
        SaleItem.objects.tenant_db_for(self.client_id).filter(sale_id__in=self._sale_ids_affected) \
            .update(dirty=True, financial_dirty=True, modified=self.time_now)
        self._sale_ids_affected.clear()

    def _update_success_summary(self):
        for pk, obj in self.items_chunk_map.items():
            obj.meta_addition = dict(command=self.command)
            obj.status = self._status_complete
            obj.is_valid = True
            obj.is_complete = True
            obj.processing_errors = []
            obj.modified = self.time_now
        bulk_update(self.items_chunk_map.values(), update_fields=self.fields_raw_import_accept, using=self.client_db)
        self.items_chunk_map = {}

    def _update_error_summary(self, error_source, **kwargs):
        ids = kwargs.get('ids', [])
        item_chunk_map = copy.deepcopy(self.items_chunk_map)
        validation_error = {'code': error_source, 'message': kwargs.get('message', 'Unexpected error')}
        verbose_error = kwargs.get('verbose_error', settings.DEBUG)
        if verbose_error:
            processing_error = validation_error
        else:
            processing_error = {'code': error_source, 'message': 'Unexpected error'}
        if ids:
            item_chunk_map = dict(filter(lambda elem: elem[0] in ids, item_chunk_map.items()))
        for pk, obj in item_chunk_map.items():
            if not isinstance(obj.processing_errors, list):
                obj.processing_errors = []
            if not isinstance(obj.validation_errors, list):
                obj.validation_errors = []
            obj.meta_addition = dict(command=self.command)
            obj.status = self._status_complete
            obj.is_valid = False
            obj.is_complete = False
            obj.type = RAW_IGNORED_TYPE
            obj.validation_errors.append(validation_error)
            obj.processing_errors.append(processing_error)
            obj.modified = self.time_now
            del self.items_chunk_map[pk]
        bulk_update(item_chunk_map.values(), update_fields=self.fields_raw_import_accept, using=self.client_db)

    def _process_allow_sale_data_update_from(self, ids, sources: [str] = []):
        # clean ids already deleted
        try:
            invalid_sale_item_ids = SaleItem.all_objects.tenant_db_for(self.client_id) \
                .filter(id__in=ids, is_removed=True) \
                .values_list('id', flat=True)
            invalid_sale_item_ids = list(invalid_sale_item_ids)
            ids = list(set(ids) - set(invalid_sale_item_ids))
            if invalid_sale_item_ids:
                message = f"The item doesn't exist or deleted"
                self._update_error_summary(error_source='system', ids=invalid_sale_item_ids, message=message)
        except Exception as ex:
            pass
        #
        if DATA_CENTRAL in sources and self.client.is_oe:
            message = f"Do not allow to update data from Data Central"
            self._update_error_summary(error_source=DATA_CENTRAL, ids=ids, message=message, verbose_error=True)
            ids = []
        elif self.allow_sale_data_update_from:
            invalid_sale_item_ids = SaleItem.objects.tenant_db_for(self.client_id) \
                .filter(id__in=ids, sale_date__date__lt=self.allow_sale_data_update_from) \
                .values_list('id', flat=True)
            invalid_sale_item_ids = list(invalid_sale_item_ids)
            ids = list(set(ids) - set(invalid_sale_item_ids))
            if invalid_sale_item_ids:
                message = f"Do not allow to update data before {self.allow_sale_data_update_from.strftime('%m/%d/%Y')}"
                self._update_error_summary(error_source='sale_date', ids=invalid_sale_item_ids, message=message,
                                           verbose_error=True)
        else:
            pass

        return ids
