from .base import TblModelBase
from ....variable.schema_tables.financial import DB_TABLE_SALE_CHARGE_DEFAULT, DB_TABLE_SALE_CHARGE_TEMPLATE


class SaleChargeAndCostTblModel(TblModelBase):
    db_table_default = DB_TABLE_SALE_CHARGE_DEFAULT
    db_table_template = DB_TABLE_SALE_CHARGE_TEMPLATE

    @property
    def sql_schema_table(self):
        # TODO: find way get query create schema table from django model
        sql = f"""
            CREATE TABLE {self.table_name} AS
                SELECT {DB_TABLE_SALE_CHARGE_DEFAULT}.* FROM {DB_TABLE_SALE_CHARGE_DEFAULT} 
                    INNER JOIN financial_sale ON {DB_TABLE_SALE_CHARGE_DEFAULT}.sale_id = financial_sale.id
                WHERE financial_sale.client_id = '{self.client_id}';
            
            --- CONSTRAINT
            ALTER TABLE {self.table_name}
                ADD CONSTRAINT {self.table_name}andcost_pkey PRIMARY KEY (id);
                
            ALTER TABLE {self.table_name}
                ADD CONSTRAINT {DB_TABLE_SALE_CHARGE_DEFAULT}_{self.hash_client_id}_sale_id_key
                UNIQUE (sale_id);

            ALTER TABLE {self.table_name}
                ADD CONSTRAINT financial_salecharge_sale_id_{self.hash_client_id}_3e10ee0c_fk_financial
                FOREIGN KEY(sale_id)
                REFERENCES financial_{self.client_id_db}_sale(id) DEFERRABLE INITIALLY DEFERRED;

            --- INDEXES
            CREATE INDEX sale_charge_and_cost_{self.hash_client_id}_idx
                ON {self.table_name} (sale_id);
        """
        return sql
