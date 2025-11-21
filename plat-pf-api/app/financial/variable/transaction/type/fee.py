# Selling on Amazon Fees
Commission_Type = 'Commission'
CouponClipFee_Type = 'CouponClipFee'
CouponRedemptionFee_Type = 'CouponRedemptionFee'
CSBAFee_Type = 'CSBAFee'
FixedClosingFee_Type = 'FixedClosingFee'
FreshInboundTransportationFee_Type = 'FreshInboundTransportationFee'
HighVolumeListingFee_Type = 'HighVolumeListingFee'
ImagingServicesFee_Type = 'ImagingServicesFee'
MFNPostageFee_Type = 'MFNPostageFee'
ReferralFee_Type = 'ReferralFee'
RefundCommission_Type = 'RefundCommission'
SalesTaxCollectionFee_Type = 'SalesTaxCollectionFee'
Subscription_Type = 'Subscription'
TextbookRentalBuyoutFee_Type = 'TextbookRentalBuyoutFee'
TextbookRentalExtensionFee_Type = 'TextbookRentalExtensionFee'
TextbookRentalServiceFee_Type = 'TextbookRentalServiceFee'
VariableClosingFee_Type = 'VariableClosingFee'

# Fulfillment By Amazon Fees
BubblewrapFee_Type = 'BubblewrapFee'
FBACustomerReturnPerOrderFee_Type = 'FBACustomerReturnPerOrderFee'
FBACustomerReturnPerUnitFee_Type = 'FBACustomerReturnPerUnitFee'
FBACustomerReturnWeightBasedFee_Type = 'FBACustomerReturnWeightBasedFee'
FBADisposalFee_Type = 'FBADisposalFee'
FBAFulfillmentCODFee_Type = 'FBAFulfillmentCODFee'
FBAInboundConvenienceFee_Type = 'FBAInboundConvenienceFee'
FBAInboundDefectFee_Type = 'FBAInboundDefectFee'
FBAInboundTransportationFee_Type = 'FBAInboundTransportationFee'
FBAInboundTransportationProgramFee_Type = 'FBAInboundTransportationProgramFee'
FBALongTermStorageFee_Type = 'FBALongTermStorageFee'
FBAOverageFee_Type = 'FBAOverageFee'
FBAPerOrderFulfillmentFee_Type = 'FBAPerOrderFulfillmentFee'
FBAPerUnitFulfillmentFee_Type = 'FBAPerUnitFulfillmentFee'
FBARemovalFee_Type = 'FBARemovalFee'
FBAStorageFee_Type = 'FBAStorageFee'
FBATransportationFee_Type = 'FBATransportationFee'
FBAWeightBasedFee_Type = 'FBAWeightBasedFee'
FulfillmentFee_Type = 'FulfillmentFee'
FulfillmentNetworkFee_Type = 'FulfillmentNetworkFee'
LabelingFee_Type = 'LabelingFee'
OpaqueBaggingFee_Type = 'OpaqueBaggingFee'
PolybaggingFee_Type = 'PolybaggingFee'
SSOFFulfillmentFee_Type = 'SSOFFulfillmentFee'
TapingFee_Type = 'TapingFee'
TransportationFee_Type = 'TransportationFee'
UnitFulfillmentFee_Type = 'UnitFulfillmentFee'

# link http://docs.developer.amazonservices.com/en_US/finances/Finances_FeeTypes.html
FeeTypeConfig = (
    #
    (Commission_Type, 'Commission Fees'),
    (CouponClipFee_Type, 'Coupon clip fee'),
    (CouponRedemptionFee_Type, 'Coupon redemption fee'),
    (CSBAFee_Type, 'CSBA fee'),
    (FixedClosingFee_Type, 'Per-item fees for Individual Sellers'),
    (FreshInboundTransportationFee_Type, 'Fresh Inbound Transportation Fee'),
    (HighVolumeListingFee_Type, 'High-volume listing fee'),
    (ImagingServicesFee_Type, 'Amazon Imaging fee'),
    (MFNPostageFee_Type, 'Easy Ship Fee'),
    (ReferralFee_Type, 'Referral Fees'),
    (RefundCommission_Type, 'Refund Administration Fee'),
    (SalesTaxCollectionFee_Type, 'Tax Calculation Services Fees'),
    (Subscription_Type, 'Monthly subscription fee'),
    (TextbookRentalBuyoutFee_Type, 'Purchase of Rented Books'),
    (TextbookRentalExtensionFee_Type, 'Rental Extensions'),
    (TextbookRentalServiceFee_Type, 'Rental Book Service Fee'),
    (VariableClosingFee_Type, 'Closing Fees'),
    #
    (BubblewrapFee_Type, 'FBA Prep Service Fees (Bubble Wrap)'),
    (FBACustomerReturnPerOrderFee_Type, 'Returns Processing Fee-Order Handling'),
    (FBACustomerReturnPerUnitFee_Type, 'Returns Processing Fee-Pick & Pack'),
    (FBACustomerReturnWeightBasedFee_Type, 'Returns Processing Fee-Weight Handling'),
    (FBADisposalFee_Type, 'Inventory Disposals'),
    (FBAFulfillmentCODFee_Type, 'Fee for cash on delivery'),
    (FBAInboundConvenienceFee_Type, 'Inventory Placement Service Fees'),
    (FBAInboundDefectFee_Type, 'Unplanned Prep Service Fees'),
    (FBAInboundTransportationFee_Type, 'FBA Amazon-Partnered Carrier Shipment Fee/ Inbound Transportation Charge'),
    (FBAInboundTransportationProgramFee_Type, 'FBA Inbound Transportation Program Fee'),
    (FBALongTermStorageFee_Type, 'FBA Long-Term Storage Fees'),
    (FBAOverageFee_Type, 'FBA Inventory Storage Overage Fee'),
    (FBAPerOrderFulfillmentFee_Type, 'FBA Per Order Fulfillment Fee'),
    (FBAPerUnitFulfillmentFee_Type, 'FBA Fulfillment Fees'),
    (FBARemovalFee_Type, 'Inventory Removals'),
    (FBAStorageFee_Type, 'FBA Inventory Storage Fee'),
    (FBATransportationFee_Type, 'Multi-Channel Fulfillment Weight Handling'),
    (FBAWeightBasedFee_Type, 'FBA Weight Based Fee'),
    (FulfillmentFee_Type, 'FBA Fulfillment Fees'),
    (FulfillmentNetworkFee_Type, 'Cross-Border Fulfillment Fee'),
    (LabelingFee_Type, 'FBA Label Service Fee'),
    (OpaqueBaggingFee_Type, 'FBA Prep Service Fees-Adult-Bagging (black or opaque)'),
    (PolybaggingFee_Type, 'FBA Prep Service Fees (Labeling)'),
    (SSOFFulfillmentFee_Type, 'Fulfillment Fee'),
    (TapingFee_Type, 'FBA Taping Fee'),
    (TransportationFee_Type, 'FBA transportation fee'),
    (UnitFulfillmentFee_Type, 'Unit Fulfillment Fee'),
)
