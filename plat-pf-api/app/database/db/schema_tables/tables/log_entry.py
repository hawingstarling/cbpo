import hashlib
from app.database.helper import get_connection_workspace
from .base import TblModelBase
from ....variable.schema_tables.financial import DB_TABLE_LOG_ENTRY_DEFAULT, DB_TABLE_LOG_ENTRY_TEMPLATE
from django.contrib.contenttypes.models import ContentType


class LogEntryTblModel(TblModelBase):
    db_table_default = DB_TABLE_LOG_ENTRY_DEFAULT
    db_table_template = DB_TABLE_LOG_ENTRY_TEMPLATE

    @property
    def sql_schema_table(self):
        # TODO: find way get query create schema table from django model
        from app.financial.models import Sale, SaleItem
        content_type_sale_id = ContentType.objects.db_manager(
            using=get_connection_workspace(self.client_id)).get_for_model(Sale).pk
        content_type_sale_item_id = ContentType.objects.db_manager(
            using=get_connection_workspace(self.client_id)).get_for_model(SaleItem).pk
        hash_client_id = hashlib.sha1(self.client_id_db.encode("UTF-8")).hexdigest()[:8]
        sql = f"""
            CREATE TABLE {self.table_name}
            (
                id              serial
                    constraint {self.table_name}_pkey
                        primary key,
                object_pk       varchar(255)             not null,
                object_id       bigint,
                object_repr     text                     not null,
                action          smallint                 not null
                    constraint {DB_TABLE_LOG_ENTRY_DEFAULT}_{hash_client_id}_action_check
                        check (action >= 0),
                changes         text                     not null,
                timestamp       timestamp with time zone not null,
                actor_id        integer
                    constraint {DB_TABLE_LOG_ENTRY_DEFAULT}_actor_id_{hash_client_id}_fk_auth_user_id
                        references auth_user
                        deferrable initially deferred,
                content_type_id integer                  not null
                    constraint {DB_TABLE_LOG_ENTRY_DEFAULT}_content_type_id_{hash_client_id}_fk_django_co
                        references django_content_type
                        deferrable initially deferred,
                remote_addr     inet,
                additional_data jsonb
            );

            --- CONSTRAINTS
            ALTER TABLE {self.table_name}
                ADD CONSTRAINT {DB_TABLE_LOG_ENTRY_DEFAULT}_object_changes_{hash_client_id}_uniq
                UNIQUE (object_pk, action, changes, content_type_id);

            --- INDEXES
            CREATE INDEX {DB_TABLE_LOG_ENTRY_DEFAULT}_actor_id_{hash_client_id}
                ON {self.table_name} (actor_id);

            CREATE INDEX {DB_TABLE_LOG_ENTRY_DEFAULT}_content_type_id_{hash_client_id}
                ON {self.table_name} (content_type_id);

            CREATE INDEX {DB_TABLE_LOG_ENTRY_DEFAULT}_object_id_{hash_client_id}
                ON {self.table_name} (object_id);

            CREATE INDEX {DB_TABLE_LOG_ENTRY_DEFAULT}_object_pk_{hash_client_id}
                ON {self.table_name} (object_pk);

            CREATE INDEX {DB_TABLE_LOG_ENTRY_DEFAULT}_object_pk_{hash_client_id}_like
                ON {self.table_name} (object_pk varchar_pattern_ops);
            
            ---
            INSERT INTO {self.table_name} (
                    object_pk, 
                    object_id, 
                    object_repr, 
                    action, 
                    changes,
                    timestamp,
                    actor_id,
                    content_type_id,
                    remote_addr,
                    additional_data
                )
                SELECT 
                    object_pk, 
                    object_id, 
                    object_repr, 
                    action,
                    changes,
                    timestamp,
                    actor_id,
                    content_type_id,
                    remote_addr,
                    additional_data
                FROM {DB_TABLE_LOG_ENTRY_DEFAULT} 
                WHERE {DB_TABLE_LOG_ENTRY_DEFAULT}.content_type_id IN ({content_type_sale_id}, {content_type_sale_item_id}) 
                    AND {DB_TABLE_LOG_ENTRY_DEFAULT}.object_repr LIKE '%{self.client_id}%'
                ON CONFLICT ON CONSTRAINT {DB_TABLE_LOG_ENTRY_DEFAULT}_object_changes_{hash_client_id}_uniq 
                DO NOTHING;
        """
        return sql
