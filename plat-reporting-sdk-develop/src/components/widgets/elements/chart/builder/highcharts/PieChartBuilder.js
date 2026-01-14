import { AbstractBuilder } from '@/components/widgets/elements/chart/builder/AbstractBuilder'
import {
  getColorSchemes,
  getStyle,
  mappingColumnNameToAliasNameWithGrouping,
  setColorGradient
} from '@/utils/chartUtil'
import { createBinColumnAlias } from '@/utils/binUtils'
import { findIndex } from 'lodash'
import { DataTypeUtil } from '@/services/ds/data/DataTypes'
import dataFormatManager from '@/services/dataFormatManager'
import get from 'lodash/get'
import take from 'lodash/take'
import defaultsDeep from 'lodash/defaultsDeep'
import flatten from 'lodash/flatten'
import isObject from 'lodash/isObject'
import moment from 'moment'
import isArray from 'lodash/isArray'

export class PieChartBuilder extends AbstractBuilder {
  highChart = null

  getBaseConfig() {
    return {
      title: {
        text: null
      },
      plotOptions: {
        pie: {
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
                  const values = rows.find(row => {
                    const rowValue = hasBin ? row[columnIndex].label : row[columnIndex]
                    const optionValue = hasBin ? p.options.name.label : p.options.name
                    return rowValue === optionValue
                  })
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

  async buildAndRender(domId, dataSource, chartConfig, options = {}) {
    const config = this.getBaseConfig()
    const hasXColumn = this.__hasXColumnInSeries(chartConfig)

    const data = hasXColumn
      ? this.__mappingDataFromDataSource(dataSource, chartConfig)
      : this.__mappingDataFromDataSourceWithYColumnOnly(dataSource, chartConfig)

    const plotOptions = this.__buildPlotOptions(data, chartConfig)

    const tooltip = hasXColumn
      ? this.__buildTooltip(dataSource, chartConfig)
      : this.__buildTooltipWithYColumnOnly(chartConfig)

    const legend = this.__buildLegend(dataSource, chartConfig)

    hasXColumn
      ? this.__buildSeries(config, data, { tooltip, chartConfig })
      : this.__buildSeriesWithYColumnOnly(config, data, { tooltip })

    const events = this.__drillDownEvent(options.drillDown, chartConfig, dataSource)

    const colors = this.__buildColor(chartConfig)

    this.__buildConfig(config, {
      plotOptions,
      legend,
      events,
      colors
    })

    this.render(domId, config)
  }

  __mappingDataFromDataSource(dataSource, chartConfig) {
    const { rows, cols } = dataSource
    const limit = get(chartConfig.charts[0], 'options.series.limit', 1000)
    return chartConfig.charts[0].series.map(item => {
      const { x, y } = mappingColumnNameToAliasNameWithGrouping(
        item,
        chartConfig
      )

      const indexOfX = cols.findIndex((col) => col.name === x)
      const indexOfY = cols.findIndex((col) => col.name === y)

      const mappedData = [...rows.map((row) => ({ name: row[indexOfX], y: row[indexOfY] }))]

      return take(mappedData, limit)
    })
  }

  __mappingDataFromDataSourceWithYColumnOnly(dataSource, chartConfig) {
    const maxItem = get(chartConfig.charts[0], 'options.series.limit', 1000)
    const data = flatten(dataSource.rows)
    const names = chartConfig.charts[0].series.map(item => item.name)

    return take(names.map((name, index) => ({ name, y: data[index] })), maxItem)
  }

  __buildPlotOptions(dataSource, chartConfig) {
    const limit = get(chartConfig.charts[0], 'options.series.limit', 1000)
    const plotOptions = {
      series: {
        turboThreshold: limit
      },
      pie: {
        borderWidth: get(chartConfig, 'options.borderWidth', 0),
        showInLegend: get(chartConfig, 'options.legend.enabled', true)
      }
    }

    return plotOptions
  }

  __buildColor({ color_scheme: colorScheme }) {
    if (isArray(colorScheme)) return colorScheme

    const listColor = getColorSchemes(colorScheme)
    return colorScheme.includes('SC_')// gradiant colors prefix
      ? setColorGradient(listColor)
      : listColor
  }

  __buildTooltip(dataSource, chartConfig) {
    const { x, y } = get(chartConfig, 'charts[0].series[0].data')

    const columnX = get(chartConfig, 'columns', []).find(column => column.name === x)
    const columnY = get(chartConfig, 'columns', []).find(column => column.name === y)

    const xBin = get(chartConfig, 'bins', []).find(bin => bin.column.name === x)
    const isTemporal = columnX && DataTypeUtil.isTemporal(columnX.type)

    if (!columnY || !columnX) return {}

    const yFormatter = columnY.format ? dataFormatManager.create(columnY.format, true) : null
    const xFormatter = (value) => {
      if (value.match(/^-{0,1}\d+$/)) {
        return columnX.format
          ? dataFormatManager.formatBin({ xValue: value, bin: true }, columnX.format, true)
          : value
      }
      return columnX.format
        ? dataFormatManager.create(columnX.format, true)(value)
        : value
    }

    const autoFormatFunc = (value) => {
      let xTemporalFormat = null

      if (!isTemporal || xBin) {
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

      return moment(value).format(xTemporalFormat)
    }

    return {
      headerFormat: null,
      pointFormatter: function() {
        const seriesIndex = this.series.index
        const seriesName = get(chartConfig, `charts[0].series[${seriesIndex}].name`, `Series ${seriesIndex}`)
        const { y: opValue } = this.options
        let name = autoFormatFunc(isObject(this.name) ? this.name.label : this.name)
        const value = yFormatter ? yFormatter(opValue) : opValue
        // format tooltip
        return `<b>${seriesName}</b> - ${name} : ${value} (${this.percentage.toFixed(2)}%)`
      }
    }
  }

  __buildTooltipWithYColumnOnly(chartConfig) {
    const { y } = get(chartConfig, 'charts[0].series[0].data')

    const columnY = get(chartConfig, 'columns', []).find(column => column.name === y)

    if (!columnY) return {}

    const yFormatter = columnY.format ? dataFormatManager.create(columnY.format, true) : null

    return {
      headerFormat: null,
      pointFormatter: function() {
        const seriesIndex = this.colorIndex
        const seriesName = get(chartConfig, `charts[0].series[${seriesIndex}].name`, `Series ${seriesIndex}`)
        const { y: opValue } = this.options
        const value = yFormatter ? yFormatter(opValue) : opValue

        // format tooltip
        return `<b>${seriesName}</b>: ${value} (${this.percentage.toFixed(2)}%)`
      }
    }
  }

  __buildLegend(dataSource, chartConfig) {
    const colors = getStyle()
    const position = get(chartConfig, 'charts[0].options.legend.position', 'right')
    const { x } = get(chartConfig, 'charts[0].series[0].data')
    const column = dataSource.cols.find(col => col.name === x)

    const legend = {
      enabled: get(chartConfig, 'charts[0].options.legend.enabled', true),
      width: `${get(chartConfig, 'charts[0].options.legend.widthPercent', 40)}%`,
      layout: get(chartConfig, 'charts[0].options.legend.isHorizontal', false) ? 'horizontal' : 'vertical',
      navigation: {
        activeColor: colors.navigationActive,
        inactiveColor: colors.navigationInactive,
        style: {
          color: colors.accentColor
        }
      },
      itemStyle: {
        fontSize: 11,
        fontWeight: 'normal',
        color: colors.accentColor
      },
      itemHoverStyle: {
        color: colors.hoverItemColor
      },
      labelFormatter: function() {
        const formatValue = (value) => `${value} (${this.percentage.toFixed(1)}%)`
        // for bin case
        if (isObject(this.name)) return formatValue(this.name.label)
        // for x column but with date string
        if (column && column.type === 'date') return formatValue(moment(this.name).format('MM/DD/YYYY'))
        // for x column but with datetime string
        if (column && ['datetime', 'temporal'].includes(column.type)) return formatValue(moment(this.name).format('MM/DD/YYYY hh:mm a'))
        // normal case
        return formatValue(this.name)
      }
    }

    if (['right', 'left'].includes(position)) {
      legend.align = position
      legend.verticalAlign = 'middle'
    } else if (['top', 'bottom'].includes(position)) {
      legend.align = 'center'
      legend.verticalAlign = position
    }

    return legend
  }

  __buildSeries(config, data, { tooltip, chartConfig }) {
    const isDoughnut = get(chartConfig, 'charts[0].options.pie.type', 'pie') === 'doughnut'
    const minSize = 100 / (data.length || 1)
    const calculatedSize = (index) => `${100 - (minSize * index)}%`
    config.series = data.map((dataItem, dataIndex) => (
      {
        data: dataItem,
        title: 'text',
        size: calculatedSize(dataIndex),
        innerSize: isDoughnut ? '50%' : 0,
        tooltip
      }
    ))
  }

  __buildSeriesWithYColumnOnly(config, data, { tooltip }) {
    config.series = [
      {
        data,
        name: 'test',
        tooltip
      }
    ]
  }

  __buildConfig(config, { plotOptions, legend, events, colors }) {
    const color = getStyle()
    defaultsDeep(config, {
      chart: {
        type: 'pie',
        backgroundColor: color.mainColor,
        events
      },
      colors,
      plotOptions,
      legend
    })
  }
}
