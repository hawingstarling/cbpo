FBAInventoryReimbursementType = 'FBAInventoryReimbursement'
ReserveEventType = 'ReserveEvent'
PostageBillingType = 'PostageBilling'
PostageRefundType = 'PostageRefund'
LostOrDamagedReimbursementType = 'LostOrDamagedReimbursement'
CanceledButPickedUpReimbursementType = 'CanceledButPickedUpReimbursement'
ReimbursementClawbackType = 'ReimbursementClawback'
SellerRewardsType = 'SellerRewards'
ReversalReimbursementType = 'REVERSAL_REIMBURSEMENT'
PostageBillingTransactionFeeType = 'PostageBilling_TransactionFee'
PostageBillingPostageType = 'PostageBilling_Postage'
PostageBillingDeliveryConfirmationType = 'PostageBilling_DeliveryConfirmation'
ReturnPostageBillingTrackingType = 'ReturnPostageBilling_Tracking'
ReturnPostageBillingPostageType = 'ReturnPostageBilling_Postage'
ReturnPostageBillingFuelSurchargeType = 'ReturnPostageBilling_FuelSurcharge'
ReturnPostageBillingOversizeSurchargeType = 'ReturnPostageBilling_OversizeSurcharge'
ReturnPostageBillingDeliveryAreaSurchargeType = 'ReturnPostageBilling_DeliveryAreaSurcharge'
AdjustmentOtherType = 'Other'

# http://docs.developer.amazonservices.com/en_US/finances/Finances_Datatypes.html#AdjustmentEvent
AdjustmentTypeConfig = (
    (FBAInventoryReimbursementType, 'FBA Inventory Reimbursement'),
    (ReserveEventType, 'Reserve Event'),
    (PostageBillingType, 'Postage Billing'),
    (PostageRefundType, 'Postage Refund'),
    (LostOrDamagedReimbursementType, 'Lost Or Damaged Reimbursement'),
    (CanceledButPickedUpReimbursementType, 'Canceled But Picked Up Reimbursement'),
    (ReimbursementClawbackType, 'Reimbursement Clawback'),
    (SellerRewardsType, 'Seller Rewards'),
    (ReversalReimbursementType, 'Reversal Reimbursement'),
    (PostageBillingTransactionFeeType, 'Postage Billing Transaction Fee'),
    (PostageBillingPostageType, 'Postage Billing Postage'),
    (PostageBillingDeliveryConfirmationType, 'Postage Billing Delivery Confirmation'),
    (ReturnPostageBillingTrackingType, 'Return Postage Billing Tracking'),
    (ReturnPostageBillingPostageType, 'Return Postage Billing Postage'),
    (ReturnPostageBillingFuelSurchargeType, 'Return Postage Billing FuelSurcharge'),
    (ReturnPostageBillingOversizeSurchargeType, 'Return Postage Billing Oversize Surcharge'),
    (ReturnPostageBillingDeliveryAreaSurchargeType, 'Return Postage Billing Delivery Area Surcharge'),
    (AdjustmentOtherType, 'Other'),
)
