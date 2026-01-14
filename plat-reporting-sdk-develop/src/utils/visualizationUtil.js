import { getDataTypeFromType, getAggregationObjFromAggregationName, getDefaultAggregationsOfDataType } from '@/services/ds/data/DataTypes'
import { AXIS, ELEMENT } from '@/components/visualizationBuilder/VisualizationBuilderTypes'
import { DEFAULT_CONFIG_X_AXIS } from '@/components/widgets/elements/chart/types/ChartTypes'
import { isEmpty, cloneDeep, uniqBy, get } from 'lodash'
import { createBinColumnAlias } from '@/utils/binUtils'
import { TYPES } from '@/components/widgets/elements/chart/ChartConfig'
import { CONTROL_TYPE } from '@/components/widgets/form/FilterControlConfig'

export const GROUPING_TYPE = {
  COLUMNS: 'columns',
  AGGREGATIONS: 'aggregations'
}

// TODO refactor using factory method later
const handleGroupingEvent = {
  // FOR CHART
  [`${GROUPING_TYPE.COLUMNS}_${ELEMENT.CHART}`]: (element, seriesItem = null, column) => {
    let { aggregations, columns } = element.config.grouping
    let binnedCol = ''
    let mappingAggregations = element.config.charts[0].series
      .map(item => ({ name: item.data.y, id: item.id }))
      .filter(dataY => !isEmpty(dataY.name))
      .map(dataY => {
        let yColumn = element.config.columns.find(col => col.name === dataY.name)
        let aggregationData = getDefaultAggregationsOfDataType(yColumn.type)
        return { column: dataY.name, aggregation: aggregationData.aggregation, alias: `${dataY.name}_${aggregationData.aggregation}_${dataY.id}` }
      })
    // check if data is binned
    get(element, 'config.bins', [])
      .some((bin) => {
        if (bin.alias === createBinColumnAlias(column.name)) {
          binnedCol = createBinColumnAlias(column.name)
          let aggregationData = getDefaultAggregationsOfDataType(column.type)
          const xAggr = {
            column: column.name,
            aggregation: aggregationData.aggregation,
            alias: column.name
          }
          mappingAggregations = [...mappingAggregations, xAggr]
          // group columns remove column name
          columns = [...(columns || [])].filter(col => col.name !== column.name)
          return true
        }
      })
    return {
      columns: uniqBy([...columns, { name: binnedCol || column.name }], 'name'),
      aggregations: uniqBy([...aggregations, ...mappingAggregations], 'alias')
    }
  },
  [`${GROUPING_TYPE.AGGREGATIONS}_${ELEMENT.CHART}`]: (element, seriesItem = null, column) => {
    if (!seriesItem) throw new Error('Element type is Chart but item in series is empty. Please check again!!!')
    let aggregationData = getDefaultAggregationsOfDataType(column.type)
    let alias = `${column.name}_${aggregationData.aggregation}_${seriesItem.id}`
    let {aggregations, columns} = element.config.grouping
    aggregations = uniqBy([...aggregations, { column: column.name, aggregation: aggregationData.aggregation, alias: alias }], 'alias')
    return {aggregations, columns}
  },
  // FOR HEAT MAP
  [`${GROUPING_TYPE.COLUMNS}_${ELEMENT.HEAT_MAP}`]: (element, seriesItem = null, column) => {
    let { aggregations, columns } = element.config.grouping
    let binnedCol = ''
    let mappingAggregations = element.config.charts[0].series
      .map(item => ({ name: item.data.y, id: item.id }))
      .filter(dataY => !isEmpty(dataY.name))
      .map(dataY => {
        let yColumn = element.config.columns.find(col => col.name === dataY.name)
        let aggregationData = getDefaultAggregationsOfDataType(yColumn.type)
        return { column: dataY.name, aggregation: aggregationData.aggregation, alias: `${dataY.name}_${aggregationData.aggregation}_${dataY.id}` }
      })
    // check if data is binned
    get(element, 'config.bins', [])
      .some((bin) => {
        if (bin.alias === createBinColumnAlias(column.name)) {
          binnedCol = createBinColumnAlias(column.name)
          let aggregationData = getDefaultAggregationsOfDataType(column.type)
          const xAggr = {
            column: column.name,
            aggregation: aggregationData.aggregation,
            alias: column.name
          }
          mappingAggregations = [...mappingAggregations, xAggr]
          // group columns remove column name
          columns = [...columns].filter(col => col.name !== column.name)
          return true
        }
      })
    return {
      columns: uniqBy([...columns, { name: binnedCol || column.name }], 'name'),
      aggregations: uniqBy([...aggregations, ...mappingAggregations], 'alias')
    }
  },
  [`${GROUPING_TYPE.AGGREGATIONS}_${ELEMENT.HEAT_MAP}`]: (element, seriesItem = null, column) => {
    if (!seriesItem) throw new Error('Element type is Chart but item in series is empty. Please check again!!!')
    let aggregationData = getDefaultAggregationsOfDataType(column.type)
    let alias = `${column.name}_${aggregationData.aggregation}_${seriesItem.id}`
    let {aggregations, columns} = element.config.grouping
    aggregations = uniqBy([...aggregations, { column: column.name, aggregation: aggregationData.aggregation, alias: alias }], 'alias')
    return {aggregations, columns}
  },
  // FOR GAUGE
  [`${GROUPING_TYPE.COLUMNS}_${ELEMENT.GAUGE}`]: (element, seriesItem = null, column) => {
    let { aggregations, columns } = element.config.grouping
    let binnedCol = ''
    let mappingAggregations = element.config.charts[0].series
      .map(item => ({ name: item.data.y, id: item.id }))
      .filter(dataY => !isEmpty(dataY.name))
      .map(dataY => {
        let yColumn = element.config.columns.find(col => col.name === dataY.name)
        let aggregationData = getDefaultAggregationsOfDataType(yColumn.type)
        return { column: dataY.name, aggregation: aggregationData.aggregation, alias: `${dataY.name}_${aggregationData.aggregation}_${dataY.id}` }
      })
    // check if data is binned
    get(element, 'config.bins', [])
      .some((bin) => {
        if (bin.alias === createBinColumnAlias(column.name)) {
          binnedCol = createBinColumnAlias(column.name)
          let aggregationData = getDefaultAggregationsOfDataType(column.type)
          const xAggr = {
            column: column.name,
            aggregation: aggregationData.aggregation,
            alias: column.name
          }
          mappingAggregations = [...mappingAggregations, xAggr]
          // group columns remove column name
          columns = [...columns].filter(col => col.name !== column.name)
          return true
        }
      })
    return {
      columns: uniqBy([...columns, { name: binnedCol || column.name }], 'name'),
      aggregations: uniqBy([...aggregations, ...mappingAggregations], 'alias')
    }
  },
  [`${GROUPING_TYPE.AGGREGATIONS}_${ELEMENT.GAUGE}`]: (element, seriesItem = null, column) => {
    if (!seriesItem) throw new Error('Element type is Chart but item in series is empty. Please check again!!!')
    let aggregationData = getDefaultAggregationsOfDataType(column.type)
    let alias = `${column.name}_${aggregationData.aggregation}_${seriesItem.id}`
    let {aggregations, columns} = element.config.grouping
    aggregations = uniqBy([...aggregations, { column: column.name, aggregation: aggregationData.aggregation, alias: alias }], 'alias')
    return {aggregations, columns}
  },
  // FOR TABLE
  [`${GROUPING_TYPE.COLUMNS}_${ELEMENT.TABLE}`]: (element, seriesItem = null, column) => {
    let mappingAggregations = element.config.columns
      .filter(_column => _column.name !== column.name)
      .map(_column => ({ column: _column.name, aggregation: getDataTypeFromType(_column.type).defaultAggregation.aggregation, alias: _column.name }))
    let { aggregations, columns } = element.config.grouping
    return {
      columns: uniqBy([...columns, { name: column.name }], 'name'),
      aggregations: uniqBy([...aggregations, ...mappingAggregations], 'alias')
    }
  },
  [`${GROUPING_TYPE.AGGREGATIONS}_${ELEMENT.TABLE}`]: (element, seriesItem = null, column) => {
    let aggregationData = getDataTypeFromType(column.type).defaultAggregation
    let alias = column.name
    let {columns, aggregations} = element.config.grouping
    return {
      columns: columns,
      aggregations: uniqBy([...aggregations, { column: column.name, aggregation: aggregationData.aggregation, alias: alias }], 'alias')
    }
  },
  // FOR HTML EDITOR
  [`${GROUPING_TYPE.COLUMNS}_${ELEMENT.HTML_EDITOR}`]: (element, seriesItem = null, column) => {
    let mappingAggregations = element.config.columns
      .filter(_column => _column.name !== column.name)
      .map(_column => ({ column: _column.name, aggregation: getDataTypeFromType(_column.type).defaultAggregation.aggregation, alias: _column.name }))
    let { aggregations, columns } = element.config.grouping
    return {
      columns: uniqBy([...columns, { name: column.name }], 'name'),
      aggregations: uniqBy([...aggregations, ...mappingAggregations], 'alias')
    }
  },
  [`${GROUPING_TYPE.AGGREGATIONS}_${ELEMENT.HTML_EDITOR}`]: (element, seriesItem = null, column) => {
    let aggregationData = getDataTypeFromType(column.type).defaultAggregation
    let alias = column.name
    let {columns, aggregations} = element.config.grouping
    return {
      columns: columns,
      aggregations: uniqBy([...aggregations, { column: column.name, aggregation: aggregationData.aggregation, alias: alias }], 'alias')
    }
  }
}

// TODO refactor using factory method later
const handleUngroupedEvent = {
  // FOR CHART
  [`${GROUPING_TYPE.COLUMNS}_${ELEMENT.CHART}`]: (element, seriesItem = null, column) => {
    let columns = element.config.grouping.columns
      .filter(col => {
        return col.name !== column.name &&
          col.name !== createBinColumnAlias(column.name) &&
          element.config.columns.findIndex(column => col.name.includes(column.name)) !== -1
      })
    if (isEmpty(columns.length)) element.config.grouping.aggregations = []
    // remove binned axis in aggregations
    let aggregations = element.config.grouping.aggregations
      .filter(aggr => element.config.columns.findIndex(col => col.name === aggr.column) !== -1)
    return {columns, aggregations}
  },
  [`${GROUPING_TYPE.AGGREGATIONS}_${ELEMENT.CHART}`]: (element, seriesItem = null, column) => {
    let {aggregations, columns} = element.config.grouping
    aggregations = aggregations.filter(agg => !agg.alias.includes(seriesItem.id))
    return {aggregations, columns}
  },
  // FOR GAUGE
  [`${GROUPING_TYPE.COLUMNS}_${ELEMENT.GAUGE}`]: (element, seriesItem = null, column) => {
    let columns = element.config.grouping.columns
      .filter(col => {
        return col.name !== column.name &&
          col.name !== createBinColumnAlias(column.name) &&
          element.config.columns.findIndex(column => col.name.includes(column.name)) !== -1
      })
    if (isEmpty(columns.length)) element.config.grouping.aggregations = []
    // remove binned axis in aggregations
    let aggregations = element.config.grouping.aggregations
      .filter(aggr => element.config.columns.findIndex(col => col.name === aggr.column) !== -1)
    return {columns, aggregations}
  },
  [`${GROUPING_TYPE.AGGREGATIONS}_${ELEMENT.GAUGE}`]: (element, seriesItem = null, column) => {
    let {aggregations, columns} = element.config.grouping
    aggregations = aggregations.filter(agg => !agg.alias.includes(seriesItem.id))
    return {aggregations, columns}
  },
  // FOR HEAT MAP
  [`${GROUPING_TYPE.COLUMNS}_${ELEMENT.HEAT_MAP}`]: (element, seriesItem = null, column) => {
    let columns = element.config.grouping.columns
      .filter(col => {
        return col.name !== column.name &&
          col.name !== createBinColumnAlias(column.name) &&
          element.config.columns.findIndex(column => col.name.includes(column.name)) !== -1
      })
    if (isEmpty(columns.length)) element.config.grouping.aggregations = []
    // remove binned axis in aggregations
    let aggregations = element.config.grouping.aggregations
      .filter(aggr => element.config.columns.findIndex(col => col.name === aggr.column) !== -1)
    return {columns, aggregations}
  },
  [`${GROUPING_TYPE.AGGREGATIONS}_${ELEMENT.HEAT_MAP}`]: (element, seriesItem = null, column) => {
    let {aggregations, columns} = element.config.grouping
    aggregations = aggregations.filter(agg => !agg.alias.includes(seriesItem.id))
    return {aggregations, columns}
  },
  // FOR TABLE
  [`${GROUPING_TYPE.COLUMNS}_${ELEMENT.TABLE}`]: (element, seriesItem = null, column) => {
    let {columns, aggregations} = element.config.grouping
    columns = columns.filter(col => {
      return col.name !== column.name &&
        col.name !== createBinColumnAlias(column.name) &&
        element.config.columns.findIndex(column => col.name.includes(column.name)) !== -1
    })
    if (isEmpty(columns)) aggregations = []
    // remove binned axis in aggregations
    aggregations = aggregations.filter(aggr => element.config.columns.findIndex(col => col.name === aggr.column) !== -1)
    return {columns, aggregations}
  },
  [`${GROUPING_TYPE.AGGREGATIONS}_${ELEMENT.TABLE}`]: (element, seriesItem = null, column) => {
    let {aggregations, columns} = element.config.grouping
    aggregations = aggregations.filter(agg => agg.column !== column.name)
    return {aggregations, columns}
  },
  // FOR HTML EDITOR
  [`${GROUPING_TYPE.COLUMNS}_${ELEMENT.HTML_EDITOR}`]: (element, seriesItem = null, column) => {
    let {columns, aggregations} = element.config.grouping
    columns = columns.filter(col => col.name !== column.name)
    if (isEmpty(columns)) aggregations = []
    // remove binned axis in aggregations
    aggregations = aggregations.filter(aggr => element.config.columns.findIndex(col => col.name === aggr.column) !== -1)
    return {columns, aggregations}
  },
  [`${GROUPING_TYPE.AGGREGATIONS}_${ELEMENT.HTML_EDITOR}`]: (element, seriesItem = null, column) => {
    let {aggregations, columns} = element.config.grouping
    aggregations = aggregations.filter(agg => agg.column !== column.name)
    return {aggregations, columns}
  }
}

/**
 * Handle grouping for bubble
 * Will be called when user drop a column in visualization or turn on grouping in axis column modal in visualization
 * @param {Object} element - config of element
 * @param {Object} seriesItem - item of series, only available in element type chart
 * @param {Object} column - column of Element
 * @param {String} groupType - GROUPING_TYPE
 * **/
export const handleGroupingBubble = (element, seriesItem = null, column, groupType) => {
  let { type, name } = column
  let elementType = element.type
  if (elementType === ELEMENT.CHART && groupType === GROUPING_TYPE.AGGREGATIONS && isEmpty(seriesItem)) {
    throw Error('Element type is Chart but item in series is empty. Please check again!!!')
  }
  switch (groupType) {
    case GROUPING_TYPE.COLUMNS: {
      let mappingAggregations = []
      let columns = [...element.config.grouping.columns]
      let binnedCol = ''
      // Create new aggregations base on series if element is Chart
      if (elementType === ELEMENT.CHART) {
        mappingAggregations = element.config.charts[0].series
          .map(item => ({ name: item.data.z, id: item.id }))
          .filter(dataZ => !isEmpty(dataZ.name))
          .map(dataZ => {
            let zColumn = element.config.columns.find(col => col.name === dataZ.name)
            // let aggregationData = getDataTypeFromType(zColumn.type).defaultAggregation
            let aggregationData = getDefaultAggregationsOfDataType(zColumn.type)
            return { column: dataZ.name, aggregation: aggregationData.aggregation, alias: `${dataZ.name}_${aggregationData.aggregation}_${dataZ.id}` }
          })
        // check if data is binned
        if (element.config.bins && element.config.bins.length) {
          get(element, 'config.bins', [])
            .some((bin) => {
              if (bin.column.name === name) {
                binnedCol = createBinColumnAlias(name)
                // let aggregationData = getDataTypeFromType(type).defaultAggregation
                let aggregationData = getDefaultAggregationsOfDataType(type)
                const xAggr = {
                  column: name,
                  aggregation: aggregationData.aggregation,
                  alias: name
                }
                mappingAggregations = [...mappingAggregations, xAggr]
                columns = [...columns].filter(col => col.name !== name)
                return true
              }
            })
        }
      }
      // Add new created aggregations into current aggregations
      let { aggregations } = element.config.grouping
      const grouped = {
        name: binnedCol || name
      }
      columns = [...columns, grouped]
      element.config.grouping = { columns: uniqBy(columns, 'name'), aggregations: uniqBy([...aggregations, ...mappingAggregations], 'alias') }
      break
    }
    case GROUPING_TYPE.AGGREGATIONS: {
      // let aggregationData = getDataTypeFromType(type).defaultAggregation
      let aggregationData = getDefaultAggregationsOfDataType(type)
      let alias = (elementType === ELEMENT.CHART || elementType === ELEMENT.GAUGE) ? `${name}_${aggregationData.aggregation}_${seriesItem.id}` : name
      element.config.grouping.aggregations = uniqBy([...element.config.grouping.aggregations, { column: name, aggregation: aggregationData.aggregation, alias: alias }], 'alias')
      break
    }
    default: {
      throw new Error('There is no grouping type with name: ' + groupType)
    }
  }
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
  if (!handleGroupingEvent[`${groupType}_${element.type}`]) throw new Error(`Element type ${element.type} and grouping type ${groupType} is not supported`)
  element.config.grouping = handleGroupingEvent[`${groupType}_${element.type}`](element, seriesItem, column)
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
  if (!handleUngroupedEvent[`${groupType}_${element.type}`]) throw new Error(`Element type ${element.type} and grouping type ${groupType} is not supported`)
  element.config.grouping = handleUngroupedEvent[`${groupType}_${element.type}`](element, seriesItem, column)
}
/**
 * build axis chart in element config
 * @param {Object} element - config of element
 * **/
export const buildAxisChart = ({config = {}}) => {
  let zones = {x: [], y: [], z: []}
  let getColumn = (axis, index) => {
    let column = config.columns
      .find(column => column.name === config.charts[0].series[index].data[axis])
    return column || {}
  }
  if (config.charts[0].series[0].data[AXIS.X]) {
    zones.x.push(getColumn(AXIS.X, 0))
  }
  config.charts[0].series.forEach((item, index) => {
    if (item.data[AXIS.Y]) {
      zones.y.push(getColumn(AXIS.Y, index))
    }
    if (item.data[AXIS.Z]) {
      zones.z.push(getColumn(AXIS.Z, index))
    }
  })
  return zones
}

/**
 * build axis table in element config
 * @param {Object} element - config of element
 * **/
export const buildAxisTable = ({config = {}}) => {
  let zones = {x: [], y: [], z: []}
  config.columns.forEach((item) => {
    zones.x.push(item)
  })
  return zones
}

/**
 * build axis crosstab table in element config
 * @param {Object} element - config of element
 * **/
export const buildAxisCrosstabTable = ({config = {}}) => {
  let zones = {x: [], y: [], z: []}
  zones.x = cloneDeep(config.xColumns)
  zones.y = cloneDeep(config.yColumns)
  zones.z = cloneDeep(config.tColumns)
  return zones
}

/**
 * build axis in gause chart in element config
 * @param {Object} element - config of element
 * **/
export const buildAxisGause = ({config = {}}) => {
  let zones = {x: [], y: [], z: []}
  config.columns.forEach((item) => {
    zones.y.push(item)
  })
  return zones
}

/**
 * build heat map in element config
 * @param {Object} element - config of element
  */
export const buildAxisHeatMap = ({ config = {} }) => {
  let zones = {x: [], y: [], z: []}
  let getColumn = (axis, index) => {
    let column = config.columns
      .find(column => column.name === config.charts[0].series[index].data[axis])
    return column || {}
  }
  config.charts[0].series.forEach((item, index) => {
    if (item.data[AXIS.X]) {
      zones.x.push(getColumn(AXIS.X, index))
    }
    if (item.data[AXIS.Y]) {
      zones.y.push(getColumn(AXIS.Y, index))
    }
  })
  return zones
}

/**
 * removeChartColumn
 * @param {Object} element - config of element
 * @param {String} axis - axis of chart
 * @param {index} index - index of chart
 * **/
export const removeChartColumn = (element, axis, index) => {
  // Update widget config
  let flagColumn = cloneDeep(element.config.columns.find(col => col.name === element.config.charts[0].series[index].data[axis]))
  if (!(axis === AXIS.Y && element.config.grouping.aggregations.filter(aggr => aggr.column === element.config.charts[0].series[index].data[axis]).length > 1)) {
    element.config.columns = element.config.columns.filter(col => col.name !== element.config.charts[0].series[index].data[axis])
  }
  if (axis === AXIS.X) {
    element.config.charts[0].series = element.config.charts[0].series.map(ser => {
      ser.data[axis] = ''
      ser.axis.x = null
      return ser
    })
    element.config.charts[0].axis.x = []
  } else if (axis === AXIS.Y) {
    element.config.charts[0].series[index].data[axis] = ''
  }
  let seriesItem = element.config.charts[0].series[index]
  let { name, type } = cloneDeep(flagColumn)
  let groupType = axis === AXIS.X ? GROUPING_TYPE.COLUMNS : GROUPING_TYPE.AGGREGATIONS
  let typeChart = get(element, 'config.charts[0].series[0].type', null)
  if (typeChart === 'bubble') {
    groupType = axis === AXIS.X || axis === AXIS.Y ? GROUPING_TYPE.COLUMNS : GROUPING_TYPE.AGGREGATIONS
  }
  handleUngrouping(element, seriesItem, { name, type }, groupType)
}

/**
 * createNewColumnChart
 * @param {Object} element - config of element
 * @param {String} column - column of Element
 * @param {String} axis - axis of chart
 * @param {index} index - index of chart
 * **/
export const createNewColumnChart = (element, column, axis, index) => {
  let { name, displayName, type } = column
  // default value for columns in chart
  column = {...{ name, displayName, type }, ...{ format: null, aggrFormats: null }}

  // Mapping column name into each item in series
  element.config.charts[0].series[(axis === AXIS.X ? 0 : index)].data[axis] = column.name

  let dataX = element.config.charts[0].series[0].data.x
  if (!isEmpty(dataX)) {
    element.config.charts[0].series.forEach(item => { item.data.x = dataX })
  }

  // Mapping axis into series
  if (!element.config.charts[0].axis.x.length && axis === AXIS.X) {
    let axis = {id: `x_${element.config.charts[0].series[0].id}`, ...cloneDeep(DEFAULT_CONFIG_X_AXIS)}
    element.config.charts[0].axis.x.push(axis)
    element.config.charts[0].series.forEach(item => { item.axis.x = axis.id })
  }

  // Add new column if it doesn't exist
  if (!element.config.columns.find(col => col.name === column.name)) element.config.columns.push(column)

  // Update element and force grouping column by emit event to outside
  let seriesItem = element.config.charts[0].series[index]
  if (seriesItem.type !== TYPES.SCATTER) {
    let groupType = axis === AXIS.X ? GROUPING_TYPE.COLUMNS : GROUPING_TYPE.AGGREGATIONS
    let typeChart = get(element, 'config.charts[0].series[0].type', null)
    if (typeChart === 'bubble') {
      groupType = axis === AXIS.X || axis === AXIS.Y ? GROUPING_TYPE.COLUMNS : GROUPING_TYPE.AGGREGATIONS
    }
    handleGrouping(
      element,
      axis === AXIS.X ? null : element.config.charts[0].series[index],
      { name: column.name, type: column.type },
      groupType
    )
  }

  // Mapping series name by column name and aggregation name
  setTimeout(() => {
    mappingChartName(element)
  }, 0)
}

/**
 * mappingChartName
 * @param {Object} element - config of element
 * **/
const mappingChartName = (element) => {
  element.config.charts[0].series = element.config.charts[0].series.map((item, index) => {
    let column = element.config.columns.find(column => column.name === item.data.y)
    let aggregation = element.config.grouping.aggregations.find(column => column.alias.includes(item.id))
    if (column) {
      let name = `${column.displayName || column.name}`
      if (aggregation) {
        const aggr = getAggregationObjFromAggregationName(aggregation.aggregation)
        name += ` (${aggr ? aggr.label : aggregation.aggregation})`
      }
      item.name = name
      if (item.options && item.options.title) {
        item.options.title = name
      }
      if (item.options && item.options.subtitle) {
        item.options.subtitle = name
      }
    }
    return item
  })
}

/**
 * updateTableColumn
 * @param {Object} element - config of element
 * @param {Object} column - column of Element
 * @param {Number} colIndex - column index Table
 * **/
export const updateTableColumn = (element, column, colIndex) => {
  const { name, type } = cloneDeep(element.config.columns[colIndex])
  const groupType = GROUPING_TYPE.COLUMNS
  // update new column
  element.config.columns[colIndex] = {...column}
  // remove old column
  handleUngrouping(element, null, { name, type }, groupType)
}

/**
 * update grouping in table
 * @param {Object} element - config of element
 * @param {Array} groupingColumns - list grouped columns in preset
 * **/
export const updateGroupingTable = (elementConfig, groupingColumns) => {
  elementConfig.config.grouping = { columns: [], aggregations: [] }
  const { bins, columns, grouping } = elementConfig.config
  if (groupingColumns.length) {
    const { name, type } = groupingColumns[0]
    const isBinned = bins.findIndex(bin => bin.column.name === name)
    if (isBinned !== -1) {
      grouping.columns.push({ name: createBinColumnAlias(name) })
      columns.forEach(column => {
        grouping.aggregations.push({
          column: column.name,
          aggregation: getDataTypeFromType(type).defaultAggregation.aggregation,
          alias: column.name
        })
      })
    } else {
      grouping.columns.push({ name })
      columns.forEach(column => {
        if (column.name !== name) {
          grouping.aggregations.push({
            column: column.name,
            aggregation: getDataTypeFromType(type).defaultAggregation.aggregation,
            alias: column.name
          })
        }
      })
    }
  }
}

/**
 * mapping columns in filter in preset feature
 * @param {Object} query - query of builder or form filter
 * @param {Object} oldColumn - column object of current visualization
 * @param {Object} newColumn - column object of preset visualization
 * **/
export const mappingFilter = (query, oldColumn, newColumn) => {
  if (!query) return query
  if (!query.conditions || !query.conditions.length) return query
  query.conditions = query.conditions.map(cond => {
    if (cond.conditions) {
      cond = mappingFilter(cond, oldColumn, newColumn)
    } else if (cond.column) {
      if (cond.column.name === oldColumn.name) {
        const oldColumnType = getDataTypeFromType(oldColumn.type).type
        const newColumnType = getDataTypeFromType(newColumn.type).type
        if (oldColumnType === newColumnType) {
          const { displayName, label, name, type } = newColumn
          cond.column = { displayName, label, name, type }
        } else {
          cond = {}
        }
      }
    }
    return cond
  })
  // Remove empty conditions
  const filterEmptyQuery = (query) => {
    if (!query || !query.conditions) return query
    return query.conditions.filter(cond => {
      if (cond && cond.conditions) {
        return filterEmptyQuery(cond)
      }
      return !isEmpty(cond)
    })
  }
  query.conditions = query.conditions.filter(cond => {
    return !isEmpty(filterEmptyQuery(cond))
  })
  return query
}

/**
 * mapping controls in form filter in preset feature
 * @param {Array} controls - controls of form filter
 * @param {Object} oldColumn - column object of current visualization
 * @param {Object} newColumn - column object of preset visualization
 * @param {String} dataSource - dataSoure id of preset visualization
 * **/
export const mappingControlFilter = (controls, oldColumn, newColumn, dataSource = '') => {
  if (!controls || !controls.length) return controls
  const clonedControls = cloneDeep(controls)
  let newControls = clonedControls.map(ctrl => {
    if (ctrl.config.common.column.name === oldColumn.name) {
      // update with new column
      const { displayName, label, name, type } = newColumn
      ctrl.config.common.column = { displayName, label, name, type }
      // reset value
      if (ctrl.type === CONTROL_TYPE.SELECT && ctrl.config.selection.empty.enabled) {
        ctrl.config.selection.empty.isEmptySelected = true
      }
      ctrl.config.common.value = undefined
    }
    // update data source and selections
    if (dataSource && ctrl.type === CONTROL_TYPE.SELECT) {
      ctrl.config.dataSource = dataSource
      ctrl.config.selection.options = []
    }
    return ctrl
  })
  return newControls
}
