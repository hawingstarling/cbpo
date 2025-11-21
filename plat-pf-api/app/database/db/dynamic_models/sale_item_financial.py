from ..objects_manage import MultiDbTableManagerBase, SoftDeleteMultiDbTableManagerBase
from ...variable.schema_tables.financial import DB_TABLE_SALE_ITEM_FINANCIAL_DEFAULT, \
    DB_TABLE_SALE_ITEM_FINANCIAL_TEMPLATE, DB_TABLE_SALE_ITEM_ID, DB_TABLE_SALE_ID


class SaleFinancialMultiTblManager(MultiDbTableManagerBase):
    db_table_default = DB_TABLE_SALE_ITEM_FINANCIAL_DEFAULT
    db_table_template = DB_TABLE_SALE_ITEM_FINANCIAL_TEMPLATE
    db_table_relation_fields = [DB_TABLE_SALE_ID, DB_TABLE_SALE_ITEM_ID]
    using_db_table_template = True


class SaleFinancialSoftDeleteMultiTblManager(SoftDeleteMultiDbTableManagerBase):
    db_table_default = DB_TABLE_SALE_ITEM_FINANCIAL_DEFAULT
    db_table_template = DB_TABLE_SALE_ITEM_FINANCIAL_TEMPLATE
    db_table_relation_fields = [DB_TABLE_SALE_ID, DB_TABLE_SALE_ITEM_ID]
    using_db_table_template = True
