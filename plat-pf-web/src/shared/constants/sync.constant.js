export const DATASOURCES = {
  AC: 'amazon_seller_central',
  DC: 'data_central',
  PF: 'pf_calculations'
}

export const DATASOURCES_MAPPING = {
  [DATASOURCES.AC]: 'Amazon Seller Central',
  [DATASOURCES.DC]: 'Data Central',
  [DATASOURCES.PF]: 'Calculations'
}

export const DATASOURCES_IGNORE = [
  DATASOURCES.PF
]

export const DATASOURCES_OPTIONS = {
  AC_IS_FORCED: 'ac_is_forced',
  UPC: 'upc',
  BRAND: 'brand',
  COG: 'cog',
  CHANNEL_BRAND: 'channel_brand',
  DC_FIELDS: 'dc_fields',
  DC_IS_OVERRIDE: 'dc_is_override',
  PF_SHIPPING_COST: 'pf_calculation_recalculate_shipping_costs',
  PF_COG: 'pf_calculation_recalculate_cog',
  PF_TOTAL_COST: 'pf_calculation_recalculate_total_costs',
  PF_SEGMENT: 'pf_calculation_recalculate_segments',
  PF_INBOUND_FREIGHT_COST: 'pf_calculation_recalculate_inbound_freight_cost',
  PF_OUTBOUND_FREIGHT_COST: 'pf_calculation_recalculate_outbound_freight_cost',
  PF_FULFILLMENT_TYPE: 'pf_calculation_recalculate_ff',
  PF_USER_PROVIDED_COST: 'pf_calculation_recalculate_user_provided_cost',
  SKU_SKUVAULT: 'pf_calculation_recalculate_skuvault',
  PF_OVERRIDE: 'pf_calculation_is_override'
}

export const DATASOURCES_OPTIONS_MAPPING = {
  [DATASOURCES_OPTIONS.AC_IS_FORCED]: 'Directly from Seller Central',
  [DATASOURCES_OPTIONS.UPC]: 'UPC',
  [DATASOURCES_OPTIONS.BRAND]: 'Brand',
  [DATASOURCES_OPTIONS.CHANNEL_BRAND]: 'Brand (Channel)',
  [DATASOURCES_OPTIONS.COG]: 'Cost',
  [DATASOURCES_OPTIONS.DC_IS_OVERRIDE]: 'Override',
  [DATASOURCES_OPTIONS.PF_SHIPPING_COST]: 'Recalculate/Re-estimate Shipping Costs',
  [DATASOURCES_OPTIONS.PF_COG]: 'Recalculate/Re-estimate COG',
  [DATASOURCES_OPTIONS.PF_TOTAL_COST]: 'Recalculate Total Costs',
  [DATASOURCES_OPTIONS.PF_SEGMENT]: 'Recalculate Segment',
  [DATASOURCES_OPTIONS.PF_INBOUND_FREIGHT_COST]: 'Recalculate Inbound Freight Costs',
  [DATASOURCES_OPTIONS.PF_OUTBOUND_FREIGHT_COST]: 'Recalculate Outbound Freight Costs',
  [DATASOURCES_OPTIONS.PF_FULFILLMENT_TYPE]: 'Recalculate Fulfillment Type',
  [DATASOURCES_OPTIONS.PF_USER_PROVIDED_COST]: 'Recalculate User-Provided Cost',
  [DATASOURCES_OPTIONS.SKU_SKUVAULT]: 'Recalculate SKUVault',
  [DATASOURCES_OPTIONS.PF_OVERRIDE]: 'Override'
}
