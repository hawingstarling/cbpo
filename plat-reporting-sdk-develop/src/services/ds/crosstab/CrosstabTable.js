import findIndex from 'lodash/findIndex'
import uniqWith from 'lodash/uniqWith'
import isEqual from 'lodash/isEqual'
import sortBy from 'lodash/sortBy'
import isObject from 'lodash/isObject'
import cloneDeep from 'lodash/cloneDeep'
import DataManager from '../data/DataManager'
import HeaderColumnsMatching from '@/services/ds/crosstab/HeadersCrosstab'

export default class CrosstabTableManager {
  // data manager
  dm = null

  // value of Group X Columns
  x = []
  // value of Group T Columns
  t = []
  // value of X,T values, z by 'valueX_valueT'
  y = []

  // this one used for render UI
  binColumns = {
    x: [],
    y: [],
    t: []
  }

  constructor(dataSource) {
    if (dataSource) {
      this.setDataSource(dataSource)
    }
  }

  // Set new data source
  setDataSource(dataSource) {
    let {cols = [], rows = []} = dataSource
    if (!this.dm) {
      this.dm = new DataManager()
    }
    this.dm.setData(cols, rows)
    return this
  }

  setHeaders(xHeaders, tHeaders) {
    this.xHeaders = xHeaders
    this.tHeaders = tHeaders
  }

  setColumns(x, t, y) {
    /**
     * set 3 types columns x,y,t
     @param {Array} x: x columns
     @param {Array} t: t columns
     @param {Object} y: y columns
     **/
    this.x = x
    this.y = y
    this.t = t
  }

  /**
   * From 2 grouped column configs (x, t), transform current data source into 3 types x,y,t columns
   * @param {Array} bins: config bins
   * @param {Array} xColumns: config grouping of columns x
   * @param {Array} yColumns: config grouping of columns y
   * @param {Array} tColumns: config grouping of columns t
  */
  mappingDataSourceWithColumns(bins, xColumns, yColumns, tColumns, sorting) {
    // find index of all grouped columns (x, t)
    // keyIndexes and index of x,t value must be the same

    let keyIndexes = [...xColumns, ...tColumns].map((col) => {
      let bin = bins.find(bin => bin.column.name === col.name)
      return findIndex(this.dm.cols, _col => _col.name === (bin ? bin.alias : col.name))
    })

    // keyIndexes and index of x,t value must be the same to headers
    let x = this._mappingColumnsFromTabsAndHeader(bins, xColumns, sorting)
    let t = this._mappingColumnsFromTabsAndHeader(bins, tColumns, sorting)
    let y = []
    let xHeaders = HeaderColumnsMatching.getHeaders(x)
    let tHeaders = HeaderColumnsMatching.getHeaders(t)

    this.setHeaders(xHeaders, tHeaders)

    for (let iXH = 0; iXH < xHeaders.length; iXH++) {
      for (let iTH = 0; iTH < tHeaders.length; iTH++) {
        let newMappingValues = [...xHeaders[iXH], ...tHeaders[iTH]]
        let queryStr = newMappingValues.reduce((queries, current, i) => {
          let isBin = isObject(current) && current.label
          let value = isBin ? `"${current.label}"` : (current ? `"${current}"` : current)
          let query = isBin ? `row[${keyIndexes[i]}] && row[${keyIndexes[i]}].label == ${value}` : `(row[${keyIndexes[i]}] ? row[${keyIndexes[i]}].toString() : row[${keyIndexes[i]}]) == ${value}`
          queries = [...queries, query]
          return queries
        }, '').join(' && ')
        // eslint-disable-next-line no-eval
        let values = this.dm.rows.find(row => eval(queryStr))
        if (!y[iXH]) {
          y[iXH] = []
        }
        y[iXH][iTH] = values || [null]
      }
    }

    this.setColumns(x, t, y)

    return this
  }

  /**
   * Set status of each type columns if its has binning
   * @param {Array} bins: config bins
   * @param {Array} xColumns: config grouping of columns x
   * @param {Array} yColumns: config grouping of columns y
   * @param {Array} tColumns: config grouping of columns t
   */
  mappingStatusColumns(bins, xColumns, yColumns, tColumns) {
    let handlerCallback = (arr, column) => {
      let binColumn = bins.find(bin => bin.column.name === column.name)
      if (binColumn) arr.push(binColumn)
      return arr
    }
    this.binColumns.x = xColumns.reduce(handlerCallback, [])
    this.binColumns.t = tColumns.reduce(handlerCallback, [])
    this.binColumns.y = yColumns.reduce(handlerCallback, [])

    return this
  }

  /**
   * From 2 grouped column configs (x, t), transform current data source into 3 types x,y,t columns
   * @param {Array} bins: config bins
   * @param {Array} columns: xColumns or tColumns
   * */
  _mappingColumnsFromTabsAndHeader(bins, columns, sorting) {
    return columns.map(column => {
      let bin = bins.find(b => b.column.name === column.name)
      let index = findIndex(this.dm.cols, _col => _col.name === (bin ? bin.alias : column.name))
      let orderIndex = findIndex(sorting, st => st.column === (bin ? bin.alias : column.name))
      let uniqRows = cloneDeep(uniqWith(this.dm.rows.map(r => r[index]), isEqual))
      if (orderIndex === -1) return uniqRows
      let sortValues = sortBy(uniqRows, (o) => isObject(o) ? o.min && o.max : o)
      return sorting[orderIndex].direction === 'desc' ? sortValues.reverse() : sortValues
    })
  }
}
