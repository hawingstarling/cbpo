from ..objects_manage import MultiDbTableManagerBase
from ...variable.schema_tables.financial import DB_TABLE_SHIPPING_INVOICE_DEFAULT, DB_TABLE_SHIPPING_INVOICE_TEMPLATE


class ShippingInvoiceMultiTblManager(MultiDbTableManagerBase):
    db_table_default = DB_TABLE_SHIPPING_INVOICE_DEFAULT
    db_table_template = DB_TABLE_SHIPPING_INVOICE_TEMPLATE
    using_db_table_template = True
