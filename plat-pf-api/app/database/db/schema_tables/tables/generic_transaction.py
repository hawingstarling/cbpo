from .base import TblModelBase
from ....variable.schema_tables.financial import DB_TABLE_GENERIC_TRANSACTION_DEFAULT, \
    DB_TABLE_GENERIC_TRANSACTION_TEMPLATE


class GenericTransactionTblModel(TblModelBase):
    db_table_default = DB_TABLE_GENERIC_TRANSACTION_DEFAULT
    db_table_template = DB_TABLE_GENERIC_TRANSACTION_TEMPLATE

    @property
    def sql_schema_table(self):
        # TODO: find way get query create schema table from django model
        sql = f"""
            CREATE TABLE {self.table_name} AS
                SELECT * FROM {DB_TABLE_GENERIC_TRANSACTION_DEFAULT} WHERE client_id = '{self.client_id}';
            --- CONSTRAINT
            ALTER TABLE {self.table_name}
                ADD CONSTRAINT {self.table_name}_pkey PRIMARY KEY (id);
            
            ALTER TABLE {self.table_name}
                ADD CONSTRAINT financial_generictra_channel_id_{self.hash_client_id}_fk_financial
                FOREIGN KEY(channel_id)
                REFERENCES financial_channel(id) DEFERRABLE INITIALLY DEFERRED;

            ALTER TABLE {self.table_name}
                ADD CONSTRAINT financial_generictra_client_id_{self.hash_client_id}_fk_financial
                FOREIGN KEY(client_id)
                REFERENCES financial_clientportal(id) DEFERRABLE INITIALLY DEFERRED;

            ALTER TABLE {self.table_name}
                ADD CONSTRAINT financial_generictra_content_type_id_{self.hash_client_id}_fk_django_co
                FOREIGN KEY(content_type_id)
                REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED;

            ALTER TABLE {self.table_name}
                ADD CONSTRAINT financial_generictransac_client_id_content_type_i_{self.hash_client_id}_uniq
                UNIQUE (client_id, content_type_id, type, category, event, channel_sale_id, channel_id, sku, seq);

            --- INDEXES
            CREATE INDEX financial_g_channel_{self.hash_client_id}_idx
                ON {self.table_name} (channel_sale_id, content_type_id);

            CREATE INDEX financial_g_client__{self.hash_client_id}_idx
                ON {self.table_name} (client_id, channel_sale_id, channel_id, sku, content_type_id);

            CREATE INDEX financial_g_client__612b22_{self.hash_client_id}_idx
                ON {self.table_name} (client_id, channel_sale_id, channel_id, sku, content_type_id, type, category, event);

            CREATE INDEX {DB_TABLE_GENERIC_TRANSACTION_DEFAULT}_channel_id_{self.hash_client_id}
                ON {self.table_name} (channel_id);

            CREATE INDEX {DB_TABLE_GENERIC_TRANSACTION_DEFAULT}_client_id_{self.hash_client_id}
                ON {self.table_name} (client_id);

            CREATE INDEX {DB_TABLE_GENERIC_TRANSACTION_DEFAULT}_content_type_id_{self.hash_client_id}
                ON {self.table_name} (content_type_id);
                
            CREATE INDEX financial_g_client__8ef7de_{self.hash_client_id}_idx
                ON {self.table_name} (client_id, channel_id, content_type_id, dirty, date);
                
            CREATE INDEX financial_g_client__e8c4e8_{self.hash_client_id}_idx
                ON {self.table_name} (client_id, channel_id, content_type_id, dirty, modified);
            
        """
        return sql
