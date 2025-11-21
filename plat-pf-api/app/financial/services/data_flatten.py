import math
import time
from typing import Union, List, Dict

import pytz
from django.conf import settings
from django.db import connections, DatabaseError
from django.db.models import Q
from django.utils import timezone
from app.core.exceptions import SqlExecutionException
from app.core.logger import logger
from app.es.variables.config import ES_UPSERT_ACTION, ES_BULK_SIZE
from app.financial.models import SaleItem, SaleItemFinancial
from app.database.helper import get_connection_workspace
from app.financial.services.utils.common import get_flatten_source_name
from app.financial.services.utils.helper import get_es_service
from app.financial.sql_generator.flat_sql_generator_interface import FlatSqlGeneratorInterface
from app.financial.variable.common import BATCH_SIZE_DATA_SEGMENT
from app.financial.variable.data_flatten_variable import FLATTEN_SALE_ITEM_KEY, FLATTEN_SALE_ITEM_FINANCIAL_KEY, \
    FLATTEN_PG_SOURCE, FLATTEN_ES_SOURCE, DATA_FLATTEN_TYPE_ANALYSIS_LIST, CREATE_SOURCE_BY_QUERY, \
    UPDATE_SOURCE_BY_BUILD_UPSERT_QUERY, CREATE_SOURCE_BY_SCHEMA, UPDATE_SOURCE_BY_BUILD_INSERT_QUERY, \
    UPDATE_SOURCE_BY_SEGMENT_INSERT_QUERY
from app.job.utils.helper import register_list
from app.job.utils.variable import SYNC_DATA_SOURCE_CATEGORY, COMMUNITY_CATEGORY, MODE_RUN_IMMEDIATELY


class DataFlatten:
    """
    flat data from a query
    """

    def __init__(self, client_id, type_flatten, sql_generator: FlatSqlGeneratorInterface,
                 source: str = FLATTEN_PG_SOURCE, **kwargs):
        self.client_id = str(client_id)
        self.client_db = get_connection_workspace(self.client_id)
        self._sql_generator = sql_generator
        self.type_flatten = type_flatten
        self._flatten_name = get_flatten_source_name(client_id, type_flatten)
        self.kwargs = kwargs
        self.time_now = timezone.now()

        # es service
        self.es_service = get_es_service(
            client_id=client_id,
            type_flatten=type_flatten,
            properties_settings=self._sql_generator.build_properties_mapping_source(
                FLATTEN_ES_SOURCE)
        )

        self.source = source
        self.source_exist = self.is_flatten_exists()
        self.is_resync_data_source = self.get_is_resync_data_source()

        self.unique_fields = kwargs.get("unique_fields", [])
        self.index_fields = kwargs.get("index_fields", [])

        self.create_source_method = self.kwargs.get(
            "create_source_method", CREATE_SOURCE_BY_QUERY)
        self.update_source_method = self.kwargs.get(
            "update_source_method", UPDATE_SOURCE_BY_BUILD_UPSERT_QUERY)
        self.batch_size = kwargs.get("batch_size", BATCH_SIZE_DATA_SEGMENT)
        self.clear_old_data = self.kwargs.get("clear_old_data", False)
        self.last_run_synced = self.get_last_run_synced()
        self.last_rows_synced = self.get_last_rows_synced()

        self.__total_rows_synced = 0

    @property
    def total_rows_synced(self):
        return self.__total_rows_synced

    @property
    def time_starting(self):
        return self.time_now

    @property
    def filter_by_last_run(self):
        try:
            return self.kwargs["filter_by_last_run"]
        except Exception as ex:
            logger.debug(f"{self.log_format}[filter_by_last_run] {ex}")
            return False

    def get_last_rows_synced(self):
        try:
            return self.kwargs["last_rows_synced"]
        except Exception as ex:
            logger.debug(f"{self.log_format}[get_last_rows_synced] {ex}")
            return 0

    def get_last_run_synced(self):
        try:
            assert self.filter_by_last_run is True, "last_run_synced is only available when filter_by_last_run is True"
            return self.kwargs["last_run_synced"]
        except Exception as ex:
            logger.debug(f"{self.log_format}[get_last_run_synced] {ex}")
            return None

    def get_modified_filter(self, total):
        modified_filter = None
        try:
            assert self.filter_by_last_run is True, "last_run_synced is only available when filter_by_last_run is True"
            is_same_date = self.last_run_synced is not None and self.last_run_synced.date(
            ) == self.time_now.date()
            if is_same_date and total >= self.last_rows_synced:
                ds_tz_pytz = pytz.timezone(settings.DS_TZ_CALCULATE)
                modified_filter = self.last_run_synced.astimezone(
                    ds_tz_pytz).strftime("%Y-%m-%d %H:%M:%S")
        except Exception as ex:
            logger.debug(f"{self.log_format}[get_last_run_synced] {ex}")
        return modified_filter

    @property
    def log_format(self):
        return f"[{self.__class__.__name__}][{self.client_id}][{self._flatten_name}][{self.source}][{self.time_now}]"

    def get_is_resync_data_source(self):
        try:
            val = self.kwargs.pop("resync_data_source")
        except Exception as ex:
            logger.debug(f"{self.log_format}[get_is_resync_data_source] {ex}")
            val = False
        return val

    def do_flatten(self):
        """
        Create a table or insert rows from a query. Script:
        1. Check flatten table exists
        2. Create a table or insert rows into an existing table from query
        3. Revert a dirty flag (check created time for excluding cases of new rows which are doing inserting
         at the same time and in the same process)
        """
        logger.info(f"{self.log_format}[do_flatten] Beginning ...")
        if not self.source_exist:
            # Create a flattened table from a query
            self.create_table()
        # Insert rows from query to existing flatten table
        self.sync_to_table()

    def create_table(self):
        if self.source == FLATTEN_PG_SOURCE:
            self.create_pg_source()
        elif self.source == FLATTEN_ES_SOURCE:
            self.create_es_source()
        else:
            raise NotImplementedError
        self.source_exist = True

    def create_pg_source(self):
        logger.info(
            f"{self.log_format}[create_pg_source][{self.create_source_method}] Beginning ...")
        if self.create_source_method == CREATE_SOURCE_BY_QUERY:
            from_query = self._sql_generator.build_flat_query(
                client_id=self.client_id)
            from_query = from_query.replace(';', '')
            sql = f"""
                CREATE TABLE {self._flatten_name} AS
                ({from_query});
            """
        elif self.create_source_method == CREATE_SOURCE_BY_SCHEMA:
            sql = self._sql_generator.build_flat_query_schema_table(client_id=self.client_id,
                                                                    table_name=self._flatten_name)
        else:
            sql = None
        assert sql is not None, f"SQL is not None"
        #
        with connections[self.client_db].cursor() as cursor:
            try:
                logger.debug(
                    f"{self.log_format}[create_pg_source][{self.create_source_method}] SQL: {sql}"
                )

                start_time = time.time()

                cursor.execute(sql)

                # update unique index
                sql_unique_index = self._sql_generator.build_query_unique_index_flatten(self._flatten_name,
                                                                                        self.unique_fields)
                cursor.execute(sql_unique_index)

                # update indexes
                sql_indexes = self._sql_generator.build_query_indexes_flatten(
                    self._flatten_name, self.index_fields)
                if len(sql_indexes) > 0:
                    cursor.execute(sql_indexes)

                end_time = time.time()
                time_exec = end_time - start_time
                logger.info(
                    f"{self.log_format}[create_pg_source][{self.create_source_method}] "
                    f"Time execution query: {time_exec}"
                )

            except Exception or DatabaseError as err:
                logger.error(
                    f"{self.log_format}[create_pg_source][{self.create_source_method}] Error {err}"
                )
                cursor.execute("ROLLBACK")
                raise SqlExecutionException(
                    f"{self.log_format}[create_pg_source][{self.create_source_method}] "
                    f"SQL execution create table flatten error"
                )

    def create_es_source(self):
        logger.info(
            f"{self.log_format}[create_es_source][{self.create_source_method}] Beginning ...")
        #
        if not self.es_service.exist_index:
            self.es_service.create_index()
        #
        if self.create_source_method == CREATE_SOURCE_BY_QUERY:
            es_key_id = self.kwargs.get("es_key_id", "id")
            sql = self._sql_generator.build_flat_query(
                client_id=self.client_id)
            with connections[self.client_db].cursor() as cursor:
                try:
                    sql = sql.replace(";", "")
                    sql_count = f"""SELECT COUNT(*) FROM ({sql}) as table_count"""
                    cursor.execute(sql_count)
                    res = cursor.fetchone()
                    total_count = res[0]
                except Exception or DatabaseError as err:
                    logger.error(
                        f"{self.log_format}[create_es_source][{self.create_source_method}] {err}")
                    return
            bulk_size = self.kwargs.get("bulk_size") or ES_BULK_SIZE
            total_pages = math.ceil(total_count / bulk_size)
            data = []
            i = 0
            while True:
                if i == total_pages:
                    if data:
                        register_list(SYNC_DATA_SOURCE_CATEGORY, data)
                    break
                page = i + 1
                offset = i * bulk_size
                _sql_offset = self._sql_generator.build_flat_query(client_id=self.client_id, limit=bulk_size,
                                                                   offset=offset)
                data.append(
                    dict(
                        client_id=self.client_id,
                        name=f"es_sync_{self.type_flatten.lower()}_page_{page}_offset_{offset}",
                        job_name="app.es.jobs.bulk_size.handler_bulk_size_flatten_source",
                        module="app.es.jobs.bulk_size",
                        method="handler_bulk_size_flatten_source",
                        time_limit=7200,
                        meta=dict(
                            sql=_sql_offset, client_id=self.client_id, type_flatten=self.type_flatten,
                            action=ES_UPSERT_ACTION, key_id=es_key_id, es_bulk_size=bulk_size,
                            properties_settings=self._sql_generator.build_properties_mapping_source(
                                FLATTEN_ES_SOURCE)
                        )
                    )
                )
                if len(data) % 100 == 0:
                    register_list(SYNC_DATA_SOURCE_CATEGORY, data)
                    data = []
                i += 1

    def update_flatten_table_dirty(self, model_class: Union[SaleItem, SaleItemFinancial]):
        cond = Q(client_id=self.client_id, modified__lte=self.time_now)
        if self.is_resync_data_source:
            cond &= Q(dirty=False, resync=True)
        else:
            cond &= Q(dirty=True)

        query_set = model_class.all_objects.tenant_db_for(
            self.client_id).filter(cond)

        success = total_records_synced = query_set.count()
        failed_ids = []

        if not bool(total_records_synced):
            logger.info(
                f"{self.log_format}[update_flatten_table_dirty] Not found records to sync"
            )
            return success, failed_ids

        logger.info(
            f"{self.log_format}[update_flatten_table_dirty] "
            f"Total number records sync to flatten = {total_records_synced}"
        )
        page = 1

        while True:
            if not query_set.exists():
                break

            objs = list(query_set.order_by('created')[:self.batch_size])

            obj_ids_updated = set()

            obj_ids_deleted = set()

            logger.info(
                f"{self.log_format}[update_flatten_table_dirty][{page}] "
                f"Syncing {len(objs)} items ..."
            )

            for obj in objs:
                index = str(obj.id)

                if obj.is_removed:
                    obj_ids_deleted.add(index)
                else:
                    obj_ids_updated.add(index)

                # obj.dirty = False

            if len(obj_ids_deleted) > 0:
                _, ids_delete_errors = self.delete_flatten_table(
                    list(obj_ids_deleted))
                if ids_delete_errors:
                    logger.error(
                        f"{self.log_format}[update_flatten_table_dirty][{page}] "
                        f"Sync delete errors {ids_delete_errors}"
                    )
                    obj_ids_deleted = obj_ids_deleted - set(ids_delete_errors)

            if len(obj_ids_updated) > 0:
                _, ids_upsert_errors = self.update_flatten_table(
                    list(obj_ids_updated))
                if ids_upsert_errors:
                    logger.error(
                        f"{self.log_format}[update_flatten_table_dirty][{page}] "
                        f"Sync upsert errors {ids_upsert_errors}"
                    )
                    obj_ids_updated = obj_ids_updated - set(ids_upsert_errors)

            # model_class.all_objects.tenant_db_for(self.client_id).bulk_update(objs, fields=["dirty"])
            obj_ids = list(obj_ids_updated) + list(obj_ids_deleted)
            logger.info(
                f"{self.log_format}[update_flatten_table_dirty][{page}] "
                f"Sync completed {len(obj_ids)} items"
            )
            if obj_ids:
                self.revert_dirty(obj_ids, self.time_now.isoformat())
                page += 1
        return success, failed_ids

    def get_model_class(self, key):
        args = {
            FLATTEN_SALE_ITEM_KEY: SaleItem,
            FLATTEN_SALE_ITEM_FINANCIAL_KEY: SaleItemFinancial
        }
        return args.get(key, None)

    def sync_to_table(self):
        if self.type_flatten in DATA_FLATTEN_TYPE_ANALYSIS_LIST:
            model_class = self.get_model_class(self.type_flatten)
            success, failed_ids = self.update_flatten_table_dirty(model_class)
        else:
            success, failed_ids = self.update_flatten_table()
        self.__total_rows_synced = success

    def update_flatten_table(self, data: List[str] = None):
        """
        Updates the flattened table for either Elasticsearch or PostgresSQL depending on the 'target' parameter.
        :param data: Input data or config used to build SQL.
        """
        logger.info(
            f"{self.log_format}[update_flatten_table][{self.update_source_method}][{self.source}] "
            f"Beginning..."
        )
        es_key_id = self.kwargs.get("es_key_id", "id")
        success, failed_ids = 0, []
        join_fields = ",".join(map(str, self.unique_fields))
        is_clear_old_docs = self.source_exist and self.clear_old_data

        def clear_old_docs():
            if is_clear_old_docs:
                if self.source == FLATTEN_ES_SOURCE:
                    self.es_service.delete_old_docs(self.time_now.isoformat())
                else:
                    self.delete_old_docs()

        def process_update_data_to_es(sql_query_or_data: Union[str, List[Dict]]):
            logger.debug(
                f"{self.log_format}[update_flatten_table][{FLATTEN_ES_SOURCE}][{self.update_source_method}] "
                f"SQL: {sql_query_or_data}"
            )
            if not sql_query_or_data:
                return 0, []
            self.es_service.on_validate()
            _success, _failed_ids = self.es_service.on_process(
                data=sql_query_or_data, action=ES_UPSERT_ACTION, key_id=es_key_id
            )
            self.es_service.on_complete()
            return _success, _failed_ids

        def process_update_data_to_pg(sql_query: str):
            with connections[self.client_db].cursor() as cursor:
                try:
                    logger.debug(
                        f"{self.log_format}[update_flatten_table][{FLATTEN_PG_SOURCE}][{self.update_source_method}] "
                        f"SQL: {sql_query}"
                    )
                    start_time = time.time()
                    cursor.execute(sql_query)
                    _success, _failed_ids = cursor.rowcount, []
                    execution_time = time.time() - start_time
                    logger.info(
                        f"{self.log_format}[update_flatten_table][{FLATTEN_PG_SOURCE}] "
                        f"Query executed in {execution_time:.2f}s, affected rows: {_success}"
                    )
                    return _success, _failed_ids
                except Exception as ex:
                    if isinstance(ex, DatabaseError):
                        from app.job.utils.helper import register_list
                        jobs = [
                            dict(
                                client_id=self.client_id,
                                name="update_flatten_table_recover",
                                job_name="app.financial.jobs.schema_datasource.handler_sync_scheme_data_source",
                                module="app.financial.jobs.schema_datasource",
                                method="handler_sync_scheme_data_source",
                                meta=dict(client_id=str(self.client_id),
                                          type_flatten=self.type_flatten)
                            )
                        ]
                        register_list(COMMUNITY_CATEGORY, jobs,
                                      mode_run=MODE_RUN_IMMEDIATELY)
                    logger.error(
                        f"{self.log_format}[update_flatten_table][{FLATTEN_PG_SOURCE}] Database error: {ex}")
                    cursor.execute("ROLLBACK")
                    raise SqlExecutionException(
                        f"{self.log_format}[update_flatten_table][{FLATTEN_PG_SOURCE}] SQL execution error"
                    )

        # Choose processing function based on target
        processor = process_update_data_to_es if self.source == FLATTEN_ES_SOURCE else process_update_data_to_pg

        if self.update_source_method == UPDATE_SOURCE_BY_BUILD_UPSERT_QUERY:
            base_sql = (self._sql_generator.build_flat_query(client_id=self.client_id, ids=data, **self.kwargs)
                        .replace(";", ""))
            if self.source == FLATTEN_PG_SOURCE:
                set_statement = self._sql_generator.build_sql_do_update_set_by_conflict()
                sql = f"""
                        INSERT INTO {self._flatten_name} ({base_sql})
                        ON CONFLICT ({join_fields})
                        DO UPDATE SET {set_statement};
                    """
            else:
                sql = base_sql

            success, failed_ids = processor(sql)
        elif self.update_source_method == UPDATE_SOURCE_BY_BUILD_INSERT_QUERY:
            total_records = self.number_sync_rows()
            modified_filter = self.get_modified_filter(total_records)
            if modified_filter:
                is_clear_old_docs = False
            sql = self._sql_generator.build_flat_query_insert_table(
                client_id=self.client_id, table_name=self._flatten_name, index_fields=join_fields,
                source_type=self.source, modified_filter=modified_filter
            )
            success, failed_ids = processor(sql)
        elif self.update_source_method == UPDATE_SOURCE_BY_SEGMENT_INSERT_QUERY:
            total_success = total_records = self.number_sync_rows()

            if total_records == 0:
                logger.info(
                    f"{self.log_format}[update_flatten_table][{self.update_source_method}][{self.source}] "
                    f"Data not found, skip processing"
                )
                return success, failed_ids

            modified_filter = self.get_modified_filter(total_records)
            if modified_filter:
                total_records = self.number_sync_rows(
                    modified_filter=modified_filter)
                is_clear_old_docs = False

            total_pages = math.ceil(total_records / self.batch_size)

            logger.info(
                f"{self.log_format}[update_flatten_table][{self.update_source_method}][{self.source}] "
                f"Total Records = {total_records}, Total Pages = {total_pages}, Batch Size = {self.batch_size}, "
                f"Filter By Last Run = {self.filter_by_last_run}, Modified Filter = {modified_filter}"
            )

            for page_num in range(1, total_pages + 1):
                logger.info(
                    f"{self.log_format}[update_flatten_table][{self.update_source_method}][{self.source}] "
                    f"Processing page {page_num}"
                )
                sql = self._sql_generator.build_flat_query_insert_segment_table(
                    client_id=self.client_id, table_name=self._flatten_name, index_fields=join_fields,
                    total=total_records, page=page_num, size=self.batch_size, source_type=self.source,
                    modified_filter=modified_filter
                )
                logger.debug(
                    f"{self.log_format}[update_flatten_table][{self.update_source_method}][{self.source}] SQL: {sql}"
                )
                processor(sql)
            success = total_success
        else:
            raise NotImplementedError

        clear_old_docs()
        return success, failed_ids

    def delete_flatten_table(self, ids):
        logger.info(
            f"{self.log_format}[delete_flatten_table] Beginning..."
        )
        success = 0
        failed_ids = []
        if self.source == FLATTEN_PG_SOURCE:
            with connections[self.client_db].cursor() as cursor:
                ids = tuple(ids) if len(
                    ids) > 1 else """('{}')""".format(ids[0])
                sql = """
                DELETE FROM {} WHERE {}.sale_item_id in {};
                """.format(self._flatten_name,
                           self._flatten_name,
                           ids)
                logger.debug(
                    f"{self.log_format}[delete_flatten_table] SQL: {sql}"
                )
                try:
                    cursor.execute(sql)
                    success = len(ids)
                except Exception or DatabaseError as err:
                    logger.error(
                        f"{self.log_format}[delete_flatten_table] Error {err}"
                    )
                    cursor.execute("ROLLBACK")
                    raise SqlExecutionException(
                        f"{self.log_format}[delete_flatten_table] "
                        f"SQL execution delete items to table flatten error"
                    )
        elif self.source == FLATTEN_ES_SOURCE:
            ids = tuple(ids) if len(ids) > 1 else """('{}')""".format(ids[0])
            model_class = self.get_model_class(self.type_flatten)
            model_class.all_objects.tenant_db_for(self.client_id)
            db_table = model_class._meta.db_table
            if type(model_class) == type(SaleItem):
                column_filter = 'id'
            else:
                column_filter = 'sale_item_id'
            sql = f"""
            SELECT * FROM {db_table} WHERE {db_table}.{column_filter} in {ids} ORDER BY {db_table}.created ASC;
            """
            self.es_service.on_validate()
            success, failed_ids = self.es_service.on_process(
                data=sql, action="delete", key_id="id")
            self.es_service.on_complete()
        else:
            pass
        return success, failed_ids

    def is_flatten_exists(self) -> bool:
        logger.info(
            f"{self.log_format}[flatten_exists] Beginning..."
        )
        if self.source == FLATTEN_PG_SOURCE:
            with connections[self.client_db].cursor() as cursor:
                sql = self._sql_generator.build_sql_to_check_flatten_exists(
                    self.get_flatten_name)
                logger.debug(
                    f"{self.log_format}[flatten_exists] SQL: {sql}"
                )
                try:
                    cursor.execute(sql)
                    rs = cursor.fetchone()
                    return rs[0]
                except Exception or DatabaseError as err:
                    logger.error(
                        f"{self.log_format}[flatten_exists] Error {err}"
                    )
                    raise SqlExecutionException(
                        f"{self.log_format}[flatten_exists] "
                        f"SQL execution check flatten exists error"
                    )
        elif self.source == FLATTEN_ES_SOURCE:
            return self.es_service.exist_index
        else:
            raise NotImplementedError

    def drop_flatten_exists(self):
        logger.info(
            f"{self.log_format}[drop_flatten_exists] Beginning..."
        )
        if self.source == FLATTEN_PG_SOURCE:
            with connections[self.client_db].cursor() as cursor:
                sql = self._sql_generator.build_sql_to_drop_flatten(
                    self.get_flatten_name)
                logger.debug(
                    f"{self.log_format}[drop_flatten_exists] SQL: {sql}"
                )
                try:
                    cursor.execute(sql)
                except Exception or DatabaseError as err:
                    logger.error(
                        f"{self.log_format}[drop_flatten_exists] "
                        f"SQL execution drop flatten error {err}"
                    )
                    cursor.execute("ROLLBACK")
                    raise SqlExecutionException(
                        f"{self.log_format}[drop_flatten_exists] "
                        f"SQL execution drop flatten error"
                    )
        elif self.source == FLATTEN_ES_SOURCE:
            return self.es_service.drop_index()
        else:
            raise NotImplementedError
        self.source_exist = False

    def number_flatten_rows(self):
        """
        Count number row of table flatten
        :return:
        """
        with connections[self.client_db].cursor() as cursor:
            sql = self._sql_generator.build_query_for_number_flatten_rows(
                self.get_flatten_name)
            logger.debug(
                f"{self.log_format}[number_flatten_rows] SQL: {sql}"
            )
            try:
                cursor.execute(sql)
                res = cursor.fetchone()
                count = res[0]
                return count
            except Exception or DatabaseError as err:
                logger.error(
                    f"{self.log_format}[number_flatten_rows] Error {err}"
                )
                raise SqlExecutionException(
                    f"{self.log_format}[number_flatten_rows] "
                    f"SQL execution get number rows table flatten error"
                )

    def number_sync_rows(self, modified_filter: str = None) -> int:
        """
        count the number of new rows which should be flatted
        """
        sql = self._sql_generator.build_query_for_number_sync_rows(
            self.client_id, is_resync=self.is_resync_data_source, modified_filter=modified_filter)
        logger.debug(
            f"{self.log_format}[number_sync_rows] SQL: {sql}"
        )
        with connections[self.client_db].cursor() as cursor:
            try:
                cursor.execute(sql)
                res = cursor.fetchone()
                count = res[0]
                return count
            except Exception or DatabaseError as err:
                logger.error(
                    f"{self.log_format}[number_sync_rows] Error {err}"
                )
                raise SqlExecutionException(
                    f"{self.log_format}[number_sync_rows] "
                    f"SQL execution count dirty rows error"
                )

    def revert_dirty(self, ids: list = [], modified_at: str = None):
        """
        Reverts dirty records in the database for the given client and IDs with optional modified_at timestamp.

        :param ids: list of IDs to revert (default [])
        :param modified_at: timestamp for modified records (default None)
        """
        with connections[self.client_db].cursor() as cursor:
            sql = self._sql_generator.build_revert_dirty_query(client_id=self.client_id, ids=ids,
                                                               modified_at=modified_at,
                                                               is_resync=self.is_resync_data_source)
            logger.debug(
                f"{self.log_format}[revert_dirty] SQL: {sql}"
            )
            try:
                cursor.execute(sql)
            except Exception or DatabaseError as err:
                logger.error(
                    f"{self.log_format}[revert_dirty] Error {err}"
                )
                cursor.execute("ROLLBACK")
                raise SqlExecutionException(
                    f"{self.log_format}[revert_dirty] "
                    f"SQL execution revert dirty error"
                )

    def truncate_flatten_exists(self):
        with connections[self.client_db].cursor() as cursor:
            sql = self._sql_generator.build_query_truncate_flatten(
                self.get_flatten_name)
            logger.info(
                f"{self.log_format}[truncate_flatten_exists] Beginning ..."
            )
            logger.debug(
                f"{self.log_format}[truncate_flatten_exists] SQL: {sql}"
            )
            try:
                cursor.execute(sql)
            except Exception or DatabaseError as err:
                logger.error(
                    f"{self.log_format}[truncate_flatten_exists] Error {err}"
                )
                cursor.execute("ROLLBACK")
                raise SqlExecutionException(
                    f"{self.log_format}[truncate_flatten_exists] "
                    f"SQL execution truncate flatten error"
                )

    def delete_old_docs(self):
        with connections[self.client_db].cursor() as cursor:
            sql = self._sql_generator.build_query_delete_old_docs(
                self.get_flatten_name, self.time_now.isoformat())
            logger.info(
                f"{self.log_format}[delete_old_docs] Beginning ..."
            )
            logger.debug(
                f"{self.log_format}[delete_old_docs] SQL: {sql}"
            )
            try:
                cursor.execute(sql)
            except Exception or DatabaseError as err:
                logger.error(
                    f"{self.log_format}[delete_old_docs] Error {err}"
                )
                cursor.execute("ROLLBACK")
                raise SqlExecutionException(
                    f"{self.log_format}[delete_old_docs] "
                    f"SQL execution truncate flatten error"
                )

    @property
    def get_flatten_name(self) -> str:
        return self._flatten_name
