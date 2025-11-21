from auditlog.models import LogEntryManager
from ..objects_manage import MultiDbTableManagerBase
from ...variable.schema_tables.financial import DB_TABLE_LOG_ENTRY_TEMPLATE, DB_TABLE_LOG_ENTRY_DEFAULT


class LogEntryCustomManager(LogEntryManager, MultiDbTableManagerBase):
    db_table_default = DB_TABLE_LOG_ENTRY_DEFAULT
    db_table_template = DB_TABLE_LOG_ENTRY_TEMPLATE
    using_db_table_template = True
