ANALYSIS_CR_TYPE = 'Analysis'
SHIPPING_INVOICE_CR_TYPE = 'ShippingInvoice'
SHIPPING_INVOICE_TRANS_CR_TYPE = 'ShippingInvoiceTrans'
SHIPPING_INVOICE_TRANS_UNMATCHED_CR_TYPE = 'ShippingInvoiceTransUnmatched'
ITEMS_CR_TYPE = 'Items'
TOP_ASINS_CR_TYPE = 'TopASINs'
COGS_CONFLICT_CR_TYPE = 'COGSConflict'

REPORT_TYPE_ENUM = (
    (ANALYSIS_CR_TYPE, 'Export Custom Analysis'),
    (SHIPPING_INVOICE_CR_TYPE, 'Export Custom Shipping Invoices'),
    (SHIPPING_INVOICE_TRANS_CR_TYPE, 'Export Custom Shipping Invoice Transactions'),
    (SHIPPING_INVOICE_TRANS_UNMATCHED_CR_TYPE, 'Export Custom Shipping Invoice Unmatched'),
    (ITEMS_CR_TYPE, 'Export Custom Items'),
    (TOP_ASINS_CR_TYPE, 'Export Custom TopASINs'),
    (COGS_CONFLICT_CR_TYPE, 'Export Custom COGS Conflicts'),
)

REPORTING = 'reporting'
REPORTED = 'reported'
REVOKED = 'revoked'

REPORT_ENUM = (
    (REPORTING, 'Reporting'),
    (REPORTED, 'Reported'),
    (REVOKED, 'Revoked'),
)
