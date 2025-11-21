from ..objects_manage import MultiDbTableManagerBase
from ...variable.schema_tables.financial import DB_TABLE_FEDEX_SHIPMENT_DEFAULT, DB_TABLE_FEDEX_SHIPMENT_TEMPLATE, \
    DB_TABLE_SHIPPING_INVOICE_ID


class FedExShipmentMultiTblManager(MultiDbTableManagerBase):
    db_table_default = DB_TABLE_FEDEX_SHIPMENT_DEFAULT
    db_table_template = DB_TABLE_FEDEX_SHIPMENT_TEMPLATE
    db_table_relation_fields = [DB_TABLE_SHIPPING_INVOICE_ID]
    using_db_table_template = True
