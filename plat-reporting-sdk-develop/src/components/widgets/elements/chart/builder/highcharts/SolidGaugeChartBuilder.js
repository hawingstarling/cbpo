// import { AbstractBuilder } from '@/components/widgets/elements/chart/builder/AbstractBuilder'
import { BulletGaugeChartBuilder } from '@/components/widgets/elements/chart/builder/highcharts/BulletGaugeChartBuilder'
import SolidGauge from 'highcharts/modules/solid-gauge'
import HighchartsMore from 'highcharts/highcharts-more'
import get from 'lodash/get'
import toNumber from 'lodash/toNumber'
import defaultsDeep from 'lodash/defaultsDeep'
import { HC_TYPES } from '@/components/widgets/elements/chart/ChartConfig'
// import { getStyle } from '@/utils/chartUtil'
import { getStyle, getColorSchemes } from '@/utils/chartUtil'
// import * as util from '@/utils/chartUtil'
// import dsFormatManager from '@/services/dataFormatManager'

export class SolidGaugeChartBuilder extends BulletGaugeChartBuilder {
  constructor(instance) {
    super(instance)
    HighchartsMore(this.highcharts)
    SolidGauge(this.highcharts)
  }

  getBaseConfig() {
    return {
      title: {
        text: null
      }
    }
  }

  buildAndRender(domId, dataSource, chartConfig, options = {}) {
    const config = this.getBaseConfig()

    const data = this.__mappingDataFromDataSource(dataSource, chartConfig)

    const tooltip = this.__buildTooltip()

    const axis = this.__buildAxis(dataSource, chartConfig)

    const plotOptions = this.__buildPlotOptions()

    const legend = this.__buildLegend(chartConfig)

    const chart = this.__buildChart(chartConfig)

    const pane = this.__buildPane()
    const colors = this.__buildColor(chartConfig)

    let yAxis = []

    let series = []
    const seriesLength = get(chartConfig, 'charts[0].series', 1).length
    for (let index = 0; index < seriesLength; index++) {
      series.push(this.__buildSeries(chartConfig, data, index))
    }
    for (let index = 0; index < seriesLength; index++) {
      yAxis.push(this.__buildYAxis(chartConfig, index))
    }
    // this.__buildSeries(config, data, { chartConfig, axis })
    this.__buildConfig(config, {
      chartConfig,
      chart,
      legend,
      axis,
      tooltip,
      plotOptions,
      pane,
      yAxis,
      series,
      colors
    })
    const chartSetsItemHTML = `<div class="chartSetsItem" style="height: ${seriesLength === 1 ? 100 : 100 / (Math.round(seriesLength / 2))}%; width: ${seriesLength === 1 ? 100 : 50}%"></div>`
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
          pane: config.pane,
          series: [config.series[i]],
          title: config.title,
          tooltip: config.tooltip,
          xAxis: [{
            categories: [config.xAxis[0].categories[i]],
            labels: config.xAxis[0].labels
          }],
          yAxis: config.yAxis[0]
        }
        result.push(item)
      }
    } else result.push(config)
    return result
  }

  __buildChart(chartConfig) {
    const { mainColor } = getStyle()
    return {
      type: HC_TYPES.SOLIDGAUGE,
      backgroundColor: mainColor
      // inverted: get(chartConfig, 'charts[0].options.isHorizontal', false)
    }
  }

  __buildPane() {
    return {
      center: ['50%', '85%'],
      size: '95%',
      startAngle: -90,
      endAngle: 90,
      background: { innerRadius: '60%', outerRadius: '100%', shape: 'arc' }
    }
  }

  __buildConfig(config, { chart, legend, axis, tooltip, plotOptions, pane, yAxis, series, colors }) {
    defaultsDeep(config, {
      chart,
      plotOptions,
      legend,
      xAxis: axis.xAxis,
      tooltip,
      pane,
      yAxis,
      series,
      colors
    })
  }

  __buildPlotOptions() {
    return {
      solidgauge: { dataLabels: { y: 5, borderWidth: 0, useHTML: true } }
    }
  }

  __buildYAxis(chartConfig, index) {
    const yAxis = get(chartConfig, `charts[0].axis.y[${index}]`)
    let max = toNumber(toNumber(yAxis.max).toFixed(2)) || 0
    let stops = yAxis.stops && yAxis.stops.map(e => {
      let a = (toNumber(toNumber(e[0]).toFixed(2)) < max) ? (toNumber(toNumber(e[0]).toFixed(2)) / max).toFixed(2) : 1
      return [a, e[1]]
    })
    if (yAxis) {
      return {
        stops: stops || [[]],
        lineWidth: 0,
        tickWidth: 0,
        minorTickInterval: null,
        tickAmount: 2,
        title: {
          y: -100,
          text: get(yAxis, 'scaleLabel.display', false) ? get(yAxis, 'scaleLabel.labelString', '') : ''
        },
        min: 0,
        max: yAxis.max || 0,
        labels: {
          y: 16,
          useHTML: true,
          formatter: function() {
            return `${yAxis.dsFormatManager ? yAxis.dsFormatManager(this.value) : this.value}`
          }
        }
      }
    }
  }

  __buildSeries(chartConfig, data, index) {
    const style = get(chartConfig, 'widget.style.foreground_color') || null
    const { accentColor } = getStyle()
    return {
      name: get(chartConfig, `charts[0].series[${index}].name`),
      data: [data[index][0].y],
      dataLabels: {
        format:
          `<div style="text-align:center">
        <span style="font-size:${get(chartConfig, `charts[0].series[${index}].options.size`, '25')}px; color: ${style || accentColor}">{y}</span><br/>
        <span style="font-size:12px;opacity:0.4; color: ${style || accentColor}">${get(chartConfig, `charts[0].series[${index}].options.subtitle`, '')}</span>
       </div>`
      }
    }
  }

  __buildTooltip() {
    return { enabled: false }
  }

  __buildColor(chartConfig) {
    let listColor = getColorSchemes(chartConfig.color_scheme)
    return listColor
  }

// eslint-disable-next-line eol-last
}
