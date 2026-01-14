import AbstractDataSource from './AbstractDataSource'
import DataManager from '../data/DataManager'
import _ from 'lodash'
import { DataTypeUtil } from '../data/DataTypes'
import { formatArrayToBlob, handleExportFileFromBlobType } from '../../../utils/fileUtil'
import { StaticExpression } from 'plat-sdk'

const parseFilterFromStaticExpression = (filter) => {
  if (_.isEmpty(filter)) return
  filter.conditions.forEach(child => {
    if (child.conditions) {
      parseFilterFromStaticExpression(child)
    } else {
      if (_.isArray(child.value)) {
        child.value = _.map(child.value, value => {
          if (value && !_.isNumber(value) && StaticExpression.isValid(value)) {
            return StaticExpression.eval(value)
          }
          return value
        })
      }
      child.value = child.value && !_.isArray(child.value) && !_.isNumber(child.value) && StaticExpression.isValid(child.value) ? StaticExpression.eval(child.value) : child.value
    }
  })
}

/**
 * {@class LocalDataSource} is an implementation of {@link AbstractDataSource} for local data.
 * Local data is a data source that simply introduced as a data object of { cols: [], rows: [] }.
 */
class LocalDataSource extends AbstractDataSource {
  constructor(id) {
    super(id)
    this._data = window[id]
    this._dm = new DataManager(this._data.cols, this._data.rows)
  }
  /**
   * @override
   */
  async columns() {
    let dm = this._dm
    return dm.cols
  }
  /**
   * @override
   **/
  async export (params, fileName = '', fileType = 'csv', columns = []) {
    let paramsExport = _.cloneDeep(params)
    _.set(paramsExport, 'paging.limit', 50000)
    let { cols, rows } = await this.query(paramsExport)
    // manage columns
    if (!_.isEmpty(columns)) {
      cols = columns.filter(col => [true, undefined, null].includes(col.visible))
    }

    // map rows
    rows = rows.map(row => row.reduce((res, item, index) => {
      if (cols[index]) {
        res[index] = item
      }
      return res
    }, []))

    cols = [cols.map(col => col.alias || col.name)]
    let fileData = _.concat(cols, rows)
    let data = formatArrayToBlob(fileData, fileType)
    // handle download file
    handleExportFileFromBlobType(data, fileName)
  }
  /**
   * @override
   */

  async query(params, cancelToken) {
    let { paging } = params
    if (!paging) paging = {current: 1, limit: 1000}
    let { limit, current = 1 } = paging
    let dm = _.cloneDeep(this._dm)
    // filter
    if (!_.isEmpty(params.filter)) {
      let paramsFilter = _.cloneDeep(params.filter)
      parseFilterFromStaticExpression(paramsFilter)
      let filteredData = dm.filterData(paramsFilter)
      dm.setData(filteredData.cols, filteredData.rows, dm.metaRows)
    }

    // bins
    if (!_.isEmpty(params.bins)) {
      let binData = dm.makeBins(params.bins)
      dm.setData(binData.cols, binData.rows, dm.metaRows)
    }

    // group and aggregations
    if (!_.isEmpty(params.group)) {
      if (!_.isEmpty(params.group.columns) || !_.isEmpty(params.group.aggregations)) {
        let { group: {columns, aggregations}, bins } = params
        let groupedData = dm.groupData(columns, aggregations, bins)
        dm.setData(groupedData.cols, groupedData.rows, dm.metaRows)
      }
    }

    // sort
    if (!_.isEmpty(params.orders)) {
      let orderFunctions = []
      let orderDirections = []
      const getOrderParam = (orderObj) => {
        if (!_.isEmpty(orderObj)) {
          let { column, direction } = orderObj
          let bins = params.bins
          let bin = null
          if (bins && bins.length) {
            bin = bins.find(bin => bin.alias === column)
          }
          let columnIndex = _.findIndex(dm.cols, { name: bin ? bin.alias : column })
          let orderFunction = (row) => {
            if (!_.isEmpty(bin)) {
              if (!_.isUndefined(row[columnIndex].max) && !_.isNull(row[columnIndex].max)) {
                return row[columnIndex].max
              } else if (!_.isUndefined(row[columnIndex].min) && !_.isNull(row[columnIndex].min)) {
                return row[columnIndex].min
              } else {
                return null
              }
            }
            return dm.cols[columnIndex] && DataTypeUtil.isNumeric(dm.cols[columnIndex].type) ? parseFloat(row[columnIndex]) : (bin ? row[columnIndex].label : row[columnIndex])
          }
          return {
            direction,
            orderFunction
          }
        }
      }
      params.orders.forEach(order => {
        const { direction, orderFunction } = getOrderParam(order)
        orderFunctions.push(orderFunction)
        orderDirections.push(direction)
      })

      let newRows = _.orderBy(dm.rows, orderFunctions, orderDirections)

      dm.setData(dm.cols, newRows, dm.metaRows)
    }

    // page
    return { cols: dm.cols, rows: dm.rows.slice((current - 1) * limit, current * limit), dm }
  }
  /**
   * @override
   */
  async total(params, cancelToken) {
    let dm = _.cloneDeep(this._dm)

    // filter
    if (!_.isEmpty(params.filter)) {
      let filteredData = new DataManager(dm.cols, dm.rows).filterData(params.filter)
      dm.setData(filteredData.cols, filteredData.rows, dm.metaRows)
    }

    // bins
    if (!_.isEmpty(params.bins)) {
      let binData = dm.makeBins(params.bins)
      dm.setData(binData.cols, binData.rows, dm.metaRows)
    }

    // group
    if (!_.isEmpty(params.group)) {
      if (!_.isEmpty(params.group.columns)) {
        let { columns, aggregations } = params.group
        let groupedData = dm.groupData(columns, aggregations, params.bins)
        dm.setData(groupedData.cols, groupedData.rows, dm.metaRows)
      }
    }
    return _.size(dm.rows)
  }
}

export default LocalDataSource
