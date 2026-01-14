import {findIndex, reduce, each} from 'lodash'
/**
 * From original data object, build an array of index of visible columns.
 * @param {Array} dataColumns list of standard data columns
 * @param {Array} visibleColumnName list of visible columns
 * @return {Array} of matched indexes
 */
export const getIndexesOfVisibleColumns = (dataColumns, visibleColumnNames) => {
  let indexes = []
  each(visibleColumnNames, (columnName, i) => {
    let colIndex = findIndex(dataColumns, {name: columnName})
    indexes.push(colIndex)
    if (colIndex === -1) console.error(`Invalid visibleColumnNames, ${columnName} is not found`)
  })
  return indexes
}

export const getIndexesOfGroupedColumns = (dataColumns, indexesVisibleColumns, groupedColumn) => {
  return reduce(groupedColumn, (indexes, columnName, i) => {
    let colIndex = findIndex(dataColumns, {name: columnName})
    if (colIndex !== -1) {
      indexes.push(indexesVisibleColumns.indexOf(colIndex))
    } else {
      console.error(`Invalid groupedColumns, ${columnName} is not found`)
    }
    return indexes
  }, [])
}
