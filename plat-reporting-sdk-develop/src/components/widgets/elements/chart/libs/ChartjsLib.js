import AbstractLib from './AbstractLib'
import $ from 'jquery'
import { cloneDeep, forEachRight, isEmpty, defaultsDeep, extend, get, range, max, includes, reverse } from 'lodash'
import Chart from 'chart.js'
import * as util from '@/utils/chartUtil'
import dsFormatManager from '@/services/dataFormatManager'
import { TYPES_SUPPORTED_CHARTJS, INDEX_CHART, DEFAULT_CONFIG_X_AXIS, DEFAULT_CONFIG_Y_AXIS } from '../types/ChartTypes'
import { CHART_JS_TYPE, TYPES } from '@/components/widgets/elements/chart/ChartConfig'
import { createBinColumnAlias } from '@/utils/binUtils'
import { DataTypeUtil } from '@/services/ds/data/DataTypes'
import moment from 'moment'

/**
 * Apply for Chartjs.
 *
 * @override
 *
 * @param el {element}
 * @param componentConfig {Object} Chart.vue component config.
 * @param data {Object} standard data object with rows and cols.
 */

// Config ChartJS can be found at https://www.chartjs.org/docs/latest/configuration/
export default class ChartjsLib extends AbstractLib {
  fontSize = 12

  render(domId, el, componentConfig, data, callbackObj = {}) {
    this.themeStyle = util.getStyle()

    $(el).find('.chartSets').html('')
    if (componentConfig.charts) {
      let charts = cloneDeep(componentConfig.charts)
      charts.forEach((chart, chartIndex) => {
        // map all pie chart in series into one pie chart with multi dataset
        let pieSeries = []
        let scatterSeries = []
        let areaSeries = []
        let bubbleSeries = []
        forEachRight(chart.series, function (item, index) {
          switch (item.type) {
            case TYPES.PIE: {
              pieSeries.push(item)
              chart.series.splice(index, 1)
              break
            }
            case TYPES.SCATTER: {
              scatterSeries.push(item)
              chart.series.splice(index, 1)
              break
            }
            case TYPES.AREA: {
              areaSeries.push(item)
              chart.series.splice(index, 1)
              break
            }
            case TYPES.BUBBLE: {
              bubbleSeries.push(item)
              chart.series.splice(index, 1)
              break
            }
            default: {
            }
          }
        })

        // Render pie charts in series into one
        if (pieSeries.length) {
          let pieChart = cloneDeep(chart)
          pieChart.series = pieSeries
          let configPieChart = this.mappingPieConfig(componentConfig, pieChart, data)
          this.drawChart(el, componentConfig, {
            chart: chartIndex,
            series: INDEX_CHART.pie
          }, configPieChart)
        }

        // Render scatter chart in series into one
        if (scatterSeries.length) {
          let scatterChart = cloneDeep(chart)
          scatterChart.series = scatterSeries
          let configScatterChart = this.mappingScatterConfig(componentConfig, scatterChart, data)
          this.drawChart(el, componentConfig, {
            chart: chartIndex,
            series: INDEX_CHART.scatter
          }, configScatterChart)
        }

        // Render scatter chart in series into one
        if (areaSeries.length) {
          let areaChart = cloneDeep(chart)
          areaChart.series = areaSeries
          let configAreaChart = this.mappingAreaConfig(componentConfig, areaChart, data)
          this.drawChart(el, componentConfig, {
            chart: chartIndex,
            series: INDEX_CHART.scatter
          }, configAreaChart)
        }

        if (bubbleSeries.length) {
          let bubbleChart = cloneDeep(chart)
          bubbleChart.series = bubbleSeries
          let configBubbleChart = this.mappingBubbleConfig(componentConfig, bubbleChart, data)
          this.drawChart(el, componentConfig, {
            chart: chartIndex,
            series: INDEX_CHART.scatter
          }, configBubbleChart)
        }

        // Render bar, line,area charts in series into one
        if (chart.series.length) {
          chart.series = cloneDeep(chart.series).reverse()
          let configBarChart = this.mappingBarConfig(componentConfig, chart, data)
          this.drawChart(el, componentConfig, {
            chart: chartIndex,
            series: INDEX_CHART.bar_line
          }, configBarChart)
        }
      })
    }
  }

  isChartSupported(componentConfig) {
    let isSupported = true
    if (componentConfig.charts) {
      let charts = cloneDeep(componentConfig.charts)
      charts.forEach((chart) => {
        // check all support types
        for (let i = 0; i < chart.series.length; i++) {
          if (!TYPES_SUPPORTED_CHARTJS.includes(chart.series[i].type)) {
            isSupported = false
          }
        }
      })
    }
    return isSupported
  }

  getSeriesId (indexObject) {
    return `${indexObject.chart}_${indexObject.series}`
  }

  convertDatasetToPercentage(series) {
    series = series.filter(chart => {
      let meta = chart._meta
      if (meta) {
        let keysMeta = Object.keys(meta)
        return !meta[keysMeta[0]].hidden
      }
      return true
    })
    if (series.length) {
      let length = series[0].data.length
      let totalArray = range(length).map(index => {
        let total = series.reduce((total, currentChart) => {
          total += currentChart.valueDataset[index]
          return total
        }, 0)
        return total
      })
      series = series.map(item => {
        item.data = item.data.map((data, index) => (item.valueDataset[index] / (totalArray[index] || 1) * 100))
        return item
      })
    }
  }

  mappingPieConfig(componentConfig, chart, metaData) {
    let self = this
    let dataChart = this.mappingPieDataset(chart.series, metaData, componentConfig)
    let config = {
      type: get(componentConfig, 'charts[0].options.pie.type', CHART_JS_TYPE.PIE),
      data: dataChart,
      options: {
        responsive: true,
        maintainAspectRatio: false,
        layout: {
          padding: {
            left: 10,
            right: 10,
            top: 10,
            bottom: 10
          }
        },
        elements: {
          arc: {
            borderWidth: 2
          }
        },
        legendCallback: function (chart) {
          if (get(componentConfig, 'charts[0].options.legend.enabled', true)) {
            return self.buildTemplatePieLegend(chart, componentConfig)
          }
        },
        legend: {
          // we will disabled legend created by chart and append in our div.
          display: false,
          labels: {
            fontSize: this.fontSize
          },
          scales: 20, // only work with position right, left
          position: get(chart, 'options.legend.position', 'right')
        }
      }
    }
    defaultsDeep(config.options, chart.options)
    config.options.tooltips = this.formatPieTooltip(chart.series, componentConfig)
    if (chart.options.legend) {
      config.options.legend.scales = chart.options.legend.scales
    }
    if (get(config, 'options.pie.type', null) === CHART_JS_TYPE.DOUGHNUT) {
      config.type = CHART_JS_TYPE.DOUGHNUT
    }
    return config
  }

  mappingPieDataset(series, metaData, componentConfig) {
    let labels = []
    let isNoXColumn = series.every(item => !item.data.x)
    let datasets = series.reduce((datasets, item, index) => {
      let config = {
        label: item.name,
        borderWidth: get(componentConfig, 'charts[0].options.borderWidth', 0),
        data: []
      }
      const bins = componentConfig.bins && componentConfig.bins.length ? componentConfig.bins.map(bin => bin.alias) : []
      let dataRows = util.buildDataChartByLabelAndValue(metaData, util.mappingColumnNameToAliasNameWithGrouping(item, componentConfig), bins)
      config.data = dataRows.data
      config.backgroundColor = series[index].backgroundColor ? series[index].backgroundColor : util.randomColor(componentConfig.colorScheme, dataRows.labels.length)
      if (isNoXColumn) {
        dataRows.labels = [item.name]
        labels = [...labels, ...dataRows.labels]
      } else {
        labels = [...dataRows.labels]
      }
      datasets.push(config)
      return datasets
    }, [])
    if (isNoXColumn && datasets.length) {
      let newDataSets = datasets[0]
      datasets.splice(0, 1)
      datasets.forEach(ds => {
        newDataSets.data = [...newDataSets.data, ...ds.data]
        newDataSets.backgroundColor = util.randomColor(componentConfig.colorScheme, newDataSets.data.length)
      })
      datasets = [newDataSets]
    }
    return { datasets, labels }
  }

  mappingScatterConfig(componentConfig, chart, metaData) {
    let self = this
    let chartData = this.mappingScatterDataset(chart.series, metaData, componentConfig)
    let config = {
      type: CHART_JS_TYPE.SCATTER,
      data: chartData,
      options: {
        responsive: true,
        maintainAspectRatio: false,
        layout: {
          padding: {
            left: 10,
            right: 10,
            top: 10,
            bottom: 10
          }
        },
        legendCallback: function (chart) {
          // reuse this template
          if (get(componentConfig, 'charts[0].options.legend.enabled', true)) {
            return self.buildTemplateBarLegend(chart, componentConfig)
          }
        },
        legend: {
          // we will disabled legend created by chart and append in our div.
          display: false,
          position: get(chart, 'options.legend.position', 'bottom')
        }
      }
    }
    defaultsDeep(config.options, chart.options)
    config.options.tooltips = this.formatScatterTooltip(chart.series, componentConfig)
    // add axis config into chart
    if (!(isEmpty(chart.axis.x) && isEmpty(chart.axis.y))) {
      const scales = this.mappingAxis(chart, componentConfig)
      config.options.scales = {
        xAxes: cloneDeep(scales.xAxes),
        yAxes: cloneDeep(scales.yAxes).splice(0, 1)
      }
    }
    // custom config in xAxes, yAxes
    if (get(config, 'options.scales.xAxes.length', 0)) {
      const firstSeries = chart.series[0]
      const isXTemporal = self.isTemporalColumn(componentConfig, firstSeries.data.x)
      if (isXTemporal && !chartData.xLabels) {
        config.options.scales.xAxes = config.options.scales.xAxes.map(x => { x.type = 'time'; return x })
      } else if (chartData.xLabels) {
        config.options.scales.xAxes = config.options.scales.xAxes.map(x => { x.type = 'category'; return x })
      } else {
        config.options.scales.xAxes = config.options.scales.xAxes.map(x => { x.type = 'linear'; return x })
      }
    }
    if (get(config, 'options.scales.yAxes.length', 0)) {
      if (chartData.yLabels) {
        config.options.scales.yAxes = config.options.scales.yAxes.map(y => { y.type = 'category'; return y })
      } else {
        config.options.scales.yAxes = config.options.scales.yAxes.map(y => { y.type = 'linear'; return y })
      }
    }
    return cloneDeep(config)
  }

  mappingScatterDataset(series, metaData, componentConfig) {
    const bins = componentConfig.bins && componentConfig.bins.length ? componentConfig.bins.map(bin => bin.alias) : []
    let backgroundColors = util.randomColor(componentConfig.colorScheme, series.length).reverse()
    let xLabels = []
    let yLabels = []
    let datasets = series.reduce((datasets, item, index) => {
      let config = {
        label: item.name,
        data: []
      }
      config.borderColor = series[index].borderColor ? series[index].borderColor : backgroundColors[index]
      config.borderWidth = 2
      config.fill = false
      config.data = util.buildDataChartByXYZPoint(metaData, util.mappingColumnNameToAliasNameWithGrouping(item, componentConfig), bins, {x: 'x', y: 'y'})
      datasets.push(config)
      // x labels
      const xColumnAlias = createBinColumnAlias(item.data.x)
      const xBinningCol = bins.findIndex(bin => bin === xColumnAlias)
      if (xBinningCol !== -1) {
        const xCategories = util.buildDataChartByXYZPoint(metaData, {
          xCategories: xColumnAlias
        }, bins)
        xLabels = xCategories
      }
      // y labels
      const yColumnAlias = createBinColumnAlias(item.data.y, `${item.id}_bin`)
      const yBinningCol = bins.findIndex(bin => bin === yColumnAlias)
      if (yBinningCol !== -1) {
        const yCategories = util.buildDataChartByXYZPoint(metaData, {
          yCategories: yColumnAlias
        }, bins)
        yLabels = yCategories
      }
      return datasets
    }, [])
    const result = { datasets }
    if (xLabels && xLabels.length) {
      result.xLabels = xLabels
    }
    if (yLabels && yLabels.length) result.yLabels = reverse(yLabels)
    return result
  }

  mappingBubbleConfig(componentConfig, chart, metaData) {
    let self = this
    let dataChart = this.mappingBubbleDataset(chart.series, metaData, componentConfig)
    let config = {
      type: CHART_JS_TYPE.BUBBLE,
      data: dataChart,
      options: {
        responsive: true,
        maintainAspectRatio: false,
        layout: {
          padding: {
            left: 30,
            right: 30,
            top: 30,
            bottom: 30
          }
        },
        elements: {
          point: {
            radius: function(context) {
              let {v} = context.dataset.data[context.dataIndex]
              let scaleSize = get(chart, 'options.radius.scale', 24)
              let maxRadius = Math.ceil(max(context.dataset.data.map(d => d.v)) / 10) * 10
              return (context.chart.width / (scaleSize || 1)) * (Math.abs(v) / (maxRadius || 1))
            }
          }
        },
        legendCallback: function (chart) {
          if (get(componentConfig, 'charts[0].options.legend.enabled', true)) {
            return self.buildTemplateBubbleLegend(chart, componentConfig)
          }
        },
        legend: {
          // we will disabled legend created by chart and append in our div.
          display: false,
          labels: {
            fontSize: this.fontSize
          },
          scales: 20, // only work with position right, left
          position: get(chart, 'options.legend.position', 'bottom')
        }
      }
    }
    defaultsDeep(config.options, chart.options)
    // format tooltip
    config.options.tooltips = this.formatBubbleTooltip(chart.series, componentConfig)
    // add axis config into chart
    if (!(isEmpty(chart.axis.x) && isEmpty(chart.axis.y))) {
      const scales = this.mappingAxis(chart, componentConfig)
      config.options.scales = {
        xAxes: cloneDeep(scales.xAxes),
        yAxes: cloneDeep(scales.yAxes).splice(0, 1)
      }
    }
    // Binning
    // custom config in xAxes, yAxes
    if (get(config, 'options.scales.xAxes.length', 0)) {
      const firstSeries = chart.series[0]
      const isXTemporal = self.isTemporalColumn(componentConfig, firstSeries.data.x)
      if (isXTemporal && !dataChart.xLabels) {
        config.options.scales.xAxes = config.options.scales.xAxes.map(x => { x.type = 'time'; return x })
      } else if (dataChart.xLabels) {
        config.options.scales.xAxes = config.options.scales.xAxes.map(x => { x.type = 'category'; return x })
      } else {
        config.options.scales.xAxes = config.options.scales.xAxes.map(x => { x.type = 'linear'; return x })
      }
    }
    if (get(config, 'options.scales.yAxes.length', 0)) {
      if (dataChart.yLabels) {
        config.options.scales.yAxes = config.options.scales.yAxes.map(y => { y.type = 'category'; return y })
      } else {
        config.options.scales.yAxes = config.options.scales.yAxes.map(y => { y.type = 'linear'; return y })
      }
    }
    return config
  }

  mappingBubbleDataset(series, metaData, componentConfig) {
    let backgroundColors = util.randomColor(componentConfig.colorScheme, series.length).reverse()
    let xLabels = []
    let yLabels = []
    let datasets = series.reduce((datasets, item, index) => {
      let config = {
        label: item.name,
        data: []
      }
      config.borderColor = series[index].borderColor ? series[index].borderColor : backgroundColors[index]
      config.backgroundColor = series[index].borderColor ? `${series[index].borderColor}55` : `${backgroundColors[index]}55`
      config.borderWidth = 2
      config.fill = false
      const bins = componentConfig.bins && componentConfig.bins.length ? componentConfig.bins.map(bin => bin.alias) : []
      config.data = util.buildDataChartByXYZPoint(metaData, util.mappingColumnNameToAliasNameWithGrouping(item, componentConfig), bins, {x: 'x', y: 'y', z: 'v'})
      datasets.push(config)
      // x labels
      const xColumnAlias = createBinColumnAlias(item.data.x)
      const xBinningCol = bins.findIndex(bin => bin === xColumnAlias)
      if (xBinningCol !== -1) {
        const xCategories = util.buildDataChartByXYZPoint(metaData, {
          xCategories: xColumnAlias
        }, bins)
        xLabels = xCategories
      }
      // y labels
      const yColumnAlias = createBinColumnAlias(item.data.y)
      const yBinningCol = bins.findIndex(bin => bin === yColumnAlias)
      if (yBinningCol !== -1) {
        const yCategories = util.buildDataChartByXYZPoint(metaData, {
          yCategories: yColumnAlias
        }, bins)
        yLabels = yCategories
      }
      return datasets
    }, [])
    const result = { datasets }
    if (xLabels && xLabels.length) result.xLabels = xLabels
    if (yLabels && yLabels.length) result.yLabels = reverse(yLabels)
    return result
  }

  mappingBarConfig(componentConfig, chart, metaData, chartIndex) {
    let self = this
    let chartData = this.mappingBarDataset(chart.series, metaData, componentConfig)
    let isBarOnly = chart.series.every(item => item.type === CHART_JS_TYPE.BAR)
    let isLineOnly = chart.series.every(item => item.type === CHART_JS_TYPE.LINE)
    let isNoXColumn = chart.series.every(item => isEmpty(item.data.x))
    let config = {
      type: isLineOnly ? CHART_JS_TYPE.LINE : CHART_JS_TYPE.BAR,
      data: chartData,
      options: {
        responsive: true,
        maintainAspectRatio: false,
        layout: {
          padding: {
            left: 10,
            right: 10,
            top: 10,
            bottom: 10
          }
        },
        legendCallback: function (chart) {
          if (get(componentConfig, 'charts[0].options.legend.enabled', true)) {
            return self.buildTemplateBarLegend(chart, componentConfig, isBarOnly, isNoXColumn)
          }
        },
        legend: {
          // we will disabled legend created by chart and append in our div.
          display: false,
          position: get(chart, 'options.legend.position', 'right')
        }
      }
    }
    defaultsDeep(config.options, chart.options)
    // Special setting for area chart
    if (get(chart, 'options.stacking', null) !== '') {
      config = this.mappingBarStackConfig(config, chart.options.stacking)
      if (chart.options.stacking === 'percent') {
        let stackBarChart = chartData.datasets.filter(item => item.seriesType === TYPES.BAR)
        this.convertDatasetToPercentage(stackBarChart)
      }
    }
    // format tooltip
    config.options.tooltips = this.formatBarTooltip(chart.series, componentConfig, config.cbpoStackedMode)
    // add axis config into chart
    if (!isBarOnly && !isLineOnly) {
      if (!(isEmpty(chart.axis.x) && isEmpty(chart.axis.y))) {
        config.options.scales = this.mappingAxis(chart, componentConfig)
      }
    } else {
      const scales = this.mappingAxis(chart, componentConfig)
      config.options.scales = {
        xAxes: cloneDeep(scales.xAxes),
        yAxes: cloneDeep(scales.yAxes).splice(0, 1)
      }
    }
    if (config.options.isHorizontal) {
      config.type = CHART_JS_TYPE.HORIZONTAL_BAR
    }
    return config
  }

  mappingBarDataset(series, metaData, componentConfig) {
    let labels = []
    let datasets = []
    // move bar chart to behind line chart
    let backgroundColors = util.randomColor(componentConfig.colorScheme, series.length).reverse()
    // series = orderBy(series, ['type'], ['desc'])
    // check type by series
    let hasBar = false
    let hasLine = false
    let isBarOnly = series.every(item => item.type === 'bar')
    let isNoXColumn = series.every(item => isEmpty(item.data.x))
    series.forEach((ser, index) => {
      if (ser.type === CHART_JS_TYPE.BAR) hasBar = true
      if (ser.type === CHART_JS_TYPE.LINE) hasLine = true
    })
    datasets = series.reduce((datasets, item, index) => {
      let config = {
        label: item.name,
        data: []
      }
      const bins = componentConfig.bins && componentConfig.bins.length ? componentConfig.bins.map(bin => bin.alias) : []
      let dataRows = util.buildDataChartByLabelAndValue(metaData, util.mappingColumnNameToAliasNameWithGrouping(item, componentConfig), bins)
      // This series type is for config stacking mode in bar-area (chart js doesn't have type area)
      config.seriesType = item.type
      // This type is for combo bar-line
      config.type = item.type
      if (isNoXColumn) {
        dataRows.labels = [item.name]
        labels = [...labels, ...dataRows.labels]
      } else {
        labels = [...dataRows.labels]
      }
      config.data = dataRows.data
      config.valueDataset = cloneDeep(dataRows.data)
      // set background for bar and border color for line
      if (item.type === TYPES.BAR) {
        config.backgroundColor = series[index].backgroundColor ? series[index].backgroundColor : backgroundColors[index]
      } else if (item.type === TYPES.LINE) {
        config.borderColor = series[index].borderColor ? series[index].borderColor : backgroundColors[index]
        config.borderWidth = 2
        config.fill = false
      }
      // set axis for each item in series if char type is pareto
      if (hasBar && hasLine) {
        if (item.axis && item.axis.y) {
          if (!get(componentConfig, 'charts[0].options.isHorizontal', false)) {
            config.yAxisID = item.axis.y
          } else {
            config.xAxisID = item.axis.y
            delete config.type
          }
        }
      }
      datasets.push(config)
      return datasets
    }, [])
    if (isNoXColumn && isBarOnly && datasets.length) {
      let newDataSets = datasets[0]
      datasets.splice(0, 1)
      datasets.forEach(ds => {
        newDataSets.data = [...newDataSets.data, ...ds.data]
        newDataSets.valueDataset = [...newDataSets.valueDataset, ...ds.valueDataset]
        newDataSets.backgroundColor = util.randomColor(componentConfig.colorScheme, 1)[0]
      })
      datasets = [newDataSets]
    }
    return { datasets, labels }
  }

  mappingBarStackConfig(config, stackingMode) {
    let defaultTick = {
      beginAtZero: true,
      max: 100
    }
    if (stackingMode !== 'percent') {
      delete defaultTick.max
    }
    config.options = extend(config.options, {
      scales: {
        xAxes: [{ stacked: true, ticks: defaultTick }],
        yAxes: [{ stacked: true, ticks: defaultTick }]
      }
    })
    config.cbpoStackedMode = stackingMode
    return config
  }

  mappingAreaConfig(componentConfig, chart, metaData) {
    let self = this
    let dataChart = this.mappingAreaDataset(chart.series, metaData, componentConfig)
    let config = {
      type: CHART_JS_TYPE.LINE,
      data: dataChart,
      options: {
        stacking: get(componentConfig, 'charts[0].options.stacking', 'normal'),
        spanGaps: false,
        responsive: true,
        maintainAspectRatio: false,
        layout: {
          padding: {
            left: 10,
            right: 10,
            top: 10,
            bottom: 10
          }
        },
        elements: {
          line: {
            tension: 0.4
          }
        },
        legendCallback: function (chart) {
          if (get(componentConfig, 'charts[0].options.legend.enabled', true)) {
            return self.buildTemplateBarLegend(chart, componentConfig)
          }
        },
        legend: {
          // we will disabled legend created by chart and append in our div.
          enabled: get(componentConfig, 'charts[0].options.legend.enabled', true),
          widthPercent: get(componentConfig, 'charts[0].options.legend.widthPercent', 40),
          display: false,
          position: get(chart, 'options.legend.position', 'right'),
          isHorizontal: get(chart, 'options.legend.position', false)
        },
        plugin: {
          filter: {
            propagate: false
          }
        }
      }
    }
    const customScales = {
      yAxes: [
        {
          stacked: true,
          ticks: {
            beginAtZero: true,
            max: 100
          }
        }
      ]
    }
    if (config.options.stacking !== 'percent') {
      if (config.options.stacking !== 'normal') {
        config.options.stacking = 'normal'
      }
      delete customScales.yAxes[0].ticks.max
    }
    let scales = this.mappingAxis(chart, componentConfig)
    scales.yAxes = defaultsDeep(cloneDeep(scales.yAxes).splice(0, 1), customScales.yAxes)
    if (!config.options.scales) {
      config.options.scales = {}
    }
    defaultsDeep(config.options.scales, scales)
    config.cbpoStackedMode = config.options.stacking || 'normal'
    config.options.tooltips = this.formatBarTooltip(chart.series, componentConfig, config.cbpoStackedMode)
    return config
  }

  mappingAreaDataset(series, metaData, componentConfig) {
    let labels = []
    let backgroundColors = util.randomColor(componentConfig.colorScheme, series.length).reverse()
    let datasets = series.reduce((datasets, item, index) => {
      let config = {
        label: item.name,
        data: []
      }
      const bins = componentConfig.bins && componentConfig.bins.length ? componentConfig.bins.map(bin => bin.alias) : []
      let dataRows = util.buildDataChartByLabelAndValue(metaData, util.mappingColumnNameToAliasNameWithGrouping(item, componentConfig), bins)
      config.data = dataRows.data
      // This series type is for config stacking mode in bar-area (chart js doesn't have type area)
      config.seriesType = item.type
      // This type is for combo bar-line
      config.type = TYPES.LINE
      config.valueDataset = cloneDeep(dataRows.data)
      config.fill = get(item, 'options.fill', 'origin')
      config.backgroundColor = series[index].backgroundColor ? series[index].backgroundColor : backgroundColors[index]
      labels = dataRows.labels
      datasets.push(config)
      return datasets
    }, [])

    if (get(componentConfig, 'charts[0].options.stacking') === 'percent') {
      this.convertDatasetToPercentage(datasets)
    }
    return { datasets, labels }
  }

  mappingAxis(chartConfig, componentConfig) {
    let xAxes = []
    let yAxes = []
    const columns = componentConfig.columns || []
    const bins = componentConfig.bins || []
    if (chartConfig.axis.x) {
      chartConfig.axis.x.forEach(axis => {
        const serie = chartConfig.series.find(ser => axis.id.includes(ser.id))
        const columnData = columns.find(col => col.name === serie.data.x)
        let isTemporal = false
        if (columnData && columnData.type) {
          isTemporal = DataTypeUtil.isTemporal(columnData.type)
        }
        let isBinnedXAxis = -1
        isBinnedXAxis = bins.findIndex(bin => bin.alias === createBinColumnAlias(serie.data.x))
        if (!bins.length || isBinnedXAxis === -1) {
          if (isTemporal) {
            axis.type = 'time'
            // axis.distribution = 'series'
          }
        }
        if (axis.format && !isTemporal) {
          if (!axis.ticks) axis.ticks = {}
          axis.ticks.callback = (val, index, values) => {
            let data = val
            if (isBinnedXAxis !== -1) data = {label: val, bin: true}
            return dsFormatManager.formatBin(data, axis.format, false) || val
          }
        }
        xAxes.push({
          ...cloneDeep(DEFAULT_CONFIG_X_AXIS),
          ...axis,
          ...{
            ticks: {fontColor: this.themeStyle.accentColor}
          }
        })
      })
    }
    if (chartConfig.axis.y) {
      chartConfig.axis.y.forEach(axis => {
        const serie = chartConfig.series.find(ser => axis.id.includes(ser.id))
        if (serie) {
          let isBinnedYAxis = -1
          const yColumnAlias = serie.type === TYPES.BUBBLE ? createBinColumnAlias(serie.data.y) : createBinColumnAlias(serie.data.y, `${serie.id}_bin`)
          isBinnedYAxis = bins.findIndex(bin => bin.alias === yColumnAlias)
          if (axis.format) {
            if (!axis.ticks) axis.ticks = {}
            axis.ticks.callback = (val, index, values) => {
              let data = val
              if (isBinnedYAxis !== -1) data = {label: val, bin: true}
              return dsFormatManager.formatBin(data, axis.format, false) || val
            }
          }
        }
        yAxes.push({
          ...cloneDeep(DEFAULT_CONFIG_Y_AXIS),
          ...axis,
          ...{
            ticks: {fontColor: this.themeStyle.accentColor}
          }
        })
      })
    }
    if (get(chartConfig, 'options.isHorizontal', false)) {
      let flag = cloneDeep(yAxes)
      yAxes = cloneDeep(xAxes).map(axis => { axis.type = 'category'; return axis })
      xAxes = flag.map(axis => {
        axis.type = 'linear'
        axis.position = axis.position === 'right' ? 'top' : 'bottom'
        return axis
      })
    }
    return {
      xAxes: xAxes,
      yAxes: yAxes
    }
  }

  getLegendStyles(legend = {}, isEmpty, isBarAndNoColumnX = false) {
    let style = {
      canvasContainerStyle: '',
      legendStyle: '',
      legendPosition: isEmpty ? 'legend-no-data' : `legend-${legend.position}`
    }
    const widthPercent = legend.widthPercent || 20
    const isHorizontal = legend.isHorizontal
    if (!isEmpty) {
      if ((legend.position === 'left' || legend.position === 'right')) {
        if (legend.enabled && !isBarAndNoColumnX) {
          style.canvasContainerStyle = `width: ${100 - (legend.scales || widthPercent)}%`
          if (isHorizontal) {
            style.legendStyle = `overflow-x: auto; min-height: calc(${legend.scales || 20}%); max-width: ${widthPercent}%; margin: 0 auto`
          } else {
            style.legendStyle = `overflow-y: auto; min-height: calc(${legend.scales || 20}%); max-width: ${widthPercent}%; margin: 0 auto`
          }
        } else {
          style.canvasContainerStyle = `width: 100%`
          style.legendStyle = ''
        }
      } else if ((legend.position === 'bottom' || legend.position === 'top')) {
        if (legend.enabled && !isBarAndNoColumnX) {
          style.canvasContainerStyle = `height: ${100 - (legend.scales || 20)}%`
          if (isHorizontal) {
            style.legendStyle = `overflow-x: auto; min-height: calc(${legend.scales || 20}% - 20px); max-width: ${widthPercent}%; margin: 0 auto`
          } else {
            style.legendStyle = `overflow-y: auto; max-height: calc(${legend.scales || 20}% - 20px); max-width: ${widthPercent}%; margin: 0 auto`
          }
        } else {
          style.canvasContainerStyle = `height: 100%`
          style.legendStyle = ''
        }
      }
    }
    return style
  }

  getRenderTemplate(options, seriesId, empty, isBarAndNoColumnX) {
    let style = this.getLegendStyles(options.legend, empty, isBarAndNoColumnX)
    let legendTemplate = `<div style="${style.legendStyle}" data-index="${seriesId}" class="legend-container"></div>`
    let canvasTemplate = `<div style="${style.canvasContainerStyle}" class="canvas-container">
                             <canvas chart="${seriesId}"></canvas>
                          </div>`
    let renderTemplate = ''
    switch (options.legend.position) {
      case 'left':
      case 'top': {
        renderTemplate = options.legend.enabled && !isBarAndNoColumnX ? legendTemplate + canvasTemplate : canvasTemplate
        break
      }
      case 'right':
      case 'bottom': {
        renderTemplate = options.legend.enabled && !isBarAndNoColumnX ? canvasTemplate + legendTemplate : canvasTemplate
        break
      }
    }
    return `<div class="cbpo-chart-holder ${style.legendPosition} align-middle">${renderTemplate}</div>`
  }

  stackingSupported(type = '') {
    const data = [
      'Stacked',
      'Position',
      'Begin At Zero',
      'Step Size',
      'Max Ticks'
    ]
    return includes(data, type)
  }

  drawChart(el, componentConfig, indexObject, config) {
    let isBarAndNoColumnX = componentConfig.charts[0].series.every(item => isEmpty(item.data.x) && item.type === TYPES.BAR)
    let seriesId = this.getSeriesId(indexObject)
    let empty = util.isEmptyData(config.data.datasets)
    if (empty) {
      this.emptyDataChart(componentConfig)
    }
    // update bar width for bar chart
    this.updateBarWidth(config)
    let chartSets = $(el).find('.chartSets').get(indexObject.chart)
    let chartContext = $(el).find(`canvas[chart="${seriesId}"]`).get(0)
    if (!isEmpty(chartContext)) {
      $(chartSets).html('')
    }
    let renderTemplate = this.getRenderTemplate(config.options, seriesId, empty, isBarAndNoColumnX)
    $(chartSets).append(renderTemplate)
      .append(() => {
        chartContext = $(el).find(`canvas[chart="${seriesId}"]`).get(0)
        let ctx = chartContext.getContext('2d')
        if (ctx) {
          const uniqueId = `${componentConfig.id}_${seriesId}`
          $(chartContext).attr('id', uniqueId)
          if (window[uniqueId] instanceof Chart) {
            window[uniqueId].destroy()
          }
          window[uniqueId] = new Chart(ctx, config)
          if (!empty) {
            this.appendLegend(el, seriesId, window[uniqueId])
          }
        }
      })
  }

  updateBarWidth(config) {
    config.plugins = [{
      updated: false,
      beforeDraw: function(chart) {
        config.data.datasets.forEach((dataset, key) => {
          let barWidth = chart.getDatasetMeta(key).data[0]._model.width
          let seriesType = chart.getDatasetMeta(key).type
          if (seriesType === TYPES.BAR && barWidth < 1) {
            if (get(config, 'options.scales.xAxes[key]')) {
              config.options.scales.xAxes[key].barPercentage = 2
              config.options.scales.xAxes[key].categoryPercentage = 1.9
            }
          }
        })
        if (!this.updated) {
          chart.update()
          this.updated = true
        }
      }
    }]
  }

  formatPieTooltip(series, config) {
    let self = this
    let bins = config.bins
    let tooltips = {
      callbacks: {
        label: function (tooltipItem, data) {
          let {datasetIndex} = tooltipItem
          let {x, y} = series[datasetIndex].data
          let xColumn = config.columns.find(c => c.name === x)
          let yColumn = config.columns.find(c => c.name === y)
          let columnXFormat = get(xColumn, `format`, null)
          let columnYFormat = get(yColumn, `format`, null)
          let label = data.labels[tooltipItem.index]
          let dsName = data.datasets[datasetIndex].label
          let value = data.datasets[datasetIndex].data[tooltipItem.index]
          // check temporal column and is not binned
          const isBinnedXAxis = bins.findIndex(bin => bin.alias === createBinColumnAlias(x))
          let isTemporal = self.isTemporalColumn(cloneDeep(config), x)
          if (isTemporal && isBinnedXAxis === -1) label = moment(label).format('MM/DD/YYYY')
          let formatLabel
          if (columnXFormat || columnYFormat) {
            if (series[datasetIndex]) {
              let formatY
              if (columnXFormat && !isTemporal) {
                let xData = label
                if (bins.length && bins.findIndex(bin => bin.alias === createBinColumnAlias(x)) !== -1) {
                  xData = { label, bin: true }
                }
                formatLabel = dsFormatManager.formatBin(xData, columnXFormat, false)
              }
              if (columnYFormat) {
                formatY = dsFormatManager.create(columnYFormat, false)
              }
              if (formatY) value = formatY(value)
            }
          }
          if (!x) return `${dsName} : ${value}`
          return `${dsName} - ${formatLabel || label} : ${value}`
        }
      },
      borderWidth: 1,
      mode: 'nearest',
      position: 'nearest',
      titleFontStyle: 'normal',
      titleSpacing: 10,
      bodyFontSize: 12,
      bodySpacing: 10,
      cornerRadius: 3
    }
    return tooltips
  }

  formatBarTooltip(series, config, cbpoStackedMode) {
    let self = this
    let bins = config.bins || []
    let tooltips = {
      callbacks: {
        title: function(tooltipItems) {
          // Multi axis has same x column
          let {datasetIndex, label} = tooltipItems[0]
          let {x} = series[datasetIndex].data
          let xColumn = config.columns.find(c => c.name === x)
          // check temporal column and is not binned
          const isBinnedXAxis = bins.findIndex(bin => bin.alias === createBinColumnAlias(x))
          let isTemporal = self.isTemporalColumn(cloneDeep(config), x)
          if (isTemporal && isBinnedXAxis === -1) label = moment(label).format('MM/DD/YYYY')
          // format
          let columnXFormat = get(xColumn, `format`, null)
          let formatLabel
          if (columnXFormat && !isTemporal) {
            let xData = label
            if (bins.length && bins.findIndex(bin => bin.alias === createBinColumnAlias(x)) !== -1) {
              xData = { label, bin: true }
            }
            formatLabel = dsFormatManager.formatBin(xData, columnXFormat, false)
          }
          return formatLabel || label
        },
        label: function (tooltipItem, data) {
          let {datasetIndex, index} = tooltipItem
          let {y} = series[datasetIndex].data
          let yColumn = config.columns.find(c => c.name === y)
          let columnYFormat = get(yColumn, `format`, null)
          let label = data.datasets[datasetIndex].label
          let value = tooltipItem.value
          let percentageValue = tooltipItem.value
          if (cbpoStackedMode === 'percent') {
            value = data.datasets[datasetIndex].valueDataset[index]
          }
          if (series[datasetIndex]) {
            let formatY
            if (columnYFormat) {
              formatY = dsFormatManager.create(columnYFormat, false)
            }
            if (formatY) value = formatY(value)
          }
          // si-Prefix will apply when user setting in format config
          return `${label} : ${cbpoStackedMode === 'percent' ? `${Math.round(percentageValue)}% (${value})` : value}`
        }
      },
      borderWidth: 1,
      mode: 'index',
      intersect: true,
      position: 'nearest',
      titleFontStyle: 'normal',
      titleSpacing: 10,
      bodyFontSize: this.fontSize,
      bodySpacing: 10,
      cornerRadius: 3
    }
    return tooltips
  }

  formatScatterTooltip(series, config) {
    let self = this
    let bins = config.bins
    let tooltips = {
      callbacks: {
        label: function (tooltipItem, data) {
          let dsIndex = tooltipItem.datasetIndex
          let dataIndex = tooltipItem.index
          let datasetName = data.datasets[dsIndex].label
          let {x, y} = series[dsIndex].data
          let xColumn = config.columns.find(c => c.name === x)
          let yColumn = config.columns.find(c => c.name === y)
          let columnXFormat = get(xColumn, `format`, null)
          let columnYFormat = get(yColumn, `format`, null)
          let xValue = data.datasets[dsIndex].data[dataIndex].x
          let yValue = data.datasets[dsIndex].data[dataIndex].y
          // check temporal column and is not binned
          const isBinnedXAxis = bins.findIndex(bin => bin.alias === createBinColumnAlias(x))
          const isBinnedYAxis = bins.findIndex(bin => bin.alias === createBinColumnAlias(y, `${series[dsIndex].id || ''}_bin`))
          let isXTemporal = self.isTemporalColumn(cloneDeep(config), x)
          let isYTemporal = self.isTemporalColumn(cloneDeep(config), y)
          if (isXTemporal && isBinnedXAxis === -1) xValue = moment(xValue).format('MM/DD/YYYY')
          if (isYTemporal && isBinnedYAxis === -1) yValue = moment(yValue).format('MM/DD/YYYY')
          // format
          let formatXValue
          let formatYValue
          if (columnXFormat || columnYFormat) {
            if (columnXFormat && !isXTemporal) {
              let xData = xValue
              if (isBinnedXAxis !== -1) {
                xData = { xValue, bin: true }
              }
              formatXValue = dsFormatManager.formatBin(xData, columnXFormat, false)
            }

            if (columnYFormat && !isYTemporal) {
              let yData = yValue
              if (isBinnedYAxis !== -1) {
                yData = { yValue, bin: true }
              }
              formatYValue = dsFormatManager.formatBin(yData, columnYFormat, false)
            }
          }
          return `${datasetName} : { ${xColumn.displayName}: ${formatXValue || xValue}, ${yColumn.displayName}: ${formatYValue || yValue} }`
        }
      },
      borderWidth: 1,
      mode: 'index',
      intersect: true,
      position: 'nearest',
      titleFontStyle: 'normal',
      titleSpacing: 10,
      bodyFontSize: this.fontSize,
      bodySpacing: 10,
      cornerRadius: 3
    }
    return tooltips
  }

  formatBubbleTooltip(series, config) {
    let self = this
    let bins = config.bins
    let tooltips = {
      callbacks: {
        label: function (tooltipItem, data) {
          let dsIndex = tooltipItem.datasetIndex
          let dataIndex = tooltipItem.index
          let datasetName = data.datasets[dsIndex].label
          let {x, y, z} = series[dsIndex].data
          let xColumn = config.columns.find(c => c.name === x)
          let yColumn = config.columns.find(c => c.name === y)
          let zColumn = config.columns.find(c => c.name === z)
          let columnXFormat = get(xColumn, `format`, null)
          let columnYFormat = get(yColumn, `format`, null)
          let columnZFormat = get(zColumn, `format`, null)
          let xValue = data.datasets[dsIndex].data[dataIndex].x
          let yValue = data.datasets[dsIndex].data[dataIndex].y
          let zValue = data.datasets[dsIndex].data[dataIndex].v
          // check temporal column and is not binned
          const isBinnedXAxis = bins.findIndex(bin => bin.alias === createBinColumnAlias(x))
          const isBinnedYAxis = bins.findIndex(bin => bin.alias === createBinColumnAlias(y))
          let isXTemporal = self.isTemporalColumn(cloneDeep(config), x)
          let isYTemporal = self.isTemporalColumn(cloneDeep(config), y)
          if (isXTemporal && isBinnedXAxis === -1) xValue = moment(xValue).format('MM/DD/YYYY')
          if (isYTemporal && isBinnedYAxis === -1) yValue = moment(yValue).format('MM/DD/YYYY')
          // format
          let formatXValue
          let formatYValue
          if (columnXFormat || columnYFormat || columnZFormat) {
            let formatZ
            if (columnXFormat && !isXTemporal) {
              let xData = xValue
              if (isBinnedXAxis !== -1) {
                xData = { xValue, bin: true }
              }
              formatXValue = dsFormatManager.formatBin(xData, columnXFormat, false)
            }
            if (columnYFormat && !isYTemporal) {
              let yData = yValue
              if (isBinnedYAxis !== -1) {
                yData = { yValue, bin: true }
              }
              formatYValue = dsFormatManager.formatBin(yData, columnYFormat, false)
            }
            if (columnZFormat) {
              formatZ = dsFormatManager.create(columnZFormat, false)
            }
            if (formatZ) zValue = formatZ(zValue)
          }
          let message = `{ ${xColumn.displayName}: ${formatXValue || xValue}, ${yColumn.displayName}: ${formatYValue || yValue}, ${zColumn.displayName}: ${zValue} }`
          return datasetName ? `${datasetName} : ${message}` : `${message}`
        }
      },
      borderWidth: 1,
      mode: 'index',
      intersect: true,
      position: 'nearest',
      titleFontStyle: 'normal',
      titleSpacing: 10,
      bodyFontSize: this.fontSize,
      bodySpacing: 10,
      cornerRadius: 3
    }
    return tooltips
  }

  buildTemplatePieLegend(chart, componentConfig) {
    const legendWidth = get(componentConfig, 'charts[0].options.legend.widthPercent', 40)
    const isHorizontal = get(componentConfig, 'charts[0].options.legend.isHorizontal', false)
    const liWidth = (100 / (legendWidth / 30)) / 2
    const horizontalStyle = `width: ${liWidth}%; display: inline-block; margin-right: 5px;`
    const verticalStyle = `width: auto; display: flex;`
    let text = ''
    // check column type
    const firstSeries = get(componentConfig, 'charts[0].series[0]', {})
    const isTemporal = this.isTemporalColumn(cloneDeep(componentConfig), firstSeries.data.x)
    // check bins
    let bins = componentConfig.bins || []
    let isBinnedCol = bins.findIndex(bin => bin.alias === createBinColumnAlias(firstSeries.data.x))
    // let datasetsKeys = Object.keys(chart.data.datasets)[0]
    chart.data.datasets.forEach((dataSet, key) => {
      let metaKeys = Object.keys(dataSet._meta)[0]
      let total = (dataSet._meta[metaKeys].total || 1)
      chart.data.labels.forEach((label, i) => {
        let data = dataSet.data[i]
        let convertedDate = util.parseDate(label)
        let percentage = parseFloat(data / total * 100).toFixed(2)
        let background = dataSet.backgroundColor[i]
        // support circle, square and default rectangle
        text += `<li style="${isHorizontal ? horizontalStyle : verticalStyle}"
                    title="${isTemporal ? moment(convertedDate).format('MM/DD/YYYY') : label} (${percentage}%)">
                  <span class="circle" style="background-color: ${background}"></span>
                  <div class="text" style="color: ${this.themeStyle.accentColor}">${isTemporal && isBinnedCol === -1 ? moment(convertedDate).format('MM/DD/YYYY') : label} (${percentage}%)</div>
                </li>`
      })
    })
    return `<ul class="${chart.id}-legend">${text}</ul>`
  }

  buildTemplateBarLegend(chart, componentConfig, isBarOnly, isNoXColumn) {
    if (isNoXColumn) return ''
    const legendWidth = get(componentConfig, 'charts[0].options.legend.widthPercent', 40)
    const isHorizontal = get(componentConfig, 'charts[0].options.legend.isHorizontal', false)
    const liWidth = (100 / (legendWidth / 30)) / 2
    const horizontalStyle = `width: ${liWidth}%; display: inline-block; margin-right: 5px;`
    const verticalStyle = `width: auto; display: flex;`
    let text = ''
    for (let data of chart.data.datasets) {
      let name = data.label
      let type = data.type === TYPES.LINE ? 'circle' : 'square'
      // support circle, square and default rectangle
      text += `<li title="${name}" style="${isHorizontal ? horizontalStyle : verticalStyle}">
                <span class="${type}" style="border: 1px solid ${data.borderColor || 'transparent'}; background-color: ${data.backgroundColor || 'transparent'}"></span>
                <div style="font-size: ${this.fontSize}px; color: ${this.themeStyle.accentColor || ''}" class="text">${name}</div>
              </li>`
      // if (isBarOnly) break
    }
    return `<ul class="${chart.id}-legend">${text}</ul>`
  }

  buildTemplateBubbleLegend(chart, componentConfig) {
    const legendWidth = get(componentConfig, 'charts[0].options.legend.widthPercent', 40)
    const isHorizontal = get(componentConfig, 'charts[0].options.legend.isHorizontal', false)
    const liWidth = (100 / (legendWidth / 30)) / 2
    const horizontalStyle = `width: ${liWidth}%; display: inline-block; margin-right: 5px;`
    const verticalStyle = `width: auto; display: flex;`
    let text = ''
    chart.data.datasets.forEach((data) => {
      let type = data.type === TYPES.LINE ? 'circle' : 'square'
      // support circle, square and default rectangle
      text += `<li title="${data.label}" style="${isHorizontal ? horizontalStyle : verticalStyle}">
                  <span class="${type}" style="border: 1px solid ${data.borderColor || 'transparent'}; background-color: ${data.backgroundColor || 'transparent'}"></span>
                  <div style="font-size: ${this.fontSize}px; color: ${this.themeStyle.accentColor}" class="text">${data.label}</div>
               </li>`
    })
    return `<ul class="${chart.id}-legend">${text}</ul>`
  }

  appendLegend(el, seriesId, chartElement) {
    // We can edit legend html template so can add checkbox, buttons like (check all, reset,...) for chart filter
    let legendHtml = chartElement.generateLegend()
    let container = $(el).find(`.legend-container[data-index="${seriesId}"]`).get(0)
    if (container && !isEmpty(legendHtml)) {
      let series = seriesId.split('_')[1]
      container.innerHTML = legendHtml
      // Add event listener for each child in legend
      switch (parseInt(series)) {
        case INDEX_CHART.pie:
          this.addPieLegendEvent(container, chartElement)
          break
        case INDEX_CHART.scatter:
        case INDEX_CHART.bar_line:
          this.addBarLegendEvent(container, chartElement)
          break
      }
    }
  }

  addPieLegendEvent(container, chartElement) {
    $(container).find('li').on('click', function (e) {
      let index = $(this).index()
      $(this).toggleClass('strike')
      // this object is not an array, its key likes index and only contain one property.
      chartElement.data.datasets.forEach(ds => {
        let meta = ds._meta
        let keysMeta = Object.keys(meta)
        let curr = meta[keysMeta[0]].data[index]
        curr.hidden = !curr.hidden
      })
      // update the chart
      chartElement.update()
    })
  }

  addBarLegendEvent(container, chartElement) {
    let self = this
    $(container).find('li').on('click', function (e) {
      let index = $(this).index()
      $(this).toggleClass('strike')
      // this object is not an array, its key likes index and only contain one property.
      if (!chartElement.getDatasetMeta(index).hidden) {
        chartElement.getDatasetMeta(index).hidden = true
      } else {
        chartElement.getDatasetMeta(index).hidden = null
      }
      if (chartElement.config.cbpoStackedMode === 'percent') {
        let charts = chartElement.config.data.datasets.filter(chart => chart.seriesType === TYPES.AREA || chart.seriesType === TYPES.BAR)
        self.convertDatasetToPercentage(charts)
      }
      // update the chart
      chartElement.update()
    })
  }

  updateChart(id, indexObject) {
    let seriesId = this.getSeriesId(indexObject)
    if (window[`${id}_${seriesId}`]) {
      window[`${id}_${seriesId}`].update()
    } else {
      console.error('Cannot update undefined')
    }
  }

  emptyDataChart(config) {
    let isExisted = false
    if (Chart.plugins._plugins) {
      isExisted = !!Chart.plugins._plugins.find(plugin => plugin.afterDraw)
    }
    if (!isExisted) {
      Chart.plugins.register({
        afterDraw: function (chart) {
          let empty = util.isEmptyData(chart.data.datasets)
          if (empty) {
            // No data is present
            let ctx = chart.chart.ctx
            let width = chart.chart.width
            let height = chart.chart.height
            chart.clear()
            ctx.save()
            ctx.textAlign = 'center'
            ctx.textBaseline = 'middle'
            ctx.fillStyle = 'rgba(0, 0, 0, 0.03)'
            ctx.fillRect(0, 0, width, height)
            ctx.fillStyle = 'black'
            ctx.fontSize = this.fontSize
            ctx.fillText(isEmpty(config.filter) ? config.messages.no_data_at_all : config.messages.no_data_found, width / 2, height / 2)
            ctx.restore()
          }
        }
      })
    }
  }

  isTemporalColumn (config, axisName) {
    const columns = config.columns || []
    const columnData = columns.find(col => col.name === axisName)
    let isTemporal = false
    if (columnData && columnData.type) isTemporal = DataTypeUtil.isTemporal(columnData.type)
    return isTemporal
  }

  updateColor (color, id, yAxisNum = 1, chartType) {
    Chart.helpers.merge(Chart.defaults.global, {
      defaultColor: color.color,
      defaultFontColor: color.color
      // tooltips: {
      //   backgroundColor: 'rgba(0,0,0,0)',
      //   bodyFontColor: color.color,
      //   footerFontColor: color.color,
      //   titleFontColor: color.color
      // }
    })
    if (this) {
      let seriesId = this.getSeriesId({chart: 0, series: INDEX_CHART[chartType]})
      console.log('series', seriesId)
      if (window[`${id}_${seriesId}`]) {
        window[`${id}_${seriesId}`].update()
      } else {
        console.error('Cannot update undefined')
      }
    }
  }
}
