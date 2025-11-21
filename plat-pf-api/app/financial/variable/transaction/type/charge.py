# http://docs.developer.amazonservices.com/en_US/finances/Finances_Datatypes.html#ChargeComponent

PrincipalType = 'Principal'
TaxType = 'Tax'
MarketplaceFacilitatorTaxPrincipalType = 'MarketplaceFacilitatorTax-Principal'
MarketplaceFacilitatorTaxShippingType = 'MarketplaceFacilitatorTax-Shipping'
MarketplaceFacilitatorTaxGiftwrapType = 'MarketplaceFacilitatorTax-Giftwrap'
MarketplaceFacilitatorTaxOtherType = 'MarketplaceFacilitatorTax-Other'
DiscountType = 'Discount'
TaxDiscountType = 'TaxDiscount'
CODItemChargeType = 'CODItemCharge'
CODItemTaxChargeType = 'CODItemTaxCharge'
CODOrderChargeType = 'CODOrderCharge'
CODOrderTaxChargeType = 'CODOrderTaxCharge'
CODShippingChargeType = 'CODShippingCharge'
CODShippingTaxChargeType = 'CODShippingTaxCharge'
ShippingChargeType = 'ShippingCharge'
ShippingTaxType = 'ShippingTax'
GoodwillType = 'Goodwill'
GiftWrapType = 'GiftWrap'
GiftWrapTaxType = 'GiftWrapTax'
RestockingFeeType = 'RestockingFee'
ReturnShippingType = 'ReturnShipping'
PointsFeeType = 'PointsFee'
GenericDeductionType = 'GenericDeduction'
FreeReplacementReturnShippingType = 'FreeReplacementReturnShipping'
PaymentMethodFeeType = 'PaymentMethodFee'
ExportChargeType = 'ExportCharge'
SAFETReimbursementType = 'SAFE-TReimbursement'
TCS_CGSTType = 'TCS-CGST'
TCS_SGSTType = 'TCS-SGST'
TCS_IGSTType = 'TCS-IGST'
TCS_UTGSTType = 'TCS-UTGST'

ChargeTypeConfig = (
    (PrincipalType,
     "The selling price of the order item, equal to the selling price of the item multiplied by the quantity ordered"),
    (TaxType,
     "The tax collected by the seller on the Principal"),
    (MarketplaceFacilitatorTaxPrincipalType,
     "The tax withheld by Amazon on the Principal"),
    (MarketplaceFacilitatorTaxShippingType,
     "The tax withheld by Amazon on the ShippingCharge"),
    (MarketplaceFacilitatorTaxGiftwrapType,
     "The tax withheld by Amazon on the Giftwrap charge"),
    (MarketplaceFacilitatorTaxOtherType,
     "The tax withheld by Amazon on other miscellaneous charges"),
    (DiscountType,
     "The promotional discount for an order item"),
    (TaxDiscountType,
     "The tax amount deducted for promotional rebates"),
    (CODItemChargeType,
     "The COD charge for an order item"),
    (CODItemTaxChargeType,
     "The tax collected by the seller on a CODItemCharge"),
    (CODOrderChargeType,
     "The COD charge for an order"),
    (CODOrderTaxChargeType,
     "The tax collected by the seller on a CODOrderCharge"),
    (CODShippingChargeType,
     "Shipping charges for a COD order"),
    (CODShippingTaxChargeType,
     "The tax collected by the seller on a CODShippingCharge"),
    (ShippingChargeType,
     "The shipping charge"),
    (ShippingTaxType,
     "The tax collected by the seller on a ShippingCharge"),
    (GoodwillType,
     "The amount given to a buyer as a gesture of goodwill or to compensate for pain and suffering in the buying experience"),
    (GiftWrapType,
     "The gift wrap charge"),
    (GiftWrapTaxType,
     "The tax collected by the seller on a Giftwrap charge"),
    (RestockingFeeType,
     "The charge that Amazon charges the buyer when returning a product in certain categories"),
    (ReturnShippingType,
     "The amount given to the buyer to compensate for shipping the item back to Amazon in the event Amazon is at fault"),
    (PointsFeeType,
     "The value of Amazon Points deducted from the refund if the buyer does not have enough Amazon Points to cover the deduction"),
    (GenericDeductionType,
     "A generic bad debt deduction"),
    (FreeReplacementReturnShippingType,
     "The compensation for return shipping when a buyer receives the wrong item, requests a free replacement, and returns the incorrect item to Amazon"),
    (PaymentMethodFeeType,
     "The fee collected for certain payment methods in certain marketplaces"),
    (ExportChargeType,
     "The export duty that is charged when Amazon ships an item to an international destination as part of the Amazon Global program"),
    (SAFETReimbursementType,
     "The SAFE-T claim amount for the item"),
    (TCS_CGSTType,
     "Tax Collected at Source (TCS) for Central Goods and Services Tax (CGST)"),
    (TCS_SGSTType,
     "Tax Collected at Source for State Goods and Services Tax (SGST)"),
    (TCS_IGSTType,
     "Tax Collected at Source for Integrated Goods and Services Tax (IGST)"),
    (TCS_UTGSTType,
     "Tax Collected at Source for Union Territories Goods and Services Tax (UTGST)"),
)
