import hashlib
import itertools
import logging
import time
from django.db import connections, DatabaseError
from app.core.exceptions import SqlExecutionException
from app.database.helper import get_connection_workspace
from app.database.variable.objects_manage import DB_TABLE_RELATION_FIELDS, DB_TABLE_RELATION_FIELDS_CONFIGS, \
    DB_TABLE_MANAGED

logger = logging.getLogger(__name__)


class DBTableModelManage:
    def __init__(self, client_id: str, tbl_model_service: any, **kwargs):
        self.client_id = client_id
        self.client_db = get_connection_workspace(self.client_id)
        self.kwargs = kwargs
        self.tbl_model_service = tbl_model_service(client_id=self.client_id)
        self.client_id_tbl = self.client_id.replace('-', '_')
        self.hash_client_id = hashlib.sha1(
            self.client_id_tbl.encode("UTF-8")).hexdigest()[:8]

    @property
    def is_new_table(self):
        return self.kwargs.get('new_table', False)

    @property
    def is_sync_col(self):
        return self.kwargs.get('sync_column', False)

    def exists_db_table(self) -> bool:
        # check table exist
        with connections[self.client_db].cursor() as cursor:
            sql = f"""
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables
                                WHERE  table_schema = 'public'
                        AND  table_name = '{self.tbl_model_service.table_name}');
                    """
            try:
                # main
                cursor.execute(sql)
                rs = cursor.fetchone()
                #
                return rs[0]
            except Exception or DatabaseError as err:
                logger.error(
                    f'[{self.__class__.__name__}][{self.client_id}] {err}')
            finally:
                pass
            return False

    def __get_schema_columns_table(self, table):
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

    def compare_schema_table(self):
        db_table_default_columns = self.__get_schema_columns_table(
            self.tbl_model_service.db_table_default)
        db_table_template_columns = self.__get_schema_columns_table(
            self.tbl_model_service.table_name)
        new_columns = [
            item for item in db_table_default_columns if item not in db_table_template_columns]
        return new_columns

    def __get_schema_indexes_table(self, table):
        sql = f"""
                select i.relname as index_name,
                       a.attname as column_name
                from pg_class t,
                     pg_class i,
                     pg_index ix,
                     pg_attribute a
                where t.oid = ix.indrelid
                  and i.oid = ix.indexrelid
                  and a.attrelid = t.oid
                  and a.attnum = ANY (ix.indkey)
                  and t.relkind = 'r'
                  and t.relname = '{table}'
                  and ix.indisunique is false
                order by t.relname,
                         i.relname;
        """
        constraints_info = {}
        #
        constraint_total_columns = []
        with connections[self.client_db].cursor() as cursor:
            try:
                constraint_columns = []
                cursor.execute(sql)
                columns = [col[0] for col in cursor.description]
                for row in cursor.fetchall():
                    item = dict(zip(columns, row))
                    constraint_columns.append(item)
                for g_key, g_values in itertools.groupby(constraint_columns, lambda x: x['index_name']):
                    constraints_info.update(
                        {g_key: [str(item["column_name"]) for item in g_values]})
                    #
                    constraint_total_columns += constraints_info[g_key]
            except Exception or DatabaseError as err:
                logger.error(err)
            #
            return constraints_info, list(set(constraint_total_columns))

    def migrate_sql_schema_indexes_key_column(self):
        indexes_root, indexes_root_columns = self.__get_schema_indexes_table(
            self.tbl_model_service.db_table_default)
        indexes_tbl, indexes_tbl_columns = self.__get_schema_indexes_table(
            self.tbl_model_service.table_name)
        sql = f""""""
        if not set(indexes_root_columns).symmetric_difference(set(indexes_tbl_columns)):
            return sql
        try:
            for k in indexes_tbl.keys():
                sql += f"""DROP INDEX {k};"""
            for k, v in indexes_root.items():
                hash_columns = hashlib.sha256(
                    '_'.join(v).encode("UTF-8")).hexdigest()[:8]
                unique_index_name = f"{self.tbl_model_service.db_table_default}__{hash_columns}__{self.hash_client_id}_idx"
                sql += f"""
                    CREATE INDEX IF NOT EXISTS {unique_index_name} ON {self.tbl_model_service.table_name} ({','.join(v)});"""
        except Exception or DatabaseError as err:
            sql = f""""""
            logger.error(
                f'[{self.__class__.__name__}][{self.client_id}][get_sql_schema_column] {err}')
        return sql

    def __get_schema_unique_table(self, table):
        sql = f"""
                SELECT tc.constraint_name, c.column_name
                FROM information_schema.table_constraints tc
                JOIN information_schema.constraint_column_usage AS ccu USING (constraint_schema, constraint_name)
                JOIN information_schema.columns AS c ON c.table_schema = tc.constraint_schema
                  AND tc.table_name = c.table_name AND ccu.column_name = c.column_name
                WHERE constraint_type = 'UNIQUE' and tc.table_name = '{table}';
                    """
        constraints_info = {}
        #
        constraint_total_columns = []
        with connections[self.client_db].cursor() as cursor:
            try:
                constraint_columns = []
                cursor.execute(sql)
                columns = [col[0] for col in cursor.description]
                for row in cursor.fetchall():
                    item = dict(zip(columns, row))
                    constraint_columns.append(item)
                for g_key, g_values in itertools.groupby(constraint_columns, lambda x: x['constraint_name']):
                    constraints_info.update(
                        {g_key: [str(item["column_name"]) for item in g_values]})
                    #
                    constraint_total_columns += constraints_info[g_key]
            except Exception or DatabaseError as err:
                logger.error(err)
            #
            return constraints_info, list(set(constraint_total_columns))

    def migrate_sql_schema_foreign_key_column(self):
        cons_root, cons_root_columns = self.__get_schema_unique_table(
            self.tbl_model_service.db_table_default)
        cons_tbl, cons_tbl_columns = self.__get_schema_unique_table(
            self.tbl_model_service.table_name)
        sql = f""""""
        if not set(cons_root_columns).symmetric_difference(set(cons_tbl_columns)):
            return sql
        try:
            for k in cons_tbl.keys():
                sql += f"""ALTER TABLE {self.tbl_model_service.table_name} DROP CONSTRAINT {k};"""
            for k, v in cons_root.items():
                hash_columns = hashlib.sha256(
                    '_'.join(v).encode("UTF-8")).hexdigest()[:8]
                sql += f"""
                    ALTER TABLE {self.tbl_model_service.table_name}
                        ADD CONSTRAINT {self.tbl_model_service.db_table_default}__{hash_columns}__{self.hash_client_id}_uniq
                        UNIQUE ({','.join(v)});"""
        except Exception or DatabaseError as err:
            sql = f""""""
            logger.error(
                f'[{self.__class__.__name__}][{self.client_id}][get_sql_schema_column] {err}')
        return sql

    def __get_schema_constraints_table(self, table: str):
        sql = f"""
                SELECT
                    kcu.column_name
                FROM
                    information_schema.table_constraints AS tc
                    JOIN information_schema.key_column_usage AS kcu
                      ON tc.constraint_name = kcu.constraint_name
                      AND tc.table_schema = kcu.table_schema
                    JOIN information_schema.constraint_column_usage AS ccu
                      ON ccu.constraint_name = tc.constraint_name
                      AND ccu.table_schema = tc.table_schema
                WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_name='{table}';
            """
        columns = []
        with connections[self.client_db].cursor() as cursor:
            try:
                cursor.execute(sql)
                columns = [item[0] for item in cursor.fetchall()]
            except Exception or DatabaseError as err:
                logger.error(err)
            return columns

    def get_sql_schema_foreign_key_column(self, columns):
        columns = tuple(columns) if len(
            columns) > 1 else """('{}')""".format(columns[0])
        sql_find_schema = f"""
                SELECT
                    tc.table_schema,
                    tc.constraint_name,
                    tc.table_name,
                    kcu.column_name,
                    ccu.table_schema AS foreign_table_schema,
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name
                FROM
                    information_schema.table_constraints AS tc
                    JOIN information_schema.key_column_usage AS kcu
                      ON tc.constraint_name = kcu.constraint_name
                      AND tc.table_schema = kcu.table_schema
                    JOIN information_schema.constraint_column_usage AS ccu
                      ON ccu.constraint_name = tc.constraint_name
                      AND ccu.table_schema = tc.table_schema
                WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_name='{self.tbl_model_service.db_table_default}' 
                      AND kcu.column_name IN {columns};
            """
        sql = f""""""
        with connections[self.client_db].cursor() as cursor:
            try:
                cursor.execute(sql_find_schema)
                columns = [col[0] for col in cursor.description]
                for row in cursor.fetchall():
                    item = dict(zip(columns, row))
                    column_name = item['column_name']
                    if column_name in DB_TABLE_RELATION_FIELDS:
                        references_table = DB_TABLE_RELATION_FIELDS_CONFIGS[column_name][DB_TABLE_MANAGED][
                            False].format(client_id_tbl=self.client_id_tbl)
                    else:
                        references_table = item['foreign_column_name']
                    sql += f"""
                        ALTER TABLE {self.tbl_model_service.table_name}
                        ADD CONSTRAINT {self.tbl_model_service.db_table_default}_{column_name}_{self.hash_client_id}_fk_financial_{column_name}
                        FOREIGN KEY({column_name})
                        REFERENCES {references_table} DEFERRABLE INITIALLY DEFERRED;
                    """
            except Exception or DatabaseError as err:
                sql = f""""""
                logger.error(
                    f'[{self.__class__.__name__}][{self.client_id}][get_sql_schema_column] {err}')
        return sql

    def get_sql_schema_column(self, columns):
        # get foreign key columns
        foreign_tbl_default = self.__get_schema_constraints_table(
            self.tbl_model_service.db_table_default)
        #
        columns = tuple(columns) if len(
            columns) > 1 else """('{}')""".format(columns[0])
        sql_find_schema = f"""
            SELECT 
                column_name, 
                data_type, 
                character_maximum_length, 
                numeric_precision, 
                numeric_scale, 
                column_default, 
                is_nullable,
                udt_name
            FROM 
                INFORMATION_SCHEMA.COLUMNS 
            WHERE 
                table_name = '{self.tbl_model_service.db_table_default}' and column_name IN {columns};
        """
        prefix_sql = f"""
            ALTER TABLE {self.tbl_model_service.table_name}
        """
        sql = """"""
        foreign_columns = []
        with connections[self.client_db].cursor() as cursor:
            try:
                cursor.execute(sql_find_schema)
                columns = [col[0] for col in cursor.description]
                for row in cursor.fetchall():
                    item = dict(zip(columns, row))
                    #
                    new = f"""ADD COLUMN {item["column_name"]} """
                    data_type = item["data_type"]
                    #
                    if data_type == "character varying":
                        data_type = "VARCHAR"
                    elif data_type == "ARRAY":
                        if item["udt_name"] == "_varchar":
                            max_length = item.get(
                                'character_maximum_length') or 100
                            data_type = f"VARCHAR({max_length})[]"
                        elif item["udt_name"] == "_int4":
                            data_type = "INT[]"
                        elif item["udt_name"] == "_int8":
                            data_type = "BIGINT[]"
                        elif item["udt_name"] == "_float8":
                            data_type = "DOUBLE PRECISION[]"
                        elif item["udt_name"] == "_text":
                            data_type = "TEXT[]"
                        elif item["udt_name"] == "_boolean":
                            data_type = "BOOLEAN[]"
                        elif item["udt_name"] == "_timestamp":
                            data_type = "TIMESTAMP[]"
                        else:
                            pass
                    else:
                        pass
                    new += f""" {data_type} """
                    #
                    if data_type == "VARCHAR" and item.get('character_maximum_length'):
                        new += f"""({item.get('character_maximum_length')})"""
                    elif data_type == "numeric" and item.get('numeric_precision', 6) and item.get('numeric_scale', 2):
                        new += f"""({item.get('numeric_precision')}, {item.get('numeric_scale')})"""
                    #
                    if not item.get('is_nullable'):
                        new += f"""NOT NULL"""
                    #
                    if item.get('column_default'):
                        new += f""" DEFAULT {item.get('column_default')}"""
                    sql += f"""{prefix_sql} {new}; """
                    #
                    if item["column_name"] in foreign_tbl_default:
                        foreign_columns.append(item['column_name'])
                if len(foreign_columns) > 0:
                    sql += self.get_sql_schema_foreign_key_column(
                        foreign_columns)
                sql += self.migrate_sql_schema_foreign_key_column()
                sql += self.migrate_sql_schema_indexes_key_column()
            except Exception or DatabaseError as err:
                sql = """"""
                logger.error(
                    f'[{self.__class__.__name__}][{self.client_id}][get_sql_schema_column] {err}')
            return sql

    def migrate_new_columns(self):
        try:
            new_columns = self.compare_schema_table()
            if len(new_columns) == 0:
                logger.info(
                    f'[{self.__class__.__name__}][{self.client_id}][migrate_new_columns] not founds new column changes')
                return
            logger.info(
                f'[{self.__class__.__name__}][{self.client_id}][migrate_new_columns] new columns find {new_columns}')
            sql_migrate_columns = self.get_sql_schema_column(new_columns)
            if not sql_migrate_columns:
                logger.error(
                    f'[{self.__class__.__name__}][{self.client_id}][migrate_new_columns] not founds sql migrate columns')
                return
            logger.info(
                f'[{self.__class__.__name__}][{self.client_id}][migrate_new_columns] sql_migrate_columns = {sql_migrate_columns}')
            with connections[self.client_db].cursor() as cursor:
                try:
                    cursor.execute(sql_migrate_columns)
                except Exception or DatabaseError as err:
                    logger.error(
                        f'[{self.__class__.__name__}][{self.client_id}][migrate_new_columns][cursor] {err}')
                    cursor.execute("ROLLBACK")
        except Exception as ex:
            logger.error(
                f'[{self.__class__.__name__}][{self.client_id}][migrate_new_columns] {ex}')

    def create_db_table(self):
        if self.exists_db_table():
            if not self.is_new_table:
                logger.info(
                    f'[{self.__class__.__name__}][{self.client_id}] tbl {self.tbl_model_service.table_name} exists')
                if self.is_sync_col:
                    logger.info(
                        f'[{self.__class__.__name__}][{self.client_id}] tbl {self.tbl_model_service.table_name} sync columns')
                    self.migrate_new_columns()
                return
            self.drop_db_table()
        #
        with connections[self.client_db].cursor() as cursor:
            sql = self.tbl_model_service.sql_schema_table
            try:
                start_time = time.time()

                # main
                cursor.execute(sql)

                end_time = time.time()
                time_exec = end_time - start_time
                logger.info(
                    '[create_db_table] Time exec query : {}'.format(time_exec))
            except Exception or DatabaseError as err:
                raise SqlExecutionException(f'[create_db_table] {err}')
            finally:
                pass

    def drop_db_table(self):
        with connections[self.client_db].cursor() as cursor:
            sql = f"""
            DROP TABLE {self.tbl_model_service.table_name} CASCADE;
            """
            try:
                start_time = time.time()

                # main
                cursor.execute(sql)

                end_time = time.time()
                time_exec = end_time - start_time
                logger.info(
                    '[drop_db_table] Time exec query : {}'.format(time_exec))
            except Exception or DatabaseError as err:
                cursor.execute("ROLLBACK")
                logger.error(
                    f'[{self.__class__.__name__}][{self.client_id}] {err}')
            finally:
                pass

    @property
    def model(self):
        return self.tbl_model_service.model
