from ..objects_manage import MultiDbTableManagerBase, SoftDeleteMultiDbTableManagerBase
from ...variable.schema_tables.financial import DB_TABLE_ITEM_DEFAULT, DB_TABLE_ITEM_TEMPLATE


class ItemMultiTblManager(MultiDbTableManagerBase):
    db_table_default = DB_TABLE_ITEM_DEFAULT
    db_table_template = DB_TABLE_ITEM_TEMPLATE
    using_db_table_template = True


class ItemSoftDeleteMultiTblManager(SoftDeleteMultiDbTableManagerBase):
    db_table_default = DB_TABLE_ITEM_DEFAULT
    db_table_template = DB_TABLE_ITEM_TEMPLATE
    using_db_table_template = True