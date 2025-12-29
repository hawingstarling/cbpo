<template>
  <div class="widget-p-and-l d-flex flex-column position-relative h-100">
    <div v-if="showTitle" class="widget-p-and-l-header" :class="{ '--show': showTitle }">
      <span class="title">P&L</span>
      <span class="date">{{ formatDate(_fromDate) }} - {{ formatDate(_toDate) }}</span>
      <cbpo-widget-menu-control class="custom-menu" :config-obj="this.mixinsWidgetMenuConfig"
        @click="menuEventHandler" />
    </div>
    <div class="widget-p-and-l-body" v-cbpo-loading="{ loading: isLoading }">
      <div class="d-none">
        <DataWidgetPAndL ref="dataWidget" :data-source="dsId.data_source_id" :from-date="_fromDate" :to-date="_toDate"
          :bin-options="_binOptions" :custom-filter="customFilter" @changed="buildAndRefreshWidget" />
      </div>
      <template v-if="!isLoading">
        <div class="summary">
          <table>
            <tr class="group --gross">
              <td class="font-weight-bold">{{ summaryData.gross.text }}</td>
              <td class="font-weight-bold">{{ summaryData.gross.value | number }}</td>
            </tr>
            <tr class="group --expense">
              <td class=" font-weight-bold">{{ summaryData.expenses.text }}</td>
              <td class="font-weight-bold">{{ summaryData.expenses.value | number }}</td>
            </tr>
            <tr :key="index" v-for="(child, index) in summaryData.expenses.children">
              <td>{{ child.text }}</td>
              <td>{{ child.value | number }}</td>
            </tr>
            <tr class="group --profit">
              <td class="font-weight-bold">{{ summaryData.profit.text }}</td>
              <td class="font-weight-bold">{{ summaryData.profit.value | number }}</td>
            </tr>
            <tr class="group --margin">
              <td class="font-weight-bold">{{ summaryData.margin.text }}</td>
              <td class="font-weight-bold">{{ summaryData.margin.value | numberPercent }}</td>
            </tr>
          </table>
        </div>
        <div class="chart">
          <cbpo-widget :key="localDsId" :config-obj="config" />
        </div>
      </template>
    </div>
  </div>
</template>

<script>
import WidgetMenu from '@/components/pages/sales/overview/common/widget-menu'
import DataWidgetPAndL from '@/components/pages/sales/overview/widgets/custom/p-and-l/DataWidgetPAndL'
import sum from 'lodash/sum'

export default {
  name: 'PAndL',
  components: { DataWidgetPAndL },
  mixins: [
    WidgetMenu
  ],
  props: {
    dsId: Object,
    config: Object,
    showTitle: Boolean,
    toDate: String,
    fromDate: String,
    binOptions: Object,
    isEmptyFilterDate: {
      type: Boolean,
      default: false
    },
    customFilter: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
      localDsId: null,
      chartData: null,
      summaryData: {
        expense: {
          text: '',
          value: null,
          children: []
        },
        profit: {
          text: '',
          value: null
        },
        gross: {
          text: '',
          value: null
        }
      },
      isLoading: true
    }
  },
  filters: {
    number(value) {
      return value === 0
        ? 'No data'
        : `${value < 0 ? '-' : ''}$${Math.abs(value).toLocaleString('en')}`
    },
    numberPercent(value) {
      return value || value === 0 ? `${parseFloat(value).toFixed(2)}%` : `No data`
    }
  },
  computed: {
    formatDate() {
      return (value) => value ? this.$moment(value).format('MMM DD, YYYY') : value
    },
    _fromDate() {
      if (this.isEmptyFilterDate) {
        return this.fromDate
      }
      return this.fromDate || this.$moment(new Date(this.$moment().subtract(7, 'd').startOf('day'))).format('YYYY-MM-DD')
    },
    _toDate() {
      if (this.isEmptyFilterDate) {
        return this.toDate
      }
      return this.toDate || this.$moment(new Date(this.$moment().endOf('day'))).format('YYYY-MM-DD')
    },
    // Doc: https://mayoretailinternetservices.atlassian.net/wiki/spaces/DSP/pages/3932256/Queries
    _binOptions() {
      return this.binOptions || {
        alg: 'uniform',
        uniform: {
          width: 1,
          unit: 'd'
        }
      }
    }
  },
  methods: {
    menuEventHandler() {
      this.$refs.dataWidget.exportData()
    },
    buildAndRefreshWidget({ cols, rows } = {}) {
      this.localDsId = this.config.elements[0].config.dataSource = `id_ds_${Date.now()}`

      // for table summary in left side
      const findIndexColumn = (columns, columnName) => columns.findIndex(col => col.name === columnName)
      const sumData = cols.reduce(
        (sumValues, col, index) => [
          ...sumValues,
          sum(rows.map(row => row[index]))
        ], []
      )
      const grossIndex = findIndexColumn(cols, this.$refs.dataWidget.$data.grossColumn)
      const expenseIndex = findIndexColumn(cols, this.$refs.dataWidget.$data.expenseColumn)
      const profitIndex = findIndexColumn(cols, this.$refs.dataWidget.$data.profitColumn)
      const expenseColumns = this.$refs.dataWidget.getExpenseColumnName

      this.summaryData = {
        gross: {
          text: cols[grossIndex].displayName,
          value: sumData[grossIndex]
        },
        expenses: {
          text: cols[expenseIndex].displayName,
          value: sumData[expenseIndex],
          children: expenseColumns.map(name => {
            const index = findIndexColumn(cols, name)
            return {
              text: cols[index].displayName,
              value: sumData[index]
            }
          })
        },
        profit: {
          text: cols[profitIndex].displayName,
          value: sumData[profitIndex]
        },
        margin: {
          text: 'Margin Percentage',
          value: sumData[profitIndex] / sumData[grossIndex] * 100
        }
      }

      // for chart in right side
      this.chartData = window[this.localDsId] = { cols, rows }
      this.setMaxTickForChart(
        ...rows.map(row => row[grossIndex]),
        ...rows.map(row => row[profitIndex])
      )

      // show custom widget
      this.isLoading = false

      // reflow chart after widget size changed
      this.$nextTick(() => {
        this.reflowChart()
        this.setupResizeObserver()
      })
    },
    setupResizeObserver() {
      // Only setup once
      if (this.resizeObserver || typeof ResizeObserver === 'undefined') {
        return
      }
      const chartContainer = this.$el.querySelector('.chart')
      if (chartContainer) {
        this.resizeObserver = new ResizeObserver(() => {
          clearTimeout(this.resizeTimer)
          this.resizeTimer = setTimeout(() => {
            this.reflowChart()
          }, 250)
        })
        this.resizeObserver.observe(chartContainer)
      }
    },
    setMaxTickForChart(...values) {
      const maxPoint = Math.max(...values) || 0
      const maxTick = (Math.pow(10, Math.ceil(Math.log10(maxPoint))) || 10) / 2
      const numOfTick = 5
      this.config.elements[0].config.charts[0].axis.y[0].ticks = {
        maxTicksLimit: numOfTick + 1,
        stepSize: maxTick / numOfTick
      }
      this.config.elements[0].config.charts[0].chart = {
        ...this.config.elements[0].config.charts[0].chart,
        reflow: true,
        width: null,
        height: null
      }
    },
    reflowChart() {
      // Reflow charts after widget size changed
      const chartElement = this.$el.querySelector('.chart .cbpo-widget')
      if (chartElement && window.Highcharts) {
        // Only reflow charts inside this widget
        const chartContainers = chartElement.querySelectorAll('.highcharts-container')
        chartContainers.forEach(container => {
          const chart = window.Highcharts.charts.find(
            c => c && c.container === container
          )
          if (chart) {
            chart.reflow()
          }
        })
      }
    }
  },
  created() {
    this.$watch(vm => [vm.toDate, vm.fromDate, vm.binOptions], () => {
      this.isLoading = true
    })
  },
  mounted() {
    this.resizeHandler = () => {
      // Shared timer with ResizeObserver to prevent duplicate reflows
      clearTimeout(this.resizeTimer)
      this.resizeTimer = setTimeout(() => {
        this.reflowChart()
      }, 250)
    }

    window.addEventListener('resize', this.resizeHandler)
  },
  beforeDestroy() {
    // Cleanup
    if (this.resizeHandler) {
      window.removeEventListener('resize', this.resizeHandler)
    }
    if (this.resizeObserver) {
      this.resizeObserver.disconnect()
    }
    if (this.resizeTimer) {
      clearTimeout(this.resizeTimer)
    }
  }
}
</script>

<style lang="scss" scoped>
.widget-p-and-l {
  display: flex;
  flex-direction: column;
  border: solid 1px #d9d9d9;
  height: 100%;
  background-color: #fff;
  min-height: 321px;

  .widget-p-and-l-header {
    position: relative;
    text-align: left;
    padding-top: 17px;
    padding-left: 8px;

    &.--show {
      margin-bottom: 16px;
    }

    span {
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
    }
  }

  .widget-p-and-l-body {
    height: 100%;
    display: flex;
    flex-wrap: wrap;

    >.chart {
      flex: 0 0 60%;
      min-width: 300px;
      max-width: 60%;
      min-height: 265px;

      ::v-deep .cbpo-widget {
        border: 0 !important;
        padding: 0 !important;
        width: 100% !important;
        max-width: 100% !important;
        .cbpo-control-features {
          padding: 0 !important;
        }

        .highcharts-container {
          width: 100% !important;
        }
      }
    }

    >.summary {
      flex: 0 0 40%;
      min-width: 300px;
      max-width: 40%;

      table {
        width: calc(100% - 25px);
        margin-left: 25px;
      }

      tr.group {
        &:first-child td {
          padding-bottom: 5px;
        }

        &:last-child td {
          padding-top: 30px;
        }

        position: relative;

        td:first-child::before {
          content: '';
          position: absolute;
          display: block;
          width: 16px;
          height: 16px;
          left: -17px;
        }

        &.--expense {
          td {
            &:first-child::before {
              background: #4472c4;
            }
          }
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

    @media (max-width: 1200px) {
      > .summary,
      > .chart {
        flex: 0 0 100%;
        max-width: 100%;
      }
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
</style>
