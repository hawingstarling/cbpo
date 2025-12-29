<template>
  <div class="d-none">
    <cbpo-element-table
      ref="table"
      :config-obj="configObj.elements[0].config"
      @dataFetched="convertToDataSourceAndEmit"
    />
  </div>
</template>

<script>
import cloneDeep from 'lodash/cloneDeep'

export default {
  name: 'OverallSalesData',
  props: {
    configObj: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      isLoading: false
    }
  },
  methods: {
    convertToDataSourceAndEmit() {
      const dataTable = cloneDeep(this.$refs.table.dataTable)
      try {
        this.$emit('changed', dataTable.items && dataTable.items.length ? dataTable.items.map(item => item.data) : [])
      } catch (e) {
        console.log('Datasource from widget Overall Sales is not valid.', e)
      }
    },
    exportCSV() {
      this.$refs.table.widgetExport('csv', 'overall-sales-widget')
    }
  }
}
</script>
