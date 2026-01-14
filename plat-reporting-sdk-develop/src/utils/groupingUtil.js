import { getDataTypeFromType } from '@/services/ds/data/DataTypes'
import { ELEMENT } from '@/components/visualizationBuilder/VisualizationBuilderTypes'
import isEmpty from 'lodash/isEmpty'

export const GROUPING_TYPE = {
  COLUMNS: 'columns',
  AGGREGATIONS: 'aggregations'
}

/**
 * Handle grouping
 * Will be called when user drop a column in visualization or turn on grouping in axis column modal in visualization
 * @param {Object} element - config of element
 * @param {Object} seriesItem - item of series, only available in element type chart
 * @param {Object} column - column of Element
 * @param {String} groupType - GROUPING_TYPE
 * **/
export const handleGrouping = (element, seriesItem = null, column, groupType) => {
  let { type, name } = column
  let elementType = element.type
  if (elementType === ELEMENT.CHART && groupType === GROUPING_TYPE.AGGREGATIONS && isEmpty(seriesItem)) {
    throw Error('Element type is Chart but item in series is empty. Please check again!!!')
  }
  switch (groupType) {
    case GROUPING_TYPE.COLUMNS: {
      let mappingAggregations = []
      // Create new aggregations base on config columns if element is Table
      if (elementType === ELEMENT.TABLE) {
        mappingAggregations = element.config.columns
          .filter(_column => _column.name !== column.name)
          .map(_column => ({ column: _column.name, aggregation: getDataTypeFromType(_column.type).defaultAggregation.aggregation, alias: _column.name }))
      }
      // Create new aggregations base on series if element is Chart
      if (elementType === ELEMENT.CHART) {
        mappingAggregations = element.config.charts[0].series
          .map(item => ({ name: item.data.y, id: item.id }))
          .filter(dataY => !isEmpty(dataY.name))
          .map(dataY => {
            let yColumn = element.config.columns.find(col => col.name === dataY.name)
            let aggregationData = getDataTypeFromType(yColumn.type).defaultAggregation
            return { column: dataY.name, aggregation: aggregationData.aggregation, alias: `${dataY.name}_${aggregationData.aggregation}_${dataY.id}` }
          })
      }
      // Add new created aggregations into current aggregations
      let { aggregations } = element.config.grouping
      element.config.grouping = { columns: [{name}], aggregations: [...aggregations, ...mappingAggregations] }
      break
    }
    case GROUPING_TYPE.AGGREGATIONS: {
      let aggregationData = getDataTypeFromType(type).defaultAggregation
      let alias = elementType === ELEMENT.CHART ? `${name}_${aggregationData.aggregation}_${seriesItem.id}` : name
      element.config.grouping.aggregations = [...element.config.grouping.aggregations, { column: name, aggregation: aggregationData.aggregation, alias: alias }]
      break
    }
    default: {
      throw new Error('There is no grouping type with name: ' + groupType)
    }
  }
}

/**
 * Handle ungrouping
 * Will be called when user remove a column in axis area or turn off grouping in axis column modal in visualization
 * @param {Object} element - config of element
 * @param {Object} seriesItem - item of series, only available in element type chart
 * @param {Object} column - column of Element
 * @param {String} groupType - GROUPING_TYPE
 * **/
export const handleUngrouping = (element, seriesItem = null, column, groupType) => {
  let { name } = column
  let elementType = element.type
  if (elementType === ELEMENT.CHART && groupType === GROUPING_TYPE.AGGREGATIONS && isEmpty(seriesItem)) {
    throw Error('Element type is Chart but item in series is empty. Please check again!!!')
  }
  if (groupType === GROUPING_TYPE.COLUMNS) {
    let columns = element.config.grouping.columns
      .filter(col => col.name !== name)
    if (!columns.length) {
      element.config.grouping.aggregations = []
    }
    element.config.grouping.columns = columns
  } else if (groupType === GROUPING_TYPE.AGGREGATIONS) {
    element.config.grouping.aggregations = element.config.grouping.aggregations
      .filter(agg =>
        elementType === ELEMENT.CHART
          ? (!agg.alias.includes(seriesItem.id))
          : (agg.column !== name)
      )
  }
}
