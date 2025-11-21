from .base import TblModelBase
from ....variable.schema_tables.financial import DB_TABLE_ITEM_COG_TEMPLATE, DB_TABLE_ITEM_COG_DEFAULT, \
    DB_TABLE_ITEM_TEMPLATE, DB_TABLE_ITEM_DEFAULT


class ItemCOGTblModel(TblModelBase):
    db_table_default = DB_TABLE_ITEM_COG_DEFAULT
    db_table_template = DB_TABLE_ITEM_COG_TEMPLATE

    @property
    def table_item_name(self):
        return DB_TABLE_ITEM_TEMPLATE.format(client_id_tbl=self.client_id_db)

    @property
    def sql_schema_table(self):
        # TODO: find way get query create schema table from django model
        sql = f"""
            CREATE TABLE {self.table_name} AS
                SELECT {DB_TABLE_ITEM_COG_DEFAULT}.* FROM {DB_TABLE_ITEM_COG_DEFAULT} 
                    LEFT JOIN {DB_TABLE_ITEM_DEFAULT} ON {DB_TABLE_ITEM_COG_DEFAULT}.item_id = {DB_TABLE_ITEM_DEFAULT}.id
                WHERE {DB_TABLE_ITEM_DEFAULT}.client_id = '{self.client_id}';
            --- CONSTRAINT
            ALTER TABLE {self.table_name}
                ADD CONSTRAINT {self.table_name}_pkey PRIMARY KEY (id);

            ALTER TABLE {self.table_name}
                ADD CONSTRAINT {DB_TABLE_ITEM_COG_DEFAULT}_item_id_{self.hash_client_id}_fk_financial_item_id
                FOREIGN KEY(item_id)
                REFERENCES {self.table_item_name}(id) DEFERRABLE INITIALLY DEFERRED;

            --- INDEXES
            CREATE INDEX {DB_TABLE_ITEM_COG_DEFAULT}_item_id_{self.hash_client_id}
                ON {self.table_name} (item_id);
        """
        return sql
