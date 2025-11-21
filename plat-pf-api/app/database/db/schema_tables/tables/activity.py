from .base import TblModelBase
from ....variable.schema_tables.financial import DB_TABLE_ACTIVITY_DEFAULT, DB_TABLE_ACTIVITY_TEMPLATE


class ActivityTblModel(TblModelBase):
    db_table_default = DB_TABLE_ACTIVITY_DEFAULT
    db_table_template = DB_TABLE_ACTIVITY_TEMPLATE

    @property
    def sql_schema_table(self):
        # TODO: find way get query create schema table from django model
        sql = f"""
            CREATE TABLE {self.table_name} AS
                SELECT * FROM {DB_TABLE_ACTIVITY_DEFAULT} WHERE client_id = '{self.client_id}';

            --- CONSTRAINTS

            ALTER TABLE {self.table_name}
                ADD CONSTRAINT {self.table_name}_pkey PRIMARY KEY (id);

            ALTER TABLE {self.table_name}
                ADD CONSTRAINT {DB_TABLE_ACTIVITY_DEFAULT}_client_id_{self.hash_client_id}_fk_financial
                FOREIGN KEY(client_id)
                REFERENCES financial_clientportal(id) DEFERRABLE INITIALLY DEFERRED;

            ALTER TABLE {self.table_name}
                ADD CONSTRAINT {DB_TABLE_ACTIVITY_DEFAULT}_user_id_{self.hash_client_id}_fk_financial_user_user_id
                FOREIGN KEY(user_id)
                REFERENCES financial_user(user_id) DEFERRABLE INITIALLY DEFERRED;

            --- INDEXES
            CREATE INDEX {DB_TABLE_ACTIVITY_DEFAULT}_client_id_{self.hash_client_id}
                ON {self.table_name} (client_id);

            CREATE INDEX financial_a_client__{self.hash_client_id}_idx
                ON {self.table_name} (client_id, user_id, action);

            CREATE INDEX json_data_{self.hash_client_id}_idx
                ON {self.table_name} using gin (data jsonb_path_ops);

            CREATE INDEX {DB_TABLE_ACTIVITY_DEFAULT}_user_id_{self.hash_client_id}
                ON {self.table_name} (user_id);
        """
        return sql
