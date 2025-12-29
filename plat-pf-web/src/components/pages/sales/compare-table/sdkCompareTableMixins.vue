<script>
import _ from 'lodash'
import baseQueryMixins from '@/mixins/baseQueryMixins'
import { filterColumnName } from '@/shared/filters'
import { UNIQUE_KEY_DS, INVISIBLE_COLUMN_COMPARE_TABLE } from '@/shared/constants/column.constant'

const TypeAggr = {
  AVG: 'avg',
  SUM: 'sum'
}

const marginColumn = {
  name: 'item_margin',
  alias: 'item_margin',
  displayName: 'Margin',
  sortable: {
    enabled: false
  },
  cell: {
    width: 160,
    format: {
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
        prefix: '$',
        suffix: null
      },
      type: 'numeric'
    },
    aggrFormats: {}
  },
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
    },
    expr: `(SUM (@item_profit) / SUM (@item_sale_charged) * 100)as 'item_margin'`
  },
  visible: true,
  type: 'float'
}

const defaultFormat = {
  type: 'text',
  common: {
    plain: {
      nil: 'NULL',
      empty: 'EMPTY',
      na: 'N/A'
    },
    html: {
      nil: '<span class="dc-null-style d-null">null</span>',
      empty: '<span class="dc-empty-style d-empty">empty</span>',
      na: '<span class="dc-na-style d-na">n/a</span>'
    },
    prefix: null,
    suffix: null
  }
}

const buildGroupingCompareTable = (columns, type) => {
  return _.cloneDeep(columns).map(column => {
    const type = column.alias.split('_').pop()
    if (type === TypeAggr.AVG || type === TypeAggr.SUM) {
      return {
        column: column.name,
        alias: column.alias,
        aggregation: type
      }
    }
  })
}

const buildColumnCompareTable = (columns, type) => {
  return _.cloneDeep(columns).map(column => {
    column = {
      ...column,
      alias: `${column.name}_${type}`,
      visible: true,
      displayName: `${column.displayName} (${_.startCase(_.toLower(type))})`,
      ...{
        cell: {
          format: _.cloneDeep(defaultFormat),
          aggrFormats: {
            int: { // config format for aggr type count and distinct
              type: 'numeric',
              common: {
                plain: {
                  nil: 'NULL',
                  empty: 'EMPTY',
                  na: 'N/A'
                },
                html: {
                  nil: '<span class="dc-null-style d-null">null</span>',
                  empty: '<span class="dc-empty-style d-empty">empty</span>',
                  na: '<span class="dc-na-style d-na">n/a</span>'
                },
                prefix: null,
                suffix: null
              },
              config: {
                precision: 0,
                comma: true,
                siPrefix: false
              }
            }
          }
        }
      }
    }
    // column.displayName = this.$options.filters.filterColumnName(column.name)
    if (INVISIBLE_COLUMN_COMPARE_TABLE.includes(column.alias)) column.visible = false
    if (column.name === UNIQUE_KEY_DS) column.isUniqueKey = true

    if (!column.type) {
      column.type = 'text'
    }
    switch (column.type) {
      case 'datetime':
      case 'date': {
        column.cell.width = 100
        column.cell.format.type = 'temporal'
        column.cell.format.config = {
          format: 'MM/DD/YYYY hh:mm A' // any moment format
        }
        column.cell.style = { 'text-align': 'right' }
        break
      }
      case 'boolean': {
        column.cell.format.type = 'bool'
        column.cell.format.config = {
          positive: {
            text: 'Yes', // default Yes
            html: '<span class="d-bool-p">Yes</span>'
          },
          negative: {
            text: 'No', // default No
            html: '<span class="d-bool-n">No</span>'
          }
        }
        break
      }
      case 'number': {
        column.cell.format.type = 'numeric'
        column.cell.format.config = {
          precision: 2
        }
        column.cell.style = { 'text-align': 'right' }
        break
      }
      case 'long': {
        column.cell.format.type = 'numeric'
        column.cell.format.config = {
          precision: 0
        }
        break
      }
      case 'float': {
        column.cell.format.type = 'numeric'
        column.cell.format.config = {
          precision: 2
        }
        break
      }
    }
    switch (column.name) {
      case 'refund_admin_fee': {
        column.cell.width = 160
        break
      }
      case 'fulfillment_type': {
        column.cell.width = 145
        column.cell.computeClass = (valueObj, rowValue) => {
          return rowValue.fulfillment_type_accuracy && rowValue.fulfillment_type_accuracy.base < 100 ? 'inaccurate-style' : ''
        }
        break
      }
      case 'channel_tax_withheld': {
        column.cell.width = 145
        column.cell.computeClass = (valueObj, rowValue) => {
          return rowValue.channel_tax_withheld_accuracy && rowValue.channel_tax_withheld_accuracy.base < 100 ? 'inaccurate-style' : ''
        }
        break
      }
      case 'sku': {
        column.cell.width = 140
        break
      }
      case 'item_sale_status':
      case 'state':
      case 'asin':
      case 'item_profit':
      case 'item_profit_status': {
        column.cell.width = 160
        break
      }
      case 'title': {
        column.cell.width = 300
        break
      }
      case 'upc':
      case 'item_total_charged':
      case 'cog': {
        column.cell.width = 160
        break
      }
      case 'sale_id': {
        column.cell.format = null
        break
      }
      case 'item_margin': {
        column = {}
        break
      }
      case 'item_channel_listing_fee': {
        column.cell.width = 145
        column.cell.computeClass = (valueObj, rowValue) => {
          return rowValue.channel_listing_fee_accuracy && rowValue.channel_listing_fee_accuracy.base < 100 ? 'inaccurate-style' : ''
        }
        break
      }
      case 'warehouse_processing_fee': {
        column.cell.width = 160
        column.cell.computeClass = (valueObj, rowValue) => {
          return rowValue.warehouse_processing_fee_accuracy && rowValue.warehouse_processing_fee_accuracy.base < 100 ? 'inaccurate-style' : ''
        }
        break
      }
      case 'item_sale_charged':
      case 'estimated_shipping_cost':
      case 'actual_shipping_cost': {
        column.cell.width = 160
        break
      }
      case 'item_shipping_cost': {
        column.cell.width = 145
        column.cell.computeClass = (valueObj, rowValue) => {
          return rowValue.shipping_cost_accuracy && rowValue.shipping_cost_accuracy.base < 100 ? 'inaccurate-style' : ''
        }
        break
      }
      case 'quantity': {
        column.cell.format.type = 'numeric'
        column.cell.format.config = {
          precision: 0
        }
        break
      }
      case 'refunded_quantity': {
        column.cell.format.type = 'numeric'
        column.cell.format.config = {
          precision: 0
        }
        break
      }
      case 'channel_tax_withheld_accuracy':
      case 'inbound_freight_cost_accuracy':
      case 'outbound_freight_cost_accuracy':
      case 'warehouse_processing_fee_accuracy':
      case 'fulfillment_type_accuracy': {
        column.cell.width = 160
        column.cell.format.type = 'numeric'
        column.cell.format.common.suffix = '%'
        column.cell.format.config = {
          precision: 0
        }
        break
      }
      case 'inbound_freight_cost': {
        column.cell.width = 160
        column.cell.computeClass = (valueObj, rowValue) => {
          return rowValue.inbound_freight_cost_accuracy && rowValue.inbound_freight_cost_accuracy.base < 100 ? 'inaccurate-style' : ''
        }
        break
      }
      case 'outbound_freight_cost': {
        column.cell.width = 160
        column.cell.computeClass = (valueObj, rowValue) => {
          return rowValue.outbound_freight_cost_accuracy && rowValue.outbound_freight_cost_accuracy.base < 100 ? 'inaccurate-style' : ''
        }
        break
      }
    }
    return column
  })
}

const orderColumnAlias = [
  'cog_avg',
  'cog_sum',
  'warehouse_processing_fee_avg',
  'warehouse_processing_fee_sum',
  'item_profit_avg',
  'item_profit_sum',
  'refund_admin_fee_avg',
  'refund_admin_fee_sum',
  'item_sale_charged_avg',
  'item_sale_charged_sum'
]

export default {
  data() {
    const titleColumn = {
      name: 'view_title',
      alias: 'view_title',
      displayName: 'View Title',
      sortable: {
        enabled: true
      },
      cell: {
        width: 160,
        format: {
          common: {
            prefix: '$',
            suffix: null
          },
          type: 'string'
        }
      },
      visible: true,
      type: 'text'
    }
    const saleChargedColumns = [
      {
        name: 'item_sale_charged',
        alias: 'item_sale_charged_sum',
        displayName: 'Sale Charged (Sum)',
        sortable: {
          enabled: false
        },
        cell: {
          format: {
            common: {
              prefix: '$',
              suffix: null
            },
            type: 'numeric'
          },
          aggrFormats: {}
        },
        format: {
          type: 'numeric',
          common: {
            prefix: null,
            suffix: ''
          },
          expr: `SUMIF (@item_sale_charged, @item_sale_status in ['Pending', 'Unshipped', 'Shipped', 'Partially Refunded']) as 'item_sale_charged_sum'`
        },
        visible: true,
        type: 'float'
      },
      {
        name: 'item_sale_charged',
        alias: 'item_sale_charged_avg',
        displayName: 'Sale Charged (Avg)',
        sortable: {
          enabled: false
        },
        cell: {
          format: {
            common: {
              prefix: '$',
              suffix: null
            },
            type: 'numeric'
          }
        },
        format: {
          type: 'numeric',
          common: {
            prefix: null,
            suffix: ''
          },
          expr: `AVGIF (@item_sale_charged, @item_sale_status in ['Pending', 'Unshipped', 'Shipped', 'Partially Refunded']) as 'item_sale_charged_avg'`
        },
        visible: false,
        type: 'float'
      }
    ]
    return {
      titleColumn,
      saleChargedColumns,
      sdkConfig: {
        menu: {
          enabled: false
        },
        widget: {
          title: {
            enabled: false
          }
        },
        exportConfig: {
          fileName: 'view-comparison'
        },
        filter: {
          builder: {
            enabled: true,
            enabledFilterReadable: false,
            config: {
              ignore: {
                base: {
                  visible: true
                }
              }
            }
          }
        },
        columnManager: {
          enabled: true,
          config: {
            mode: 'single',
            managedColumns: []
          }
        },
        elements: [
          {
            type: 'cbpo-element-comparable-table',
            config: {
              styles: {
                beautyScrollbar: true
              },
              dataSource: '',
              messages: {
                no_data_at_all: 'No data',
                no_data_found: 'No data found'
              },
              header: {
                resizeMinWidth: 5,
                multiline: true,
                draggable: false
              },
              widget: {
                title: {
                  enabled: false
                }
              },
              timezone: {
                enabled: true,
                utc: 'America/Los_Angeles',
                visible: true
              },
              pagination: {
                type: 'lazy',
                limit: 20
              },
              grouping: {
                columns: [],
                aggregations: []
              },
              rows: [],
              columns: [titleColumn, ...saleChargedColumns],
              exportConfig: {
                fileName: 'view-comparison'
              },
              id: 'id-eae27e97-5c48-4764-b8bc-b56d0f15a1e4'
            }
          }
        ]
      },
      defaultSdkConfig: null
    }
  },
  mixins: [baseQueryMixins],
  filters: {
    filterColumnName
  },
  methods: {
    // get, set default config (reset everything before apply new config)
    getDefaultConfig() {
      return _.cloneDeep(this.defaultSdkConfig)
    },
    setDefaultConfig(config) {
      this.defaultSdkConfig = _.cloneDeep(config)
    },
    // set dataSource into config
    setDataSource(dataSourceId) {
      this.sdkConfig.elements[0].config.dataSource = dataSourceId
    },
    setColumns(columns) {
      let dsColumnTypeSum = buildColumnCompareTable(columns, TypeAggr.SUM)
      let dsColumnTypeAvg = buildColumnCompareTable(columns, TypeAggr.AVG)
      let dsColumn = [...dsColumnTypeSum, ...dsColumnTypeAvg, ...this.saleChargedColumns]
      dsColumn = _.sortBy(dsColumn, 'displayName')

      // Filter only get column with type numeric
      dsColumn = dsColumn.filter(column => _.get(column, 'cell.format.type', 'text') === 'numeric')

      // Build grouping
      this.sdkConfig.elements[0].config.grouping.aggregations = buildGroupingCompareTable(dsColumn)

      this.sdkConfig.elements[0].config.columns = [
        _.cloneDeep(this.titleColumn),
        ...orderColumnAlias.map(alias => dsColumn.find(col => col.alias === alias)),
        ...dsColumn.filter(column => !orderColumnAlias.includes(column.alias)),
        marginColumn
      ]
    },
    getEmptyColumns() {
      return []
    },
    // get, set config all
    getConfig() {
      let el = _.cloneDeep(this.sdkConfig)
      return el
    },
    setConfig(config) {
      let el = _.cloneDeep(config)
      this.$set(this, 'sdkConfig', el)
    },
    // get, set Element config
    getElementConfig() {
      let el = _.cloneDeep(this.sdkConfig.elements[0])
      return el
    },
    setElementConfig(elements) {
      let el = _.cloneDeep(elements)
      if (_.get(elements, 'config.timezone')) {
        this.$set(this.sdkConfig.elements[0].config, 'timezone', el.config.timezone)
      }
      this.$set(this.sdkConfig.elements[0].config, 'columns', el.config.columns)
    },
    setTimezone(timezone) {
      let tz = _.cloneDeep(timezone)
      this.$set(this.sdkConfig.elements[0].config, 'timezone', tz)
    },
    // get, set filter
    getEmptyFilter() {
      return {
        builder: {
          enabled: true,
          config: {}
        }
      }
    },
    getFilter() {
      return _.cloneDeep(this.sdkConfig.filter)
    },
    setFilterConfig(filter, type) {
      if (type === 'forceUpdateBaseQuery') {
        this.selectBaseQueryFilter(filter)
      } else {
        const baseQueryFilter = this.setBaseQueryFilter()
        this.$set(filter, 'base', baseQueryFilter)
      }
      if (_.isEmpty(_.get(filter, 'builder.config.ignore'))) {
        filter.builder.config.ignore = {
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
      // reset filter
      this.$set(this.sdkConfig.elements[0].config.pagination, 'current', 1)
      this.$set(this.sdkConfig, 'filter', _.cloneDeep(filter))
    },
    setFormOptions(form) {
      this.$set(this.sdkConfig.filter.builder.config, 'form', form)
    },
    setDefaultWidth() {
      this.sdkConfig.elements[0].config.columns.map(column => {
        if (!_.get(column, 'cell.width')) {
          _.set(column, 'cell.width', 100)
        }
      })
    }
  },
  computed: {
    getColumnsForColumnManager() {
      return this.sdkConfig.elements.map(e => {
        let columns = e.config.columns ? e.config.columns.map((c, i) => {
          let { name, displayName, visible, alias } = c
          return { name, displayName: displayName, visible: visible !== undefined ? visible : true, alias }
        }) : []
        let table = { columns }
        return table
      })
    }
  }
}
</script>
