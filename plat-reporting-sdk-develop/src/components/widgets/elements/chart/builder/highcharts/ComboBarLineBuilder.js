import { BarChartBuilder } from '@/components/widgets/elements/chart/builder/highcharts/BarChartBuilder'
import dataFormatManager from '@/services/dataFormatManager'
import { getColorForSpecificItemSeries, getStyle } from '@/utils/chartUtil'
import defaultsDeep from 'lodash/defaultsDeep'
import get from 'lodash/get'
import isObject from 'lodash/isObject'
import uniq from 'lodash/uniq'
import uniqBy from 'lodash/uniqBy'
import moment from 'moment'
import { HC_TYPES } from '@/components/widgets/elements/chart/ChartConfig'

export class ComboBarLineBuilder extends BarChartBuilder {
  getBaseConfig() {
    return {
      title: {
        text: null
      }
    }
  }

  __buildAxis(dataSource, chartConfig) {
    const color = getStyle()

    const firstSeries = get(chartConfig, 'charts[0].series[0]')

    const xBin = get(chartConfig, 'bins', []).find(bin => bin.column.name === firstSeries.data.x)
    const xAxisConfig = get(chartConfig, 'charts[0].axis.x', []).find(axis => axis.id === firstSeries.axis.x)

    const xIndex = dataSource.cols.findIndex(column => column.name === (xBin ? xBin.alias : firstSeries.data.x))
    const xFormat = xAxisConfig ? xAxisConfig.format : null
    const xFormatter = xFormat ? dataFormatManager.create(xFormat, true) : null

    const sourceXColumn = dataSource.cols[xIndex]

    let xAxis = {
      visible: true,
      title: {
        enabled: false
      },
      labels: {
        style: {
          color: color.accentColor
        }
      }
    }

    let yAxis = get(chartConfig, 'charts[0].series', []).map((item, index) => {
      const yAxisConfig = get(chartConfig, 'charts[0].axis.y', []).find(axis => axis.id === item.axis.y)

      const yFormat = yAxisConfig ? yAxisConfig.format : null
      const yFormatter = yFormat ? dataFormatManager.create(yFormat, true) : null

      let newYAxis = {
        dataId: item.axis.y || index,
        min: 0,
        visible: true,
        reversed: false,
        title: {
          enabled: false
        },
        tickAmount: get(yAxisConfig, 'ticks.maxTicksLimit', undefined),
        tickInterval: get(yAxisConfig, 'ticks.stepSize', undefined) || undefined,
        opposite: get(yAxisConfig, 'position', 'left') === 'right',
        labels: {
          style: {
            color: color.accentColor
          },
          formatter: function() {
            return yFormatter ? yFormatter(this.value) : this.value
          }
        }
      }

      if (yAxisConfig && get(yAxisConfig, 'scaleLabel.display')) {
        yAxis = {
          ...yAxis,
          ...{
            title: {
              enabled: true,
              text: yAxisConfig.scaleLabel.labelString || ''
            }
          }
        }
      }

      return newYAxis
    })

    if (xAxisConfig && get(xAxisConfig, 'scaleLabel.display')) {
      xAxis = {
        ...xAxis,
        ...{
          title: {
            enabled: true,
            text: xAxisConfig.scaleLabel.labelString || ''
          }
        }
      }
    }

    if (['datetime', 'date', 'temporal'].includes(sourceXColumn.type) && !xBin) {
      const timeAxis = {
        type: 'datetime'
      }
      xAxis = {...xAxis, ...timeAxis}
    } else {
      const categoriesAxis = {
        categories: uniq(dataSource.rows.map(row => {
          if (!xBin && sourceXColumn) {
            if (sourceXColumn.type === 'date') {
              // for x column but with date string
              return moment(row[xIndex]).format('MM/DD/YYYY')
            } else if (['datetime', 'temporal'].includes(sourceXColumn.type)) {
              // for x column but with datetime string
              return moment(row[xIndex]).format('MM/DD/YYYY hh:mm a')
            }
          }
          const value = isObject(row[xIndex])
            ? row[xIndex].label
            : row[xIndex]
          return xFormatter ? xFormatter(value) : value
        }))
      }
      xAxis = {...xAxis, ...categoriesAxis}
    }

    return {
      xAxis: [xAxis],
      yAxis: [...uniqBy(yAxis, 'dataId')]
    }
  }

  __buildSeries(config, data, { axis, chartConfig }) {
    config.series = data.map((item, index) => {
      const seriesItem = chartConfig.charts[0].series[index]
      let step = get(seriesItem, `options.step`)
      let type = seriesItem.type
      const dashStyle = type === 'line' ? get(seriesItem, `options.dashStyle`, 'solid') : null
      if (type === 'bar') type = get(seriesItem, 'options.isHorizontal') ? HC_TYPES.BAR : HC_TYPES.COLUMN
      if (type === 'line' && !step) type = HC_TYPES.SPLINE

      const yAxisIndex = axis.yAxis.findIndex(axis => axis.dataId === seriesItem.axis.y)
      return {
        data: item,
        yAxis: yAxisIndex !== -1 ? yAxisIndex : index,
        name: seriesItem.name || ('Series ' + index),
        type,
        step: ['left', 'right', 'center'].includes(step) ? step : undefined,
        color: getColorForSpecificItemSeries(seriesItem),
        dashStyle
      }
    })
  }

  __buildConfig(config, { chartConfig, tooltip, legend, axis, plotOptions, colors }) {
    const color = getStyle()

    defaultsDeep(config, {
      chart: {
        backgroundColor: color.mainColor
      },
      plotOptions,
      colors,
      tooltip,
      legend,
      xAxis: axis.xAxis,
      yAxis: axis.yAxis
    })
  }
}
