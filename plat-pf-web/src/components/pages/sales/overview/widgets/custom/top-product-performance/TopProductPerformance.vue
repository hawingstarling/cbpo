<template>
  <div class="widget-top-product-performance d-flex flex-column position-relative h-100">
    <div v-if="showTitle" class="widget-top-product-performance-header" :class="{ '--show': showTitle }">
      <span class="title">Top Product Performance Last 30 Days</span>
      <cbpo-widget-menu-control class="custom-menu" :config-obj="this.mixinsWidgetMenuConfig"
        @click="menuEventHandler" />
    </div>
    <div class="widget-top-product-performance-body">
      <div>
        <DataWidgetTopProductPerformance ref="dataWidget" :data-source="dsId.data_source_id" :from-date="_fromDate"
          :to-date="_toDate" @changed="buildAndRefreshWidget" />

      </div>
      <div class="summary" v-cbpo-loading="{ loading: isLoading }">
        <b-table outlined striped head-variant="light" class="mx-0 mb-0 h-100" table-variant="secondary"
          :fields="topProductTableFields" :items="rowData" empty-text="" show-empty
          :class="{ 'hide-thead': isLoading}"
        >
          <template v-slot:empty>
            <div v-if="!isLoading" class="align-items-center d-flex justify-content-center">
              <div>There are no data to show</div>
            </div>
          </template>
          <template v-slot:cell(product)="row">
            <p class="mb-0 product-title" :title="row.item.product.title">{{ row.item.product.title }}</p>
            <a v-if="row.item.product.link" :href="row.item.product.link" class="product-link" target="_blank">Product
              Link</a>
            <div class="product-info">
              <span><strong>{{ row.item.product.fulfillment_type }}:</strong> {{ row.item.product.fba }}</span>
              <span>{{ row.item.product.asin }} / {{ row.item.product.sku }}</span>
            </div>
          </template>
          <template v-slot:cell(gross_revenue)="row">
            {{ row.item.gross_revenue | numberCurrency }}
          </template>
          <template v-slot:cell(expenses)="row">
            {{ row.item.expenses | numberCurrency }}
          </template>
          <template v-slot:cell(net_profit)="row">
            {{ row.item.net_profit | numberCurrency }}
          </template>
          <template v-slot:cell(margin)="row">
            {{ row.item.margin | numberPercent }}
          </template>
          <template v-slot:cell(ROI)="row">
            {{ row.item.ROI | numberPercent }}
          </template>
          <template v-slot:cell(refunds)="row">
            {{ row.item.refunds | numberCurrency }}
          </template>
          <template v-slot:cell(action)="row">
            <div class="d-flex align-items-center">
              <button title="Expand" size="sm"
                class="mr-3 btn btn-primary text-truncate custom-btn toggle-btn toggle-manage-btn expand-btn"
                :class="{ 'rotate-icon-up': row.detailsShowing }" @click="row.toggleDetails">
                Expand
              </button>
            </div>
          </template>
          <template v-slot:row-details="row" class="px-0">
            <div class="row my-1 py-2">
              <div class="col-3">
                <ComplexRangeDatepicker class="d-flex justify-content-center select-date"
                  v-model="row.item.currentDateQuery" is-show-option-all :notAfterTime=getTotAfterTime
                  @onChangeDate="dataFilter => onChangeBaseQuery(dataFilter, row.item)"></ComplexRangeDatepicker>
              </div>
              <div class="col-9 p-and-l-product">
                <PAndL :show-title="false" is-empty-filter-date
                  :ds-id="dsIdForMapping ? dsIdForMapping.SALE_ITEMS : {}" :config="configs.PAndL.config"
                  :toDate="row.item.toDate" :fromDate="row.item.fromDate" :binOptions="row.item.binOptions"
                  :custom-filter="row.item.product.sku ? [{ column: 'sku', operator: '$eq', value: row.item.product.sku }] : []" />
              </div>
            </div>
          </template>
        </b-table>
      </div>
    </div>
  </div>
</template>

<script>

import WidgetMenu from '@/components/pages/sales/overview/common/widget-menu'
import DataWidgetTopProductPerformance from '@/components/pages/sales/overview/widgets/custom/top-product-performance/DataWidgetTopProductPerformance'
import PAndL from '@/components/pages/sales/overview/widgets/custom/p-and-l/PAndL'
import { mapGetters } from 'vuex'
import dashboardWidget from '@/components/pages/sales/overview/WidgetConfig/DetailWidgetConfig'
import ComplexRangeDatepicker from '@/components/common/ComplexRangeDatepicker/ComplexRangeDatepicker'
import cloneDeep from 'lodash/cloneDeep'
import { TODAY_OPTION, YESTERDAY_OPTION, LAST_WEEK_OPTION, LAST_30_DAYS_OPTION, THIS_MONTH_OPTION, LAST_MONTH_OPTION, THIS_YEAR_OPTION, LAST_YEAR_OPTION, ALL_OPTION } from '@/shared/constants/date.constant'

const mapBinOptions = {
  [TODAY_OPTION.id]: {
    alg: 'uniform',
    uniform: {
      width: 1,
      unit: 'd'
    }
  },
  [YESTERDAY_OPTION.id]: {
    alg: 'uniform',
    uniform: {
      width: 1,
      unit: 'd'
    }
  },
  [LAST_WEEK_OPTION.id]: {
    alg: 'uniform',
    uniform: {
      width: 1,
      unit: 'd'
    }
  },
  [LAST_30_DAYS_OPTION.id]: {
    alg: 'uniform',
    uniform: {
      width: 1,
      unit: 'd'
    }
  },
  [THIS_MONTH_OPTION.id]: {
    alg: 'uniform',
    uniform: {
      width: 1,
      unit: 'd'
    }
  },
  [LAST_MONTH_OPTION.id]: {
    alg: 'uniform',
    uniform: {
      width: 1,
      unit: 'd'
    }
  },
  [THIS_YEAR_OPTION.id]: {
    alg: 'uniform',
    uniform: {
      width: 1,
      unit: 'M'
    }
  },
  [LAST_YEAR_OPTION.id]: {
    alg: 'uniform',
    uniform: {
      width: 1,
      unit: 'M'
    }
  },
  [ALL_OPTION.id]: {
    alg: 'uniform',
    uniform: {
      width: 1,
      unit: 'M'
    }
  }
}

export default {
  name: 'TopProductPerformance',
  components: {
    DataWidgetTopProductPerformance,
    ComplexRangeDatepicker,
    PAndL
  },
  mixins: [
    WidgetMenu
  ],
  props: {
    dsId: Object,
    config: Object,
    showTitle: Boolean
  },
  data() {
    return {
      localDsId: `id_ds_${Date.now()}`,
      chartData: null,
      isLoading: true,
      topProductTableFields: [
        { key: 'product', lable: 'Product', tdClass: 'align-middle w-10 first-td', thClass: 'first-td' },
        { key: 'gross_revenue', lable: 'Gross Revenue', tdClass: 'align-middle text-center', thClass: 'text-center' },
        { key: 'expenses', lable: 'expenses', tdClass: 'align-middle text-center', thClass: 'text-center' },
        { key: 'net_profit', lable: 'net_profit', tdClass: 'align-middle text-center', thClass: 'text-center' },
        { key: 'margin', lable: 'Margin', tdClass: 'align-middle action-col text-center', thClass: 'text-center' },
        { key: 'ROI', lable: 'roi', tdClass: 'align-middle action-col text-center', thClass: 'text-center' },
        { key: 'refunds', lable: 'refunds', tdClass: 'align-middle action-col text-center', thClass: 'text-center' },
        { key: 'units_sold', lable: 'Units Sold', tdClass: 'align-middle action-col text-center', thClass: 'text-center' },
        { key: 'action', lable: '', tdClass: 'align-middle action-col', thClass: 'hide-th' }
      ],
      rowData: [],
      configs: cloneDeep(dashboardWidget)
    }
  },
  filters: {
    numberCurrency(value) {
      return value || value === 0 ? `${value < 0 ? '-' : ''}$${Math.abs(value).toLocaleString('en')}` : `No data`
    },
    numberPercent(value) {
      return value || value === 0 ? `${parseFloat(value).toFixed(2)}%` : `No data`
    }
  },
  computed: {
    ...mapGetters({
      dsIdForMapping: `pf/overview/dsIdForMapping`
    }),
    formatDate() {
      return (value) => value ? this.$moment(value).format('MMM DD, YYYY') : value
    },
    _fromDate() {
      return "DATE_START_OF(DATE_LAST(30,'day'), 'day')"
    },
    _toDate() {
      return "DATE_END_OF(TODAY(), 'day')"
    },
    getTotAfterTime() {
      return this.$moment().subtract(1, 'year')
    }
  },
  methods: {
    menuEventHandler() {
      this.$refs.dataWidget.exportData()
    },
    buildAndRefreshWidget({ cols, rows } = {}) {
      this.rowData = rows
      // for chart in right side
      this.isLoading = false
    },
    onChangeBaseQuery(dataFilter, rowItem) {
      rowItem.toDate = rowItem.currentDateQuery[1]
      rowItem.fromDate = rowItem.currentDateQuery[0]
      // Build bin options
      rowItem.binOptions = dataFilter && mapBinOptions[dataFilter.id]
        ? mapBinOptions[dataFilter.id]
        : this.generateBinOptions(rowItem.currentDateQuery[0], rowItem.currentDateQuery[1])
    },
    generateBinOptions(fromDate, toDay) {
      const diff = this.$moment(toDay).diff(this.$moment(fromDate), 'days')
      return {
        alg: 'uniform',
        uniform: {
          width: 1,
          unit: diff <= 31 ? 'd' : 'M'
        }
      }
    }
  },
  created() {
    this.config.elements[0].config.dataSource = this.localDsId
  }
}
</script>

<style lang="scss" scoped>
@import '@/assets/scss/button.scss';

.widget-top-product-performance {
  display: flex;
  flex-direction: column;
  border: solid 1px #d9d9d9;
  height: 100%;
  overflow: hidden;

  .widget-top-product-performance-header {
    position: relative;
    text-align: left;
    padding-top: 17px;
    padding-left: 8px;

    &.--show {
      margin-bottom: 16px;
    }

    span {
      padding-left: 24px;
      margin: 0.7rem 0;
      font-weight: 500;
      font-stretch: normal;
      font-style: normal;
      color: #080e2c;
      vertical-align: middle;

      &.title {
        font-size: 14px;
        line-height: 16px;
        letter-spacing: 0.02px;
      }

      &.date {
        font-size: 10px;
        line-height: 12px;
        letter-spacing: 0.05px;
        margin-left: 32px;
      }
    }

    ::v-deep .menu-control-select {
      position: absolute;
      right: calc(25px + 0.5rem);
      top: 17px;

      .btn:not(.not-button).btn-secondary.btn-secondary:not(.disabled):not(:disabled):hover {
        background: inherit !important;
        color: inherit !important;
      }
    }
  }

  .widget-top-product-performance-body {
    height: 100%;
    display: flex;
    flex-wrap: wrap;

    .first-td {
      padding-left: 24px;
    }

    >.summary {
      flex: 40%;

      >.table {
        border-left: 0 !important;
        border-right: 0 !important;
        border-bottom: 0 !important;

        tr.group {
          position: relative;

          td:first-child::before {
            content: '';
            position: absolute;
            display: block;
            width: 16px;
            height: 16px;
            left: -17px;
          }

          &.--gross td:first-child::before {
            background: #52C0E1;
          }

          &.--profit td:first-child::before {
            background: #91E4AB;
          }
        }

        td {
          font-family: 'Inter', serif;
          font-size: 10px;
          line-height: 16px;
          padding: 0 5px;

          &:last-child {
            text-align: right;
          }
        }
      }
    }
  }
}

::v-deep .table {
  .hide-th {
    width: 6%;
  }

  td {
    padding: 8px 1rem;

    &:first-child {
      padding-left: 24px;
    }
  }

  .b-table-details {
    border-top: 1px solid #E6E8F0;
  }

  tbody {
    tr {
      &:nth-of-type(odd) {
        background-color: #FFFFFF !important;
      }

      &:nth-of-type(even) {
        background-color: #FCFCFD !important;
      }

      td:not(:first-child) {
        font-size: 12px;
        font-family: Inter, sans-serif;
        font-weight: 500;
      }
    }
  }

  th {
    color: #080E2C;
    font-size: 14px;

    &:first-child {
      padding-left: 24px;
    }

    &:last-child {
      font-size: 0;
    }
  }
}

::v-deep .p-and-l-product {
  min-height: 100px;

  .widget-p-and-l {
    border: none;
  }

  .widget-p-and-l-body {
    .summary {
      padding-right: 58px;

      table {
        td {
          border: none;
        }
      }
    }
  }
}

::v-deep .btn.custom-btn {
  display: inline-flex !important;
  align-items: center;
  justify-content: center;
  padding: 8px 14px;

  &::after {
    background-color: #FFFFFF;
  }

  &.rotate-icon-up {
    &::after {
      transform: rotate(180deg);
    }
  }

  &.toggle-btn {
    color: #FFFFFF !important;
    background-color: #146EB4 !important;
    border-color: #146EB4 !important;
    @include button-icon(false, 'chevron-down.svg', 12px, 12px);
  }
}

::v-deep .complex-range-datepicker {
  .dropdown-toggle {
    i {
      display: none;
    }
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

.product-title {
  font-size: 12px;
  font-weight: 600;
  color: #232f3e;
}

.product-link {
  font-size: 10px;
  font-weight: 600;
  color: #0645ad;
}

.product-info {
  span {
    font-size: 10px;
    font-weight: 600;
  }
}

.btn.custom-btn.toggle-btn.expand-btn {
  font-size: 12px !important;

  &::after {
    width: 10px !important;
    height: 5px !important;
  }
}

::v-deep .hide-thead thead {
  display: none !important;
}
</style>
