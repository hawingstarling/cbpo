from .base import TblModelBase
from ....variable.schema_tables.financial import DB_TABLE_SALE_ITEM_DEFAULT, DB_TABLE_SALE_ITEM_TEMPLATE


class SaleItemTblModel(TblModelBase):
    db_table_default = DB_TABLE_SALE_ITEM_DEFAULT
    db_table_template = DB_TABLE_SALE_ITEM_TEMPLATE

    @property
    def sql_schema_table(self):
        # TODO: find way get query create schema table from django model
        sql = f"""
            CREATE TABLE {self.table_name} AS
                SELECT * FROM {DB_TABLE_SALE_ITEM_DEFAULT} WHERE client_id = '{self.client_id}';
            --- CONSTRAINT
            ALTER TABLE {self.table_name}
                ADD CONSTRAINT {self.table_name}_pkey PRIMARY KEY (id);
            
            ALTER TABLE {self.table_name}
                ADD CONSTRAINT {DB_TABLE_SALE_ITEM_DEFAULT}_brand_id_{self.hash_client_id}_fk_financial_brand_id
                FOREIGN KEY(brand_id)
                REFERENCES financial_brand(id) DEFERRABLE INITIALLY DEFERRED;
            
            ALTER TABLE {self.table_name}
                ADD CONSTRAINT {DB_TABLE_SALE_ITEM_DEFAULT}_client_id_{self.hash_client_id}_fk_financial
                FOREIGN KEY(client_id)
                REFERENCES financial_clientportal(id) DEFERRABLE INITIALLY DEFERRED;
            
            ALTER TABLE {self.table_name}
                ADD CONSTRAINT {DB_TABLE_SALE_ITEM_DEFAULT}_fulfillment_type_id_{self.hash_client_id}_fk_financial
                FOREIGN KEY(fulfillment_type_id)
                REFERENCES financial_fulfillmentchannel(id) DEFERRABLE INITIALLY DEFERRED;
            
            ALTER TABLE {self.table_name}
                ADD CONSTRAINT {DB_TABLE_SALE_ITEM_DEFAULT}_profit_status_id_{self.hash_client_id}_fk_financial
                FOREIGN KEY(profit_status_id)
                REFERENCES financial_profitstatus(id) DEFERRABLE INITIALLY DEFERRED;
            
            ALTER TABLE {self.table_name}
                ADD CONSTRAINT {DB_TABLE_SALE_ITEM_DEFAULT}_sale_id_{self.hash_client_id}_fk_financial_sale_id
                FOREIGN KEY(sale_id)
                REFERENCES financial_{self.client_id_db}_sale DEFERRABLE INITIALLY DEFERRED;
            
            ALTER TABLE {self.table_name}
                ADD CONSTRAINT {DB_TABLE_SALE_ITEM_DEFAULT}_sale_status_id_{self.hash_client_id}_fk_financial
                FOREIGN KEY(sale_status_id)
                REFERENCES financial_salestatus(id) DEFERRABLE INITIALLY DEFERRED;
            
            ALTER TABLE {self.table_name}
                ADD CONSTRAINT {DB_TABLE_SALE_ITEM_DEFAULT}_size_id_{self.hash_client_id}_fk_financial_variant_id
                FOREIGN KEY(size_id)
                REFERENCES financial_variant(id) DEFERRABLE INITIALLY DEFERRED;
            
            ALTER TABLE {self.table_name}
                ADD CONSTRAINT {DB_TABLE_SALE_ITEM_DEFAULT}_style_id_{self.hash_client_id}_fk_financial_variant_id
                FOREIGN KEY(style_id)
                REFERENCES financial_variant(id) DEFERRABLE INITIALLY DEFERRED;
                
            ALTER TABLE {self.table_name}
                ADD CONSTRAINT {DB_TABLE_SALE_ITEM_DEFAULT}_client_id_sale_id_sku_{self.hash_client_id}_uniq
                UNIQUE (client_id, sale_id, sku);
                
            --- INDEXES
            CREATE INDEX financial_s_client__{self.hash_client_id}__74cd6e_idx
                ON {self.table_name} (client_id, sale_id, sku);
            
            CREATE INDEX financial_s_client__{self.hash_client_id}__da564a_idx
                ON {self.table_name} (client_id, sale_id);
            
            CREATE INDEX financial_s_client__{self.hash_client_id}__ac18c7_idx
                ON {self.table_name} (client_id, dirty);
            
            CREATE INDEX {DB_TABLE_SALE_ITEM_DEFAULT}_brand_id__{self.hash_client_id}__6feff604
                ON {self.table_name} (brand_id);
            
            CREATE INDEX {DB_TABLE_SALE_ITEM_DEFAULT}_client_id__{self.hash_client_id}__a2d01b49
                ON {self.table_name} (client_id);
            
            CREATE INDEX {DB_TABLE_SALE_ITEM_DEFAULT}_fulfillment_type_id__{self.hash_client_id}__bdf75ce7
                ON {self.table_name} (fulfillment_type_id);
            
            CREATE INDEX {DB_TABLE_SALE_ITEM_DEFAULT}_profit_status_id__{self.hash_client_id}__947c1885
                ON {self.table_name} (profit_status_id);
            
            CREATE INDEX {DB_TABLE_SALE_ITEM_DEFAULT}_sale_id__{self.hash_client_id}__1f4c1fb9
                ON {self.table_name} (sale_id);
            
            CREATE INDEX {DB_TABLE_SALE_ITEM_DEFAULT}_sale_status_id__{self.hash_client_id}__3b552193
                ON {self.table_name} (sale_status_id);
            
            CREATE INDEX {DB_TABLE_SALE_ITEM_DEFAULT}_size_id__{self.hash_client_id}__f110d755
                ON {self.table_name} (size_id);
            
            CREATE INDEX {DB_TABLE_SALE_ITEM_DEFAULT}_style_id__{self.hash_client_id}__b15d8d8a
                ON {self.table_name} (style_id);
            
            CREATE INDEX financial_s_client__{self.hash_client_id}__18eef9_idx
                ON {self.table_name} (client_id, tracking_fedex_id);
        """
        return sql
