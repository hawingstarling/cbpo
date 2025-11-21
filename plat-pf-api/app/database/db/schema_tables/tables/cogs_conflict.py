from .base import TblModelBase
from ....variable.schema_tables.financial import DB_TABLE_COGS_CONFLICT_TEMPLATE, \
    DB_TABLE_COGS_CONFLICT_DEFAULT


class COGSConflictTblModel(TblModelBase):
    db_table_default = DB_TABLE_COGS_CONFLICT_DEFAULT
    db_table_template = DB_TABLE_COGS_CONFLICT_TEMPLATE

    @property
    def sql_schema_table(self):
        # TODO: find way get query create schema table from django model
        sql = f"""
            CREATE TABLE {self.table_name} AS
                SELECT * FROM {DB_TABLE_COGS_CONFLICT_DEFAULT} WHERE client_id = '{self.client_id}';
            --- CONSTRAINT
            ALTER TABLE {self.table_name}
                ADD CONSTRAINT {self.table_name}_pkey PRIMARY KEY (id);

            ALTER TABLE {self.table_name}
                ADD CONSTRAINT extensiv_cogsconflic_client_id_{self.hash_client_id}_fk_financial
                FOREIGN KEY(client_id)
                REFERENCES financial_clientportal(id) DEFERRABLE INITIALLY DEFERRED;

            --- INDEXES
            CREATE INDEX extensiv_co_sku_{self.hash_client_id}_7613dc_idx
                ON {self.table_name} (sku, status);

            CREATE INDEX extensiv_cogsconflict_sku_{self.hash_client_id}_fcaa28c4
                ON {self.table_name} (sku);
                
            CREATE INDEX extensiv_cogsconflict_sku_{self.hash_client_id}_fcaa28c4_like
                ON {self.table_name} (sku varchar_pattern_ops);

            CREATE INDEX {DB_TABLE_COGS_CONFLICT_DEFAULT}_channel_id_{self.hash_client_id}_fbd61e5a
                ON {self.table_name} (channel_id);
                
            CREATE INDEX {DB_TABLE_COGS_CONFLICT_DEFAULT}_client_id_{self.hash_client_id}_ce847581
                ON {self.table_name} (client_id);

        """
        return sql
