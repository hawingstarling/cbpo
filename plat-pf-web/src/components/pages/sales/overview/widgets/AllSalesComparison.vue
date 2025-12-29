<template>
  <b-card class="sales-amount-card rounded-0 h-100">
    <div class="h-100 d-flex flex-column overflow-hidden">
      <widget-header title="All Sales Comparison" :lastUpdated="lastUpdated">
        <template #menu-control>
          <cbpo-widget-menu-control :config-obj="mixinsWidgetMenuConfig"
            @click="menuEventHandler"/>
        </template>
      </widget-header>

      <div class="sales-comparison d-flex justify-content-start align-items-end flex-wrap flex-grow-1">
        <div class="sales-comparison_filter position-relative w-25 flex-column align-items-start mr-2">
          <label class="label-name mb-2">Category</label>
          <div class="position-relative">
            <v-select :options="categoryOptions" :clearable="false" v-model="selectedCategory" class="custom-v-select">
              <template #open-indicator="{ attributes }">
                <i class="fa fa-angle-down" v-bind="attributes"></i>
              </template>
            </v-select>
            <input v-if="isLoading" type="text" class="select-box-mark w-100" placeholder="All categories">
            <div v-if="isLoading" class="icon-loading">
              <i class="fa fa-circle-o-notch fa-spin"></i>
            </div>
          </div>
        </div>
        <div class="sales-comparison_filter position-relative w-25 flex-column align-items-start">
          <label class="label-name mb-2">Segment</label>
          <div class="position-relative">
            <v-select :options="segmentsOptions" :clearable="false" v-model="selectedSegment" class="custom-v-select">
              <template #open-indicator="{ attributes }">
                <i class="fa fa-angle-down" v-bind="attributes"></i>
              </template>
            </v-select>
            <input v-if="isLoading" type="text" class="select-box-mark w-100" placeholder="All segments">
            <div v-if="isLoading" class="icon-loading">
              <i class="fa fa-circle-o-notch fa-spin"></i>
            </div>
          </div>
        </div>
      </div>

      <div class="mt-2 px-0 h-100 overflow-hidden widget-all-sales-comparison">
        <template v-if="isSDKReady">
          <cbpo-widget ref="widget" class="border-right-0 border-bottom-0 border-left-0 all-sales-comparison-table"
            :key="sdkKey" :config-obj="sdkConfig.config" @getLastUpdated="lastUpdated = $event"/>
        </template>
        <template v-else>
          <div class="w-100 h- 100 d-flex justify-content-center align-items-center">
            <i class="fa fa-circle-o-notch fa-spin"></i>
          </div>
        </template>
      </div>
    </div>
  </b-card>
</template>

<script>
import moment from 'moment'
import 'vue-select/dist/vue-select.css'
import Vue from 'vue'
import vSelect from 'vue-select'
import WidgetMenu from '@/components/pages/sales/overview/common/widget-menu'
import widgetSellerMixins from '@/mixins/widgetSellerMixins'
import { CATEGORY_OPTIONS, SEGMENT_OPTIONS } from '@/shared/constants'
import AllSaleComparison from '@/components/pages/sales/overview/WidgetConfig/DetailWidgetConfig/AllSalesComparison.json'
import WidgetHeader from '@/components/pages/sales/overview/common/WidgetHeader.vue'

Vue.component('v-select', vSelect.VueSelect)

export default {
  components: { WidgetHeader },
  name: 'AllSalesComparison',
  mixins: [WidgetMenu, widgetSellerMixins],
  props: {
    sdkConfig: Object,
    dsId: Object
  },
  data() {
    const timezone = 'America/Los_Angeles'
    const currentYear = moment.utc().tz(timezone).clone().year()
    const lastYear = moment.utc().tz(timezone).clone().subtract(1, 'year').year()
    const yesterday = moment.utc().tz(timezone).clone().subtract(1, 'days').format('MM/DD/YYYY')
    const yesterdayOfLastYear = moment.utc().tz(timezone).clone().subtract(1, 'year').subtract(1, 'days').format('MM/DD/YYYY')
    return {
      categoryOptions: CATEGORY_OPTIONS,
      segmentsOptions: SEGMENT_OPTIONS,
      selectedCategory: {
        value: 'daily',
        label: 'Daily'
      },
      selectedSegment: {
        value: 'all',
        label: 'All'
      },
      firstDate: yesterday,
      secondDate: yesterdayOfLastYear,
      sdkKey: 0,
      currentYear,
      lastYear,
      yesterday,
      yesterdayOfLastYear,
      optionsMap: {
        'all-daily': { units: ['d0_unit', 'd1_unit', 'd_diff_unit'], amounts: ['d0_amount', 'd1_amount', 'd_diff_amount'], position: 4, aggregration: true },
        'all-30days': { units: ['y0_30d_unit', 'y1_30d_unit', 'y_30d_diff_unit'], amounts: ['y0_30d_amount', 'y1_30d_amount', 'y_30d_diff_amount'], position: 4, aggregration: true },
        'all-ytd': { units: ['y0_ytd_unit', 'y1_ytd_unit', 'y_ytd_diff_unit'], amounts: ['y0_ytd_amount', 'y1_ytd_amount', 'y_ytd_diff_amount'], position: 4, aggregration: true },
        'asin-daily': { units: ['d0_unit', 'd1_unit', 'd_diff_unit'], amounts: ['d0_amount', 'd1_amount', 'd_diff_amount'], position: 1, aggregration: false },
        'asin-30days': { units: ['y0_30d_unit', 'y1_30d_unit', 'y_30d_diff_unit'], amounts: ['y0_30d_amount', 'y1_30d_amount', 'y_30d_diff_amount'], position: 1, aggregration: false },
        'asin-ytd': { units: ['y0_ytd_unit', 'y1_ytd_unit', 'y_ytd_diff_unit'], amounts: ['y0_ytd_amount', 'y1_ytd_amount', 'y_ytd_diff_amount'], position: 1, aggregration: false },
        'product-daily': { units: ['d0_unit', 'd1_unit', 'd_diff_unit'], amounts: ['d0_amount', 'd1_amount', 'd_diff_amount'], position: 1, aggregration: false },
        'product-30days': { units: ['y0_30d_unit', 'y1_30d_unit', 'y_30d_diff_unit'], amounts: ['y0_30d_amount', 'y1_30d_amount', 'y_30d_diff_amount'], position: 1, aggregration: false },
        'product-ytd': { units: ['y0_ytd_unit', 'y1_ytd_unit', 'y_ytd_diff_unit'], amounts: ['y0_ytd_amount', 'y1_ytd_amount', 'y_ytd_diff_amount'], position: 1, aggregration: false },
        'type-daily': { units: ['d0_unit', 'd1_unit', 'd_diff_unit'], amounts: ['d0_amount', 'd1_amount', 'd_diff_amount'], position: 1, aggregration: false },
        'type-30days': { units: ['y0_30d_unit', 'y1_30d_unit', 'y_30d_diff_unit'], amounts: ['y0_30d_amount', 'y1_30d_amount', 'y_30d_diff_amount'], position: 1, aggregration: false },
        'type-ytd': { units: ['y0_ytd_unit', 'y1_ytd_unit', 'y_ytd_diff_unit'], amounts: ['y0_ytd_amount', 'y1_ytd_amount', 'y_ytd_diff_amount'], position: 1, aggregration: false }
      },
      columnMap: {
        'daily': ['d0_unit', 'd0_amount', 'd1_unit', 'd1_amount'],
        '30days': ['y0_30d_unit', 'y0_30d_amount', 'y1_30d_unit', 'y1_30d_amount'],
        'ytd': ['y0_ytd_unit', 'y0_ytd_amount', 'y1_ytd_unit', 'y1_ytd_amount']
      },
      lastUpdated: null
    }
  },
  methods: {
    menuEventHandler(type) {
      if (type !== 'csv' || !this.$refs.widget) return
      this.$refs.widget.widgetExport(type)
    },
    setNoDataMessage(name) {
      const message = name === 'default'
        ? AllSaleComparison.config.elements[0].config.messages.no_data_found
        : `<p style='margin-bottom:0px; margin-left: 40%'>No data found </p><p style='font-size:10px;margin-top:-20px;'>Please provide the required information for this field: ${name} </p>`
      const messages = this.sdkConfig.config.elements[0].config.messages
      messages.no_data_found = message
      messages.no_data_at_all = message
    },
    setColumnAndExpressions(unitNames, amountNames, startPosition, aggregration) {
      const elementsConfig = this.sdkConfig.config.elements[0].config
      // {{first_date}} quantity
      elementsConfig.columns[startPosition].name = unitNames[0]
      elementsConfig.columns[startPosition].displayName = this.firstDate
      // {{second_date}} quantity
      elementsConfig.columns[startPosition + 1].name = unitNames[1]
      elementsConfig.columns[startPosition + 1].displayName = this.secondDate
      elementsConfig.columns[startPosition + 2].name = unitNames[2]

      // {{first_date}} $ amount
      elementsConfig.columns[startPosition + 3].name = amountNames[0]
      elementsConfig.columns[startPosition + 3].displayName = this.firstDate + ' '
      elementsConfig.columns[startPosition + 4].name = amountNames[1]
      elementsConfig.columns[startPosition + 4].displayName = this.secondDate + ' '
      // {{second_date}} $ amount
      elementsConfig.columns[startPosition + 5].name = amountNames[2]
      // summaries
      elementsConfig.tableSummary.summaries = this.summaryForCol(unitNames[0], unitNames[1], amountNames[0], amountNames[1])

      // aggregation
      if (aggregration) {
        this.sdkConfig.config.elements[0].config.grouping.columns = AllSaleComparison.config.elements[0].config.grouping.columns
        this.sdkConfig.config.elements[0].config.grouping.aggregations = AllSaleComparison.config.elements[0].config.grouping.aggregations
        this.sdkConfig.config.elements[0].config.grouping.aggregations[3].column = unitNames[0]
        this.sdkConfig.config.elements[0].config.grouping.aggregations[3].alias = unitNames[0]
        this.sdkConfig.config.elements[0].config.grouping.aggregations[4].column = unitNames[1]
        this.sdkConfig.config.elements[0].config.grouping.aggregations[4].alias = unitNames[1]
        this.sdkConfig.config.elements[0].config.grouping.aggregations[5].column = unitNames[2]
        this.sdkConfig.config.elements[0].config.grouping.aggregations[5].alias = unitNames[2]
        this.sdkConfig.config.elements[0].config.grouping.aggregations[6].column = amountNames[0]
        this.sdkConfig.config.elements[0].config.grouping.aggregations[6].alias = amountNames[0]
        this.sdkConfig.config.elements[0].config.grouping.aggregations[7].column = amountNames[1]
        this.sdkConfig.config.elements[0].config.grouping.aggregations[7].alias = amountNames[1]
        this.sdkConfig.config.elements[0].config.grouping.aggregations[8].column = amountNames[2]
        this.sdkConfig.config.elements[0].config.grouping.aggregations[8].alias = amountNames[2]
      } else {
        this.sdkConfig.config.elements[0].config.grouping = {}
      }
    },
    queryData() {
      const option = `${this.selectedSegment.value}-${this.selectedCategory.value}`
      const config = this.optionsMap[option]
      if (config) {
        this.setColumnAndExpressions(config.units, config.amounts, config.position, config.aggregration)
        this.sdkKey = new Date().getTime()
      }
    },
    summaryForCol(col1, col2, col3, col4) {
      return [
        {
          label: '',
          column: this.sdkConfig.config.elements[0].config.columns[0].name,
          format: {
            type: 'override',
            config: {
              format: {
                text: 'Total:'
              }
            }
          },
          expr: "COUNT () as 'product'",
          style: { 'justify-content': 'right' }
        },
        {
          label: '',
          column: col1,
          format: {
            type: 'numeric',
            config: {
              comma: true,
              precision: 0
            }
          },
          expr: `SUM (@${col1}) as '${col1}'`,
          style: { 'justify-content': 'left' }
        },
        {
          label: '',
          column: col2,
          format: {
            type: 'numeric',
            config: {
              comma: true,
              precision: 0
            }
          },
          expr: `SUM (@${col2}) as '${col2}'`,
          style: { 'justify-content': 'left' }
        },
        {
          label: '',
          column: col3,
          format: {
            type: 'currency',
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
          },
          expr: `SUM (@${col3}) as '${col3}'`,
          style: { 'justify-content': 'left' }
        },
        {
          label: '',
          column: col4,
          format: {
            type: 'currency',
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
          },
          expr: `SUM (@${col4}) as '${col4}'`,
          style: { 'justify-content': 'left' }
        }
      ]
    },
    getLastUpdated(lastUpdated) {
      this.lastUpdated = this.lastUpdated || lastUpdated
    }
  },
  created() {
    this.isSDKReady = true
    this.sdkConfig.config.elements[0].config.dataSource = this.dsId['SALE_COMPARISION'].data_source_id
    this.sdkConfig.config.elements[0].config.columns[4].displayName = this.yesterday
    this.sdkConfig.config.elements[0].config.columns[5].displayName = this.yesterdayOfLastYear
    this.sdkConfig.config.elements[0].config.columns[7].displayName = this.yesterday + ' '
    this.sdkConfig.config.elements[0].config.columns[8].displayName = this.yesterdayOfLastYear + ' '
  },
  watch: {
    selectedCategory(newVal, oldVal) {
      switch (newVal.value) {
        case 'daily':
          this.firstDate = this.yesterday
          this.secondDate = this.yesterdayOfLastYear
          break
        case '30days':
          this.firstDate = `30 Days ${this.currentYear}`
          this.secondDate = `30 Days ${this.lastYear}`
          break
        default: // YTD
          this.firstDate = `YTD ${this.currentYear}`
          this.secondDate = `YTD ${this.lastYear}`
          break
      }
      // change base condition
      this.columnMap[newVal.value].forEach((column, index) => {
        this.sdkConfig.config.filter.base.config.query.conditions[index].column = column
      })
      this.queryData()
    },
    selectedSegment(newVal, oldVal) {
      const AllColumns = AllSaleComparison.config.elements[0].config.columns
      switch (newVal.value) {
        case 'type':
          this.sdkConfig.config.elements[0].config.dataSource = this.dsId['PRODT_COMPARISON'].data_source_id
          this.sdkConfig.config.elements[0].config.columns = [AllColumns[1], ...AllColumns.slice(4)]
          this.setNoDataMessage('Product Type')
          break
        case 'product':
          this.sdkConfig.config.elements[0].config.dataSource = this.dsId['PROD_COMPARISON'].data_source_id
          this.sdkConfig.config.elements[0].config.columns = [AllColumns[0], ...AllColumns.slice(4)]
          this.setNoDataMessage('Product')
          break
        case 'asin':
          this.sdkConfig.config.elements[0].config.dataSource = this.dsId['PASIN_COMPARISON'].data_source_id
          this.sdkConfig.config.elements[0].config.columns = [AllColumns[2], ...AllColumns.slice(4)]
          this.setNoDataMessage('Parent ASIN')
          break
        default:
          this.sdkConfig.config.elements[0].config.dataSource = this.dsId['SALE_COMPARISION'].data_source_id
          this.sdkConfig.config.elements[0].config.columns = AllColumns
          this.setNoDataMessage('default')
          break
      }
      this.queryData()
    }
  }
}
</script>

<style lang="scss" scoped>
@import '@/assets/scss/button.scss';

::v-deep .all-sales-comparison-table {
  border: none !important;
}

::v-deep .cbpo-control-features {
  padding: 2px !important;
}

::v-deep .cbpo-control-features,
.all-sales-comparison-table {
  background-color: #f9fbfb !important;
}

.sales-amount-card {
  background-color: #f9fbfb;

  .card-body {
    height: 100%;
    padding: 0 0;
    overflow: hidden;
  }

  .card-header {
    height: 37.8px;
    padding: .7rem;
    background: #ebebeb;
    text-align: center;
    font-size: 12px;
  }

  .icon-loading {
    top: 0;
    left: 0;
    bottom: 0;
    right: 0;
    display: flex;
    justify-content: flex-end;
    align-items: center;
    padding-right: 12px;
    position: absolute;
  }
}

.sales-comparison {
  margin-top: 8px;
  padding: 0 8px;

  .sales-comparison_filter {
    min-width: 160px;
  }
}

::v-deep .overview__menu-control .menu-control-select {
  margin: 0 !important;

  .btn:not(.not-button).btn-secondary.btn-secondary:not(.disabled):not(:disabled):hover {
    background-color: #fff !important;
  }
}

::v-deep .custom-v-select .vs__dropdown-toggle {
  font-size: 0.85em;
  background-color: white;
  height: 100%;
  padding-bottom: unset;
  font-weight: 400;
  line-height: 1.5;
  color: rgb(92, 104, 115);
  border-radius: 4px;
  border: 1px solid #c8ced3;
}

::v-deep .custom-v-select {
  width: 100%;
  height: 36px;

  .vs__dropdown-toggle {
    height: 100%;
  }

  .vs__dropdown-menu {
    max-height: 185px !important;
    margin: 0.125rem 0 0;
    border-top: 1px solid rgba(60, 60, 60, .26);
  }
}

::v-deep .dropdown-item {
  font-size: 0.875rem;

  &:hover {
    color: #fff;
    background: #5897fb;
    border-radius: 0;
  }
}

// custom v-select
::v-deep .custom-v-select .vs__search {
  color: rgb(130, 139, 147);
  padding-bottom: 4px;
}

::v-deep .custom-v-select .vs__dropdown-menu {
  font-size: 14px;

  li {
    font-size: 14px;
  }
}

::v-deep .custom-v-select .vs__open-indicator {
  color: rgb(35, 40, 44);
  cursor: pointer;
  font-size: 16px;
}

::v-deep .custom-v-select .vs__clear,
::v-deep .custom-v-select .vs__open-indicator {
  margin-bottom: 4px;
}

::v-deep .separate {
  height: 1px;
  border-bottom: 1px solid #808080;
  margin: 5px 20px;
}

.select-box-mark {
  height: 30px;
  border-radius: 4px;
  background-color: rgb(248, 248, 248);
  border: 1px solid rgb(200, 206, 211);
  font-size: 0.85em;
  padding-left: 8px;
  padding-top: 5px;
}

.label-name {
  font-weight: normal;
  font-stretch: normal;
  font-style: normal;
  line-height: 1.33;
  letter-spacing: 0.12px;
  font-size: 12px;
  color: #667085;
}

.label-name .save-as-default.custom-control-label {
  font-weight: 400;
  font-size: 12px;
  line-height: 16px;
  letter-spacing: 0.01em;
  color: #667085;
}

.widget-all-sales-comparison::v-deep {
  .cbpo-table-container {
    background-color: #d9d9d9;

    .cbpo-table-footer.cbpo-table-summary .tbl-col-header {
      justify-content: flex-end;
    }

    .vue-recycle-scroller__item-view .cbpo-table-cell:not(:first-child) {
      text-align: right;
    }
  }
}

::v-deep .custom-v-select .vs__dropdown-menu {
  max-height: 300px;
}

::v-deep .cbpo-header-col {
  text-align: center !important;
}

::v-deep .fa-caret-down,
::v-deep .fa-caret-up {
  font-size: 20px;
  position: relative;
  top: 3px;
}

::v-deep .fa-minus {
  position: relative;
  font-size: 14px;
  top: 2px;
}

.overview__menu-control {
  height: 57px !important;
}

::v-deep .vs__selected {
  margin-top: 0px;
}

::v-deep .vs--open .vs__selected {
  margin-top: 4px !important;
}

::v-deep .cbpo-pagination {
  display: flex !important;
  justify-content: center !important;
}

::v-deep .cbpo-pagination-sizing {
  width: 40% !important;
  align-items: center;

  button {
    border-color: #D0D5DD !important;
    color: #1D2939 !important;
  }

  button {
    &[data-button="page"]:is(*) {
      padding: 6px !important;
      font-weight: 600;
      font-size: 12px;
      max-width: 32px !important;
      height: 32px !important;
      border: 1px 1px 1px 0 !important;
    }

    &:hover {
      color: $primary !important;
      text-decoration: none;
      background-color: #F9FAFB !important;
      border-color: #D0D5DD;
    }

    &[data-button="prev"]:is(*) {
      @include button-icon(true, 'arrow-right.svg', 20px, 20px);
      border-top-left-radius: 6px !important;
      border-bottom-left-radius: 6px !important;
      color: #73818f;
      padding: 10px 16px !important;
      max-height: 32px !important;

      &::before {
        transform: rotate(180deg);
        background-color: $primary !important;
      }
    }

    &[data-button="prev"]:disabled {
      background-color: #fff !important;
      color: #73818f !important;

      &::before {
        transform: rotate(180deg);
        background-color: #73818f !important;
      }
    }

    &[data-button="next"]:is(*) {
      @include button-icon(false, 'arrow-right.svg', 20px, 20px);
      border-top-right-radius: 6px !important;
      border-bottom-right-radius: 6px !important;
      border-right: 1px solid #d9d9d9 !important;
      color: #73818f;
      padding: 10px 16px !important;
      max-height: 32px !important;

      &::after {
        background-color: $primary !important;
      }
    }

    &[data-button="next"]:disabled {
      background-color: #fff !important;
      color: #73818f !important;

      &::after {
        background-color: #73818f !important;
      }
    }

    &:disabled {
      background-color: #d9d9d9 !important;
      opacity: 1 !important;
    }
  }
}

::v-deep .cbpo-table-element-container {
  background-color: #f9fbfb;
}
::v-deep .ps-container {
  min-height: 300px;
}
</style>
