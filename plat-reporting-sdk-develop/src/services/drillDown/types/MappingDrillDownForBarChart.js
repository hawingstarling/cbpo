import { AbstractMappingDrillDownData } from '@/services/drillDown/types/AbstractMappingDrillDownData'
import { getDataAggregationFromType } from '@/services/ds/data/DataTypes'
import cloneDeep from 'lodash/cloneDeep'
import isEmpty from 'lodash/isEmpty'

export class MappingDrillDownForBarChart extends AbstractMappingDrillDownData {
  constructor(...aggrs) {
    super(aggrs)
  }

  mapData() {
    let drillDownData = this.getDrillDownData()
    let config = this.getConfig()
    let { columns: listColumns, query: { bins, grouping: { columns, aggregations } } } = drillDownData

    // set bins
    config.bins = bins

    // find column with name
    let findName = isEmpty(bins) ? columns[0].name : bins[0].column.name
    let findColumn = listColumns.find((column) => column.name === findName)

    // replace old column
    config.columns = config.columns.filter(column => column.name !== config.charts[0].series[0].data.x)
    config.columns = [...config.columns, findColumn]

    // keep only 1 item in series
    config.charts[0].series = [config.charts[0].series[0]]

    // map name
    let aggregation = getDataAggregationFromType(aggregations[0].aggregation)
    config.charts[0].series[0].name = `${findColumn.displayName || findColumn.name} (${aggregation.label})`
    config.charts[0].series[0].data.x = findColumn.name

    console.log(config)

    this.setConfig(config)
  }

  getDrillDownData() {
    return cloneDeep(this.drillData)
  }

  setDrillDownData(drillData) {
    this.drillData = cloneDeep(drillData)
  }

  getConfig() {
    return cloneDeep(this.config)
  }

  setConfig(config) {
    this.config = cloneDeep(config)
  }
}
