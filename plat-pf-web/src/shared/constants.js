import { DSType } from '@/shared/constants/ds.constant'
import cloneDeep from 'lodash/cloneDeep'
export const DEFAULT_CHANNEL = 'amazon.com'

export const CURRENCY_FORMAT = {
  type: 'currency',
  common: {
    plain: {
      nil: 'NULL', // default NULL
      empty: 'EMPTY', // default EMPTY
      na: 'N/A'
    },
    html: {
      nil: '<span class="d-null">null</span>',
      empty: '<span class="empty">empty</span>',
      na: '<span class="d-na">n/a</span>'
    },
    prefix: null
  },
  config: {
    currency: {
      symbol: '$',
      symbolPrefix: true,
      inCents: false
    },
    numeric: {
      comma: true,
      precision: 2,
      siPrefix: false
    }
  }
}

export const EDIT_ITEMS_DATA_FIELD = [
  // Sale Group
  {
    group: 'INFO',
    data: [
      {
        id: 'sku',
        name: 'sku',
        type: 'input',
        label: 'SKU',
        format: ['readonly']
      },
      {
        id: 'upc',
        name: 'upc',
        type: 'input',
        label: 'UPC',
        rules: ['upc']
      },
      {
        id: 'asin',
        name: 'asin',
        type: 'input',
        label: 'ASIN',
        rules: ['length:10']
      },
      {
        id: 'title',
        name: 'title',
        type: 'input',
        label: 'Title',
        format: ['required']
      },
      {
        id: 'description',
        name: 'description',
        type: 'input',
        label: 'Description',
        format: ['required']
      },
      {
        id: 'product_number',
        name: 'product_number',
        type: 'input',
        label: 'Product Number',
        format: ['required']
      },
      {
        id: 'parent_asin',
        name: 'parent_asin',
        type: 'input',
        label: 'Parent ASIN',
        format: ['required']
      }
    ]
  },
  {
    group: 'hide',
    data: [
      {
        id: 'style',
        name: 'style',
        type: 'combobox',
        label: 'Style'
      },
      {
        id: 'size',
        name: 'size',
        type: 'combobox',
        label: 'Size'
      },
      {
        id: 'brand',
        name: 'brand',
        type: 'combobox',
        label: 'Brand'
      },
      {
        id: 'est_shipping_cost',
        name: 'est_shipping_cost',
        type: 'input',
        label: 'Estimated Shipping Cost',
        format: ['currency'],
        rules: ['currency']
      },
      {
        id: 'est_drop_ship_cost',
        name: 'est_drop_ship_cost',
        type: 'input',
        label: 'Estimated Dropship Cost',
        format: ['currency'],
        rules: ['currency']
      },
      {
        id: 'product_type',
        name: 'product_type',
        type: 'input',
        label: 'Product Type',
        format: ['required']
      }
    ]
  },
  {
    group: 'COGs',
    data: [
      {
        id: 'cogs',
        name: 'cogs',
        type: 'cogs'
      }
    ]
  }
]

export const EDITABLE_DATA_FIELD = [
  // Sale Group
  {
    group: 'sale',
    data: [
      {
        id: 'sale_id', // following BE variable
        name: 'sale_id', // following column of data source
        type: 'input', // input | datepicker | textarea | combobox
        format: ['readonly'] // readonly | datetime | currency | select (use with 'combobox type')
        // rules: [] // all rules from vee-validate && your own custom rules
      },
      {
        id: 'channel_id',
        name: 'channel_id',
        type: 'input',
        format: ['readonly']
      },
      {
        id: 'channel_name',
        name: 'channel_name',
        type: 'input',
        format: ['readonly']
      },
      {
        id: 'fulfillment_type',
        name: 'fulfillment_type',
        type: 'combobox',
        format: ['select']
      },
      {
        id: 'is_prime',
        name: 'is_prime',
        type: 'checkbox',
        format: ['checkbox']
      },
      {
        id: 'sale_date',
        name: 'sale_date',
        type: 'datepicker',
        format: ['datetime'],
        rules: ['required', 'beforeDate:@item_ship_date']
      },
      {
        id: 'ship_date',
        name: 'item_ship_date',
        type: 'datepicker',
        format: ['datetime']
      },
      {
        id: 'created',
        name: 'created',
        type: 'input',
        format: ['datetime', 'readonly']
      },
      {
        id: 'modified',
        name: 'modified',
        type: 'input',
        format: ['datetime', 'readonly']
      }
    ]
  },
  // Info Group
  {
    group: 'info',
    data: [
      {
        id: 'title',
        name: 'title',
        type: 'textarea'
      },
      {
        id: 'upc',
        name: 'upc',
        type: 'input',
        rules: ['upc']
      },
      {
        id: 'sku',
        name: 'sku',
        type: 'input',
        rules: ['required']
      },
      {
        id: 'asin',
        name: 'asin',
        type: 'input',
        rules: ['length:10']
      },
      {
        id: 'brand_sku',
        name: 'brand_sku',
        type: 'input'
      },
      {
        id: 'size_variant',
        name: 'size',
        type: 'combobox'
      },
      {
        id: 'style_variant',
        name: 'style',
        type: 'combobox'
      },
      {
        id: 'brand',
        name: 'brand',
        type: 'combobox'
      },
      {
        id: 'segment',
        name: 'segment',
        type: 'textarea'
      },
      {
        id: 'product_number',
        name: 'product_number',
        type: 'input'
      },
      {
        id: 'product_type',
        name: 'product_type',
        type: 'input'
      },
      {
        id: 'parent_asin',
        name: 'parent_asin',
        type: 'input'
      }
    ]
  },
  // Charges Group
  {
    group: 'charges',
    data: [
      {
        id: 'sale_charged',
        name: 'item_sale_charged',
        type: 'input',
        format: ['currency'],
        rules: ['required', 'currency', 'positive'],
        helpText: (internalData) => {
          if (!internalData && !internalData.channel_id) return
          const channelID = internalData.channel_id.base
          const targetLink = `https://sellercentral.amazon.com/payments/event/view?accountType=ALL&orderId=${channelID}&resultsPerPage=10&pageNumber=1`
          return `This is a copy of Amazon Seller Central; Please click <a href='${targetLink}' target='_blank'>here</a> to double check the financial transactions.`
        }
      },
      {
        id: 'shipping_charged',
        name: 'item_shipping_charged',
        type: 'input',
        format: ['currency'],
        rules: ['currency', 'positive']
      },
      {
        id: 'tax_charged',
        name: 'item_tax_charged',
        type: 'input',
        format: ['currency'],
        rules: ['currency', 'positive']
      }
    ],
    subGroup: [
      {
        group: 'address',
        data: [
          {
            id: 'state',
            name: 'state',
            type: 'input',
            rules: ['max:45']
          },
          {
            id: 'country',
            name: 'country',
            type: 'input'
          },
          {
            id: 'city',
            name: 'city',
            type: 'input'
          },
          {
            id: 'postal_code',
            name: 'postal_code',
            type: 'input'
          },
          {
            id: 'recipient_name',
            name: 'recipient_name',
            type: 'input'
          },
          {
            id: 'customer_name',
            name: 'customer_name',
            type: 'input'
          },
          {
            id: 'tracking_fedex_id',
            name: 'tracking_fedex_id',
            type: 'input'
          }
        ]
      }
    ]
  },
  // Costs Group
  {
    group: 'costs',
    data: [
      {
        id: 'cog',
        name: 'cog',
        type: 'input',
        format: ['currency'],
        rules: ['currency', 'positive'],
        helpText: () => 'COGs = Unit COGs * Quantity'
      },
      {
        id: 'estimated_shipping_cost',
        name: 'estimated_shipping_cost',
        type: 'input',
        format: ['currency'],
        rules: ['currency', 'positive']
      },
      {
        id: 'actual_shipping_cost',
        name: 'actual_shipping_cost',
        type: 'input',
        format: ['currency'],
        rules: ['currency', 'positive']
      },
      {
        id: 'channel_tax_withheld',
        name: 'channel_tax_withheld',
        type: 'input',
        format: ['currency'],
        rules: ['currency', 'positive']
      },
      {
        id: 'reimbursement_costs',
        name: 'item_reimbursement_costs',
        type: 'input',
        format: ['currency'],
        rules: ['currency', 'positive']
      },
      {
        id: 'freight_cost',
        name: 'freight_cost',
        type: 'input',
        format: ['currency'],
        rules: ['currency', 'positive']
      },
      {
        id: 'inbound_freight_cost',
        name: 'inbound_freight_cost',
        type: 'input',
        format: ['currency'],
        rules: ['currency']
      },
      {
        id: 'outbound_freight_cost',
        name: 'outbound_freight_cost',
        type: 'input',
        format: ['currency'],
        rules: ['currency']
      },
      {
        id: 'label_cost',
        name: 'label_cost',
        type: 'input',
        format: ['currency'],
        rules: ['currency']
      }
    ],
    subGroup: [
      {
        group: 'fees',
        data: [
          {
            id: 'channel_listing_fee',
            name: 'item_channel_listing_fee',
            type: 'input',
            format: ['currency'],
            rules: ['currency']
          },
          {
            id: 'return_postage_billing',
            name: 'return_postage_billing',
            type: 'input',
            format: ['currency', 'readonly'],
            rules: ['currency']
          },
          {
            id: 'other_channel_fees',
            name: 'item_other_channel_fees',
            type: 'input',
            format: ['currency'],
            rules: ['currency']
          },
          {
            id: 'warehouse_processing_fee',
            name: 'warehouse_processing_fee',
            type: 'input',
            format: ['currency'],
            rules: ['currency']
          }
        ]
      }
    ]
  },

  // Summary Group
  {
    group: 'summary',
    data: [
      {
        id: 'sale_status',
        name: 'item_sale_status',
        type: 'combobox',
        format: ['select']
      },
      {
        id: 'profit_status',
        name: 'item_profit_status',
        type: 'combobox',
        format: ['select']
      },
      {
        id: 'profit',
        name: 'item_profit',
        type: 'input',
        format: ['readonly', 'currency']
      },
      {
        id: 'margin',
        name: 'item_margin',
        type: 'input',
        format: ['readonly', 'percent']
      }
    ],
    subGroup: [
      {
        group: 'Accuracy',
        data: [
          {
            id: 'shipping_cost_accuracy',
            name: 'shipping_cost_accuracy',
            type: 'input',
            format: ['percent'],
            rules: ['between:0,100']
          },
          {
            id: 'channel_listing_fee_accuracy',
            name: 'channel_listing_fee_accuracy',
            type: 'input',
            format: ['percent'],
            rules: ['between:0,100']
          },
          {
            id: 'sale_charged_accuracy',
            name: 'sale_charged_accuracy',
            type: 'input',
            format: ['percent'],
            rules: ['between:0,100']
          },
          {
            id: 'warehouse_processing_fee_accuracy',
            name: 'warehouse_processing_fee_accuracy',
            type: 'input',
            format: ['percent'],
            rules: ['between:0,100']
          },
          {
            id: 'fulfillment_type_accuracy',
            name: 'fulfillment_type_accuracy',
            type: 'input',
            format: ['percent'],
            rules: ['between:0,100']
          },
          {
            id: 'freight_cost_accuracy',
            name: 'freight_cost_accuracy',
            type: 'input',
            format: ['percent'],
            rules: ['between:0,100']
          },
          {
            id: 'inbound_freight_cost_accuracy',
            name: 'inbound_freight_cost_accuracy',
            type: 'input',
            format: ['percent'],
            rules: ['between:0,100']
          },
          {
            id: 'outbound_freight_cost_accuracy',
            name: 'outbound_freight_cost_accuracy',
            type: 'input',
            format: ['percent'],
            rules: ['between:0,100']
          },
          {
            id: 'channel_tax_withheld_accuracy',
            name: 'channel_tax_withheld_accuracy',
            type: 'input',
            format: ['percent'],
            rules: ['between:0,100']
          }
        ]
      }
    ]
  }
]

export const NUMERIC_ACTIONS = {
  ADD: 'add',
  SUBTRACT: 'subtract',
  MULTIPLY_BY: 'multiply_by',
  DIVIDE_BY: 'divide_by',
  PERCENT_INCREASE: 'percent_increase',
  PERCENT_DECREASE: 'percent_decrease',
  UNDO_PERCENT_INCREASE: 'undo_percent_increase',
  UNDO_PERCENT_DECREASE: 'undo_percent_decrease'
}

export const CHANGE_TO_ACTION = 'change_to'

export const UPDATE_ACTIONS = {
  numberic: [
    { value: CHANGE_TO_ACTION, label: 'Change to' },
    { value: NUMERIC_ACTIONS.ADD, label: 'Add' },
    { value: NUMERIC_ACTIONS.SUBTRACT, label: 'Subtract' },
    { value: NUMERIC_ACTIONS.MULTIPLY_BY, label: 'Multiply by' },
    { value: NUMERIC_ACTIONS.DIVIDE_BY, label: 'Divide by' },
    { value: NUMERIC_ACTIONS.PERCENT_INCREASE, label: 'Percent increase' },
    { value: NUMERIC_ACTIONS.PERCENT_DECREASE, label: 'Percent decrease' },
    { value: NUMERIC_ACTIONS.UNDO_PERCENT_INCREASE, label: 'Undo percent increase' },
    { value: NUMERIC_ACTIONS.UNDO_PERCENT_DECREASE, label: 'Undo percent decrease' }
  ],
  text: [
    { value: CHANGE_TO_ACTION, label: 'Change to' },
    { value: 'append', label: 'Append' },
    { value: 'prepend', label: 'Prepend' }
  ],
  default: [
    { value: CHANGE_TO_ACTION, label: 'Change to' }
  ]
}

export const NUMERIC_FORMAT = {
  type: 'numeric',
  common: {
    plain: {
      nil: 'NULL', // default NULL
      empty: 'EMPTY', // default EMPTY
      na: 'N/A'
    },
    html: {
      nil: '<span class="d-null">null</span>',
      empty: '<span class="empty">empty</span>',
      na: '<span class="d-na">n/a</span>'
    },
    prefix: null
  },
  config: {
    comma: true,
    precision: 0,
    siPrefix: false
  }
}

export const OPTIONS_VIEW = [
  {
    text: 'Standard Layout',
    value: DSType.STANDARD_LAYOUT
  },
  {
    text: 'Financial Layout',
    value: DSType.FINANCIAL_LAYOUT
  }
]

export const DEFAULT_VIEW = DSType.STANDARD_LAYOUT

export const DEFAULT_SUMMARIES = [
  {
    label: '',
    column: 'item_sale_charged',
    format: cloneDeep(CURRENCY_FORMAT),
    expr: `SUM (@item_sale_charged) as 'item_sale_charged'`,
    style: { justifyContent: 'flex-end' }
  },
  {
    label: '',
    column: 'item_shipping_charged',
    format: cloneDeep(CURRENCY_FORMAT),
    expr: `SUM (@item_shipping_charged) as 'item_shipping_charged'`,
    style: { justifyContent: 'flex-end' }
  },
  {
    label: '',
    column: 'item_tax_charged',
    format: cloneDeep(CURRENCY_FORMAT),
    expr: `SUM (@item_tax_charged) as 'item_tax_charged'`,
    style: { justifyContent: 'flex-end' }
  },
  {
    label: '',
    column: 'cog',
    format: cloneDeep(CURRENCY_FORMAT),
    expr: `SUM (@cog) as 'cog'`,
    style: { justifyContent: 'flex-end' }
  },
  {
    label: '',
    column: 'quantity',
    format: cloneDeep(NUMERIC_FORMAT),
    expr: `SUM (@quantity) as 'quantity'`,
    style: { justifyContent: 'flex-end' }
  },
  {
    label: 'Sum',
    column: 'actual_shipping_cost',
    format: cloneDeep(CURRENCY_FORMAT),
    expr: `SUM (@actual_shipping_cost) as 'actual_shipping_cost_sum'`,
    style: { justifyContent: 'flex-end' },
    alias: 'actual_shipping_cost_sum'
  },
  {
    label: 'Sum',
    column: 'estimated_shipping_cost',
    format: cloneDeep(CURRENCY_FORMAT),
    expr: `SUM (@estimated_shipping_cost) as 'estimated_shipping_cost_sum'`,
    style: { justifyContent: 'flex-end' },
    alias: 'estimated_shipping_cost_sum'
  },
  {
    label: 'Sum',
    column: 'item_shipping_cost',
    format: cloneDeep(CURRENCY_FORMAT),
    expr: `SUM (@item_shipping_cost) as 'item_shipping_cost_sum'`,
    style: { justifyContent: 'flex-end' },
    alias: 'item_shipping_cost_sum'
  },
  {
    label: 'Avg',
    column: 'item_shipping_cost',
    format: cloneDeep(CURRENCY_FORMAT),
    expr: `AVG (@item_shipping_cost) as 'item_shipping_cost_avg'`,
    style: { justifyContent: 'flex-end' },
    alias: 'item_shipping_cost_avg'
  },
  {
    label: 'Avg',
    column: 'actual_shipping_cost',
    format: cloneDeep(CURRENCY_FORMAT),
    expr: `AVG (@actual_shipping_cost) as 'actual_shipping_cost_avg'`,
    style: { justifyContent: 'flex-end' },
    alias: 'actual_shipping_cost_avg'
  },
  {
    label: 'Avg',
    column: 'estimated_shipping_cost',
    format: cloneDeep(CURRENCY_FORMAT),
    expr: `AVG (@estimated_shipping_cost) as 'estimated_shipping_cost_avg'`,
    style: { justifyContent: 'flex-end' },
    alias: 'estimated_shipping_cost_avg'
  },
  {
    label: '',
    column: 'item_total_charged',
    format: cloneDeep(CURRENCY_FORMAT),
    expr: `SUM (@item_total_charged) as 'item_total_charged'`,
    style: { justifyContent: 'flex-end' }
  },
  {
    label: '',
    column: 'item_total_cost',
    format: cloneDeep(CURRENCY_FORMAT),
    expr: `SUM (@item_total_cost) as 'item_total_cost'`,
    style: { justifyContent: 'flex-end' }
  },
  {
    label: '',
    column: 'item_profit',
    format: cloneDeep(CURRENCY_FORMAT),
    expr: `SUM (@item_profit) as 'item_profit'`,
    style: { justifyContent: 'flex-end' }
  },
  {
    label: '',
    column: 'item_channel_listing_fee',
    format: cloneDeep(CURRENCY_FORMAT),
    expr: `SUM (@item_channel_listing_fee) as 'item_channel_listing_fee'`,
    style: { justifyContent: 'flex-end' }
  },
  {
    label: '',
    column: 'return_postage_billing',
    format: cloneDeep(CURRENCY_FORMAT),
    expr: `SUM (@return_postage_billing) as 'return_postage_billing'`,
    style: { justifyContent: 'flex-end' }
  },
  {
    label: '',
    column: 'item_other_channel_fees',
    format: cloneDeep(CURRENCY_FORMAT),
    expr: `SUM (@item_other_channel_fees) as 'item_other_channel_fees'`,
    style: { justifyContent: 'flex-end' }
  },
  {
    label: '',
    column: 'item_reimbursement_costs',
    format: cloneDeep(CURRENCY_FORMAT),
    expr: `SUM (@item_reimbursement_costs) as 'item_reimbursement_costs'`,
    style: { justifyContent: 'flex-end' }
  },
  {
    label: '',
    column: 'refund_admin_fee',
    format: cloneDeep(CURRENCY_FORMAT),
    expr: `SUM (@refund_admin_fee) as 'refund_admin_fee'`,
    style: { justifyContent: 'flex-end' }
  },
  {
    label: '',
    column: 'freight_cost',
    format: cloneDeep(CURRENCY_FORMAT),
    expr: `SUM (@freight_cost) as 'freight_cost'`,
    style: { justifyContent: 'flex-end' }
  },
  {
    label: '',
    column: 'inbound_freight_cost',
    format: cloneDeep(CURRENCY_FORMAT),
    expr: `SUM (@inbound_freight_cost) as 'inbound_freight_cost'`,
    style: { justifyContent: 'flex-end' }
  },
  {
    label: '',
    column: 'outbound_freight_cost',
    format: cloneDeep(CURRENCY_FORMAT),
    expr: `SUM (@outbound_freight_cost) as 'outbound_freight_cost'`,
    style: { justifyContent: 'flex-end' }
  },
  {
    label: '',
    column: 'user_provided_cost',
    format: cloneDeep(CURRENCY_FORMAT),
    expr: `SUM (@user_provided_cost) as 'user_provided_cost'`,
    style: { justifyContent: 'flex-end' }
  },
  {
    label: '',
    column: 'item_margin',
    format: {
      type: 'numeric',
      common: {
        plain: {
          nil: 'NULL', // default NULL
          empty: 'EMPTY', // default EMPTY
          na: 'N/A'
        },
        html: {
          nil: '<span class="d-null">null</span>',
          empty: '<span class="empty">empty</span>',
          na: '<span class="d-na">n/a</span>'
        },
        prefix: null,
        suffix: '%'
      },
      config: {
        comma: true,
        precision: 2,
        siPrefix: false
      }
    },
    expr: `(SUM (@item_profit) / SUM (@item_sale_charged) * 100)as 'item_margin'`,
    style: { justifyContent: 'flex-end' }
  }
]

export const DEFAULT_TABLE_SUMMARY = {
  enabled: true,
  position: 'header',
  labelColumnSummary: '',
  labelActionColumn: '',
  summaries: cloneDeep(DEFAULT_SUMMARIES)
}

export const WIDGET_NAME = {
  dollar: 'dollar',
  unit: 'unit'
}

export const SALE_STATUS_TEXT_BLUR = ['Unshipped', 'Cancelled']

export const BRAND_OPTION = { label: 'Brand', value: 'brand' }
export const SKU_OPTION = { label: 'SKU', value: 'sku' }

export const BRAND_ALL_OPTION = { label: 'All brands', value: null }
export const SKU_ALL_OPTION = { label: 'All SKU', value: null }
export const FULFILLMENT_ALL_OPTION = { label: 'All fulfillment', value: null }
export const PERCENT_BIGMOVES_OPTIONS = [
  { label: '> 10%', value: 10 },
  { label: '> 20%', value: 20 },
  { label: '> 30%', value: 30 },
  { label: '> 40%', value: 40 },
  { label: '> 50%', value: 50 }
]
export const DAY_BIGMOVES_OPTIONS = [
  { label: 'Day vs 30Day Avg', value: 'quantity_d_vs_quantity_avg_30d' },
  { label: '30Day vs 12Mo Avg', value: 'quantity_30d_vs_quantity_avg_12m' }
]

export const REPORT_CATEGORIES = {
  getV2SettlementReportDataFlatFileV2: 'GET_V2_SETTLEMENT_REPORT_DATA_FLAT_FILE_V2',
  brandsSummaryMonthlyDataReport: 'BRANDS_SUMMARY_MONTHLY_DATA_REPORT'
}

export const FULFILLMENT_METHODS_ALL = { label: 'All', value: null }
export const FULFILLMENT_METHODS_FBA = { label: 'FBA', value: 'FBA' }
export const FULFILLMENT_METHODS_MFN_DS = { label: 'MFN-DS', value: 'MFN-DS' }

export const CATEGORY_OPTIONS = [
  { label: 'Daily', value: 'daily' },
  { label: '30 Days', value: '30days' },
  { label: 'YTD', value: 'ytd' }
]
export const SEGMENT_OPTIONS = [
  { label: 'All', value: 'all' },
  { label: 'By Product Type', value: 'type' },
  { label: 'By Product', value: 'product' },
  { label: 'By Parent ASIN', value: 'asin' }
]
export const SEGMENT_OPTIONS_FOR_TOP_PERFORMING = [
  {
    label: 'Parent ASIN',
    value: 'parent_asin'
  },
  {
    label: 'SKU',
    value: 'sku'
  },
  {
    label: 'Segment',
    value: 'segment'
  }
]
