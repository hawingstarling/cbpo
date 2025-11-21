from ..objects_manage import MultiDbTableManagerBase, SoftDeleteMultiDbTableManagerBase
from ...variable.schema_tables.financial import DB_TABLE_GENERIC_TRANSACTION_DEFAULT, \
    DB_TABLE_GENERIC_TRANSACTION_TEMPLATE


class GenericTransactionMultiTblManager(MultiDbTableManagerBase):
    db_table_default = DB_TABLE_GENERIC_TRANSACTION_DEFAULT
    db_table_template = DB_TABLE_GENERIC_TRANSACTION_TEMPLATE
    using_db_table_template = True


class GenericTransactionSoftDeleteMultiTblManager(SoftDeleteMultiDbTableManagerBase):
    db_table_default = DB_TABLE_GENERIC_TRANSACTION_DEFAULT
    db_table_template = DB_TABLE_GENERIC_TRANSACTION_TEMPLATE
    using_db_table_template = True
