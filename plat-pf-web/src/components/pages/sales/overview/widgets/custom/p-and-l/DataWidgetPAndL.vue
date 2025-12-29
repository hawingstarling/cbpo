<template>
  <div class="d-none">
    <cbpo-element-table
      ref="table"
      :config-obj="config"
      :filter-obj="tableFilterObj"
      @dataFetched="convertToDataSourceAndEmit"
    />
    <cbpo-element-table
      v-if="localDsId"
      ref="tableExport"
      :config-obj="configExport"
      :key="localDsId"
    />
  </div>
</template>

<script>
import cloneDeep from 'lodash/cloneDeep'
import sum from 'lodash/sum'

export default {
  name: 'DataWidgetPAndL',
  props: {
    dataSource: {
      type: String,
      required: true
    },
    fromDate: {
      type: String,
      required: true
    },
    toDate: {
      type: String,
      required: true
    },
    customFilter: {
      type: Array,
      default: () => []
    },
    binOptions: {
      type: Object,
      default: () => {}
    }
  },
  data() {
    const profitColumn = 'item_profit'
    const grossColumn = 'item_sale_charged'
    const expenseColumn = 'expense'
    return {
      profitColumn,
      expenseColumn,
      grossColumn,
      config: {
        dataSource: this.dataSource,
        columns: [
          { name: 'item_sale_charged', displayName: 'Gross Revenue' },
          { name: 'cog', displayName: 'COGs', isExpense: true },
          { name: 'item_shipping_cost', displayName: 'Shipping Costs', isExpense: true },
          { name: 'inbound_freight_cost', displayName: 'Inbound Freight Cost', isExpense: true },
          { name: 'outbound_freight_cost', displayName: 'Outbound Freight Cost', isExpense: true },
          { name: 'item_reimbursement_costs', displayName: 'Reimbursement Costs', isExpense: true },
          { name: 'warehouse_processing_fee', displayName: 'Warehouse Processing Fee', isExpense: true },
          { name: 'item_channel_listing_fee', displayName: 'Sales Channel Commission', isExpense: true },
          { name: 'item_other_channel_fees', displayName: 'Other Channel Fees', isExpense: true },
          { name: profitColumn, displayName: 'Profit' },
          { name: 'sale_date', displayName: 'Sale Date' }
        ],
        bins: [{
          column: {
            name: 'sale_date',
            type: 'date'
          },
          alias: 'sale_date_bin',
          options: this.binOptions
        }],
        grouping: {
          columns: [{ name: 'sale_date_bin' }],
          aggregations: [
            { column: 'item_sale_charged', alias: 'item_sale_charged', aggregation: 'sum' },
            { column: 'cog', alias: 'cog', aggregation: 'sum' },
            { column: 'item_shipping_cost', alias: 'item_shipping_cost', aggregation: 'sum' },
            { column: 'inbound_freight_cost', alias: 'inbound_freight_cost', aggregation: 'sum' },
            { column: 'outbound_freight_cost', alias: 'outbound_freight_cost', aggregation: 'sum' },
            { column: 'item_reimbursement_costs', alias: 'item_reimbursement_costs', aggregation: 'sum' },
            { column: 'warehouse_processing_fee', alias: 'warehouse_processing_fee', aggregation: 'sum' },
            { column: 'item_channel_listing_fee', alias: 'item_channel_listing_fee', aggregation: 'sum' },
            { column: 'item_other_channel_fees', alias: 'item_other_channel_fees', aggregation: 'sum' },
            { column: profitColumn, alias: profitColumn, aggregation: 'sum' },
            { column: 'sale_date', alias: 'sale_date', aggregation: 'max' }
          ]
        },
        pagination: {
          limit: 1000,
          current: 0
        },
        timezone: {
          enabled: true,
          utc: 'America/Los_Angeles'
        },
        exportConfig: {
          fileName: 'P-And-L-widget'
        },
        id: '3ed8d07a-6313-4398-bcca-b0c6219401c1'
      },
      configExport: {
        dataSource: 'pAndLDSLocal',
        id: 'p-and-l-export',
        exportConfig: {
          fileName: 'P-And-L-widget'
        }
      },
      localDsId: ''
    }
  },
  computed: {
    tableFilterObj() {
      const filter = {
        type: 'AND',
        conditions: [
          {
            column: 'channel_name',
            operator: '$eq',
            value: 'amazon.com'
          },
          {
            column: 'item_sale_status',
            operator: 'in',
            value: ['Pending', 'Shipped']
          },
          ...this.customFilter
        ]
      }
      if (this.getToDateFilter) {
        filter.conditions.push(this.getToDateFilter)
      }
      if (this.getFromDateFilter) {
        filter.conditions.push(this.getFromDateFilter)
      }
      return filter
    },
    getToDateFilter() {
      return this.toDate
        ? {
          column: 'sale_date',
          operator: '$lte',
          value: this.toDate
        } : null
    },
    getFromDateFilter() {
      return this.toDate
        ? {
          column: 'sale_date',
          operator: '$gte',
          value: this.fromDate
        } : null
    },
    getExpenseColumnName() {
      return this.config.columns.filter(col => col.isExpense).map(col => col.name)
    }
  },
  methods: {
    convertToDataSourceAndEmit() {
      const { items, columns } = cloneDeep(this.$refs.table.dataTable)
      const dataSource = {
        cols: [
          ...columns.map(({ name, type, displayName }) => ({ name, type, displayName, alias: name })),
          { name: this.expenseColumn, displayName: 'Expenses', type: 'number', alias: this.expenseColumn },
          { name: 'sale_date_bin_from', displayName: 'Sale_date_bin_from', type: 'date', alias: 'sale_date_bin_from' },
          { name: 'sale_date_bin_to', displayName: 'Sale_date_bin_to', type: 'date', alias: 'sale_date_bin_to' }
        ],
        rows: items.map(item => [
          ...Object.keys(item.data).map(name => name !== 'sale_date' ? item.data[name].base : item.data[name].base.min),
          sum(
            Object.keys(item.data)
              .filter(name => this.getExpenseColumnName.includes(name))
              .map(name => item.data[name].base)
          ),
          item.data['sale_date'].base.min,
          item.data['sale_date'].base.max
        ])
      }
      this.configExport.rows = dataSource.rows
      this.configExport.columns = dataSource.cols
      this.$emit('changed', dataSource)
      this.savePAndLWidgetDsLocal()
    },
    savePAndLWidgetDsLocal() {
      const pAndLDataSourceExportLocal = this.configExport.dataSource

      // Clear data source local
      if (window[pAndLDataSourceExportLocal]) {
        delete window[pAndLDataSourceExportLocal]
      }

      // Build column for export
      const columnsExport = this.buildColumnsExport(this.configExport.columns)
      this.configExport.columns = columnsExport

      window[pAndLDataSourceExportLocal] = this.buildTableExportConfig(this.configExport.rows, columnsExport)
      this.configExport = {
        ...this.configExport,
        columns: columnsExport
      }

      // Force Vue to remount tableExport to read the new data.
      this.localDsId = `${pAndLDataSourceExportLocal}-${Date.now()}`
    },
    exportData() {
      this.savePAndLWidgetDsLocal()
      this.$nextTick(() => {
        this.$refs.tableExport.widgetExport('csv', 'P-And-L-widget')
      })
    },
    buildColumnsExport(cols) {
      return cols.map(col => ({
        ...col,
        alias: col.displayName || col.name
      }))
    },
    buildTableExportConfig(rows, columns) {
      return {
        cols: cloneDeep(columns),
        rows: cloneDeep(this.buildRowLocal(rows, columns))
      }
    },
    buildRowLocal(rows, columns) {
      return rows.map(row => {
        const rowData = []
        columns.forEach((col, index) => {
          rowData[index] = row[index]
        })
        return rowData
      })
    }
  }
}
</script>
