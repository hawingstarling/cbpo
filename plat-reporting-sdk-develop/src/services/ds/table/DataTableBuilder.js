import { DsQueryExecService } from '@/services/ds/expression/DsQueryExec'
import QueryBuilder from '@/services/ds/query/QueryBuilder'
import { generateIdIfNotExist } from '@/utils/configUtil'
import {
  isEmpty,
  find,
  findIndex,
  map,
  reduce,
  flatten,
  cloneDeep,
  startCase,
  filter,
  get,
  flattenDeep,
  isFunction,
  groupBy
} from 'lodash'
import { DataTypeUtil, getAggregationDataTypeStr, getDataTypeFromType } from '@/services/ds/data/DataTypes'
import { createBinColumnAlias } from '@/utils/binUtils'
import dsFormatManager, { FORMAT_DATA_TYPES } from '@/services/dataFormatManager'
import { DsQueryExpr } from 'plat-expr-sdk'
import uuidv4 from 'uuid'
import CBPO from '@/services/CBPO'
// import { index } from 'd3'

const convert2DArrayToObjectData = ({ items, columns }) => {
  return map(items, row => {
    return reduce(columns, (obj, col, index) => {
      obj[col.name] = row[index]
      return obj
    }, {})
  })
}
const buildItemsData = ({ items, columns }) => {
  return map(items, row => {
    return reduce(columns, (obj, col, index) => {
      obj[col.alias] = row[index]
      return obj
    }, {})
  })
}

const changeIndexColumn = ({ group }, columnConfigs) => {
  let columns = cloneDeep(columnConfigs)
  let groupedColumn = (group.columns && group.columns[0]) || null
  if (!groupedColumn) return columns

  // find column and change splice it
  const index = findIndex(columnConfigs, column => [column.name, createBinColumnAlias(column.name)].includes(groupedColumn.name))
  const cachedColumn = columns[index]
  columns.splice(index, 1)

  return [cachedColumn, ...columns]
}

const changeIndexData = ({ bins, group }, configColumns, { items, columns }) => {
  // find bin if existed
  const binGroupedColumn = find(bins, bin => bin.alias === group.columns[0].name)

  // find grouped column
  const groupedIndex = isEmpty(binGroupedColumn)
    ? findIndex(configColumns, col => col.name === group.columns[0].name)
    : findIndex(configColumns, col => col.name === binGroupedColumn.column.name)

  // cache data and delete
  let groupedData = flatten(items.map(row => row[groupedIndex]))

  items = items.map(row => {
    row.splice(groupedIndex, 1)
    return row
  })

  // add cache data into first array
  items = items.map((row, index) => [groupedData[index], ...row])

  return { items, columns }
}

const formatDataByColumnConfig = ({ bins, group }, columnConfigs, { cols, rows }, isChild, isParentBin) => {
  const data = reduce(columnConfigs, (newData, column, columnIndex) => {
    let bin = find(bins, bin => bin.column.name === column.name)
    let aggregation = find(group.aggregations, aggr => aggr.column === (bin ? bin.alias : column.name))
    let colIndex = findIndex(cols, col => col.name === (bin ? bin.alias : column.name))

    // empty data if defined column is not found in datasource
    if (colIndex === -1) {
      newData.columns.push({ name: column.name, type: 'string' })
      newData.items = newData.items.map(row => {
        row = [...row, {
          base: '',
          format: ''
        }]
        return row
      })
    } else {
      // push format data into data table
      let formatFn = null
      let formatTooltipFn = null
      let formatConfig = null

      let aggrType = aggregation ? getAggregationDataTypeStr(cols[colIndex].type, aggregation.aggregation) : cols[colIndex].type

      if (!bin) {
        DataTypeUtil.isTemporal(cols[colIndex].type) && !get(column, 'cell.format.config.timezone', null)
          ? formatConfig = {
            type: 'temporal',
            config: {
              timezone: CBPO.channelManager()
                .getChannel()
                .getTimezoneSvc()
                .getTimezone()
            }
          }
          : formatConfig = column.cell.format
        formatFn = (data, isHtml = true) => {
          return aggregation && column.aggrFormats
            ? dsFormatManager.createAggrFormat(aggrType, formatConfig, aggregation.aggregation, column.aggrFormats, isHtml)(data)
            : (
              formatConfig && formatConfig.type === FORMAT_DATA_TYPES.CUSTOM
                ? dsFormatManager.create(formatConfig, isHtml)
                : dsFormatManager.create(formatConfig, isHtml)(data)
            )
        }
        formatTooltipFn = (data, isHtml = true) => {
          return aggregation && column.aggrFormats
            ? dsFormatManager.createAggrFormat(aggrType, column.cell.formatTooltip, aggregation.aggregation, column.aggrFormats, isHtml)(data)
            : (
              column.cell.formatTooltip && column.cell.formatTooltip.type === FORMAT_DATA_TYPES.CUSTOM
                ? dsFormatManager.create(column.cell.formatTooltip, isHtml)
                : dsFormatManager.create(column.cell.formatTooltip, isHtml)(data)
            )
        }
      } else {
        formatConfig = column.cell.format
        // formatFn = isChild && columnIndex === 0
        //   ? dsFormatManager.create(formatConfig, true)
        //   : (data) => {
        //     return dsFormatManager.formatBin(data, formatConfig, true)
        //   }

        formatFn = (data, isHtml = true) => {
          return isChild && columnIndex === 0
            ? dsFormatManager.create(formatConfig, isHtml)
            : dsFormatManager.formatBin(data, formatConfig, isHtml)
        }
        formatTooltipFn = (data, isHtml = true) => {
          return aggregation && column.aggrFormats
            ? dsFormatManager.createAggrFormat(aggrType, column.cell.formatTooltip, aggregation.aggregation, column.aggrFormats, isHtml)(data)
            : (
              column.cell.formatTooltip && column.cell.formatTooltip.type === FORMAT_DATA_TYPES.CUSTOM
                ? dsFormatManager.create(column.cell.formatTooltip, isHtml)
                : dsFormatManager.create(column.cell.formatTooltip, isHtml)(data)
            )
        }
      }
      newData.columns.push({ name: bin ? bin.column.name : cols[colIndex].name, type: cols[colIndex].type })
      newData.items = newData.items
        .map((row, index) => {
          let data = rows[index][colIndex]
          let item = isChild && columnIndex === 0
            ? {
              base: data,
              format: isParentBin ? formatFn(data) : '',
              formatFn: formatFn,
              tooltip: column.cell.formatTooltip ? formatTooltipFn(data, false) : formatFn(data, false)
            } // isChild will true when expand group, this is data of child group, only show if it's bin value
            : {
              base: data,
              format: formatFn ? formatFn(data) : data,
              formatFn: formatFn,
              tooltip: column.cell.formatTooltip ? formatTooltipFn(data, false) : formatFn(data, false)
            }
          row = [...row, item]
          return row
        })
    }
    return newData
  }, {
    columns: [],
    items: rows.map(_row => [])
  })

  data.items = data.items.map(rowItem => {
    const rowValue = data.columns.reduce((row, col, i) => {
      row[col.name] = rowItem[i]
      return row
    }, {})
    return rowItem.map(item => {
      if (isFunction(item.format)) {
        item.tooltip = item.format(item.base, rowValue, false)
        item.format = item.format(item.base, rowValue)
      }
      if (isFunction(item.tooltip)) {
        item.tooltip = isFunction(item.tooltip) && item.tooltip(item.base, rowValue, false)
      }
      return item
    })
  })

  return data
}

const formatDataByCol = ({ bins, group }, columnConfigs, { cols, rows }, isChild, isParentBin) => {
  const data = reduce(columnConfigs, (newData, column, columnIndex) => {
    let bin = find(bins, bin => bin.column.name === column.name)
    let aggregation = find(group.aggregations, aggr => aggr.column === (bin ? bin.alias : column.alias))
    let colIndex = findIndex(cols, col => col.name === (bin ? bin.alias : column.alias))

    // empty data if defined column is not found in datasource
    if (colIndex === -1) {
      newData.columns.push({ name: column.name, type: 'string', alias: column.alias })
      newData.items = newData.items.map(row => {
        row = [...row, {
          base: '',
          format: ''
        }]
        return row
      })
    } else {
      // push format data into data table
      let formatFn = null
      let formatConfig = null

      let aggrType = aggregation ? getAggregationDataTypeStr(cols[colIndex].type, aggregation.aggregation) : cols[colIndex].type

      if (!bin) {
        DataTypeUtil.isTemporal(cols[colIndex].type) && !get(column, 'cell.format.config.timezone', null)
          ? formatConfig = {
            type: 'temporal',
            config: {
              timezone: CBPO.channelManager()
                .getChannel()
                .getTimezoneSvc()
                .getTimezone()
            }
          }
          : formatConfig = column.cell.format
        formatFn = (data, isHtml = true) => {
          return aggregation && column.aggrFormats
            ? dsFormatManager.createAggrFormat(aggrType, formatConfig, aggregation.aggregation, column.aggrFormats, isHtml)(data)
            : (
              formatConfig && formatConfig.type === FORMAT_DATA_TYPES.CUSTOM
                ? dsFormatManager.create(formatConfig, isHtml)
                : dsFormatManager.create(formatConfig, isHtml)(data)
            )
        }
      } else {
        formatConfig = column.cell.format
        // formatFn = isChild && columnIndex === 0
        //   ? dsFormatManager.create(formatConfig, true)
        //   : (data) => {
        //     return dsFormatManager.formatBin(data, formatConfig, true)
        //   }

        formatFn = (data, isHtml = true) => {
          return isChild && columnIndex === 0
            ? dsFormatManager.create(formatConfig, isHtml)
            : dsFormatManager.formatBin(data, formatConfig, isHtml)
        }
      }
      newData.columns.push({ name: bin ? bin.column.name : cols[colIndex].name, type: cols[colIndex].type, alias: cols[colIndex].alias })
      newData.items = newData.items
        .map((row, index) => {
          let data = rows[index][colIndex]
          let item = isChild && columnIndex === 0
            ? {
              base: data,
              format: isParentBin ? formatFn(data) : '',
              formatFn: formatFn,
              tooltip: formatFn(data, false)
            } // isChild will true when expand group, this is data of child group, only show if it's bin value
            : {
              base: data,
              format: formatFn ? formatFn(data) : data,
              formatFn: formatFn,
              tooltip: formatFn(data, false)
            }
          row = [...row, item]
          return row
        })
    }
    return newData
  }, {
    columns: [],
    items: rows.map(_row => [])
  })

  data.items = data.items.map(rowItem => {
    const rowValue = data.columns.reduce((row, col, i) => {
      row[col.alias] = rowItem[i]
      return row
    }, {})
    return rowItem.map(item => {
      if (isFunction(item.format)) {
        item.tooltip = item.format(item.base, rowValue, false)
        item.format = item.format(item.base, rowValue)
      }

      return item
    })
  })

  return data
}

const buildColumnsTable = ({ group, orders }, columnConfig, columns) => {
  let hasGroup = group.columns.length > 0
  let hasAggregation = group.aggregations.length > 0

  // mapping and filter prop from config
  return columnConfig.map((column, index) => {
    let { type } = columns.find(col => [column.name, createBinColumnAlias(column.name)].includes(col.name))
    let order = find(orders, order => [column.name, createBinColumnAlias(column.name)].includes(order.column))
    let newConfigColumn = {
      displayName: column.label || column.displayName || startCase(column.name),
      name: column.name,
      visible: column.visible,
      cell: column.cell,
      header: column.header,
      sort: {
        enabled: column.sortable.enabled,
        direction: order ? order.direction : null
      },
      type: type.split('_bin')[0]
    }
    if (hasGroup && index === 0) {
      newConfigColumn.grouped = true
    }
    if (column.childColumn) {
      newConfigColumn.childColumn = column.childColumn
    }
    if (hasAggregation && (!hasGroup || index > 0)) {
      let listAggregations = getDataTypeFromType(type).aggregations
      newConfigColumn = {
        ...newConfigColumn,
        ...{ aggregation: { list: listAggregations, selected: listAggregations[0] } }
      }
    }

    return newConfigColumn
  })
}

const buildDataTable = ({ group }, items, isChild) => {
  return items.map(item => {
    return {
      key: 0,
      pk_id_sdk: uuidv4(),
      data: item,
      size: 32,
      viewDetail: {
        isOpen: false,
        isChild: false
      },
      group: {
        hasGroup: !!group.columns.length,
        level: isChild ? 1 : 0,
        isOpen: false,
        isCached: false,
        cachedData: []
      }
    }
  })
}

export default class DataTableBuilder {
  dsId = null

  constructor(dsId) {
    this.dsId = dsId
  }

  // isChild will be true when fetch group, it will hide group data
  buildData(query, data, columnConfigs, isChild = false, isParentBin = false) {
    data = cloneDeep(data)
    // change columns index before build data
    const orderConfigColumns = changeIndexColumn(query, columnConfigs)
    // remove all column in data do not defined in config column and format value if formatter existed
    let formatData = formatDataByColumnConfig(query, orderConfigColumns, data, isChild, isParentBin)
    // change index column if table has grouping column
    if (!isEmpty(query.group.columns)) {
      formatData = changeIndexData(query, orderConfigColumns, formatData)
    }
    // convert 2d array rows into format object key and value
    const items = convert2DArrayToObjectData(formatData)

    const buildColumns = buildColumnsTable(query, orderConfigColumns, formatData.columns)
    const item = {
      items: buildDataTable(query, items, isChild),
      columns: buildColumns
    }
    return item
  }

  buildDataComparableTable (query, data, columnConfigs, isChild = false, isParentBin = false) {
    data = cloneDeep(data)
    const orderConfigColumns = changeIndexColumn(query, columnConfigs)
    let formatData = formatDataByCol(query, columnConfigs, data, isChild, isParentBin)
    if (!isEmpty(query.group.columns)) {
      formatData = changeIndexData(query, orderConfigColumns, formatData)
    }
    const items = buildItemsData(formatData)
    return buildDataTable(query, items, isChild)
  }

  async buildSummaries(columns, summaries, filter = {}, timezone = '') {
    const mapSummaries = cloneDeep(summaries).map(sum => {
      generateIdIfNotExist(sum)
      return sum
    })
    // build query
    const result = mapSummaries.reduce((result, summary, index) => {
      const parseQuery = DsQueryExpr.parse(summary.expr)
      if (parseQuery.parsedExprs[0].type === 'exec' && isEmpty(parseQuery.parsedExprs[0].query.filter)) {
        result.mergeSummaries.push({
          id: summary.id,
          index,
          parseQuery
        })
      } else {
        result.standaloneSummaries.push({
          id: summary.id,
          index,
          parseQuery,
          expression: summary.expr
        })
      }
      return result
    }, {
      mergeSummaries: [],
      standaloneSummaries: []
    })

    // build merge query
    const mergeAggregations = flattenDeep(result.mergeSummaries.map(data => [...data.parseQuery.parsedExprs[0].query.group.aggregations]))
    const query = new QueryBuilder()
    query.setGroup([], mergeAggregations)
    query.setFilter(filter)
    query.setTimezone(timezone)
    const resultMergeSummaries = CBPO.dsManager().getDataSource(this.dsId).query(query.params)

    // build standalone query
    const dsQueryExec = new DsQueryExecService(filter, timezone)
    const dsQueryExpr = new DsQueryExpr(dsQueryExec)
    const resultStandAloneSummaries = result.standaloneSummaries.map(data => {
      return dsQueryExpr.eval(this.dsId, data.expression)
    })
    // merge with promise
    const promiseAll = Promise.all(
      (result.mergeSummaries.length ? [resultMergeSummaries, ...resultStandAloneSummaries] : resultStandAloneSummaries)
        .map(
          promise => promise
            .then(value => ({ status: 'fulfilled', value }))
            .catch(reason => ({ status: 'rejected', value: reason }))
        )
    )

    // build summaries data with columns index
    try {
      const summariesData = await promiseAll
      let groupedSummaries = groupBy(mapSummaries, 'column')
      // build merge result
      return columns.map(column => {
        let summary = mapSummaries.find(sum => sum.column === column.name)
        if (!summary) return { column: column.name, value: undefined }
        // multi summaries
        if (groupedSummaries[column.name].length > 1) {
          let options = []
          const multiSummaries = cloneDeep(groupedSummaries[column.name])
          multiSummaries.forEach((sum, index) => {
            for (const item of summariesData) {
              if (item.status === 'fulfilled') {
                let formatFn = dsFormatManager.create(sum.format, false)
                const multiSummariesIndex = item.value.cols.findIndex(col => col.name === sum.alias)
                if (multiSummariesIndex !== -1) options.push({value: formatFn(item.value.rows[0][multiSummariesIndex]), text: sum.label})
              }
            }
            if (options.length !== index + 1) options.push({value: sum.noDataMessage, text: sum.label})
          })
          return { column: summary.column, options: options }
        } else {
          let indexMergeSummaryIndex = result.mergeSummaries.findIndex(sum => sum.id === summary.id)
          let indexStandaloneSummary = result.standaloneSummaries.findIndex(sum => sum.id === summary.id)
          let formatFn = dsFormatManager.create(summary.format, false)

          if (indexMergeSummaryIndex !== -1) {
            if (summariesData[0].status === 'rejected') return summary.noDataMessage
            let value = summariesData[0].value.rows[0][indexMergeSummaryIndex]
            return value !== null
              ? { column: summary.column, value: formatFn(value) }
              : { column: summary.column, value: summary.noDataMessage }
          } else {
            let index = result.mergeSummaries.length ? indexStandaloneSummary + 1 : indexStandaloneSummary
            return summariesData[index].status === 'fulfilled'
              ? { column: summary.column, value: formatFn(summariesData[index].value.rows[0][0]) }
              : { column: summary.column, value: summary.noDataMessage }
          }
        }
      })
    } catch (e) {
      console.error('Error summaries', e)
      return []
    }
  }

  // this function to map current columns base on column config
  mapIndexConfigColumnsToCurrentTableColumns(configColumns, currentColumns) {
    return map(currentColumns, column => {
      return find(configColumns, col => col.name === column.name)
    })
  }

  // this function to map current columns base on column config
  mapIndexTableColumnsToCurrentConfigColumns(configColumns, currentColumns, summaries, group) {
    let groupedColumn = group.columns[0]
    let newIndexColumns = map(configColumns, column => {
      return find(currentColumns, col => col.name === column.name)
    }).filter(column => !!column)
    let newColumns = filter(configColumns, column => {
      return !find(currentColumns, col => col.name === column.name)
    })
    newIndexColumns = [...newIndexColumns, ...newColumns]
    // grouped column must be the first one
    if (groupedColumn) {
      let col = cloneDeep(find(currentColumns, col => [col.name, createBinColumnAlias(col.name)].includes(groupedColumn.name)))
      newIndexColumns = [col, ...filter(newIndexColumns, column => column.name !== col.name)]
    }
    return {
      summaries: newIndexColumns.map(column => {
        return summaries.find(sum => sum ? sum.column === column.name : false)
      }),
      columns: newIndexColumns.map(column => {
        let col = configColumns.find(col => col.name === column.name)
        column.visible = col.visible
        return column
      })
    }
  }

  // this function to map new size for item
  setDataSize(data, size) {
    if (data && data.items) {
      let internalData = cloneDeep(data)
      internalData.items.map(item => {
        return (item.size = size)
      })
      return internalData
    }
  }

  // change format of column data
  formatChange({ columns, items }, colData, { aggregations }, bins) {
    let formatFn = null
    let column = columns.find(column => column.name === colData.col.name)
    let aggregation = aggregations.find(aggr => aggr.column === colData.col.name)

    // map data
    return {
      columns,
      items: items.map(item => {
        if (bins && bins.findIndex(bin => bin.column.name === colData.col.name) !== -1) { // has bin
          let formatConfig = column.cell.format
          formatFn = (data) => dsFormatManager.formatBin(data, formatConfig, true)
        } else if (column.aggregation) { // is aggregation
          let aggrType = aggregation ? getAggregationDataTypeStr(column.type, aggregation.aggregation) : column.type

          formatFn = column.aggrFormats
            ? dsFormatManager.createAggrFormat(aggrType, column.cell.format, aggregation.aggregation, column.aggrFormats, true)
            : dsFormatManager.create(column.cell.format, true)
        } else if (column.cell.format) { // for normal case
          formatFn = dsFormatManager.create(column.cell.format, true)
        }
        // format data
        formatFn
          ? item.data[column.name].format = formatFn(item.data[column.name].base)
          : item.data[column.name].format = item.data[column.name].base
        // save format function into current item
        item.data[column.name].formatFn = formatFn
        // return item
        return item
      })
    }
  }

  updateSummaries(columns, summaries) {
    const summaryMap = summaries.reduce((map, sum) => {
      map[sum.column] = sum
      return map
    }, {})

    return columns.map(column => {
      const summary = summaryMap[column.name]

      if (!summary) {
        return { column: column.name, value: undefined }
      }

      if (summary.options) {
        return { column: summary.column, options: summary.options }
      }

      const formatFn = dsFormatManager.create(summary.format, false)
      return { column: summary.column, value: summary.value ? formatFn(summary.value) : undefined }
    })
  }
}
