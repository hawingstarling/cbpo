<template>
  <div class="widget-broken-down d-flex flex-column position-relative h-100 overflow-hidden"
    v-cbpo-loading="{ loading: isLoading }">
    <widget-header :lastUpdated="lastUpdated">
      <template #menu-control>
        <cbpo-widget-menu-control class="custom-menu" :config-obj="mixinsWidgetMenuConfig"
          @click="menuEventHandler" />
      </template>
    </widget-header>
    <div class="widget-broken-down-body">
      <data-widget-broken-down-sales ref="dataWidget" :data-source="dsId.data_source_id"
        @changed="buildAndRefreshWidget" />
      <template v-if="!isLoading">
        <div class="broken-down-segments">
          <template v-for="(data, index) in [unitSalesData, salesChargedData, profitMarginData]">
            <div :key="index" class="group">
              <div :class="[data.className]" class="trend">
                <div class="title">{{ data.title }}</div>
                <div class="main-data">{{ data.main }}</div>
                <div :key="indexChild" v-for="(child, indexChild) in data.childData">
                  <div class="child">
                    <i :class="[child.className]"></i>
                    <span>{{ child.data }}</span>
                    {{ child.text }}
                  </div>
                </div>
              </div>
            </div>
          </template>
        </div>
        <cbpo-widget ref="BrokenDownSalesWidget" class="custom-widget d-none" :key="localDsId" :config-obj="config">
        </cbpo-widget>
        <div class="table-broken-down">
          <b-table outlined striped head-variant="light" class="mx-0 mb-0" table-variant="secondary"
            :fields="brokenDownFields" :items="dataTable.rows" empty-text="There are no data to show" show-empty>
            <template v-slot:empty>
              <div class="align-items-center d-flex justify-content-center" v-if="isLoading">
                <div class="spinner-border thin-spinner spinner-border-sm"></div>
                &nbsp;Loading...
              </div>
              <div class="align-items-center d-flex justify-content-center" v-else>
                <div>There are no data to show.</div>
              </div>
            </template>
            <template v-slot:cell(title)="row">
              <p class="mb-0 product-title font-weight-bold" :title="row.item[5]">{{ row.item[5] }}</p>
            </template>
            <template v-slot:cell(unit_sales)="row">
              <span :class="getClassCreaseValue(row.item[1])">{{ row.item[1] | formatNumber }}</span>
            </template>
            <template v-slot:cell(sale_charged)="row">
              <span :class="getClassCreaseValue(row.item[2])">{{ row.item[2] | formatCurrency }}</span>
            </template>
            <template v-slot:cell(profit)="row">
              <span :class="getClassCreaseValue(row.item[3])">{{ row.item[3] | formatCurrency }}</span>
            </template>
            <template v-slot:cell(margin)="row">
              <span v-if="![4, 5, 6].includes(row.index)">{{ row.item[4] | formatPercent }} </span>
              <span v-else :class="getClassCreaseValue(row.item[4])">{{ row.item[4] | formatPercent }}</span>
            </template>
          </b-table>
        </div>
      </template>
    </div>
  </div>
</template>

<script>
import DataWidgetBrokenDownSales from './DataWidgetBrokenDownSales'
import WidgetMenu from '@/components/pages/sales/overview/common/widget-menu'
import isArray from 'lodash/isArray'
import { formatCurrency, formatNumber, formatPercent } from '@/shared/filters'
import WidgetHeader from '@/components/pages/sales/overview/common/WidgetHeader.vue'

export default {
  name: 'BrokenDownTable',
  components: { DataWidgetBrokenDownSales, WidgetHeader },
  props: {
    dsId: Object,
    config: Object
  },
  filters: {
    formatCurrency,
    formatNumber,
    formatPercent
  },
  mixins: [
    WidgetMenu
  ],
  data() {
    return {
      isLoading: true,
      dataTable: {
        cols: [],
        rows: []
      },
      todayData: null,
      compareRowData: [],
      localDsId: null,
      brokenDownFields: [
        { key: 'title', lable: '', tdClass: 'align-middle w-25 first-td', thClass: 'first-td' },
        { key: 'unit_sales', lable: 'Units Sales', tdClass: 'align-middle text-center' },
        { key: 'sale_charged', lable: 'Sales Charged', tdClass: 'align-middle text-center' },
        { key: 'profit', lable: 'Profit', tdClass: 'align-middle text-center' },
        { key: 'margin', lable: 'Margin', tdClass: 'align-middle action-col text-center', thClass: 'text-center' }
      ],
      lastUpdated: null
    }
  },
  computed: {
    widgetRef() {
      return this.$refs.dataWidget
    },
    unitSalesData() {
      const index = this.dataTable.cols.findIndex(col => col.name === 'Unit-Sales')
      const childData = this.compareRowData.map(
        ({ text, row }) => ({
          text,
          data: row[index],
          className: this.getClassName(row[index])
        }))
      const saleChargedValue = formatNumber(this.todayData.row[index])
      return {
        title: 'Unit Sales',
        main: saleChargedValue,
        childData,
        className: this.getClassName(childData)
      }
    },
    salesChargedData() {
      const index = this.dataTable.cols.findIndex(col => col.name === 'Sale-Charged')
      const childData = this.compareRowData.map(
        ({ text, row }) => ({
          text,
          data: row[index],
          className: this.getClassName(row[index])
        }))
      const saleChargedValue = formatCurrency(this.todayData.row[index])
      return {
        title: 'Sales Charged',
        main: saleChargedValue,
        childData,
        className: this.getClassName(childData)
      }
    },
    profitMarginData() {
      const indexProfit = this.dataTable.cols.findIndex(col => col.name === 'Profit')
      const indexMargin = this.dataTable.cols.findIndex(col => col.name === 'Margin')
      const childData = this.compareRowData.map(
        ({ text, row }) => ({
          text,
          data: row[indexMargin],
          className: this.getClassName(row[indexMargin])
        }))
      const profitTodayData = formatCurrency(this.todayData.row[indexProfit])
      const marginTodayData = formatPercent(this.todayData.row[indexMargin])
      return {
        title: 'Profit & Margin',
        main: (profitTodayData !== '-' || marginTodayData !== '-') ? `${profitTodayData} - ${marginTodayData}` : '-',
        childData,
        className: this.getClassName(childData)
      }
    }
  },
  methods: {
    getClassCreaseValue(value) {
      if (String(value).includes('%') && String(value).includes('-')) {
        return 'decrease-value'
      } else if (String(value).includes('%') && parseInt(value) !== 0) {
        return 'increase-value'
      }
    },
    getClassName(compareRowData) {
      return isArray(compareRowData)
        ? compareRowData.some(d => String(d.data).includes('-')) ? 'decrease' : 'increase'
        : String(compareRowData).includes('-') ? 'custom-arrow-down' : 'custom-arrow-up'
    },
    menuEventHandler() {
      this.$refs.BrokenDownSalesWidget.widgetExport('csv', 'Broken-down-widget')
    },
    buildAndRefreshWidget({ dataSource, lastUpdated }) {
      const findRow = (name) => this.dataTable.rows.find(row => row.includes(name))
      this.lastUpdated = this.lastUpdated || lastUpdated
      this.dataTable = { ...dataSource }
      // Clear data local
      if (window['brokenDownSalesDsLocal']) {
        delete window['brokenDownSalesDsLocal']
      }
      window.brokenDownSalesDsLocal = { ...dataSource }
      this.todayData = {
        text: '',
        row: findRow(this.widgetRef.today.compareName)
      }
      this.compareRowData = [
        {
          text: 'vs yesterday',
          row: findRow(this.widgetRef.yesterday.compareName)
        },
        {
          text: 'vs same day last week',
          row: findRow(this.widgetRef.sameDayLastWeek.compareName)
        },
        {
          text: 'vs same day last year',
          row: findRow(this.widgetRef.sameDayLastYear.compareName)
        }
      ]
      this.config.elements[0].config.dataSource = 'brokenDownSalesDsLocal'
      this.config.elements[0].config.columns.forEach(col => {
        if (col.name === 'view_title') return
        col.cell = {
          computeClass: value => value.base.includes('-')
            ? 'decrease-value'
            : value.base.includes('0.00')
              ? ''
              : 'increase-value'
        }
      })
      this.localDsId = `id_broken_down_sale_${Date.now()}`
      this.isLoading = false
    }
  }
}
</script>

<style scoped lang="scss">
.widget-broken-down {
  border: solid 1px #d9d9d9;
}

.broken-down-segments {
  display: flex;
  padding: 20px 8px;

  .group {
    width: calc(100% / 3);
  }

  .trend {
    position: relative;
    height: 100%;

    &:before {
      position: absolute;
      bottom: 10px;
      right: 31px;
    }

    &.increase::before {
      content: url("~@/assets/img/icon/up-trend.svg");
    }

    &.decrease::before {
      content: url("~@/assets/img/icon/down-trend.svg");
    }
  }

  .title {
    font-family: Inter, serif;
    font-size: 14px;
    line-height: 16px;
    font-weight: 500;
  }

  .main-data {
    font-family: Inter, serif;
    font-weight: 700;
    font-size: 24px;
    line-height: 32px;
    margin: 5px 0;
  }

  .child {
    font-family: Inter, serif;
    font-weight: 400;
    font-size: 14px;
    line-height: 20px;
    margin-bottom: 5px;
    padding-right: 88px;

    span {
      display: inline-block;
      margin-left: 5px;
    }

    i.custom-arrow-up+span {
      color: #027A48;
    }

    i.custom-arrow-down+span {
      color: #D92D20;
    }
  }
}

.custom-widget::v-deep {
  border: none !important;

  .cbpo-control-features,
  .cbpo-table-element-container {
    padding: 0 !important;
  }

  .cbpo-table {
    border: none !important;
    border-top: 1px solid #d9d9d9 !important;
  }

  .cbpo-pagination {
    display: none;
  }

  .tbl-col-header .name {
    font-family: 'Inter', serif;
    font-size: 14px;
    line-height: 20px;
  }

  .tbl-cell-body {
    display: flex;
    align-items: center;

    .text {
      font-family: 'Inter', serif;
      font-size: 12px;
      line-height: 16px;
    }
  }

  .tbl-col-header {
    text-align: center;
  }

  .cbpo-header-col {
    height: 36px !important;
    line-height: 36px !important;
    border: none !important;
  }

  .cbpo-table-cell {
    border-left: none !important;
    border-right: none !important;
    border-bottom: none !important;
    background-color: #ffffff !important;

    &:not([data-col="view_title"]) .tbl-cell-body {
      justify-content: center;
    }

    &[data-col="view_title"] .text {
      font-weight: bold;

    }
  }

  .vue-recycle-scroller__item-view {

    &:nth-last-child(1),
    &:nth-last-child(2),
    &:nth-last-child(3) {
      .increase-value {
        color: #027A48;
      }

      .decrease-value {
        color: #D92D20;
      }
    }
  }
}

::v-deep .table td {
  padding: 6px 9px !important;
  font-size: 12px !important;
}

::v-deep .table tbody tr:hover:not(.b-table-empty-row) {
  background-color: #E6E6E6 !important;
  color: inherit !important;
}

::v-deep .table th {
  padding: 8px 9px !important;
  text-align: center;
}

::v-deep th.first-td {
  text-indent: -9999px;
  overflow: hidden;
}

.increase-value {
  color: #027a48;
}

.decrease-value {
  color: #d92d20;
}

table {
  border: none !important;
}

::v-deep .dropdown-item {
  font-size: 0.875rem;

  &:hover {
    color: #fff;
    background: #5897fb;
    border-radius: 0;
  }
}
</style>
