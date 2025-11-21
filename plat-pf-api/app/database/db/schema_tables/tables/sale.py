from .base import TblModelBase
from ....variable.schema_tables.financial import DB_TABLE_SALE_TEMPLATE, DB_TABLE_SALE_DEFAULT


class SaleTblModel(TblModelBase):
    db_table_default = DB_TABLE_SALE_DEFAULT
    db_table_template = DB_TABLE_SALE_TEMPLATE

    @property
    def sql_schema_table(self):
        # TODO: find way get query create schema table from django model
        sql = f"""
            CREATE TABLE {self.table_name} AS
                SELECT * FROM financial_sale WHERE client_id = '{self.client_id}';
            --- CONSTRAINT
            ALTER TABLE {self.table_name}
                ADD CONSTRAINT {self.table_name}_pkey PRIMARY KEY (id);

            ALTER TABLE {self.table_name}
                ADD CONSTRAINT financial_sale_channel_id_e880cc9d_fk_financial_channel_id
                FOREIGN KEY(channel_id)
                REFERENCES financial_channel(id) DEFERRABLE INITIALLY DEFERRED;

            ALTER TABLE {self.table_name}
                ADD CONSTRAINT financial_sale_client_id_{self.hash_client_id}_fk_financial_clientportal_id
                FOREIGN KEY(client_id)
                REFERENCES financial_clientportal(id) DEFERRABLE INITIALLY DEFERRED;

            ALTER TABLE {self.table_name}
                ADD CONSTRAINT financial_sale_population_id_{self.hash_client_id}_fk_financial
                FOREIGN KEY(population_id)
                REFERENCES financial_statepopulation(id) DEFERRABLE INITIALLY DEFERRED;

            ALTER TABLE {self.table_name}
                ADD CONSTRAINT financial_sale_profit_status_id_{self.hash_client_id}_fk_financial
                FOREIGN KEY(profit_status_id)
                REFERENCES financial_profitstatus(id) DEFERRABLE INITIALLY DEFERRED;

            ALTER TABLE {self.table_name}
                ADD CONSTRAINT financial_sale_sale_status_id_{self.hash_client_id}_fk_financial
                FOREIGN KEY(sale_status_id)
                REFERENCES financial_salestatus(id) DEFERRABLE INITIALLY DEFERRED;
                
            ALTER TABLE {self.table_name}
                ADD CONSTRAINT financial_sale_client_id_channel_sale_i_{self.hash_client_id}_uniq
                UNIQUE (client_id, channel_sale_id, channel_id);

            --- INDEXES
            CREATE INDEX financial_s_client__{self.hash_client_id}__ce2d08_idx
                ON {self.table_name} (client_id, channel_sale_id, channel_id);
            
            CREATE INDEX financial_sale_channel_id_{self.hash_client_id}_e880cc9d
                ON {self.table_name} (channel_id);
            
            CREATE INDEX financial_sale_client_id_{self.hash_client_id}_05a2f5ab
                ON {self.table_name} (client_id);
            
            CREATE INDEX financial_sale_population_id_{self.hash_client_id}_4e207cd3
                ON {self.table_name} (population_id);
            
            CREATE INDEX financial_sale_profit_status_id_{self.hash_client_id}_44d8ebd0
                ON {self.table_name} (profit_status_id);
            
            CREATE INDEX financial_sale_sale_status_id_{self.hash_client_id}_4415f5cd
                ON {self.table_name} (sale_status_id);
        """
        return sql
