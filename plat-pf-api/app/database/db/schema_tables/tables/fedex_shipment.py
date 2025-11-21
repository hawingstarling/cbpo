from .base import TblModelBase
from ....variable.schema_tables.financial import DB_TABLE_FEDEX_SHIPMENT_TEMPLATE, \
    DB_TABLE_FEDEX_SHIPMENT_DEFAULT


class FedExShipmentTblModel(TblModelBase):
    db_table_default = DB_TABLE_FEDEX_SHIPMENT_DEFAULT
    db_table_template = DB_TABLE_FEDEX_SHIPMENT_TEMPLATE

    @property
    def sql_schema_table(self):
        # TODO: find way get query create schema table from django model
        sql = f"""
            CREATE TABLE {self.table_name} AS
                SELECT * FROM {DB_TABLE_FEDEX_SHIPMENT_DEFAULT} WHERE client_id = '{self.client_id}';
            --- CONSTRAINT
            ALTER TABLE {self.table_name}
                ADD CONSTRAINT {self.table_name}_pkey PRIMARY KEY (id);

            ALTER TABLE {self.table_name}
                ADD CONSTRAINT financial_fedexshipm_client_id_{self.hash_client_id}_fk_financial
                FOREIGN KEY(client_id)
                REFERENCES financial_clientportal(id) DEFERRABLE INITIALLY DEFERRED;
                
            ALTER TABLE {self.table_name}
                ADD CONSTRAINT {DB_TABLE_FEDEX_SHIPMENT_DEFAULT}_shipping_invoice_id_{self.hash_client_id}_fk_financial_shipping_invoice_id
                FOREIGN KEY(shipping_invoice_id)
                REFERENCES financial_{self.client_id_db}_shippinginvoice DEFERRABLE INITIALLY DEFERRED;

            ALTER TABLE {self.table_name}
                ADD CONSTRAINT financial_fedexshipment_client_id_tracking_id_in__{self.hash_client_id}_uniq
                UNIQUE (client_id, tracking_id, invoice_number);

            --- INDEXES
            CREATE INDEX financial_f_status_{self.hash_client_id}_9ba01c_idx
                ON {self.table_name} (status);
            
            CREATE INDEX financial_f_recipie_{self.hash_client_id}_b05886_idx
                ON {self.table_name} (recipient_country, recipient_state, recipient_zip_code);

            CREATE INDEX {DB_TABLE_FEDEX_SHIPMENT_DEFAULT}_client_id_{self.hash_client_id}_ce847581
                ON {self.table_name} (client_id);

            CREATE INDEX financial_f_client__{self.hash_client_id}_6205a9_idx
                ON {self.table_name} (client_id, tracking_id);
                
            CREATE INDEX {DB_TABLE_FEDEX_SHIPMENT_DEFAULT}_shipping_invoice_id_{self.hash_client_id}_ce847581
                ON {self.table_name} (shipping_invoice_id);

        """
        return sql
