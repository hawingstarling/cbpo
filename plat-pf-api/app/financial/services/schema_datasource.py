import logging
from typing import Dict

from django.utils import timezone
from plat_import_lib_api.services.modules.serializer import SerializerHandle
from rest_framework.fields import FloatField, IntegerField, DecimalField, DateTimeField, BooleanField, \
    DateField

from app.core.services.ds_service import DSManager
from app.financial.models import DataFlattenTrack
from app.database.helper import get_connection_workspace
from app.financial.services.utils.source_config import data_source_generator_config
from django.db import connections, DatabaseError
from app.financial.services.data_flatten import DataFlatten
from app.financial.sub_serializers.client_sale_item_log import ClientSaleLogSerializer, SaleItemLogSerializer
from app.financial.variable.data_flatten_variable import DATA_FLATTEN_TYPE_ANALYSIS_LIST, FLATTEN_PG_SOURCE, \
    FLATTEN_ES_SOURCE
from app.financial.variable.job_status import SUCCESS, ERROR

logger = logging.getLogger(__name__)


class SyncSchemaDatasource:

    def __init__(self, client_id: str, **kwargs):
        self.client_id = str(client_id)
        self.client_db = get_connection_workspace(self.client_id)
        self.kwargs = kwargs
        self.type_flatten_request = self.get_type_flatten_demand()
        self.date_now = timezone.now()

    def get_type_flatten_demand(self):
        try:
            return self.kwargs.pop("type_flatten")
        except Exception as ex:
            logger.debug(f"[{self.__class__.__name__}][{self.client_id}][get_type_flatten_demand] {ex}")
        return None

    @property
    def is_new_source(self):
        return self.kwargs.get("is_new_source", False)

    def get_source(self, source: str):
        return self.kwargs.get("source", source)

    @property
    def datasource_config(self):
        if self.type_flatten_request and self.type_flatten_request in data_source_generator_config():
            ds_config = {self.type_flatten_request: data_source_generator_config()[self.type_flatten_request]}
        elif self.kwargs.get("recover_data_source"):
            source_types = (DataFlattenTrack.objects.tenant_db_for(self.client_id).filter(status=ERROR)
                            .values_list("type", flat=True))
            logger.info(
                f"[{self.__class__.__name__}][{self.client_id}][datasource_config] "
                f"Recover {len(source_types)} Data Sources"
            )
            ds_config = {
                source_type: data_source_generator_config()[source_type] for source_type in source_types
            }
        elif self.kwargs.get("resync_data_source"):
            ds_config = {
                source_type: data_source_generator_config()[source_type] for source_type in
                DATA_FLATTEN_TYPE_ANALYSIS_LIST
            }
        else:
            ds_config = data_source_generator_config()
        return ds_config

    @property
    def columns_analysis_schema(self):
        sale_schema = SerializerSchemaHandle(ClientSaleLogSerializer, {})
        columns_schema = sale_schema.columns
        sale_item_schema = SerializerSchemaHandle(SaleItemLogSerializer, {})
        columns_schema.update(sale_item_schema.columns)
        columns_schema.update({
            "sale_id": "bigint",
            "financial_id": "uuid",
            "sale_item_id": "uuid",
            "notes": "text",
            "profit": "numeric(10, 2)",
            "margin": "numeric(10, 2)"
        })
        return columns_schema

    def __get_schema_datasource(self, table):
        sql = f"""
                SELECT 
                    column_name
                FROM information_schema.columns
                WHERE 
                    table_schema = 'public' 
                    AND table_name  = '{table}';
            """
        columns = []
        with connections[self.client_db].cursor() as cursor:
            try:
                cursor.execute(sql)
                columns = [item[0] for item in cursor.fetchall()]
            except Exception or DatabaseError as err:
                logger.error(err)
            return columns

    def __init_data_flatten(self, client_id: str, type_flatten: str, config: Dict, source: str,
                            resync_data_source: bool = False, batch_size: int = 1000):
        return DataFlatten(client_id=client_id, type_flatten=type_flatten, **config, source=source,
                           resync_data_source=resync_data_source, batch_size=batch_size)

    def __is_sync(self, original, target):
        is_sync = False
        if len(original) != len(target):
            return is_sync
        is_sync = not any(not item in target for item in original)  # exist item origin not found target ds
        return is_sync

    def make_flatten_ready(self, type_flatten):
        DataFlattenTrack.objects.tenant_db_for(self.client_id).filter(type=type_flatten, client_id=self.client_id) \
            .update(status=SUCCESS, log=None)

    def process(self):
        for type_flatten, config in self.datasource_config.items():
            try:
                self.process_flatten(type_flatten, config)
            except Exception as ex:
                logger.error(f"[{self.__class__.__name__}][{self.client_id}][{type_flatten}][process] {ex}")

    def resync_data_source(self, data_flatten_track: DataFlattenTrack, config: Dict):
        type_flatten = data_flatten_track.type
        source = self.get_source(data_flatten_track.source)
        logger.info(
            f"[{self.__class__.__name__}][{self.client_id}][{type_flatten}][{source}]"
            f"[resync_data_source] Beginning ..."
        )
        data_flatten_service = self.__init_data_flatten(
            client_id=self.client_id,
            type_flatten=type_flatten,
            config=config,
            source=source,
            resync_data_source=True,
            batch_size=data_flatten_track.batch_size
        )
        if not data_flatten_service.number_sync_rows():
            logger.info(
                f"[{self.__class__.__name__}][{self.client_id}][{type_flatten}][{source}]"
                f"[resync_data_source] Not found data"
            )
            return
        data_flatten_service.sync_to_table()

    def reconfig_data_source(self, data_flatten_track: DataFlattenTrack, config: Dict):
        self.reconfig_data_source_es(data_flatten_track.data_source_es_id, data_flatten_track.type, config)
        self.reconfig_data_source_pg(data_flatten_track.data_source_id, data_flatten_track.type, config)

    def reconfig_data_source_es(self, data_source_id: str, type_flatten: str, config: Dict):
        try:
            assert data_source_id is not None, "data_source_id is not empty"
            logger.info(
                f"[{self.__class__.__name__}][{self.client_id}][{type_flatten}][{data_source_id}]"
                f"[reconfig_data_source_es] Beginning ..."
            )
            data_flatten_service = self.__init_data_flatten(
                client_id=self.client_id,
                type_flatten=type_flatten,
                config=config,
                source=FLATTEN_ES_SOURCE
            )
            data_flatten_service.es_service.sync_settings_index()
            data_flatten_service.es_service.sync_mappings_index()
            #
            ds_service = DSManager(client_id=self.client_id)
            rs = ds_service.clear_cache_ds(data_source_id)
            logger.info(f"[{self.__class__.__name__}] {rs}")
        except Exception as ex:
            logger.error(f"[{self.__class__.__name__}][{self.client_id}][{type_flatten}][reconfig_data_source_es] {ex}")

    def reconfig_data_source_pg(self, data_source_id: str, type_flatten: str, config: Dict):
        try:
            assert data_source_id is not None, "data_source_id is not empty"
            data_flatten_service = self.__init_data_flatten(
                client_id=self.client_id,
                type_flatten=type_flatten,
                config=config,
                source=FLATTEN_PG_SOURCE
            )
            flatten_exists = data_flatten_service.is_flatten_exists()

            origin_schema = config["sql_generator"].columns_update
            logger.debug(
                f"[{self.__class__.__name__}][{self.client_id}][{type_flatten}][{data_source_id}]"
                f"[reconfig_data_source_pg] Origin Schema: {origin_schema}"
            )
            target_schema = self.__get_schema_datasource(data_flatten_service.get_flatten_name)
            logger.debug(
                f"[{self.__class__.__name__}][{self.client_id}][{type_flatten}][{data_source_id}]"
                f"[reconfig_data_source_pg] Target Schema: {target_schema}"
            )
            assert flatten_exists is True and not self.__is_sync(origin_schema, target_schema), \
                f"Schema Doesn't Exist or Is synced"
            logger.info(
                f"[{self.__class__.__name__}][{self.client_id}][{type_flatten}][{data_source_id}]"
                f"[reconfig_data_source_pg] Beginning ..."
            )
            if type_flatten in DATA_FLATTEN_TYPE_ANALYSIS_LIST and data_flatten_service.is_flatten_exists():
                self.process_flatten_analysis(type_flatten, data_flatten_service, origin_schema, target_schema)
        except Exception as ex:
            logger.error(f"[{self.__class__.__name__}][{self.client_id}][{type_flatten}][reconfig_data_source_pg] {ex}")

    def process_flatten(self, type_flatten, config):
        data_flatten_track, _ = DataFlattenTrack.objects.tenant_db_for(self.client_id) \
            .get_or_create(type=type_flatten, client_id=self.client_id)

        if self.kwargs.get("reconfig_data_source"):
            self.reconfig_data_source(data_flatten_track, config)
            return
        if self.kwargs.get("resync_data_source"):
            self.resync_data_source(data_flatten_track, config)
            return

        self._process_flatten_source_config(data_flatten_track, config)

    def _process_flatten_source_config(self, data_flatten_track: DataFlattenTrack, config):
        type_flatten = data_flatten_track.type
        source = self.get_source(data_flatten_track.source)
        data_flatten_service = self.__init_data_flatten(
            client_id=self.client_id,
            type_flatten=type_flatten,
            config=config,
            source=source,
            batch_size=data_flatten_track.batch_size
        )
        flatten_exists = data_flatten_service.is_flatten_exists()
        if data_flatten_service.source == FLATTEN_PG_SOURCE:
            #
            origin_schema = config["sql_generator"].columns_update
            target_schema = self.__get_schema_datasource(data_flatten_service.get_flatten_name)
            logger.debug(
                f"Origin Schema: {origin_schema}, Target Schema: {target_schema} - "
                f"Is Sync : {self.__is_sync(origin_schema, target_schema)}"
            )
            if not self.is_new_source and flatten_exists:
                if self.__is_sync(origin_schema, target_schema):
                    self.make_flatten_ready(type_flatten)
                    return
                logger.info(
                    f"[{self.__class__.__name__}][{self.client_id}][{type_flatten}][{data_flatten_service.source}]"
                    f"[{source}][process] Sync Schema ..."
                )
                if type_flatten in DATA_FLATTEN_TYPE_ANALYSIS_LIST and data_flatten_service.is_flatten_exists():
                    if self.process_flatten_analysis(type_flatten, data_flatten_service, origin_schema, target_schema):
                        return
        # default action
        if self.is_new_source and flatten_exists:
            logger.info(
                f"[{self.__class__.__name__}][{self.client_id}][{type_flatten}][{data_flatten_service.source}]"
                f"[{source}][process] Drop table create new source"
            )
            data_flatten_service.drop_flatten_exists()
        # Generate ds
        logger.info(
            f"[{self.__class__.__name__}][{self.client_id}][{type_flatten}][{data_flatten_service.source}]"
            f"[{source}][process] Begin generating ..."
        )
        data_flatten_service.do_flatten()
        data_flatten_track.status = SUCCESS
        data_flatten_track.last_run = self.date_now
        data_flatten_track.last_rows_synced = data_flatten_service.total_rows_synced
        data_flatten_track.save()

    def process_flatten_analysis(self, type_flatten, data_flatten_service, origin_schema, target_schema):
        try:
            # because data source large by time so we add column missing to flatten instead of delete source then create new
            table_flatten = data_flatten_service.get_flatten_name
            flatten_columns = self.columns_analysis_schema
            #
            columns_remove = [item for item in target_schema if item not in origin_schema]
            columns_update = [item for item in origin_schema if item not in target_schema]

            # delete columns schema flatten
            if columns_remove:
                logger.info(
                    f"[{self.__class__.__name__}][process_flatten_analysis][{self.client_id}][{table_flatten}] "
                    f"Columns Remove: {columns_remove}"
                )
                sql_remove_columns = self.__remove_column_schema_datasource(table_flatten, columns_remove)
                self._run_sql_flatten(sql_remove_columns)

            # add columns schema flatten
            if columns_update:
                logger.info(
                    f"[{self.__class__.__name__}][process_flatten_analysis][{self.client_id}][{table_flatten}] "
                    f"Columns Update: {columns_update}"
                )
                sql_add_columns = self.__add_column_schema_datasource(table_flatten, columns_update, flatten_columns)
                self._run_sql_flatten(sql_add_columns)
            self.make_flatten_ready(type_flatten)
            return True
        except Exception as ex:
            logger.error(f"[{self.__class__.__name__}][{self.client_id}][{type_flatten}][process] {ex}")
            return False

    def __add_column_schema_datasource(self, table, columns, flatten_columns):
        try:
            # Build column definitions
            column_defs = []
            for column in columns:
                column_type = flatten_columns.get(column, "varchar(500)")
                column_defs.append(f"ADD COLUMN {column} {column_type}")
            # Join all definitions with commas
            sql_columns_define = ", ".join(column_defs)

            # Format the full SQL statement
            sql = f"""
                ALTER TABLE {table} 
                {sql_columns_define};
            """
        except Exception as ex:
            sql = ""
        return sql

    def __remove_column_schema_datasource(self, table, columns):
        try:
            # Build DROP COLUMN statements
            column_defs = [f"DROP COLUMN IF EXISTS {column}" for column in columns]

            # Join with commas
            sql_columns_define = ", ".join(column_defs)

            # Construct the full SQL statement
            sql = f"""
                ALTER TABLE {table}
                {sql_columns_define};
            """
        except Exception as ex:
            sql = ""
        return sql

    def _run_sql_flatten(self, sql: str = """"""):
        if not sql:
            return
        with connections[self.client_db].cursor() as cursor:
            try:
                logger.info(
                    f"[{self.__class__.__name__}][_run_sql_flatten][{self.client_id}] SQL: {sql}"
                )
                cursor.execute(sql)
            except Exception or DatabaseError as err:
                cursor.execute("ROLLBACK")
                logger.error(err)


class SerializerSchemaHandle(SerializerHandle):
    def get_column_config(self, name_detector: bool = False):
        rs = {}
        columns = self.serializer.get_fields()
        for field in columns:
            content_type = columns[field]
            field_type = self.get_field_type(content_type)
            rs.update({field: field_type})
        return rs

    @staticmethod
    def get_field_type(content_type):
        if isinstance(content_type, DecimalField) and isinstance(content_type, FloatField) or isinstance(content_type,
                                                                                                         DecimalField):
            return "numeric(10, 2)"
        elif isinstance(content_type, IntegerField):
            return "integer"
        elif isinstance(content_type, DateTimeField):
            return "timestamp with time zone"
        elif isinstance(content_type, DateField):
            return "date"
        # elif isinstance(content_type, BooleanField) or isinstance(content_type, NullBooleanField):
        #     return "boolean"
        elif isinstance(content_type, BooleanField):
            return "boolean"
        else:
            length = "500"
            try:
                length = content_type.max_length
            except Exception as ex:
                pass
            return f"varchar({length})"
