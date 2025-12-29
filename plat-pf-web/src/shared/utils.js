import {filterColumnName} from '@/shared/filters'
import {get} from 'lodash'
export function random(min, max) {
  return Math.floor(Math.random() * (max - min + 1) + min)
}

/**
 * Randomize array element order in-place.
 * Using Durstenfeld shuffle algorithm.
 */
export const slugify = (string) => {
  return string.replace(/\s+/g, '-') // Replace spaces with hyphens
}

export const shuffleArray = (array) => {
  for (let i = array.length - 1; i > 0; i--) {
    let j = Math.floor(Math.random() * (i + 1))
    let temp = array[i]
    array[i] = array[j]
    array[j] = temp
  }
  return array
}

export const buildUrlQueryString = (object) => {
  let url = ''
  let keys = Object.keys(object)
  keys.forEach((k, i) => {
    if (object[k] !== '' && object[k] !== undefined && object[k] !== null) {
      url += `${k}=${encodeURIComponent(object[k])}&`
    }
  })
  return `${url.replace(/([&?])$/g, '')}`
}

export const isValidASINOrUPC = (value) => {
  if (!value) {
    return true
  }
  let list = value.replace(/[\s+,]/g, '\n').split('\n').filter(e => !!e)
  if (!list.length) {
    return false
  }
  const regexps = [
    // ASIN regex
    new RegExp(`^[A-Z0-9]{10}$`),
    // UPC regex
    new RegExp(`^[0-9]{12}$`),
    // EAN regex
    new RegExp(`^[0-9]{13}$`)
  ]
  return list
    .map(
      a => regexps
        .map(r => !!a.trim().match(r))
        .filter(r => r === true).length > 0
    )
    .filter(r => r === false).length === 0
}

export const isASIN = (string) => {
  let asinRegex = /^[A-Z0-9]{10}$/
  return string.match(asinRegex) !== null
}

export const isUPC = (string) => {
  let upcRegex = /^[0-9]{12}$/
  return string.match(upcRegex) !== null
}

export const isEAN = (string) => {
  let eanRegex = /^[0-9]{13}$/
  return string.match(eanRegex) !== null
}

export const landingComponents = [
  {
    router_name: 'MTBrandOverview',
    view_permission_code: 'ovview',
    edit_permission_code: 'ovedit'
  },
  {
    router_name: 'MTOperationalAnalytics',
    view_permission_code: 'oaview',
    edit_permission_code: 'oaedit'
  },
  {
    router_name: 'MTProductListings',
    view_permission_code: 'plview',
    edit_permission_code: 'pledit'
  },
  {
    router_name: 'MTMarketingPerformance',
    view_permission_code: 'mpview',
    edit_permission_code: 'mpedit'
  },
  {
    router_name: 'MTCustomerReviews',
    view_permission_code: 'crview',
    edit_permission_code: 'credit'
  },
  {
    router_name: 'MTCategoryMarketShare',
    view_permission_code: 'cmview',
    edit_permission_code: 'cmedit'
  },
  {
    router_name: 'MTSellersAndInvestigations',
    view_permission_code: 'siview',
    edit_permission_code: 'siedit'
  },
  {
    router_name: 'MTAddCustomDashboard',
    view_permission_code: 'cdview',
    edit_permission_code: 'cdedit'
  }
]

export const checkFieldFormatMixins = {
  methods: {
    isReadonly(formatField) {
      return Array.isArray(formatField)
        ? formatField.includes('readonly')
        : false
    },
    isCurrency(formatField) {
      return Array.isArray(formatField)
        ? formatField.includes('currency')
        : false
    },
    isPercent(formatField) {
      return Array.isArray(formatField)
        ? formatField.includes('percent')
        : false
    },
    isSelect(formatField) {
      return Array.isArray(formatField)
        ? formatField.includes('select')
        : false
    },
    isDatetime(formatField) {
      return Array.isArray(formatField)
        ? formatField.includes('datetime')
        : false
    },
    isCheckBox(formatField) {
      return Array.isArray(formatField)
        ? formatField.includes('checkbox')
        : false
    }
  }
}
export const validateMixins = {
  filters: {
    filterColumnName
  },
  computed: {
    isHasError() {
      return errors => (errors.length ? false : null)
    },
    stringRules() {
      return (rules) => rules ? rules.join('|') : null
    },
    filteredName() {
      return (name) => this.$options.filters.filterColumnName(name)
    },
    isValidString() {
      // Function help to check if the string only contains whitespace.
      return (string) => {
        const result = string.replace(/ /g, '')
        return result
      }
    }
  }
}

export const convertedPermissions = {
  filter: {
    create: 'SALE_REPORT_CREATE_FILTER',
    edit: 'SALE_REPORT_EDIT_FILTER',
    delete: 'SALE_REPORT_DELETE_FILTER',
    share: 'SALE_REPORT_SHARE_FILTER',
    view: 'SALE_REPORT_VIEW_FILTER'
  },
  columnSet: {
    create: 'SALE_REPORT_CREATE_COLUMN',
    edit: 'SALE_REPORT_EDIT_COLUMN',
    delete: 'SALE_REPORT_DELETE_COLUMN',
    share: 'SALE_REPORT_SHARE_COLUMN',
    view: 'SALE_REPORT_VIEW_COLUMN'
  },
  view: {
    create: 'SALE_REPORT_CREATE_REPORT',
    edit: 'SALE_REPORT_EDIT_REPORT',
    delete: 'SALE_REPORT_DELETE_REPORT',
    share: 'SALE_REPORT_SHARE_REPORT',
    viewAll: 'SALE_REPORT_VIEW_ALL_REPORT',
    view24h: 'SALE_REPORT_VIEW_24H_REPORT'
  },
  sale: {
    import: 'SALE_IMPORT',
    viewAll: 'SALE_VIEW_ALL',
    view24h: 'SALE_VIEW_24H',
    bulkEdit: 'SALE_BULK_EDIT',
    bulkDelete: 'SALE_BULK_DELETE',
    singleEdit: 'SALE_SINGLE_EDIT',
    singleDelete: 'SALE_SINGLE_DELETE',
    auditLog: 'SALE_VIEW_AUDIT_LOG',
    bulkProcessingView: 'SALE_BULK_PROCESSING_VIEW'
  },
  admin: {
    tool: 'TOOLS_VIEW',
    activity: 'ACTIVITY_VIEW',
    syncWorkspace: 'SYNC_WORKSPACE',
    generateDS: 'GENERATE_DATASOURCE',
    itemView: 'PF_ITEM_VIEW',
    itemBulkDelete: 'PF_ITEM_BULK_DELETE',
    itemBulkEdit: 'PF_ITEM_BULK_EDIT',
    itemCreate: 'PF_ITEM_CREATE',
    itemDelete: 'PF_ITEM_DELETE',
    itemEdit: 'PF_ITEM_EDIT',
    itemImport: 'PF_ITEM_IMPORT',
    settingsView: 'CLIENT_SETTINGS_VIEW',
    settingsChange: 'CLIENT_SETTINGS_CHANGE'
  },
  brand: {
    edit: 'PF_BRAND_SETTING_EDIT',
    view: 'PF_BRAND_SETTING_VIEW',
    delete: 'PF_BRAND_SETTING_DELETE',
    import: 'PF_BRAND_SETTING_IMPORT',
    export: 'PF_BRAND_SETTING_EXPORT',
    updateItems: 'PF_BRAND_SETTING_UPDATE_ITEMS',
    updateSales: 'PF_BRAND_SETTING_UPDATE_SALES'
  },
  overview: {
    dashboardManagement: 'PF_OVERVIEW_DASHBOARD_MANAGEMENT'
  },
  advertising: {
    dashboardManagement: 'PF_AD_DASHBOARD_MANAGEMENT'
  },
  fedEx: {
    view: 'PF_FEDEX_VIEW',
    import: 'PF_FEDEX_IMPORT'
  },
  repricing: {
    view: 'PF_REPRICING_VIEW',
    edit: 'PF_REPRICING_EDIT',
    delete: 'PF_REPRICING_DELETE'
  },
  cogsConflictsReport: {
    view: 'PF_EXTENSIV_VIEW',
    edit: 'PF_EXTENSIV_EDIT',
    delete: 'PF_EXTENSIV_DELETE',
    import: 'PF_EXTENSIV_IMPORT',
    export: 'PF_EXTENSIV_EXPORT'
  },
  customReport: {
    view: 'PF_CUSTOM_REPORT_VIEW',
    export: 'PF_CUSTOM_REPORT_EXPORT'
  },
  client: {
    isClient: 'PF_CLIENT_IS'
  },
  topASINs: {
    view: 'PF_TOP_ASINs_VIEW',
    edit: 'PF_TOP_ASINs_EDIT',
    delete: 'PF_TOP_ASINs_DELETE',
    import: 'PF_TOP_ASINs_IMPORT',
    export: 'PF_TOP_ASINs_EXPORT'
  }
}

export const saleItems = ['filter', 'columnSet', 'view']

export const numberFormat = (value, locale = 'en-US') => {
  return new Intl.NumberFormat(locale).format(value)
}

export const makeDefaultFilterConfig = (filterConfig) => {
  if (!get(filterConfig, 'builder.config.form')) {
    filterConfig.builder.config.form = {}
  }
  if (!get(filterConfig, 'builder.config.ignore')) {
    filterConfig.builder.config.ignore = {
      global: {
        visible: false,
        value: false
      },
      base: {
        visible: true,
        value: false
      }
    }
  }
  filterConfig.builder.config.hiddenColumns = []
  return filterConfig
}

export const makeDefaultColumnConfig = (columnConfig) => {
  if (!get(columnConfig, 'config.timezone')) {
    columnConfig.timezone = {
      enabled: true,
      utc: 'Antarctica/Davis'
    }
  }
  columnConfig.config.globalControlOptions = {
    aggregation: {
      enabled: false
    },
    globalGrouping: {
      enabled: false,
      config: {
        value: false
      },
      position: 'top'
    },
    grouping: {
      enabled: false
    },
    editColumn: {
      enabled: false
    },
    editColumnLabel: {
      enabled: false
    },
    editColumnFormat: {
      enabled: false
    },
    editBin: {
      enabled: false
    }
  }
  columnConfig.config.compactMode = {
    enabled: false,
    mode: 'high'
  }
  columnConfig.config.header = {
    draggable: false,
    multiline: true,
    resizeMinWidth: 5
  }
  return columnConfig
}

export const addVariantData = (listVariant) => {
  listVariant.push({
    name: 'shipping_cost_accuracy',
    type: 'input',
    value: 100,
    operator: '$eq'
  })
  listVariant.push({
    name: 'channel_listing_fee_accuracy',
    type: 'input',
    value: 100,
    operator: '$eq'
  })
  listVariant.push({
    name: 'sale_charged_accuracy',
    type: 'input',
    value: 100,
    operator: '$eq'
  })
  listVariant.push({
    name: 'warehouse_processing_fee_accuracy',
    type: 'input',
    value: 100,
    operator: '$eq'
  })
  listVariant.push({
    name: 'channel_tax_withheld_accuracy',
    type: 'input',
    value: 100,
    operator: '$eq'
  })
  listVariant.push({
    name: 'fulfillment_type_accuracy',
    type: 'input',
    value: 100,
    operator: '$eq'
  })
  listVariant.push({
    name: 'freight_cost_accuracy',
    type: 'input',
    value: 100,
    operator: '$eq'
  })
  return listVariant
}
export const showCreaterName = (qSelecter, userId) => {
  let userName = ''
  let currentUserId = userId
  if (currentUserId !== qSelecter.user_info.user_id) {
    userName = `(${qSelecter.user_info.username})`
  } else {
    userName = '(You)'
  }
  return userName
}

export const formatLastTime = (time) => {
  if (!time) return null
  const differentDate = new Date() - new Date(time)
  const seconds = Math.floor(differentDate / 1000)
  const minutes = Math.floor(seconds / 60)
  const hours = Math.floor(minutes / 60)
  const days = Math.floor(hours / 24)
  const weeks = Math.floor(days / 7)
  const months = Math.floor(days / 30)
  const years = Math.floor(months / 12)

  if (years > 0) return years === 1 ? '1 year ago' : `${years} years ago`
  if (months > 0) return months === 1 ? '1 month ago' : `${months} months ago`
  if (weeks > 0) return weeks === 1 ? '1 week ago' : `${weeks} weeks ago`
  if (days > 0) return days === 1 ? '1 day ago' : `${days} days ago`
  if (hours > 0) return hours === 1 ? '1 hour ago' : `${hours} hours ago`
  if (minutes > 0) return minutes === 1 ? '1 minute ago' : `${minutes} minutes ago`
  return seconds === 1 ? '1 second ago' : `${seconds} seconds ago`
}
