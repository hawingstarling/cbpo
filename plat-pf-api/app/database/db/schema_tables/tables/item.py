from .base import TblModelBase
from ....variable.schema_tables.financial import DB_TABLE_ITEM_TEMPLATE, DB_TABLE_ITEM_DEFAULT


class ItemTblModel(TblModelBase):
    db_table_default = DB_TABLE_ITEM_DEFAULT
    db_table_template = DB_TABLE_ITEM_TEMPLATE

    @property
    def sql_schema_table(self):
        # TODO: find way get query create schema table from django model
        sql = f"""
            CREATE TABLE {self.table_name} AS
                SELECT * FROM {DB_TABLE_ITEM_DEFAULT} WHERE client_id = '{self.client_id}';
            --- CONSTRAINT
            ALTER TABLE {self.table_name}
                ADD CONSTRAINT {self.table_name}_pkey PRIMARY KEY (id);

            ALTER TABLE {self.table_name}
                ADD CONSTRAINT {DB_TABLE_ITEM_DEFAULT}_brand_id_{self.hash_client_id}_fk_financial_brand_id
                FOREIGN KEY(brand_id)
                REFERENCES financial_brand(id) DEFERRABLE INITIALLY DEFERRED;

            ALTER TABLE {self.table_name}
                ADD CONSTRAINT {DB_TABLE_ITEM_DEFAULT}_client_id_{self.hash_client_id}_fk_financial_clientportal_id
                FOREIGN KEY(client_id)
                REFERENCES financial_clientportal(id) DEFERRABLE INITIALLY DEFERRED;

            ALTER TABLE {self.table_name}
                ADD CONSTRAINT {DB_TABLE_ITEM_DEFAULT}_channel_id_{self.hash_client_id}_fk_financial_channel_id
                FOREIGN KEY(channel_id)
                REFERENCES financial_channel(id) DEFERRABLE INITIALLY DEFERRED;

            ALTER TABLE {self.table_name}
                ADD CONSTRAINT {DB_TABLE_ITEM_DEFAULT}_fulfillment_type_id_{self.hash_client_id}_fk_financial
                FOREIGN KEY(fulfillment_type_id)
                REFERENCES financial_fulfillmentchannel(id) DEFERRABLE INITIALLY DEFERRED;
                
            ALTER TABLE {self.table_name}
                ADD CONSTRAINT {DB_TABLE_ITEM_DEFAULT}_size_id_{self.hash_client_id}_fk_financial_variant_id
                FOREIGN KEY(size_id)
                REFERENCES financial_variant(id) DEFERRABLE INITIALLY DEFERRED;
                
            ALTER TABLE {self.table_name}
                ADD CONSTRAINT {DB_TABLE_ITEM_DEFAULT}_style_id_{self.hash_client_id}_fk_financial_variant_id
                FOREIGN KEY(style_id)
                REFERENCES financial_variant(id) DEFERRABLE INITIALLY DEFERRED;
                
            ALTER TABLE {self.table_name}
                ADD CONSTRAINT {DB_TABLE_ITEM_DEFAULT}_client_id_sku_{self.hash_client_id}_uniq
                UNIQUE (client_id, sku);

            --- INDEXES
            CREATE INDEX {DB_TABLE_ITEM_DEFAULT}_brand_id_{self.hash_client_id}
                ON {self.table_name} (brand_id);

            CREATE INDEX {DB_TABLE_ITEM_DEFAULT}_channel_id_{self.hash_client_id}
                ON {self.table_name} (channel_id);

            CREATE INDEX {DB_TABLE_ITEM_DEFAULT}_client_id_{self.hash_client_id}
                ON {self.table_name} (client_id);
                
            CREATE INDEX {DB_TABLE_ITEM_DEFAULT}_fulfillment_type_id_{self.hash_client_id}
                ON {self.table_name} (fulfillment_type_id);
                
            CREATE INDEX {DB_TABLE_ITEM_DEFAULT}_size_id_{self.hash_client_id}
                ON {self.table_name} (size_id);
                
            CREATE INDEX {DB_TABLE_ITEM_DEFAULT}_style_id_{self.hash_client_id}
                ON {self.table_name} (style_id);
        """
        return sql
