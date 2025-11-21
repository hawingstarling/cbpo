from .base import TblModelBase
from ....variable.schema_tables.financial import DB_TABLE_SKU_VAULT_PRIME_TRACK_TEMPLATE, \
    DB_TABLE_SKU_VAULT_PRIME_TRACK_DEFAULT


class SKUVaultPrimeTrackTblModel(TblModelBase):
    db_table_default = DB_TABLE_SKU_VAULT_PRIME_TRACK_DEFAULT
    db_table_template = DB_TABLE_SKU_VAULT_PRIME_TRACK_TEMPLATE

    @property
    def sql_schema_table(self):
        # TODO: find way get query create schema table from django model
        sql = f"""
            CREATE TABLE {self.table_name} AS
                SELECT * FROM {DB_TABLE_SKU_VAULT_PRIME_TRACK_DEFAULT} WHERE client_id = '{self.client_id}';
            --- CONSTRAINT
            ALTER TABLE {self.table_name}
                ADD CONSTRAINT {self.table_name}_pkey PRIMARY KEY (id);

            ALTER TABLE {self.table_name}
                ADD CONSTRAINT financial_skuvaultpr_channel_id_{self.hash_client_id}_fk_financial
                FOREIGN KEY(channel_id)
                REFERENCES financial_channel(id) DEFERRABLE INITIALLY DEFERRED;
                
            ALTER TABLE {self.table_name}
                ADD CONSTRAINT financial_skuvaultpr_client_id_{self.hash_client_id}_fk_financial
                FOREIGN KEY(client_id)
                REFERENCES financial_clientportal(id) DEFERRABLE INITIALLY DEFERRED;
                
            ALTER TABLE {self.table_name}
                ADD CONSTRAINT financial_skuvaultprimet_client_id_channel_id_cha_{self.hash_client_id}_uniq
                UNIQUE (client_id, channel_id, channel_sale_id);

            --- INDEXES
            CREATE INDEX financial_s_client__{self.hash_client_id}_ef5008_idx
                ON {self.table_name} (client_id, channel_id, channel_sale_id);
                
            CREATE INDEX financial_s_channel_{self.hash_client_id}_86bcda_idx
                ON {self.table_name} (channel_sale_id);
                
            CREATE INDEX {DB_TABLE_SKU_VAULT_PRIME_TRACK_DEFAULT}_channel_id_{self.hash_client_id}
                ON {self.table_name} (channel_id);
                
            CREATE INDEX {DB_TABLE_SKU_VAULT_PRIME_TRACK_DEFAULT}_client_id_{self.hash_client_id}
                ON {self.table_name} (client_id);
        
        """
        return sql
