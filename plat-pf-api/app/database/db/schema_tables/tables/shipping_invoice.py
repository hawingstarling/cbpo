from .base import TblModelBase
from ....variable.schema_tables.financial import DB_TABLE_SHIPPING_INVOICE_DEFAULT, DB_TABLE_SHIPPING_INVOICE_TEMPLATE


class ShippingInvoiceTblModel(TblModelBase):
    db_table_default = DB_TABLE_SHIPPING_INVOICE_DEFAULT
    db_table_template = DB_TABLE_SHIPPING_INVOICE_TEMPLATE

    @property
    def sql_schema_table(self):
        # TODO: find way get query create schema table from django model
        alias_name_pkey = f"{self.table_name[:55]}_pkey"
        sql = f"""
            CREATE TABLE {self.table_name} AS
                SELECT * FROM {DB_TABLE_SHIPPING_INVOICE_DEFAULT} WHERE client_id = '{self.client_id}';
            --- CONSTRAINT
            ALTER TABLE {self.table_name}
                ADD CONSTRAINT {alias_name_pkey} PRIMARY KEY (id);

            ALTER TABLE {self.table_name}
                ADD CONSTRAINT financial_shippinginvoice_client_id_{self.hash_client_id}_fk_financial
                FOREIGN KEY(client_id)
                REFERENCES financial_clientportal(id) DEFERRABLE INITIALLY DEFERRED;

            ALTER TABLE {self.table_name}
                ADD CONSTRAINT financial_shippinginvoic_client_id_invoice_number_{self.hash_client_id}_uniq
                UNIQUE (client_id, invoice_number, payee_account_id);

            --- INDEXES
            CREATE INDEX financial_s_client_{self.hash_client_id}_9a1541_idx
                ON {self.table_name} (client_id, payer_account_id, payee_account_id);

            CREATE INDEX financial_s_client_{self.hash_client_id}_a816fa_idx
                ON {self.table_name} (client_id, invoice_date, invoice_number);

        """
        return sql
