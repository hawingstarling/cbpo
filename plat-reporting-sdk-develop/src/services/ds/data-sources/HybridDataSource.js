import LocalDataSource from './LocalDataSource'
import DataManager from '../data/DataManager'
import _ from 'lodash'
import { formatArrayToBlob, handleExportFileFromBlobType } from '../../../utils/fileUtil'
import { DsQueryExpr } from 'plat-expr-sdk'
import { DsQueryExecService } from '@/services/ds/expression/DsQueryExec'
import get from 'lodash/get'

class HybridDataSource extends LocalDataSource {
  constructor(id) {
    super(id)
    this._data = window[id]
    this._dm = new DataManager(this._data.cols, this._data.rows)
  }
  async processRows (rows, cols, params) {
    const promises = rows.map(async (row) => {
      const newRow = []
      const apiCalls = []
      for (let index = 0; index < row.length; index++) {
        if (cols[index]) {
          newRow[index] = row[index]
        }
        const { filter, timezone, dataSource } = params

        if (typeof row[index] === 'number') {
          newRow[index] = row[index]
        } else {
          const dsQueryExec = new DsQueryExecService(filter, timezone)
          const dsQueryExpr = new DsQueryExpr(dsQueryExec)
          apiCalls.push(dsQueryExpr.eval(dataSource, row[index].replace(/[{}]/g, '')))
        }
      }
      const evaluatedResults = await Promise.all(apiCalls)
      evaluatedResults.forEach((evaluated, index) => {
        newRow[index] = get(evaluated, 'rows[0][0]')
      })
      return newRow
    })
    const rowsData = await Promise.all(promises)
    return rowsData
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

    const rowsData = await this.processRows(rows, cols, params)
    rows = rowsData

    cols = [cols.map(col => col.alias || col.name)]
    let fileData = _.concat(cols, rows)
    let data = formatArrayToBlob(fileData, fileType)
    // handle download file
    handleExportFileFromBlobType(data, fileName)
  }
}

export default HybridDataSource
