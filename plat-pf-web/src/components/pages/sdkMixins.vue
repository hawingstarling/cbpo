<script>
import _ from 'lodash'
import baseQueryMixins from '@/mixins/baseQueryMixins'
import { UNIQUE_KEY_DS, INVISIBLE_COLUMN } from '@/shared/constants/column.constant'
import { CURRENCY_FORMAT, NUMERIC_FORMAT, SALE_STATUS_TEXT_BLUR } from '@/shared/constants'
import { filterColumnName } from '@/shared/filters'
import { DEFAULT_SUMMARIES } from '@/shared/constants.js'
export default {
  data() {
    return {
      sdkConfig: {
        menu: {
          enabled: false,
          position: 'table',
          config: {
            dataSource: null,
            icons: {css: 'fa fa-ellipsis-v'},
            label: {text: ''},
            selection: {
              dsUrl: '',
              options: [
                // {
                //   label: 'Export Custom CSV',
                //   icon: 'fa fa-cog',
                //   value: 'custom-csv',
                //   type: 'item'
                // }
              ]
            }
          }
        },
        widget: {
          title: {
            text: 'Analysis',
            enabled: false
          }
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
              },
              format: {
                temporal: {
                  date: {
                    type: 'date',
                    formatValue: 'YYYY-MM-DD',
                    formatLabel: 'MM/DD/YYYY'
                  },
                  datetime: {
                    type: 'datetime',
                    formatValue: 'YYYY-MM-DDTHH:mm:ss',
                    formatLabel: 'MM/DD/YYYY hh:mm:ss A'
                  }
                }
              }
            }
          }
        },
        columnManager: {
          enabled: true,
          config: {
            modal: {
              modalClass: 'custom-columns-modal',
              buttons: {
                reset: {
                  text: 'Reset all changes'
                },
                cancel: {
                  visible: false
                }
              }
            },
            hiddenColumns: [
              { name: 'shipping_cost_accuracy' },
              { name: 'channel_listing_fee_accuracy' },
              { name: 'sale_charged_accuracy' }
            ],
            managedColumns: []
          }
        },
        widgetManager: {
          enabled: true,
          config: {
            modal: {
              title: 'Widget Settings',
              modalClass: 'custom-columns-modal',
              buttons: {
                reset: {
                  visible: true,
                  text: 'Reset to Default'
                },
                cancel: {
                  visible: false
                },
                apply: {
                  visible: true,
                  text: 'Save'
                }
              }
            }
          }
        },
        elements: [
          {
            type: 'cbpo-element-table',
            config: {
              styles: {
                beautyScrollbar: true
              },
              dataSource: '',
              widget: {
                title: {
                  enabled: false
                }
              },
              header: {
                draggable: false,
                resizeMinWidth: null,
                multiline: true
              },
              globalControlOptions: {
                aggregation: {
                  enabled: true
                },
                grouping: {
                  enabled: true
                },
                editColumn: {
                  enabled: false
                },
                editColumnLabel: {
                  enabled: true
                },
                editColumnFormat: {
                  enabled: true
                },
                editBin: {
                  enabled: true
                }
              },
              pagination: {
                type: 'lazy',
                limit: 50
              },
              sorting: [{ column: 'sale_date', direction: 'desc' }],
              columns: [],
              timezone: {
                enabled: true,
                utc: 'America/Los_Angeles',
                storable: true
              },
              compactMode: {
                enabled: false,
                mode: 'high'
              },
              rowActions: {
                enabled: true,
                inline: 1,
                display: 'always',
                position: 'left',
                controls: [],
                colWidth: 110,
                eventHandler: (eventName, rowData) => {
                  if (eventName === 'dblClick') {
                    this.openEditModal(rowData)
                  }
                }
              },
              bulkActions: {
                enabled: true,
                labels: {
                  actionColumn: ''
                },
                enableInlineAction: false,
                mode: 'both'
              },
              globalSummary: {
                enabled: true,
                summaries: [{
                  label: 'In view',
                  tooltip: {
                    position: 'top',
                    trigger: '<i class="fa fa-question-circle-o" aria-hidden="true"></i>',
                    content: 'Gross Sales and Unit Sales omit all returns and cancellations shown.'
                  },
                  position: 'right'
                },
                {
                  label: 'Gross Sales',
                  position: 'right',
                  format: _.cloneDeep(CURRENCY_FORMAT),
                  expr: `SUMIF (@item_sale_charged, @'item_sale_status' != 'Returning' AND @'item_sale_status' != 'Partially Returning' AND @'item_sale_status' != 'Refunded' AND @'item_sale_status' != 'Partially Refunded' AND @'item_sale_status' != 'Cancelled') as 'item_sale_charged'`
                },
                {
                  label: 'Unit Sales',
                  position: 'right',
                  format: _.cloneDeep(NUMERIC_FORMAT),
                  expr: `SUMIF (@quantity, @'item_sale_status' != 'Returning' AND @'item_sale_status' != 'Partially Returning' AND @'item_sale_status' != 'Refunded' AND @'item_sale_status' != 'Partially Refunded' AND @'item_sale_status' != 'Cancelled') as 'quantity'`
                },
                {
                  label: 'Row Count',
                  position: 'right',
                  format: {
                    type: 'numeric',
                    config: {
                      comma: true,
                      precision: 0,
                      siPrefix: false
                    }
                  },
                  expr: `COUNT () as 'count_alias'`
                }]
              },
              tableSummary: {
                enabled: true,
                position: 'header',
                labelColumnSummary: '',
                labelActionColumn: '',
                summaries: _.cloneDeep(DEFAULT_SUMMARIES)
              }
            }
          }
        ]
      },
      defaultSdkConfig: null
    }
  },
  mixins: [ baseQueryMixins ],
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
    getEmptyColumns() {
      return []
    },
    // set columns into config
    setColumns(columns) {
      let defaultFormat = {
        type: 'text',
        common: {
          plain: {
            nil: 'NULL',
            empty: 'EMPTY',
            na: 'N/A'
          },
          html: {
            nil: '<span>-</span>',
            empty: '<span class="dc-empty-style d-empty">empty</span>',
            na: '<span class="dc-na-style d-na">n/a</span>'
          },
          prefix: null,
          suffix: null
        }
      }
      this.sdkConfig.elements[0].config.columns = _.cloneDeep(columns).map(column => {
        column = {
          ...column,
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
        column.displayName = this.$options.filters.filterColumnName(column.name)
        if (INVISIBLE_COLUMN.includes(column.name)) column.visible = false
        if (column.name === UNIQUE_KEY_DS) column.isUniqueKey = true

        if (!column.type) {
          column.type = 'text'
        }
        switch (column.type) {
          case 'datetime':
          case 'date': {
            column.cell.width = 120
            column.cell.format.type = 'temporal'
            column.cell.format.config = {
              format: 'MM/DD/YYYY hh:mm A' // any moment format
            }
            column.cell.style = {'text-align': 'right'}
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
            column.cell.style = {'text-align': 'right'}
            break
          }
          case 'long': {
            column.cell.format.type = 'numeric'
            column.cell.format.config = {
              precision: 0
            }
            column.cell.style = {'text-align': 'right'}
            break
          }
          case 'float': {
            column.cell.format.type = 'numeric'
            column.cell.format.config = {
              precision: 2
            }
            column.cell.style = {'text-align': 'right'}
            break
          }
          case 'text': {
            column.cell.style = {'text-align': 'center'}
            break
          }
        }
        switch (column.name) {
          case 'channel_id': {
            column.cell.format.type = 'link'
            column.cell.format.config = {
              target: '_blank',
              text: '{value}',
              baseTemplate: 'https://sellercentral.amazon.com/orders-v3/order/{value}'
            }
            column.cell.width = 130
            break
          }
          case 'fulfillment_type': {
            column.cell.width = 120
            column.cell.computeClass = (valueObj, rowValue) => {
              return rowValue.fulfillment_type_accuracy && rowValue.fulfillment_type_accuracy.base < 100 ? 'inaccurate-style' : ''
            }
            break
          }
          case 'channel_tax_withheld': {
            column.cell.width = 105
            column.cell.computeClass = (valueObj, rowValue) => {
              return rowValue.channel_tax_withheld_accuracy && rowValue.channel_tax_withheld_accuracy.base < 100 ? 'inaccurate-style' : ''
            }
            break
          }
          case 'sku': {
            column.cell.width = 140
            break
          }
          case 'item_sale_status': {
            column.cell.width = 105
            column.cell.computeClass = (valueObj, rowValue) => {
              return rowValue.item_sale_status && SALE_STATUS_TEXT_BLUR.includes(rowValue.item_sale_status.base) ? 'text-blur' : ''
            }
            break
          }
          case 'state':
          case 'asin':
          case 'item_profit_status': {
            column.cell.width = 105
            break
          }
          case 'title': {
            column.cell.width = 300
            break
          }
          case 'upc':
          case 'item_total_charged':
          case 'cog': {
            column.cell.width = 105
            break
          }
          case 'sale_id': {
            column.cell.format = null
            break
          }
          case 'item_margin': {
            column.cell.width = 105
            column.cell.format.type = 'numeric'
            column.cell.format.common.suffix = '%'
            column.cell.format.config = {
              precision: 2
            }
            break
          }
          case 'item_channel_listing_fee': {
            column.cell.width = 105
            column.cell.computeClass = (valueObj, rowValue) => {
              return rowValue.channel_listing_fee_accuracy && rowValue.channel_listing_fee_accuracy.base < 100 ? 'inaccurate-style' : ''
            }
            break
          }
          case 'warehouse_processing_fee': {
            column.cell.width = 105
            column.cell.computeClass = (valueObj, rowValue) => {
              return rowValue.warehouse_processing_fee_accuracy && rowValue.warehouse_processing_fee_accuracy.base < 100 ? 'inaccurate-style' : ''
            }
            break
          }
          case 'item_sale_charged': {
            column.cell.width = 105
            column.cell.computeClass = (valueObj, rowValue) => {
              return rowValue.sale_charged_accuracy && rowValue.sale_charged_accuracy.base < 100 ? 'inaccurate-style' : ''
            }
            break
          }
          case 'item_shipping_cost': {
            column.cell.width = 105
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
            column.cell.style = {'text-align': 'center'}
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
            column.cell.width = 105
            column.cell.format.type = 'numeric'
            column.cell.format.common.suffix = '%'
            column.cell.format.config = {
              precision: 0
            }
            break
          }
          case 'inbound_freight_cost': {
            column.cell.width = 105
            column.cell.computeClass = (valueObj, rowValue) => {
              return rowValue.inbound_freight_cost_accuracy && rowValue.inbound_freight_cost_accuracy.base < 100 ? 'inaccurate-style' : ''
            }
            break
          }
          case 'outbound_freight_cost': {
            column.cell.width = 105
            column.cell.computeClass = (valueObj, rowValue) => {
              return rowValue.outbound_freight_cost_accuracy && rowValue.outbound_freight_cost_accuracy.base < 100 ? 'inaccurate-style' : ''
            }
            break
          }
        }
        // config special style here
        // column.cell.computeClass = (valueObj) => {
        // }
        return column
      })
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
    // set Action buttons
    setActions({ enabled, controls }) {
      this.sdkConfig.elements[0].config.rowActions.enabled = enabled
      this.sdkConfig.elements[0].config.rowActions.controls = controls
    },
    setBulkActions({ enabled, controls }) {
      this.sdkConfig.elements[0].config.bulkActions.enabled = enabled
      this.sdkConfig.elements[0].config.bulkActions.controls = controls
    },
    setFormOptions(form) {
      this.$set(this.sdkConfig.filter.builder.config, 'form', form)
    },
    setDefaultWidth() {
      this.sdkConfig.elements[0].config.columns.map(column => {
        if (!column.cell.width) {
          column.cell.width = 120
        }
      })
    }
  },
  computed: {
    getColumnsForColumnManager() {
      return this.sdkConfig.elements.map(e => {
        let columns = e.config.columns ? e.config.columns.map((c, i) => {
          let {name, displayName, visible} = c
          return {name, displayName: displayName, visible: visible !== undefined ? visible : true}
        }) : []
        let table = { columns }
        return table
      })
    }
  }
}
</script>
