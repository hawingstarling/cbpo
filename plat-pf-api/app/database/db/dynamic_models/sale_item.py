from ..objects_manage import MultiDbTableManagerBase, SoftDeleteMultiDbTableManagerBase
from ...variable.schema_tables.financial import DB_TABLE_SALE_ITEM_DEFAULT, DB_TABLE_SALE_ITEM_TEMPLATE, \
    DB_TABLE_SALE_ID


class SaleItemMultiTblManager(MultiDbTableManagerBase):
    db_table_default = DB_TABLE_SALE_ITEM_DEFAULT
    db_table_template = DB_TABLE_SALE_ITEM_TEMPLATE
    db_table_relation_fields = [DB_TABLE_SALE_ID]
    using_db_table_template = True


class SaleItemSoftDeleteMultiTblManager(SoftDeleteMultiDbTableManagerBase):
    db_table_default = DB_TABLE_SALE_ITEM_DEFAULT
    db_table_template = DB_TABLE_SALE_ITEM_TEMPLATE
    db_table_relation_fields = [DB_TABLE_SALE_ID]
    using_db_table_template = True
