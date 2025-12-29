<template>
    <b-modal :id="id" size="xl" hide-footer>
        <template v-slot:modal-title>
          <span>Return log of </span>
          <span v-html="channelSaleId"></span>
        </template>
        <b-container fluid>
            <div>
              <label class="mr-1 font-weight-bold">UPC:</label> <span v-html="upc"></span>
            </div>
            <div>
              <label class="mr-1 font-weight-bold">ASIN:</label> <span v-html="asin"></span>
            </div>
            <div>
              <label class="mr-1 font-weight-bold">SKU:</label> <span v-html="sku"></span>
            </div>
            <div>
              <label class="mr-1 font-weight-bold">Title:</label> <span v-html="title"></span>
            </div>
            <div>
              <label class="mr-1 font-weight-bold">Brand:</label> <span v-html="brand"></span>
            </div>
            <div>
              <label class="mr-1 font-weight-bold">Fulfillment Type:</label> <span v-html="fulfillmentType"></span>
            </div>
            <div class="cbpo-widget-wrapper">
                <cbpo-widget  v-if="isReady" ref="widgetSDK" :key="sdkUniqueState" :configObj.sync="sdkConfig">
                    <template v-slot:queryBuilder>
                        <div class="d-none"></div>
                    </template>
                    <template v-slot:columnManager>
                        <div class="d-none"></div>
                    </template>
                </cbpo-widget>
            </div>
        </b-container>
    </b-modal>
</template>
<script>
import _ from 'lodash'
import { mapActions, mapGetters } from 'vuex'
import { CURRENCY_FORMAT } from '@/shared/constants'
import sdkMixins from '@/components/pages/sdkMixins'
export default {
  name: 'ReturnLogModal',
  props: {
    id: {
      type: String,
      required: true
    },
    dataRow: {
      type: [Object, Array]
    },
    timezone: {
      type: String
    }
  },
  data() {
    return {
      isReady: false,
      returnColList: ['item_sale_status', 'sale_date', 'quantity', 'item_sale_charged', 'item_tax_charged', 'cog', 'inbound_freight_cost', 'outbound_freight_cost', 'item_shipping_cost', 'warehouse_processing_fee', 'channel_tax_withheld', 'item_channel_listing_fee', 'refund_admin_fee', 'return_postage_billing', 'item_other_channel_fees', 'item_profit', 'item_margin']
    }
  },
  created() {
    // do nothing
  },
  mixins: [
    sdkMixins
  ],
  computed: {
    ...mapGetters({
      sdkUniqueState: `pf/analysis/sdkUniqueState`,
      dsIdOfFinancialView: `pf/analysis/dsIdOfFinancialView`,
      dsColumns: `pf/analysis/dsColumns`
    }),
    channelSaleId() {
      return this.dataRow ? this.dataRow.data.channel_id.format : ''
    },
    fulfillmentType() {
      return this.dataRow ? this.dataRow.data.fulfillment_type.format : ''
    },
    brand() {
      return this.dataRow ? this.dataRow.data.brand.format : ''
    },
    sku() {
      return this.dataRow ? this.dataRow.data.sku.format : ''
    },
    asin() {
      return this.dataRow ? this.dataRow.data.asin.format : ''
    },
    upc() {
      return this.dataRow ? this.dataRow.data.upc.format : ''
    },
    title() {
      return this.dataRow ? this.dataRow.data.title.format : ''
    }
  },
  watch: {
    dataRow() {
      this.handleGetReturnLog()
    },
    timezone() {
      this.setTimezone()
    }
  },
  methods: {
    ...mapActions({
      // empty
    }),
    async handleGetReturnLog() {
      this.buildBaseFilter()
      this.setDataSource(this.dsIdOfFinancialView)
      _.set(this.sdkConfig, 'elements[0].config.sorting[0].direction', 'asc')
      this.setTimezone()
      const columns = this.dsColumns.filter(col => this.returnColList.includes(col.name))
      this.setColumns(columns)
      this.initTableSummary()
      this.initGlobalSummary()
      this.setTimezoneReadonly()
      this.handleFormatCustomRefunded()
      this.readonlyRowActions()
      this.isReady = true
    },
    readonlyRowActions () {
      _.set(this.sdkConfig, 'elements[0].config.rowActions.enabled', false)
    },
    handleFormatCustomRefunded() {
      this.sdkConfig.elements[0].config.columns.forEach(column => {
        switch (column.name) {
          case 'item_margin':
            column.cell.format = this.formatCustom()
            break
          case 'item_profit':
            column.cell.format = this.formatCustom()
            break
        }
      })
    },
    formatCustom() {
      return {
        type: 'custom',
        config: {
          condition(cellValue, rowValue) {
            if (rowValue.item_sale_status.base === 'Refunded') {
              return {
                type: 'override',
                // common: {
                //   plain: {
                //     nil: 'NULL',
                //     empty: 'EMPTY',
                //     na: 'N/A'
                //   },
                //   html: {
                //     nil: '<span class="dc-null-style d-null">null</span>',
                //     empty: '<span class="dc-empty-style d-empty">empty</span>',
                //     na: '<span class="dc-na-style d-na">n/a</span>'
                //   },
                //   suffix: null
                // }
                config: {
                  format: {
                    text: '_'
                  }
                }
              }
            } else {
              return {
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
                  suffix: '%'
                }
              }
            }
          }
        }
      }
    },
    setTimezoneReadonly() {
      _.set(this.sdkConfig, 'elements[0].config.timezone.readonly', true)
    },
    setTimezone() {
      _.set(this.sdkConfig, 'elements[0].config.timezone.utc', this.timezone)
    },
    initTableSummary() {
      _.set(this.sdkConfig, 'elements[0].config.tableSummary.position', 'footer')
      const summaries = [
        {
          label: '',
          column: 'item_sale_charged',
          format: _.cloneDeep(CURRENCY_FORMAT),
          expr: `SUM (@item_sale_charged) as 'item_sale_charged'`,
          style: { justifyContent: 'flex-end' }
        },
        {
          label: '',
          column: 'item_tax_charged',
          format: _.cloneDeep(CURRENCY_FORMAT),
          expr: `SUM (@item_tax_charged) as 'item_tax_charged'`,
          style: { justifyContent: 'flex-end' }
        },
        {
          label: '',
          column: 'cog',
          format: _.cloneDeep(CURRENCY_FORMAT),
          expr: `SUM (@cog) as 'cog'`,
          style: { justifyContent: 'flex-end' }
        },
        {
          label: '',
          column: 'inbound_freight_cost',
          format: _.cloneDeep(CURRENCY_FORMAT),
          expr: `SUM (@inbound_freight_cost) as 'inbound_freight_cost'`,
          style: { justifyContent: 'flex-end' }
        },
        {
          label: '',
          column: 'outbound_freight_cost',
          format: _.cloneDeep(CURRENCY_FORMAT),
          expr: `SUM (@outbound_freight_cost) as 'outbound_freight_cost'`,
          style: { justifyContent: 'flex-end' }
        },
        {
          label: '',
          column: 'item_shipping_cost',
          format: _.cloneDeep(CURRENCY_FORMAT),
          expr: `SUM (@item_shipping_cost) as 'item_shipping_cost'`,
          style: { justifyContent: 'flex-end' }
        },
        {
          label: '',
          column: 'warehouse_processing_fee',
          format: _.cloneDeep(CURRENCY_FORMAT),
          expr: `SUM (@warehouse_processing_fee) as 'warehouse_processing_fee'`,
          style: { justifyContent: 'flex-end' }
        },
        {
          label: '',
          column: 'channel_tax_withheld',
          format: _.cloneDeep(CURRENCY_FORMAT),
          expr: `SUM (@channel_tax_withheld) as 'channel_tax_withheld'`,
          style: { justifyContent: 'flex-end' }
        },
        {
          label: '',
          column: 'item_channel_listing_fee',
          format: _.cloneDeep(CURRENCY_FORMAT),
          expr: `SUM (@item_channel_listing_fee) as 'item_channel_listing_fee'`,
          style: { justifyContent: 'flex-end' }
        },
        {
          label: '',
          column: 'refund_admin_fee',
          format: _.cloneDeep(CURRENCY_FORMAT),
          expr: `SUM (@refund_admin_fee) as 'refund_admin_fee'`,
          style: { justifyContent: 'flex-end' }
        },
        {
          label: '',
          column: 'return_postage_billing',
          format: _.cloneDeep(CURRENCY_FORMAT),
          expr: `SUM (@return_postage_billing) as 'return_postage_billing'`,
          style: { justifyContent: 'flex-end' }
        },
        {
          label: '',
          column: 'item_other_channel_fees',
          format: _.cloneDeep(CURRENCY_FORMAT),
          expr: `SUM (@item_other_channel_fees) as 'item_other_channel_fees'`,
          style: { justifyContent: 'flex-end' }
        },
        {
          label: '',
          column: 'item_profit',
          format: _.cloneDeep(CURRENCY_FORMAT),
          expr: `SUM (@item_profit) as 'item_profit'`,
          style: { justifyContent: 'flex-end' }
        },
        {
          label: '',
          column: 'item_margin',
          format: {
            type: 'override',
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
              precision: 2,
              siPrefix: false,
              format: {
                text: '_'
              }
            }
          },
          expr: `SUM (@item_margin) as 'item_margin'`,
          style: { justifyContent: 'flex-end' }
        }
      ]
      _.set(this.sdkConfig, 'elements[0].config.tableSummary.summaries', summaries)
    },
    initGlobalSummary() {
      _.set(this.sdkConfig, 'elements[0].config.globalSummary.enabled', false)
    },
    buildBaseFilter() {
      let filter = {
        type: 'AND',
        conditions: [
          {
            column: 'channel_id',
            operator: '$eq',
            value: this.dataRow.data.channel_id.base
          },
          {
            column: 'sku',
            operator: '$eq',
            value: this.dataRow.data.sku.base
          }
        ]
      }
      _.set(this.sdkConfig, 'filter.base.config.query', filter)
    }
  }
}
</script>
<style lang="scss" scoped>
  ::v-deep .modal-content {
    min-height: 50vh;
  }
  ::v-deep .cbpo-widget-menu {
    margin-left: unset !important;
  }
  ::v-deep .cbpo-timezone-selector {
    margin-left: auto;
  }
  ::v-deep .checkbox {
    display: none !important;
  }
  ::v-deep #returnlog-modal .modal-xl {
    max-width: 98vw;
  }
  ::v-deep .d-null {
    line-height: normal;
    border-radius: 3px;
    padding: 0 .25rem;
    display: inline-block;
    font-size: 90%;
    background-color: #989898;
    color: #fff;
  }
  ::v-deep button:focus {
    outline: unset;
  }
</style>
