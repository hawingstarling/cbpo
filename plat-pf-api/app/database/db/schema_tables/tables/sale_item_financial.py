from .base import TblModelBase
from ....variable.schema_tables.financial import DB_TABLE_SALE_ITEM_FINANCIAL_DEFAULT, \
    DB_TABLE_SALE_ITEM_FINANCIAL_TEMPLATE


class SaleItemFinancialTblModel(TblModelBase):
    db_table_default = DB_TABLE_SALE_ITEM_FINANCIAL_DEFAULT
    db_table_template = DB_TABLE_SALE_ITEM_FINANCIAL_TEMPLATE

    @property
    def sql_schema_table(self):
        # TODO: find way get query create schema table from django model
        sql = f"""
            CREATE TABLE {self.table_name} AS
                SELECT * FROM {DB_TABLE_SALE_ITEM_FINANCIAL_DEFAULT} WHERE client_id = '{self.client_id}';
            --- CONSTRAINT
            ALTER TABLE {self.table_name}
                ADD CONSTRAINT {self.table_name}_pkey PRIMARY KEY (id);

            ALTER TABLE {self.table_name}
                ADD CONSTRAINT financial_saleitemfi_brand_id_{self.hash_client_id}_fk_financial
                FOREIGN KEY(brand_id)
                REFERENCES financial_brand(id) DEFERRABLE INITIALLY DEFERRED;

            ALTER TABLE {self.table_name}
                ADD CONSTRAINT financial_saleitemfi_client_id_{self.hash_client_id}_fk_financial
                FOREIGN KEY(client_id)
                REFERENCES financial_clientportal(id) DEFERRABLE INITIALLY DEFERRED;

            ALTER TABLE {self.table_name}
                ADD CONSTRAINT financial_saleitemfi_fulfillment_type_id_{self.hash_client_id}_fk_financial
                FOREIGN KEY(fulfillment_type_id)
                REFERENCES financial_fulfillmentchannel(id) DEFERRABLE INITIALLY DEFERRED;

            ALTER TABLE {self.table_name}
                ADD CONSTRAINT financial_saleitemfi_profit_status_id_{self.hash_client_id}_fk_financial
                FOREIGN KEY(profit_status_id)
                REFERENCES financial_profitstatus(id) DEFERRABLE INITIALLY DEFERRED;

            ALTER TABLE {self.table_name}
                ADD CONSTRAINT financial_saleitemfi_sale_id_{self.hash_client_id}_fk_financial_sale_id
                FOREIGN KEY(sale_id)
                REFERENCES financial_{self.client_id_db}_sale DEFERRABLE INITIALLY DEFERRED;
                
            ALTER TABLE {self.table_name}
                ADD CONSTRAINT financial_saleitemfi_sale_item_id_{self.hash_client_id}_fk_financial
                FOREIGN KEY(sale_item_id)
                REFERENCES financial_{self.client_id_db}_saleitem DEFERRABLE INITIALLY DEFERRED;

            ALTER TABLE {self.table_name}
                ADD CONSTRAINT financial_saleitemfi_sale_status_id_{self.hash_client_id}_fk_financial
                FOREIGN KEY(sale_status_id)
                REFERENCES financial_salestatus(id) DEFERRABLE INITIALLY DEFERRED;

            ALTER TABLE {self.table_name}
                ADD CONSTRAINT financial_saleitemfi_size_id_{self.hash_client_id}_fk_financial_variant_id
                FOREIGN KEY(size_id)
                REFERENCES financial_variant(id) DEFERRABLE INITIALLY DEFERRED;

            ALTER TABLE {self.table_name}
                ADD CONSTRAINT financial_saleitemfi_style_id_{self.hash_client_id}_fk_financial_variant_id
                FOREIGN KEY(style_id)
                REFERENCES financial_variant(id) DEFERRABLE INITIALLY DEFERRED;

            ALTER TABLE {self.table_name}
                ADD CONSTRAINT financial_saleitemfinanc_client_id_sale_id_sale_i_{self.hash_client_id}_uniq
                UNIQUE (client_id, sale_id, sale_item_id, sku, sale_status_id);

            --- INDEXES
            CREATE INDEX financial_s_client__{self.hash_client_id}__d7c537_idx
                ON {self.table_name} (client_id, sale_id, sale_item_id, sku, sale_status_id);

            CREATE INDEX financial_s_client__{self.hash_client_id}__c07f74_idx
                ON {self.table_name} (client_id, sale_item_id);

            CREATE INDEX financial_s_client__{self.hash_client_id}__8b8c5f_idx
                ON {self.table_name} (client_id, dirty);

            CREATE INDEX financial_saleitemfi_brand_id__{self.hash_client_id}_47a67e9a
                ON {self.table_name} (brand_id);

            CREATE INDEX financial_saleitemfi_client_id__{self.hash_client_id}_37a765cf
                ON {self.table_name} (client_id);

            CREATE INDEX financial_saleitemfi_fulfillment_type_id__{self.hash_client_id}__ba485ff7
                ON {self.table_name} (fulfillment_type_id);

            CREATE INDEX financial_saleitemfi_profit_status_id__{self.hash_client_id}__cf5c2280
                ON {self.table_name} (profit_status_id);

            CREATE INDEX financial_saleitemfi_sale_id__{self.hash_client_id}__4790eacc
                ON {self.table_name} (sale_item_id);

            CREATE INDEX financial_saleitemfi_sale_status_id__{self.hash_client_id}__a728b590
                ON {self.table_name} (sale_status_id);

            CREATE INDEX financial_saleitemfi_size_id__{self.hash_client_id}__19578708
                ON {self.table_name} (size_id);

            CREATE INDEX financial_saleitemfi_style_id__{self.hash_client_id}__38b69cd9
                ON {self.table_name} (style_id);
            
            CREATE INDEX financial_s_client__{self.hash_client_id}__69a5e2_idx
                ON {self.table_name} (client_id, tracking_fedex_id);
        """
        return sql
