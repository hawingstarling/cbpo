from ..objects_manage import MultiDbTableManagerBase, SoftDeleteMultiDbTableManagerBase
from ...variable.schema_tables.financial import DB_TABLE_CACHE_TRANSACTION_TEMPLATE, \
    DB_TABLE_CACHE_TRANSACTION_DEFAULT


class CacheTransactionMultiTblManager(MultiDbTableManagerBase):
    db_table_default = DB_TABLE_CACHE_TRANSACTION_DEFAULT
    db_table_template = DB_TABLE_CACHE_TRANSACTION_TEMPLATE
    using_db_table_template = True


class CacheTransactionSoftDeleteMultiTblManager(SoftDeleteMultiDbTableManagerBase):
    db_table_default = DB_TABLE_CACHE_TRANSACTION_DEFAULT
    db_table_template = DB_TABLE_CACHE_TRANSACTION_TEMPLATE
    using_db_table_template = True
