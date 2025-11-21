from ..objects_manage import MultiDbTableManagerBase
from ...variable.schema_tables.financial import DB_TABLE_ACTIVITY_DEFAULT, DB_TABLE_ACTIVITY_TEMPLATE


class ActivityMultiTblManager(MultiDbTableManagerBase):
    db_table_default = DB_TABLE_ACTIVITY_DEFAULT
    db_table_template = DB_TABLE_ACTIVITY_TEMPLATE
    using_db_table_template = True