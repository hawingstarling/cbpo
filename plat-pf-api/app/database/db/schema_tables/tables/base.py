import hashlib
from abc import ABC
from app.database.db.schema_tables.tables.abstract import TblModelAbstract


class TblModelBase(TblModelAbstract, ABC):
    db_table_default = None
    db_table_template = None

    def __init__(self, client_id: str, **kwargs):
        self.client_id = client_id
        self.client_id_db = self.client_id.replace('-', '_')
        self.hash_client_id = hashlib.sha1(self.client_id_db.encode("UTF-8")).hexdigest()[:8]
        self.kwargs = kwargs

    @property
    def table_name(self):
        return self.db_table_template.format(client_id_tbl=self.client_id_db)

    @property
    def schema_alter_table(self):
        return None
