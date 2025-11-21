SALE_PENDING_STATUS = 'Pending'
SALE_UNPAID_STATUS = 'Unpaid'
SALE_CANCELLED_STATUS = 'Cancelled'
SALE_UNSHIPPED_STATUS = 'Unshipped'
SALE_PARTIALLY_UNSHIPPED_STATUS = 'Partially Unshipped'
SALE_PARTIALLY_SHIPPED_STATUS = 'Partially Shipped'
SALE_SHIPPED_STATUS = 'Shipped'
SALE_COMPLETED_STATUS = 'Completed'
SALE_RETURNING_STATUS = 'Returning'
SALE_PARTIALLY_RETURNING_STATUS = 'Partially Returning'
SALE_REFUNDED_STATUS = 'Refunded'
SALE_PARTIALLY_REFUNDED_STATUS = 'Partially Refunded'
SALE_OTHER_STATUS = 'Other'
RETURN_REVERSED_STATUS = 'Return Reversed'

SALE_STATUS = (
    ((SALE_PENDING_STATUS, SALE_PENDING_STATUS), (1000, 'Information not yet all received.')),
    ((SALE_UNPAID_STATUS, SALE_UNPAID_STATUS), (2000, 'Customer has yet to pay.')),
    ((SALE_CANCELLED_STATUS, SALE_CANCELLED_STATUS), (3000, 'Order has been cancelled.')),
    ((SALE_UNSHIPPED_STATUS, SALE_UNSHIPPED_STATUS), (4000, 'Order received and ready to be processed and shipped.')),
    ((SALE_PARTIALLY_UNSHIPPED_STATUS, SALE_PARTIALLY_UNSHIPPED_STATUS),
     (5000,
      'Some items have been shipped, but others have yet to be.Can also indicate an order that is to only be partially filled.')),
    ((SALE_PARTIALLY_SHIPPED_STATUS, SALE_PARTIALLY_SHIPPED_STATUS),
     (6000, 'Some items have been shipped, are in transit, and no items remain to be shipped.')),
    ((SALE_SHIPPED_STATUS, SALE_SHIPPED_STATUS),
     (7000, 'All items that should have shipped, have been, and are in transit.')),
    ((SALE_COMPLETED_STATUS, SALE_COMPLETED_STATUS), (8000, 'Carrier confirms all items have arrived.')),
    ((SALE_RETURNING_STATUS, SALE_RETURNING_STATUS),
     (9000, 'Customer has made a valid claim for return and is sending the order back for a refund.')),
    ((SALE_PARTIALLY_RETURNING_STATUS, SALE_PARTIALLY_RETURNING_STATUS),
     (10000, 'Same as above, but only for some items in the order.')),
    ((SALE_REFUNDED_STATUS, SALE_REFUNDED_STATUS),
     (11000, 'Returned item was received, processed, and refunded. Considered completed.')),
    ((SALE_PARTIALLY_REFUNDED_STATUS, SALE_PARTIALLY_REFUNDED_STATUS),
     (12000, 'Same as above but only for some items.')),
    ((SALE_OTHER_STATUS, SALE_OTHER_STATUS), (13000, 'Exception sale status. See internal notes.')),
    (
        (RETURN_REVERSED_STATUS, RETURN_REVERSED_STATUS),
        (14000, 'Has Refund AND Has Adjustment.Reserval_Reimbursement.')),
)

SALE_STATUS_ENUM = tuple(item[0] for item in SALE_STATUS)

SALE_STATUS_ORDER_DICT = {item[0][0]: item[1][0] for item in SALE_STATUS}
