import cloneDeep from 'lodash/cloneDeep'
import isObject from 'lodash/isObject'
import groupBy from 'lodash/groupBy'
import uniq from 'lodash/uniq'
import range from 'lodash/range'
import flatten from 'lodash/flatten'

export class CrosstabChart {
  /**
   * @typedef DataSource
   * @type Object
   * @property {Array} cols - columns
   * @property {Array} rows - 2D array which contains values of columns
   **/

  /**
   * @typedef CrosstabDataSource
   * @type Object
   * @property {Array} cols - columns
   * @property {Array} rows - 2D array which contains values of columns
   * @property {Array} tValues - values of t column
   **/

  /**
   * This method will build data from grouping datasource into crosstab datasource
   * Only work with 1 X column, 1 T Column and 1 Y Value
   * @param {DataSource} dataSource
   * @param {Object} chartConfig - object config of crosstab chart
   * @return {CrosstabDataSource} crosstab datasource
   * **/
  static buildCrosstabChartData(dataSource, chartConfig) {
    // get bins
    const bins = cloneDeep(chartConfig.bins)

    // find indexes
    const xIndexes = chartConfig.charts[0].series.map(item => {
      const xName = item.data.x
      const binX = bins.find(bin => bin.column.name === xName)
      return dataSource.cols.findIndex(col => col.name === (binX ? binX.alias : xName))
    })

    const yIndexes = chartConfig.charts[0].series.map(item => {
      const { name, aggregation } = item.data.y
      return dataSource.cols.findIndex(col => col.name === `${name}_${aggregation}_${item.id}`)
    })

    const tIndexes = chartConfig.charts[0].series.map(item => {
      const tName = item.data.t
      const binT = bins.find(bin => bin.column.name === tName)
      return dataSource.cols.findIndex(col => col.name === (binT ? binT.alias : tName))
    })

    // build crosstab data
    const xValues = uniq(flatten(dataSource.rows.map(row => row.filter((v, i) => xIndexes.includes(i)))))
    const tValues = uniq(flatten(dataSource.rows.map(row => row.filter((v, i) => tIndexes.includes(i)))))

    // build columns
    let cols = tValues.reduce((cols, tValue) => {
      yIndexes.forEach((yIndex, i) => {
        cols.push({
          name: `${dataSource.cols[yIndex].name}_${tValue}`,
          type: 'int',
          baseName: chartConfig.charts[0].series[i].data.y.name
        })
      })
      return cols
    }, dataSource.cols
      .filter((col, i) => xIndexes.includes(i))
      .map((col, i) => {
        col.baseName = chartConfig.charts[0].series[i].data.x
        return col
      })
    )

    // build rows
    const group = groupBy(
      dataSource.rows,
      (row) => row
        .filter((v, i) => xIndexes.includes(i))
        .map(v => isObject(v) ? v.label : v)
        .join('_')
    )

    const rows = Object
      .keys(group)
      .reduce((rows, key) => {
        // 1 x value has many t value
        const xData = xValues.find(value => (isObject(value) ? value.label : value) === key)
        const tData = flatten(
          tValues
            .map(value => {
              const defaultRow = range(dataSource.cols.length).map((v, i) => {
                return tIndexes.includes(i)
                  ? value
                  : 0
              })
              let row = group[key]
                .filter(row => {
                  const tValue = row[tIndexes[0]]
                  const v1 = isObject(tValue) ? tValue.label : tValue
                  const v2 = isObject(value) ? value.label : value
                  return v1 === v2
                })[0] || defaultRow
              return row.filter((v, i) => yIndexes.includes(i))
            })
        )
        rows = [...rows, [xData, ...tData]]
        return rows
      }, [])

    return {
      cols,
      rows,
      tValues
    }
  }

  /**
   * This method will get only y column from basic and remove x column, x value
   * @param {DataSource} dataSource
   * @param {Object} chartConfig - object config of crosstab chart
   * @return {DataSource} crosstab datasource - which has same structure as datasource
   * **/
  static buildBasicChartData(dataSource, chartConfig) {
    // find indexes
    const yIndexes = chartConfig.charts[0].series.map(item => {
      return dataSource.cols.findIndex(col => col.name.includes(item.data.y) && col.name.includes(item.id))
    })

    // build columns
    let cols = dataSource.cols
      .filter((col, i) => yIndexes.includes(i))
      .map((col, i) => {
        col.baseName = chartConfig.charts[0].series[i].data.y
        return col
      })

    // build rows
    let rows = dataSource.rows.map(row => row.filter((v, i) => yIndexes.includes(i)))

    return {
      cols,
      rows
    }
  }
}
