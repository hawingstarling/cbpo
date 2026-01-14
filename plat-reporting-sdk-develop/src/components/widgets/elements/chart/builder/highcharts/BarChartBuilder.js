import { AbstractBuilder } from '@/components/widgets/elements/chart/builder/AbstractBuilder'
import dataFormatManager from '@/services/dataFormatManager'
import {
  getColorForSpecificItemSeries,
  getColorSchemes,
  getStyle,
  mappingColumnNameToAliasNameWithGrouping,
  setColorGradient
} from '@/utils/chartUtil'
import defaultsDeep from 'lodash/defaultsDeep'
import flatten from 'lodash/flatten'
import get from 'lodash/get'
import uniq from 'lodash/uniq'
import isString from 'lodash/isString'
import findIndex from 'lodash/findIndex'
import isObject from 'lodash/isObject'
import isArray from 'lodash/isArray'
import moment from 'moment-timezone'
import { DataTypeUtil } from '@/services/ds/data/DataTypes'
import { createBinColumnAlias } from '@/utils/binUtils'
import { HC_TYPES } from '@/components/widgets/elements/chart/ChartConfig'

export class BarChartBuilder extends AbstractBuilder {
  getBaseConfig() {
    return {
      title: {
        text: null
      },
      plotOptions: {
        bar: {
          dataLabels: {
            enabled: false
          }
        }
      }
    }
  }

  __hasXColumnInSeries(chartConfig) {
    return get(chartConfig, 'charts[0].series', []).every(item => !!item.data.x)
  }

  buildAndRender(domId, dataSource, chartConfig, options = {}) {
    const config = this.getBaseConfig()
    const hasXColumn = this.__hasXColumnInSeries(chartConfig)

    const data = hasXColumn
      ? this.__mappingDataFromDataSource(dataSource, chartConfig)
      : this.__mappingDataFromDataSourceWithYColumnOnly(dataSource, chartConfig)

    const tooltip = hasXColumn
      ? this.__buildTooltip(dataSource, chartConfig)
      : this.__buildTooltipWithYColumnOnly(chartConfig)

    const axis = this.__buildAxis(dataSource, chartConfig)

    const plotOptions = this.__buildPlotOptions(chartConfig)

    const legend = this.__buildLegend(chartConfig)

    const timezone = this.__buildTimezone(chartConfig)

    const events = this.__drillDownEvent(options.drillDown, chartConfig, dataSource)

    const colors = this.__buildColor(chartConfig)

    hasXColumn
      ? this.__buildSeries(config, data, { chartConfig, axis })
      : this.__buildSeriesWithYColumnOnly(config, data, { tooltip })

    this.__buildConfig(config, {
      chartConfig,
      legend,
      axis,
      tooltip,
      timezone,
      plotOptions,
      events,
      colors
    })
    this.render(domId, config)
  }

  __mappingDataFromDataSource(dataSource, chartConfig) {
    const { rows, cols } = dataSource
    return chartConfig.charts[0].series.map((item) => {
      const { x, y } = mappingColumnNameToAliasNameWithGrouping(
        item,
        chartConfig
      )
      const xType = cols.find(col => col.name === x).type
      const isXBin = !!chartConfig.bins.find(bin => bin.alias === x) || xType.includes('_bin')
      const isXTemporal = ['temporal', 'date', 'datetime', 'temporal_bin', 'date_bin', 'datetime_bin'].includes(xType)
      const indexOfY = cols.findIndex((col) => col.name === y)
      const indexOfX = cols.findIndex((col) => col.name === x)

      return isXTemporal && !isXBin
        ? rows.map(row => ({ x: new Date(row[indexOfX]).getTime(), y: row[indexOfY] }))
        : rows.map(row => row[indexOfY])
    })
  }

  __mappingDataFromDataSourceWithYColumnOnly(dataSource, chartConfig) {
    const data = flatten(dataSource.rows)
    const names = chartConfig.charts[0].series.map((item) => item.name)

    return names.map((name, index) => ({ name, y: data[index] }))
  }

  __buildTooltip(dataSource, chartConfig) {
    return {
      shared: true,
      useHTML: true,
      headerFormat: '',
      formatter: function() {
        let arrayPoints = this.points ? this.points : [this]
        return arrayPoints.reduce((tooltipStr, point) => {
          const targetIndex = point.series.index
          const seriesItem = chartConfig.charts[0].series[targetIndex]
          const { x, y } = seriesItem.data

          const columnX = get(chartConfig, 'columns', []).find((column) => column.name === x)
          const columnY = get(chartConfig, 'columns', []).find((column) => column.name === y)
          const binX = chartConfig.bins.find(bin => bin.column.name === x)
          const sourceColumnX = dataSource.cols.find(col => col.name === (binX ? binX.alias : x))

          const yFormatter = columnY.format
            ? dataFormatManager.create(columnY.format, true)
            : null
          const xFormatter = (value) => {
            if (value.toString().match(/^-{0,1}\d+$/)) {
              return columnX.format
                ? dataFormatManager.formatBin({ xValue: value, bin: true }, columnX.format, true)
                : value
            }
            return columnX.format
              ? dataFormatManager.create(columnX.format, true)(value)
              : value
          }
          let color = null
          if (isString(point.color)) {
            color = `<span style="color:${point.color}">\u25CF</span>`
          } else {
            color = `<div style="background-image: linear-gradient(${point.color.stops[0][1]}, ${point.color.stops[1][1]});
                height: 7px;
                width: 7px;
                border-radius: 1.5em;
                display: inline-block;"></div>`
          }
          const tooltip = `<b>${seriesItem.name}:</b> ${yFormatter ? yFormatter(point.y) : point.y}`
          const isTemporal = columnX && DataTypeUtil.isTemporal(sourceColumnX.type)
          // set header
          if (!tooltipStr) {
            const autoFormatFunc = (value) => {
              let xTemporalFormat = null

              if (!isTemporal || binX) {
                return xFormatter ? xFormatter(value) : value
              }

              switch (isTemporal) {
                case columnX.type === 'datetime' || columnX.type === 'temporal':
                  xTemporalFormat = 'MM/DD/YYYY HH:mm:ss'
                  break
                case columnX.type === 'date':
                  xTemporalFormat = 'MM/DD/YYYY'
                  break
              }
              return moment.tz(value, chartConfig.timezone.utc).format(xTemporalFormat)
            }
            tooltipStr += `<span>${autoFormatFunc(point.x)}</span></br>`
          }

          tooltipStr += `${color} <span>${tooltip}</span></br>`

          return tooltipStr
        }, '')
      }
    }
  }

  // eslint-disable-next-line camelcase
  __buildColor({ color_scheme: colorScheme }) {
    if (isArray(colorScheme)) return colorScheme

    const listColor = getColorSchemes(colorScheme)
    return colorScheme.includes('SC_')// gradiant colors prefix
      ? setColorGradient(listColor)
      : listColor
  }

  __buildTooltipWithYColumnOnly(chartConfig) {
    const { y } = get(chartConfig, 'charts[0].series[0].data')

    const columnY = get(chartConfig, 'columns', []).find(
      (column) => column.name === y
    )

    if (!columnY) return {}

    const yFormatter = columnY.format
      ? dataFormatManager.create(columnY.format, true)
      : null

    return {
      headerFormat: null,
      pointFormatter: function() {
        const seriesIndex = this.colorIndex
        const seriesName = get(
          chartConfig,
          `charts[0].series[${seriesIndex}].name`,
          `Series ${seriesIndex}`
        )
        const { y: opValue } = this.options
        const value = yFormatter ? yFormatter(opValue) : opValue

        // format tooltip
        return `<b>${seriesName}</b>: ${value}`
      }
    }
  }

  __buildPlotOptions(chartConfig) {
    let type = get(chartConfig, 'charts[0].options.stacking')
    let pointPadding = get(chartConfig, 'charts[0].options.pointPadding', 0)
    let borderColor = get(chartConfig, 'charts[0].options.borderColor', null)
    let hasColorByPoint = get(chartConfig, 'charts[0].options.colorByPoint', false)
    let markerConfig = get(chartConfig, 'charts[0].options.marker', {
      enabled: undefined,
      hoverEnabled: true
    })
    // TODO: Support circle only for now
    const symbol = get(chartConfig, 'charts[0].options.legend.customSymbol') ? 'circle' : undefined

    type = [true, 'normal', 'percent'].includes(type)
      // make it work with all old sdk version config
      ? typeof type === 'boolean' ? 'normal' : type
      : undefined

    return {
      column: hasColorByPoint ? { colorByPoint: true } : {},
      bar: hasColorByPoint ? { colorByPoint: true } : {},
      series: {
        borderColor,
        stacking: type,
        pointPadding,
        marker: {
          enabled: markerConfig.enabled,
          symbol,
          states: {
            hover: {
              enabled: markerConfig.hoverEnabled
            }
          }
        }
      }
    }
  }

  __buildLegend(chartConfig) {
    const colors = getStyle()
    const position = get(chartConfig, 'charts[0].options.legend.position', 'right')

    const legend = {
      enabled: get(chartConfig, 'charts[0].options.legend.enabled'),
      maxWidth: `${get(chartConfig, 'charts[0].options.legend.widthPercent', 40)}%`,
      layout: 'horizontal',
      navigation: {
        activeColor: colors.navigationActive,
        inactiveColor: colors.navigationInactive,
        style: {
          color: colors.accentColor
        }
      },
      align: 'center',
      itemStyle: {
        fontSize: 11,
        fontWeight: 'normal',
        color: colors.accentColor
      }
    }

    if (['right', 'left'].includes(position)) {
      legend.align = position
      legend.verticalAlign = 'middle'
    } else if (['top', 'bottom'].includes(position)) {
      legend.align = 'center'
      legend.verticalAlign = position
    }

    const customSymbol = get(chartConfig, 'charts[0].options.legend.customSymbol')
    if (['circle'].includes(customSymbol)) {
      legend.useHTML = true
      legend.labelFormatter = function() {
        const symbol = get(this, 'legendSymbol.element') || get(this, 'legendLine.element')
        symbol && symbol.remove()
        return `<div class="custom-legend" data-active="${this.visible}">
                  <svg width="10" height="10">
                    <circle fill="${this.visible ? this.color.toString() : 'rgb(204, 204, 204)'}" cx="5" cy="5" r="5" />
                  </svg>
                  <span style="vertical-align: middle">${this.name}</span>
                </div>`
      }
    }

    return legend
  }

  __buildAxis(dataSource, chartConfig) {
    const color = getStyle()
    const hasX = this.__hasXColumnInSeries(chartConfig)
    const firstSeries = get(chartConfig, 'charts[0].series[0]')
    const xBin = get(chartConfig, 'bins', []).find(bin => bin.column.name === firstSeries.data.x)
    const xAxisConfig = get(chartConfig, 'charts[0].axis.x', []).find(axis => axis.id === firstSeries.axis.x)
    const yAxisConfig = get(chartConfig, 'charts[0].axis.y', []).find(axis => axis.id === firstSeries.axis.y)
    const sourceXColumn = dataSource.cols.find((col) => col.name === firstSeries.data.x)
    const isXTemporal = !!sourceXColumn && DataTypeUtil.isTemporal(sourceXColumn.type)

    const xIndex = dataSource.cols.findIndex(column => column.name === (xBin ? xBin.alias : firstSeries.data.x))
    const xFormat = xAxisConfig ? xAxisConfig.format : null
    const xFormatter = xFormat ? dataFormatManager.create(xFormat, true) : null

    const yFormat = yAxisConfig ? yAxisConfig.format : null
    const yFormatter = yFormat ? dataFormatManager.create(yFormat, true) : null

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

    let yAxis = {
      dataId: firstSeries.axis.y || 0,
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

    switch (true) {
      case (!!xBin || (hasX && sourceXColumn.type.includes('_bin'))):
        xAxis = {
          ...xAxis,
          ...{
            categories: uniq(dataSource.rows.map(row => row[xIndex].label))
          }
        }
        break
      case isXTemporal:
        xAxis = {
          ...xAxis,
          ...{
            type: 'datetime'
          }
        }
        break
      default:
        const categoriesAxis = sourceXColumn
          ? {
            categories: uniq(dataSource.rows.map(row => {
              return xFormatter ? xFormatter(row[xIndex]) : row[xIndex]
            }))
          }
          : {
            categories: uniq(dataSource.rows[0].map((item, index) => {
              let value = get(chartConfig, `charts[0].series[${index}].name`, `Series ${index + 1}`)
              return xFormatter ? xFormatter(value) : value
            }))
          }
        xAxis = {
          ...xAxis,
          ...categoriesAxis
        }
    }

    return {
      xAxis,
      yAxis
    }
  }

  __buildTimezone(chartConfig) {
    const timezone = get(chartConfig, 'timezone')

    return timezone && timezone.utc
      ? { timezone: timezone.utc }
      : null
  }

  __buildSeries(config, data, { axis, chartConfig }) {
    config.series = data.map((dataItem, index) => {
      const seriesItem = chartConfig.charts[0].series[index]
      return {
        yAxis: 0,
        data: dataItem,
        name: seriesItem.name || 'Series ' + (index + 1),
        color: getColorForSpecificItemSeries(seriesItem)
      }
    })
  }

  __drillDownEvent(drillDownCallback, chartConfig, { rows, cols }) {
    if (!drillDownCallback) return {}

    return {
      load: function() {
      // add right event for drill down
        if (drillDownCallback) {
          this.series.forEach(item => {
            item.points.forEach(p => {
              if (p.graphic) {
                p.graphic.on('contextmenu', function(e) {
                  e.preventDefault()
                  const seriesIndex = item.index
                  const { data } = chartConfig.charts[0].series[seriesIndex]
                  const hasBin = chartConfig.bins.find(bin => bin.column.name === data.x)
                  const column = { name: data.x }
                  const columnIndex = findIndex(cols, (col) => (col.column || col.name) === (hasBin ? createBinColumnAlias(data.x) : data.x))
                  const values = rows.find(row =>
                    (isObject(row[columnIndex]) ? row[columnIndex].label : row[columnIndex]) === p.category)

                  drillDownCallback({
                    column,
                    value: values[columnIndex],
                    aggregations: chartConfig.grouping.aggregations
                  })
                })
              }
            })
          })
        }
      }
    }
  }

  __buildSeriesWithYColumnOnly(config, data) {
    config.series = data.map(item => {
      return {
        yAxis: 0,
        data: [item],
        name: item.name
      }
    })
  }

  __buildConfig(config, { chartConfig, legend, axis, tooltip, timezone, plotOptions, events, colors }) {
    const color = getStyle()

    defaultsDeep(config, {
      chart: {
        type: get(chartConfig, 'charts[0].options.isHorizontal', false) ? HC_TYPES.BAR : HC_TYPES.COLUMN,
        backgroundColor: color.mainColor,
        events
      },
      colors,
      plotOptions,
      tooltip,
      legend,
      xAxis: axis.xAxis,
      yAxis: axis.yAxis,
      moment: function() {
        return moment
      }
    })

    this.highcharts.setOptions({
      time: timezone
    })
  }
}
