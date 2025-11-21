from ..objects_manage import MultiDbTableManagerBase
from ...variable.schema_tables.financial import DB_TABLE_COGS_CONFLICT_DEFAULT, DB_TABLE_COGS_CONFLICT_TEMPLATE


class COGSConflictMultiTblManager(MultiDbTableManagerBase):
    db_table_default = DB_TABLE_COGS_CONFLICT_DEFAULT
    db_table_template = DB_TABLE_COGS_CONFLICT_TEMPLATE
    using_db_table_template = True
