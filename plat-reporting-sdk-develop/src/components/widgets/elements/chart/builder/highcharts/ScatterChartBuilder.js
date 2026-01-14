import { AbstractBuilder } from '@/components/widgets/elements/chart/builder/AbstractBuilder'
import { getColorSchemes, getStyle, mappingColumnNameToAliasNameWithGrouping } from '@/utils/chartUtil'
import defaultsDeep from 'lodash/defaultsDeep'
import moment from 'moment-timezone'
import get from 'lodash/get'
import dataFormatManager from '@/services/dataFormatManager'

export class ScatterChartBuilder extends AbstractBuilder {
  getBaseConfig() {
    return {
      title: {
        text: null
      },
      plotOptions: {
        scatter: {
          marker: {
            radius: 5
          }
        }
      }
    }
  }

  buildAndRender(domId, dataSource, chartConfig, options) {
    const config = this.getBaseConfig()

    const data = this.__mappingDataFromDataSource(dataSource, chartConfig)

    const tooltip = this.__buildTooltip(dataSource, chartConfig)

    const axis = this.__buildAxis(dataSource, chartConfig)

    const legend = this.__buildLegend(chartConfig)

    this.__buildSeries(config, data, { chartConfig, axis })

    this.__buildConfig(config, {
      chartConfig,
      legend,
      axis,
      tooltip
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
      const indexOfY = cols.findIndex((col) => col.name === y)
      const indexOfX = cols.findIndex((col) => col.name === x)

      return rows.map(row => ([row[indexOfX], row[indexOfY]]))
    })
  }

  __buildLegend(chartConfig) {
    const colors = getStyle()
    const position = get(chartConfig, 'charts[0].options.legend.position', 'right')

    const legend = {
      enabled: get(chartConfig, 'options.legend.enabled', true),
      maxWidth: `${get(chartConfig, 'options.legend.widthPercent', 40)}%`,
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

    return legend
  }

  __buildTooltip(dataSource, chartConfig) {
    return {
      useHTML: true,
      headerFormat: '',
      formatter: function() {
        const {x = 0, y = 0} = this
        const {name, index: seriesIndex, color} = this.series
        const {x: xName, y: yName} = get(chartConfig, `charts[0].series[${seriesIndex}].data`, {x: '', y: ''})

        const columnX = get(chartConfig, 'columns', []).find((column) => column.name === xName)
        const columnY = get(chartConfig, 'columns', []).find((column) => column.name === yName)

        const yFormatter = columnY.format
          ? dataFormatManager.create(columnY.format, true)
          : null
        const xFormatter = columnX.format
          ? dataFormatManager.create(columnX.format, true)
          : null

        const colorTooltip = `<span style="color:${color}">\u25CF</span>`
        const xTooltip = `<span>${columnX.displayName || columnX.name}: ${xFormatter ? xFormatter(x) : x}</span>`
        const yTooltip = `<span>${columnY.displayName || columnY.name}: ${yFormatter ? yFormatter(y) : y}</span>`

        return `${colorTooltip} <span><b>${name}: </b> <br/><br/> ${xTooltip} <br/> ${yTooltip} <br/></span>`
      }
    }
  }

  __buildAxis(dataSource, chartConfig) {
    const color = getStyle()
    const firstSeries = get(chartConfig, 'charts[0].series[0]')
    const xAxisConfig = get(chartConfig, 'charts[0].axis.x', []).find(axis => axis.id === firstSeries.axis.x)
    const yAxisConfig = get(chartConfig, 'charts[0].axis.y', []).find(axis => axis.id === firstSeries.axis.y)

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
        },
        formatter: function() {
          return xFormatter ? xFormatter(this.value) : this.value
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

    return {
      xAxis,
      yAxis
    }
  }

  __buildSeries(config, data, { chartConfig }) {
    config.series = data.map((item, index) => {
      return {
        yAxis: 0,
        data: item,
        name: get(chartConfig, `charts[0].series[${index}].name`, 'Series ' + (index + 1))
      }
    })
  }

  __buildConfig(config, { chartConfig, legend, axis, tooltip }) {
    const color = getStyle()

    defaultsDeep(config, {
      chart: {
        type: 'scatter',
        backgroundColor: color.mainColor
      },
      colors: getColorSchemes(chartConfig.color_scheme),
      tooltip,
      legend,
      xAxis: axis.xAxis,
      yAxis: axis.yAxis,
      moment: function() {
        return moment
      }
    })
  }
}
