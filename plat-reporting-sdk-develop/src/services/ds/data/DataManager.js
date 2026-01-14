import _ from 'lodash'
import precond from 'precond'
import DataRow from './DataRow'

import {
  calculateAggregationOfAnArrayOfFlatValues,
  getBinTypeFromSourceType,
  DataTypeUtil
} from './DataTypes'
import { LocalFilterExpressionBuilder } from '../filter/FilterExpessionBuilders'
import {NumericBin, TemporalBin} from 'plat-sdk'
import moment from 'moment'
import { BINNING_TYPES, createBinType } from '@/utils/binUtils'

const temporalBin = new TemporalBin()
const numericBin = new NumericBin()

/**
 * This class will manage platform data structure
 * (this won't interact with data source,
 * this is just to manage the data object received from data source)
 */
export default class DataManager {
  constructor (cols, rows) {
    this.reset()
    if (cols && rows) {
      this.setData(cols, rows)
    }
  }
  reset () {
    // list of raw rows (2D array, without columns)
    this.rows = []
    // list of raw columns
    this.cols = []
    // list of row meta data that holding profile of a rows
    this.metaRows = []
    // column name to index
    this.columnNameToIndex = {}
    this.columnNameToColumn = {}
  }
  mappingIndexMetaRows(newCols, newRows, bins) {
    let dm = new DataManager(newCols, newRows)
    return newRows.reduce((rows, row) => {
      let r = _.cloneDeep(row)
      newCols.forEach(col => {
        row.splice(this.columnNameToIndex[col.name], 1, r[dm.columnNameToIndex[col.name]])
      })
      rows.push(row)
      return rows
    }, [])
  }
  createMetaRows (rows, parentMetaRow) {
    return _.map(rows, (row) => {
      return new DataRow(row, parentMetaRow ? parentMetaRow.row : null, parentMetaRow, parentMetaRow ? parentMetaRow.level + 1 : 0)
    })
  }
  setData (cols, rows, metaRows) {
    if (_.isEmpty(metaRows)) {
      metaRows = this.createMetaRows(rows)
    }
    Object.assign(this, {cols, rows, metaRows})
    this._indexColumns()
  }
  setColumns (cols) {
    this.cols = cols
  }
  // tslint:disable-next-line
  addData (cols, rows, metaRows, atIndex) {
    this.rows.splice(atIndex, 0, ...rows)
    this.metaRows.splice(atIndex, 0, ...metaRows)
    this._indexColumns()
  }
  _indexColumns () {
    this.cols.forEach((col, i) => {
      this.columnNameToIndex[col.name] = i
      this.columnNameToColumn[col.name] = col
    })
  }
  /**
   * From the current data, make group of data.
   *
   * @param {Array} columns List of column
   * @param {Array} aggregations List of aggregations
   * @param {Array} bins List of bins
   * @return {{rows: Array, cols: []}} rows and cols
   */
  groupData (columns, aggregations, bins = []) {
    precond.checkIsArray(columns, 'columns must be an array')
    precond.checkIsArray(aggregations, 'aggregations must be an array')
    let cols = []
    let specialCharacter = '*_:_*'
    let newDM = new DataManager()

    let queryStr = (row) => _.map(columns, col => {
      let bin = bins.find(bin => bin.alias === col.name)
      return bin ? row[this.columnNameToIndex[bin.alias]].label : row[this.columnNameToIndex[col.name]]
    }).join(specialCharacter)

    // create new cols
    _.each([...columns, ...aggregations], column => {
      let isAggType = !!column.column
      let col = this.columnNameToColumn[isAggType ? column.column : column.name]
      if (col) {
        isAggType
          ? cols.push({ name: column.alias || column.column, type: col.type })
          : cols.splice(this.columnNameToIndex[column.name], 0, this.columnNameToColumn[column.name])
      }
    })

    newDM.setData(cols, [])

    bins.forEach(bin => {
      if (newDM.columnNameToIndex[bin.alias] === undefined) {
        newDM.columnNameToIndex[bin.alias] = Object.keys(newDM.columnNameToIndex).length - 1
        newDM.columnNameToColumn[bin.alias] = bin
      }
    })

    let uniqRows = _.uniqBy(this.rows, row => queryStr(row))
    let groupedRows = _.groupBy(this.rows, (row) => queryStr(row))

    let rows = _.map(uniqRows, (row) => {
      let children = groupedRows[queryStr(row)] // grouped children
      let row2 = []
      let zip = _.zip(...children)
      _.each(aggregations, (agg) => {
        let aggColIndex = this.columnNameToIndex[agg.column]
        let calcValue = calculateAggregationOfAnArrayOfFlatValues(zip[aggColIndex].map(data => {
          return data.bin ? data.label : data
        }), agg.aggregation)
        if (bins.find(bin => bin.alias === agg.column)) {
          row2.push({label: calcValue, bin: zip[aggColIndex][0].bin})
        } else {
          row2.push(calcValue)
        }
      })
      _.each(columns, column => {
        row2.splice(newDM.columnNameToIndex[column.name], 0, row[this.columnNameToIndex[column.name]])
      })
      return row2
    })
    return {cols, rows}
  }
  filterData (filter) {
    let filterBuilder = new LocalFilterExpressionBuilder()
    let exp = filterBuilder.buildExpression(filter)
    if (!exp) {
      return { rows: this.rows, cols: this.cols }
    }
    let rows = _.filter(this.rows, (row) => {
      // eslint-disable-next-line no-unused-vars
      let __colValue = (columnName) => {
        // must named it __colValue
        let val = row[[this.columnNameToIndex[columnName]]]
        if (!val) {
          return val // null or empty should be kept
        }
        let col = this.columnNameToColumn[columnName]
        return DataTypeUtil.isTemporal(col.type) ? col.type === 'date' ? moment(val).startOf('day').format() : moment(val).format() : val
      }
      // eslint-disable-next-line no-unused-vars
      let __getString = (quotedColumn) => {
        // must named it __getString
        if (
          quotedColumn === null ||
          quotedColumn === undefined ||
          (typeof quotedColumn === 'number' && isNaN(quotedColumn))
        ) {
          quotedColumn = ''
        }
        return String(quotedColumn)
      }
      // eslint-disable-next-line no-eval
      return eval(exp)
    })
    return { cols: this.cols, rows }
  }
  getColumnByName (columnName) {
    return this.columnNameToColumn[columnName]
  }
  hasChild (row) {
    return !!_.find(this.metaRows, metaRow => metaRow.parent === row)
  }
  /**
   * Get mapped data points.
   * @param {Ojbect} columnToKeyMap of column map from a key to a column name.
   *
   * @example getSeriesDataByKeysToColumns({x: 'column1', y: 'column2'}) will return [{x: 'A value of column1', y: 'A value of column2'}...] an so on.
   */
  getSeriesDataByKeysToColumns (keyToColumnMap) {
    let keys = Object.keys(keyToColumnMap)
    let series = this.rows.map((row) => {
      let obj = {}
      _.each(keys, (key) => {
        obj[key] = row[this.columnNameToIndex[keyToColumnMap[key]]]
      })
      return obj
    })
    return series
  }

  makeBins(bins) {
    let cols = [...this.cols]
    let rows = [...this.rows]
    if (_.isEmpty(rows)) {
      return {rows, cols}
    }
    const callback = (row, type) => {
      if (DataTypeUtil.isTemporal(type)) {
        let isValidDate = moment(row).isValid()
        return isValidDate ? new Date(row) : null
      } else if (DataTypeUtil.isNumeric(type)) {
        let isValidNumber = _.isNumber(row)
        return isValidNumber ? Number(row) : null
      }
      return null
    }

    // mapping rows
    bins
      // convert bin config into bin value
      .map(bin => {
        let tempData = rows.map(r => r[this.columnNameToIndex[bin.column.name]])
        let min = _.min(tempData, r => callback(r, bin.column.type))
        let max = _.max(tempData, r => callback(r, bin.column.type))
        if (DataTypeUtil.isTemporal(bin.column.type)) {
          min = new Date(min)
          max = new Date(max)
          if (bin.options.alg === BINNING_TYPES.UNIFORM) {
            return temporalBin.makeUniformBins(min, max, bin.options.uniform.unit, Number(bin.options.uniform.width))
          } else if (bin.options.alg === BINNING_TYPES.AUTO) {
            return temporalBin.makeAutoBins(min, max, Number(bin.options.numOfBins))
          }
        } else if (DataTypeUtil.isNumeric(bin.column.type)) {
          if (bin.options.alg === BINNING_TYPES.UNIFORM) {
            return numericBin.makeUniformBins(min, max, Number(bin.options.uniform.width), bin.options.nice)
          } else if (bin.options.alg === BINNING_TYPES.AUTO) {
            return numericBin.makeAutoBins(min, max, Number(bin.options.numOfBins), bin.options.nice)
          }
        } else {
          console.error('Binning not support type: ' + bin.column.type)
        }
      })
      // replace binValue into data of each row
      .forEach((binValues, index) => {
        let columnIndex = this.columnNameToIndex[bins[index].column.name]
        rows = rows.map(row => {
          let binValue = binValues.find(bin => {
            let value = DataTypeUtil.isTemporal(bins[index].column.type)
              ? new Date(row[columnIndex])
              : Number(row[columnIndex])
            return (bin.min <= value && value < bin.max)
          })
          if (!binValue && row[columnIndex] === binValues[binValues.length - 1].max) {
            binValue = binValues[binValues.length - 1]
          }
          binValue.bin = {...bins[index].options, ...{index}}
          row.push(binValue)
          return row
        })
      })

    // mapping cols
    cols = [...cols, ...bins.map(bin => ({name: bin.alias, type: getBinTypeFromSourceType(createBinType(bin.column.type))}))]

    // return data source
    return {
      rows,
      cols
    }
  }
}
