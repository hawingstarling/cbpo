from app.financial.variable.transaction.type.adjustment import PostageBillingPostageType, \
    ReturnPostageBillingTrackingType, ReturnPostageBillingPostageType, ReturnPostageBillingFuelSurchargeType, \
    ReturnPostageBillingOversizeSurchargeType, ReturnPostageBillingDeliveryAreaSurchargeType
from app.financial.variable.transaction.type.charge import TaxType, ShippingTaxType, GiftWrapTaxType, \
    MarketplaceFacilitatorTaxPrincipalType, MarketplaceFacilitatorTaxShippingType, \
    MarketplaceFacilitatorTaxGiftwrapType, MarketplaceFacilitatorTaxOtherType
from app.financial.variable.transaction.type.fee import Commission_Type, RefundCommission_Type, \
    FBAPerUnitFulfillmentFee_Type, FBAPerOrderFulfillmentFee_Type, FBACustomerReturnPerOrderFee_Type, \
    FBACustomerReturnPerUnitFee_Type, FBACustomerReturnWeightBasedFee_Type

USD_CURRENCY = 'USD'

# key of source and dest
AMAZON_KEY = 'Amazon'
OE_KEY = 'OE'

CHANNEL_LISTING_FEE_TYPES = [Commission_Type]

REFUND_ADMIN_FEE_TYPES = [RefundCommission_Type]

TAX_CHARGED_TYPES = [TaxType, ShippingTaxType, GiftWrapTaxType]

# Using shipping cost and exclude in others channel fees [FBA]
FBA_SHIPPING_COST_TYPES = [FBAPerUnitFulfillmentFee_Type, FBAPerOrderFulfillmentFee_Type]

# Using shipping cost [MFN, Is Prime]
POSTAGE_BILLING_TYPES = [PostageBillingPostageType]

# Using Other Channel Fees
RETURN_POSTAGE_BILLING_TYPES = [ReturnPostageBillingTrackingType, ReturnPostageBillingPostageType,
                                ReturnPostageBillingFuelSurchargeType, ReturnPostageBillingOversizeSurchargeType,
                                ReturnPostageBillingDeliveryAreaSurchargeType]

TRANS_COLUMN_EXIST_ADJUSTMENT_EVENT = ['shipping_cost']

CHANNEL_TAX_WITHHELD = [MarketplaceFacilitatorTaxPrincipalType, MarketplaceFacilitatorTaxShippingType,
                        MarketplaceFacilitatorTaxGiftwrapType, MarketplaceFacilitatorTaxOtherType]

#
OTHER_CHANNEL_FEES_REFUNDED = [FBACustomerReturnPerOrderFee_Type, FBACustomerReturnPerUnitFee_Type,
                               FBACustomerReturnWeightBasedFee_Type]
