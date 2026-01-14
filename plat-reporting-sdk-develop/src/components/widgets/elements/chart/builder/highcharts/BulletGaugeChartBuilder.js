import { AbstractBuilder } from '@/components/widgets/elements/chart/builder/AbstractBuilder'
import { mappingColumnNameToAliasNameWithGrouping, getStyle } from '@/utils/chartUtil'
import { HC_TYPES } from '@/components/widgets/elements/chart/ChartConfig'
import Bullet from 'highcharts/modules/bullet'
import dsFormatManager from '@/services/dataFormatManager'
import get from 'lodash/get'
import defaultsDeep from 'lodash/defaultsDeep'
import $ from 'jquery'
import { makeDOMId } from '@/components/widgets/elements/chart/types/ChartTypes'
import { CHART_LIBRARY } from '@/components/visualizationBuilder/VisualizationBuilderTypes'

export class BulletGaugeChartBuilder extends AbstractBuilder {
  constructor(instance) {
    super(instance)
    Bullet(this.highcharts)
  }

  getBaseConfig() {
    return {
      title: {
        text: null
      }
    }
  }

  render(id, config, chartSetsItemHTML) {
    const length = config.length
    for (let index = 0; index < length; index++) {
      const prefixId = makeDOMId(CHART_LIBRARY.HIGH_CHART, id)
      $(`#${prefixId} .chartSets`).append(chartSetsItemHTML)
      const document = $(`.chartSetsItem`)[index]
      if (document) {
        window[`${prefixId}_${index}`] = this.highcharts.chart(document, config[index])
        /* Some charts doesn't fit the content when first load
         * this method make sure everything will work well after it loaded
         */
        setTimeout(() => {
          window[`${prefixId}_${index}`].reflow()
        }, 500)
      }
    }
  }

  resize(id) {
    const prefixId = makeDOMId(CHART_LIBRARY.HIGH_CHART, id)
    const document = $(`#${prefixId} .chartSets .chartSetsItem`)[0]
    const chartSetsItemLength = $('.chartSetsItem').length
    for (let index = 0; index < chartSetsItemLength; index++) {
      if (window[prefixId] && document) {
        try {
          window[`${prefixId}_${index}`].setSize(document.clientWidth, document.clientHeight)
        } catch {
          console.log('There is no setSize function')
        }
      }
    }
  }

  buildAndRender(domId, dataSource, chartConfig, options = {}) {
    const config = this.getBaseConfig()

    const data = this.__mappingDataFromDataSource(dataSource, chartConfig)

    const tooltip = this.__buildTooltip(dataSource, chartConfig)

    const axis = this.__buildAxis(dataSource, chartConfig)

    const plotOptions = this.__buildPlotOptions(chartConfig)

    const legend = this.__buildLegend(chartConfig)

    const chart = this.__buildChart(chartConfig)
    this.__buildSeries(config, data, { chartConfig, axis })

    this.__buildConfig(config, {
      chartConfig,
      chart,
      legend,
      axis,
      tooltip,
      plotOptions
    })
    const inverted = get(config, 'chart.inverted')
    const seriesLength = get(config, 'series').length
    const chartSetsItemHTML = inverted ? `<div class="chartSetsItem" style="height: ${100 / seriesLength}%; width: 100%"></div>`
      : `<div class="chartSetsItem" style="height: 100%; width: ${100 / seriesLength}%"></div>`
    const newConfig = this.__splitSeriesConfig(config)
    this.render(domId, newConfig, chartSetsItemHTML)
  }

  __splitSeriesConfig(config) {
    const seriesLength = get(config, 'series').length
    let result = []
    if (seriesLength > 1) {
      for (let i = 0; i < seriesLength; i++) {
        const item = {
          chart: config.chart,
          legend: config.legend,
          plotOptions: config.plotOptions,
          series: [config.series[i]],
          title: config.title,
          tooltip: config.tooltip,
          xAxis: [{
            categories: [config.xAxis[0].categories[i]],
            labels: config.xAxis[0].labels
          }],
          yAxis: [config.yAxis[i]]
        }
        result.push(item)
      }
    } else result.push(config)
    return result
  }

  __mappingDataFromDataSource(dataSource, chartConfig) {
    return chartConfig.charts[0].series.map(item => {
      const { cols, rows } = dataSource
      const { y } = mappingColumnNameToAliasNameWithGrouping(item, chartConfig)
      const indexOfY = cols.findIndex((col) => col.name === y)
      return rows.map(row => ({
        y: row[indexOfY],
        target: Number.parseInt(get(item, 'options.target', row[indexOfY]), 10)
      }))
    })
  }

  __buildChart(chartConfig) {
    const { mainColor } = getStyle()
    return {
      type: HC_TYPES.BULLETGAUGE,
      backgroundColor: mainColor,
      inverted: get(chartConfig, 'charts[0].options.isHorizontal', false)
    }
  }

  __buildLegend(_chartConfig) {
    return { enabled: false }
  }

  __buildTooltip(dataSource, chartConfig) {
    return {
      useHTML: true,
      headerFormat: '',
      formatter: function() {
        let arrayPoints = this.points ? this.points : [this]
        return arrayPoints.reduce((tooltipStr, point) => {
          const targetIndex = point.series.index
          const seriesItem = chartConfig.charts[0].series[targetIndex]
          const { y } = seriesItem.data

          const columnY = get(chartConfig, 'columns', []).find((column) => column.name === y)

          const yFormatter = columnY.format
            ? dsFormatManager.create(columnY.format, true)
            : null
          const color = `<span style="color:${point.color}">\u25CF</span>`
          const targetPoint = point.point.options.target
          const tooltip = `<b>${seriesItem.name}:</b>
                { ${columnY.displayName || columnY.name} : ${yFormatter ? yFormatter(point.y) : point.y},
                 Target : ${yFormatter ? yFormatter(targetPoint) : targetPoint} }`

          tooltipStr += `${color} <span>${tooltip}</span></br>`

          return tooltipStr
        }, '')
      }
    }
  }

  __buildPlotOptions(_chartConfig) {
    return {
      series:
        {
          pointPadding: 0.25,
          borderWidth: 0,
          targetOptions: {
            width: '150%'
          }
        }
    }
  }

  __buildAxis(dataSource, chartConfig) {
    const series = get(chartConfig, 'charts[0].series', [])
    const { accentColor } = getStyle()
    const xAxis = [{
      labels: {
        style: {
          color: accentColor
        }
      },
      categories: series.map(item => {
        const { title = '', subtitle = '' } = get(item, 'options', {})
        return `<span class="hc-cat-title">${title}</span><br/><span>${subtitle}</span>`
      })
    }]
    const yAxis = series.map(item => {
      const yAxisId = get(item, 'axis.y', '')
      const axisItem = get(chartConfig, 'charts[0].axis.y', []).find(axis => axis.id === yAxisId)
      const yAxisFormat = get(axisItem, `format`, null)
      const isLabelVisible = get(axisItem, 'scaleLabel.display', false)
      const labelString = isLabelVisible ? get(axisItem, 'scaleLabel.labelString', '') : ''
      const formatFn = yAxisFormat
        ? dsFormatManager.create(yAxisFormat, false)
        : null

      return {
        gridLineWidth: 0,
        title: {
          text: labelString
        },
        plotBands: axisItem.plotBands || [],
        labels: {
          useHTML: true,
          style: {
            color: accentColor
          },
          formatter: function() {
            return `${formatFn ? formatFn(this.value) : this.value}`
          }
        }
      }
    })
    return {
      xAxis,
      yAxis
    }
  }

  __buildSeries(config, data, { chartConfig }) {
    config.series = data.map((item, index) => {
      return {
        id: 'id_' + new Date().getTime(),
        data: item,
        name: get(chartConfig, `charts[0].series[${index}].name`, 'Series ' + (index + 1))
      }
    })
  }

  __buildConfig(config, { chart, legend, axis, tooltip, plotOptions }) {
    defaultsDeep(config, {
      chart,
      plotOptions,
      tooltip,
      legend,
      xAxis: axis.xAxis,
      yAxis: axis.yAxis
    })
  }
}
