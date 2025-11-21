from ..objects_manage import MultiDbTableManagerBase, SoftDeleteMultiDbTableManagerBase
from ...variable.schema_tables.financial import DB_TABLE_ITEM_COG_DEFAULT, DB_TABLE_ITEM_COG_TEMPLATE, DB_TABLE_ITEM_ID


class ItemCOGMultiTblManager(MultiDbTableManagerBase):
    db_table_default = DB_TABLE_ITEM_COG_DEFAULT
    db_table_template = DB_TABLE_ITEM_COG_TEMPLATE
    db_table_relation_fields = [DB_TABLE_ITEM_ID]
    using_db_table_template = True


class ItemCOGSoftDeleteMultiTblManager(SoftDeleteMultiDbTableManagerBase):
    db_table_default = DB_TABLE_ITEM_COG_DEFAULT
    db_table_template = DB_TABLE_ITEM_COG_TEMPLATE
    db_table_relation_fields = [DB_TABLE_ITEM_ID]
    using_db_table_template = True