from app.financial.services.postgres_fulltext_search import IFieldConfigPostgresFulltextSearch

FEDEX_SHIPMENT_PENDING = 'FEDEX_SHIPMENT_PENDING'
FEDEX_SHIPMENT_ONE = 'FEDEX_SHIPMENT_ONE'
FEDEX_SHIPMENT_MULTI = 'FEDEX_SHIPMENT_MULTI'
FEDEX_SHIPMENT_NONE = 'FEDEX_SHIPMENT_NONE'
FEDEX_SHIPMENT_COMPLETED = 'FEDEX_SHIPMENT_COMPLETED'

FEDEX_SHIPMENT_CHOICE = (
    (FEDEX_SHIPMENT_PENDING, "Pending"),
    (FEDEX_SHIPMENT_ONE, "Matched One"),
    (FEDEX_SHIPMENT_MULTI, "Matched Multi"),
    (FEDEX_SHIPMENT_NONE, "Not Matched"),
    (FEDEX_SHIPMENT_COMPLETED, "Matched Completed"),
)

REOPEN_BY_AMZ_EVENT = 'REOPEN_BY_AMZ_EVENT'

REOPEN_BY_SALE_STATUS = 'REOPEN_BY_SALE_STATUS'

REOPEN_BY_EXTENSION = 'REOPEN_BY_EXTENSION'

SCHEDULER_HOURS_REOPEN_BY_EXTENSION = 2

# config for source
FEDEX_SHIPMENT_SOURCE_IMPORT = 'Import'

FEDEX_SHIPMENT_SOURCE_FTP_EDI = 'FTP EDI'
FEDEX_SHIPMENT_SOURCE_FTP_CSV = 'FTP CSV'

FEDEX_SHIPMENT_SOURCE_CHOICE = (
    (FEDEX_SHIPMENT_SOURCE_IMPORT, FEDEX_SHIPMENT_SOURCE_IMPORT),
    (FEDEX_SHIPMENT_SOURCE_FTP_EDI, FEDEX_SHIPMENT_SOURCE_FTP_EDI),
    (FEDEX_SHIPMENT_SOURCE_FTP_CSV, FEDEX_SHIPMENT_SOURCE_FTP_CSV),
)

FEDEX_EXPRESS_SERVICE_TYPE = 'FedEx Express'
FEDEX_GROUND_SERVICE_TYPE = 'FedEx Ground'
FEDEX_SMART_POST_SERVICE_TYPE = 'FedEx SmartPost'

FEDEX_SERVICE_TYPE = (
    (FEDEX_EXPRESS_SERVICE_TYPE, FEDEX_EXPRESS_SERVICE_TYPE),
    (FEDEX_GROUND_SERVICE_TYPE, FEDEX_GROUND_SERVICE_TYPE),
    (FEDEX_SMART_POST_SERVICE_TYPE, FEDEX_SMART_POST_SERVICE_TYPE),
)

FEDEX_SERVICE_TYPE_LIST = [item[0] for item in FEDEX_SERVICE_TYPE]

FEDEX_EDI_SERVICE_TYPE_MAPPING = {
    2: FEDEX_EXPRESS_SERVICE_TYPE,
    3: FEDEX_GROUND_SERVICE_TYPE,
    9: FEDEX_SMART_POST_SERVICE_TYPE
}

config_fedex_shipment_search = [
    IFieldConfigPostgresFulltextSearch(field_name='tracking_id', weight='A'),
    IFieldConfigPostgresFulltextSearch(field_name='invoice_number', weight='B'),
    IFieldConfigPostgresFulltextSearch(field_name='recipient_zip_code', weight='B'),
    IFieldConfigPostgresFulltextSearch(field_name='transaction_id', weight='B'),
    IFieldConfigPostgresFulltextSearch(field_name='recipient_state', weight='C'),
    IFieldConfigPostgresFulltextSearch(field_name='recipient_country', weight='C'),
    IFieldConfigPostgresFulltextSearch(field_name='po_number', weight='C'),
    IFieldConfigPostgresFulltextSearch(field_name='customer_ref', weight='C'),
    IFieldConfigPostgresFulltextSearch(field_name='recipient_name', weight='D'),
    IFieldConfigPostgresFulltextSearch(field_name='recipient_address_line_1', weight='D'),
    IFieldConfigPostgresFulltextSearch(field_name='recipient_address_line_2', weight='D'),
    IFieldConfigPostgresFulltextSearch(field_name='shipper_company', weight='D'),
]

config_shipping_invoice_search = [
    IFieldConfigPostgresFulltextSearch(field_name='invoice_number', weight='A'),
    IFieldConfigPostgresFulltextSearch(field_name='payer_account_id', weight='B'),
    IFieldConfigPostgresFulltextSearch(field_name='payee_account_id', weight='B'),
    IFieldConfigPostgresFulltextSearch(field_name='fedexshipment__tracking_id', weight='B'),
    IFieldConfigPostgresFulltextSearch(field_name='fedexshipment__po_number', weight='C'),
    IFieldConfigPostgresFulltextSearch(field_name='fedexshipment__customer_ref', weight='C'),
]

#
SHIPPING_INVOICE_PENDING = 'Pending'
SHIPPING_INVOICE_DONE = 'Done'
SHIPPING_INVOICE_DONE_WITH_ERRORS = 'DoneWithErrors'
