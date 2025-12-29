<template>
  <div class="d-none">
    <cbpo-element-table
      v-if="!isTableLoading"
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
import {mapActions} from 'vuex'
import cloneDeep from 'lodash/cloneDeep'
import sum from 'lodash/sum'
import get from 'lodash/get'
import take from 'lodash/take'

export default {
  name: 'DataTopProductPerformance',
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
    }
  },
  data() {
    const grossColumn = 'gross_revenue'
    return {
      isTableLoading: true,
      grossColumn,
      config: {
        dataSource: this.dataSource,
        columns: [
          { name: 'sku', displayName: 'sku', isProductInfo: true },
          { name: 'cog', displayName: 'COGs', isGross: true },
          { name: 'item_shipping_cost', displayName: 'Shipping Costs', isGross: true },
          { name: 'inbound_freight_cost', displayName: 'Inbound Freight Cost', isGross: true },
          { name: 'outbound_freight_cost', displayName: 'Outbound Freight Cost', isGross: true },
          { name: 'item_reimbursement_costs', displayName: 'Reimbursement Costs', isGross: true },
          { name: 'warehouse_processing_fee', displayName: 'Dropship Fee', isGross: true },
          { name: 'item_channel_listing_fee', displayName: 'Sales Channel Commission', isGross: true },
          { name: 'item_other_channel_fees', displayName: 'Other Channel Fees', isGross: true },
          { name: 'item_profit', displayName: 'Profit' },
          { name: 'item_sale_charged', displayName: 'Item Sale Charged' },
          { name: 'item_total_cost', displayName: 'item_total_cost' },
          { name: 'quantity', displayName: 'Quantity' },
          { name: 'asin', displayName: 'asin', isProductInfo: true },
          { name: 'fulfillment_type', displayName: 'Fulfillment Type', isProductInfo: true },
          { name: 'title', displayName: 'title', isProductInfo: true },
          { name: 'channel_name', displayName: 'channel_name', isProductInfo: true }
        ],
        sorting: [{
          column: 'quantity',
          direction: 'desc'
        }],
        grouping: {
          columns: [{ name: 'sku' }],
          aggregations: [
            { column: 'cog', alias: 'cog', aggregation: 'sum' },
            { column: 'item_shipping_cost', alias: 'item_shipping_cost', aggregation: 'sum' },
            { column: 'inbound_freight_cost', alias: 'inbound_freight_cost', aggregation: 'sum' },
            { column: 'outbound_freight_cost', alias: 'outbound_freight_cost', aggregation: 'sum' },
            { column: 'item_reimbursement_costs', alias: 'item_reimbursement_costs', aggregation: 'sum' },
            { column: 'warehouse_processing_fee', alias: 'warehouse_processing_fee', aggregation: 'sum' },
            { column: 'item_channel_listing_fee', alias: 'item_channel_listing_fee', aggregation: 'sum' },
            { column: 'item_other_channel_fees', alias: 'item_other_channel_fees', aggregation: 'sum' },
            { column: 'quantity', alias: 'quantity', aggregation: 'sum' },
            { column: 'item_sale_charged', alias: 'item_sale_charged', aggregation: 'sum' },
            { column: 'item_total_cost', alias: 'item_total_cost', aggregation: 'sum' },
            { column: 'asin', alias: 'asin', aggregation: 'concat' },
            { column: 'fulfillment_type', alias: 'fulfillment_type', aggregation: 'concat' },
            { column: 'title', alias: 'title', aggregation: 'concat' },
            { column: 'channel_name', alias: 'channel_name', aggregation: 'concat' },
            { column: 'item_profit', alias: 'item_profit', aggregation: 'sum' }
          ]
        },
        pagination: {
          limit: 5,
          current: 0
        },
        timezone: {
          enabled: true,
          utc: 'America/Los_Angeles'
        }
      },
      configExport: {
        dataSource: 'topProductPerformanceDSLocal',
        id: '21a0726d-768d-4c66-aee9-a8572f3a4633',
        exportConfig: {
          fileName: 'Top-Product-Performance-widget'
        }
      },
      localDsId: '',
      listSKU: []
    }
  },
  async created() {
    try {
      const topProductPerformance = await this.fetchGetTopProductPerformance({client_id: this.$route.params.client_id})
      this.listSKU = topProductPerformance.map(item => item.sku)
      this.isTableLoading = false
    } catch (err) {
      this.vueToast('error', 'Get top product performance error. Please retry or contact administrator.')
    }
  },
  computed: {
    tableFilterObj() {
      return {
        type: 'AND',
        conditions: [
          {
            column: 'channel_name',
            operator: '$eq',
            value: 'amazon.com'
          },
          {
            column: 'sale_date',
            operator: '$lte',
            value: this.toDate
          },
          {
            column: 'sale_date',
            operator: '$gte',
            value: this.fromDate
          },
          {
            column: 'item_sale_status',
            operator: 'in',
            value: ['Pending', 'Shipped']
          },
          {
            column: 'sku',
            operator: '$in',
            value: this.listSKU
          }
        ]
      }
    },
    getGrossColumnName() {
      return this.config.columns.filter(col => col.isGross).map(col => col.name)
    },
    getProductColumnInfo() {
      return this.config.columns.filter(col => col.isProductInfo).map(col => col.name)
    }
  },
  methods: {
    ...mapActions({
      fetchGetTopProductPerformance: `pf/overview/fetchGetTopProductPerformance`
    }),
    convertToDataSourceAndEmit() {
      const { items } = cloneDeep(this.$refs.table.dataTable)
      const dataSource = {
        rows: take(items, 5).map(item => {
          let objData = {
            product: {}
          }
          for (const colName of Object.keys(item.data)) {
            this.getProductColumnInfo.includes(colName)
              ? objData.product[colName] = item.data[colName].base
              : objData[colName] = item.data[colName].base
          }
          if (item.data['channel_name'].base && item.data.asin) {
            objData.product['link'] = `https://www.${item.data['channel_name'].base}/gp/product/${item.data.asin.base}/ref=ox_sc_act_title_1?th=1&psc=1`
          }
          objData['gross_revenue'] = get(item, 'data.item_sale_charged.base', 0)
          objData['expenses'] = sum(
            Object.keys(item.data)
              .filter(name => this.getGrossColumnName.includes(name))
              .map(name => item.data[name].base)
          )
          objData['net_profit'] = objData['gross_revenue'] - objData['expenses']
          objData['margin'] = get(item, 'data.item_profit.base', 0) / get(item, 'data.item_sale_charged.base', 0) * 100
          objData['ROI'] = objData['net_profit'] / objData['expenses'] * 100
          objData['refunds'] = item.data['item_reimbursement_costs'].base
          objData['units_sold'] = item.data['quantity'].base
          // chart
          objData['toDate'] = "DATE_END_OF(TODAY(), 'day')"
          objData['fromDate'] = "DATE_START_OF(DATE_LAST(30,'day'), 'day')"
          objData['currentDateQuery'] = [ "DATE_START_OF(DATE_LAST(30,'day'), 'day')", "DATE_END_OF(TODAY(), 'day')" ]
          objData['binOptions'] = {
            alg: 'uniform',
            uniform: {
              width: 1,
              unit: 'd'
            }
          }
          return objData
        })
      }
      this.configExport.rows = dataSource.rows
      this.$emit('changed', dataSource)
      this.saveProductPerformanceDsLocal()
    },
    saveProductPerformanceDsLocal() {
      const dataSourceExportLocal = 'dataSourceExportLocal'
      // Clear data local
      if (window[dataSourceExportLocal]) {
        delete window[dataSourceExportLocal]
      }
      const columnsExport = this.buildColumnsExport()
      this.configExport.columns = columnsExport
      window.topProductPerformanceDSLocal = this.buildTableExportConfig(this.configExport.rows, columnsExport)
      window.config = this.configExport
      this.localDsId = dataSourceExportLocal
    },
    exportData() {
      this.saveProductPerformanceDsLocal()
      this.$nextTick(() => {
        this.$refs.tableExport.widgetExport('csv', 'Top-Product-Performance-widget')
      })
    },
    buildColumnsExport() {
      return [
        { name: 'title', displayName: 'product title', type: 'string' },
        { name: 'link', displayName: 'product link', type: 'string' },
        { name: 'fulfillment_type', displayName: 'fulfillment type', type: 'string' },
        { name: 'asin', displayName: 'asin', type: 'string' },
        { name: 'sku', displayName: 'sku', type: 'string' },
        { name: 'gross_revenue', displayName: 'gross revenue', type: 'number' },
        { name: 'expenses', displayName: 'expenses', type: 'number' },
        { name: 'net_profit', displayName: 'net profit', type: 'number' },
        { name: 'margin', displayName: 'margin', type: 'number' },
        { name: 'ROI', displayName: 'ROI', type: 'number' },
        { name: 'refunds', displayName: 'Refunds', type: 'number' },
        { name: 'units_sold', displayName: 'units sold', type: 'number' }
      ]
    },
    buildTableExportConfig(rows, columns) {
      return {
        cols: cloneDeep(columns),
        rows: cloneDeep(this.buildRowLocal(rows, columns))
      }
    },
    buildRowLocal(rows, columns) {
      const data = []
      if (rows && columns) {
        rows.forEach((row, indexRow) => {
          const rowData = []
          columns.forEach((column, indexCol) => {
            if (row[column.name]) {
              rowData[indexCol] = row[column.name]
            }
            for (const key in row.product) {
              if (key === column.name && key !== 'title') {
                rowData[indexCol] = row.product[column.name]
              } else {
                if (row.product[column.name]) {
                  rowData[indexCol] = row.product[column.name].replace(/[, ]+/g, '').trim()
                }
              }
            }
          })
          data.push(rowData)
        })
      }
      return data
    }
  }
}
</script>
