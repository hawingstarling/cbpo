// import precond from 'precond'
import { AreaChartBuilder } from '@/components/widgets/elements/chart/builder/highcharts/AreaChartBuilder'
import { BarChartBuilder } from '@/components/widgets/elements/chart/builder/highcharts/BarChartBuilder'
import { ComboBarLineBuilder } from '@/components/widgets/elements/chart/builder/highcharts/ComboBarLineBuilder'
import { HeatMapBuilder } from '@/components/widgets/elements/chart/builder/highcharts/HeatMapBuilder'
import { LineChartBuilder } from '@/components/widgets/elements/chart/builder/highcharts/LineChartBuilder'
import { PieChartBuilder } from '@/components/widgets/elements/chart/builder/highcharts/PieChartBuilder'
import { ScatterChartBuilder } from '@/components/widgets/elements/chart/builder/highcharts/ScatterChartBuilder'
import { BubbleChartBuilder } from '@/components/widgets/elements/chart/builder/highcharts/BubbleChartBuilder'
import { BulletGaugeChartBuilder } from '@/components/widgets/elements/chart/builder/highcharts/BulletGaugeChartBuilder'
import { SolidGaugeChartBuilder } from '@/components/widgets/elements/chart/builder/highcharts/SolidGaugeChartBuilder'

import AbstractLib from './AbstractLib'
import Highcharts from 'highcharts'
import $ from 'jquery'
import * as util from '@/utils/chartUtil'
import { makeDOMId, TYPES_SUPPORTED_HC } from '../types/ChartTypes'
import { HC_TYPES, TYPES, CHART_JS_TYPE } from '../ChartConfig'
import {
  cloneDeep,
  forEach,
  findIndex,
  isObject,
  isNil,
  get,
  toNumber,
  without,
  includes,
  isEmpty,
  filter,
  defaultsDeep
} from 'lodash'
import { createBinColumnAlias } from '@/utils/binUtils'
import { DataTypeUtil } from '@/services/ds/data/DataTypes'
import { ComboAreaLineBuilder } from '@/components/widgets/elements/chart/builder/highcharts/ComboAreaLineBuilder'
import { CHART_LIBRARY } from '@/components/visualizationBuilder/VisualizationBuilderTypes'
import dsFormatManager from '@/services/dataFormatManager'
import moment from 'moment'

/**
 * Apply for Highcharts.
 *
 * @override
 *
 * @param el {element}
 * @param componentConfig {Object} Chart.vue component config.
 * @param data {Object} standard data object with rows and cols.
 */

const mappingBuilder = {
  [TYPES.HEAT_MAP]: new HeatMapBuilder(Highcharts),
  [TYPES.PIE]: new PieChartBuilder(Highcharts),
  [TYPES.BAR]: new BarChartBuilder(Highcharts),
  [TYPES.LINE]: new LineChartBuilder(Highcharts),
  [TYPES.AREA]: new AreaChartBuilder(Highcharts),
  [TYPES.SCATTER]: new ScatterChartBuilder(Highcharts),
  [TYPES.BUBBLE]: new BubbleChartBuilder(Highcharts),
  [TYPES.BULLETGAUGE]: new BulletGaugeChartBuilder(Highcharts),
  [TYPES.SOLIDGAUGE]: new SolidGaugeChartBuilder(Highcharts),
  comboBarLine: new ComboBarLineBuilder(Highcharts),
  comboAreaLine: new ComboAreaLineBuilder(Highcharts)
}

function addCallbackEventToDropOptions(chartConfig, { rows, cols }) {
  let _self = this
  chartConfig = Object.assign(
    chartConfig,
    {
      plotOptions:
        {
          series:
            {
              events: {
                click: function($event) {
                  if (_self.callbackObj.drillDownCallback) {
                    const seriesIndex = this.index
                    const { data } = _self.config.charts[0].series[seriesIndex]
                    const hasBin = !isEmpty(_self.config.bins)
                    const column = { name: data.x }
                    const columnIndex = findIndex(cols, col => (col.column || col.name) === (hasBin ? createBinColumnAlias(data.x) : data.x))
                    const values = rows.find(row => (hasBin ? row[columnIndex].label : row[columnIndex]) === (hasBin ? $event.point.root_Data.x.label : $event.point.root_Data.x))
                    _self.callbackObj.drillDownCallback({
                      column,
                      value: values[columnIndex],
                      aggregations: _self.config.grouping.aggregations
                    })
                  }
                }
              }
            }
        }
    })
  return chartConfig
}

export default class HighchartsLib extends AbstractLib {
  themeStyle = {}
  callbackObj = {}
  config = {}

  render(domId, el, componentConfig, data, callbackObj = {}) {
    this.themeStyle = util.getStyle()
    this.callbackObj = callbackObj
    this.config = componentConfig

    $(el).find('.chartSets').html('')
    if (componentConfig.charts) {
      let charts = cloneDeep(componentConfig.charts)
      charts.forEach((chart) => {
        let series = []
        let config = {}
        let HC_CONFIG = {}
        let isNoXColumn = chart.series.every(item => isEmpty(item.data.x))
        const chartType = chart.series[0].type
        const isComboBarLine = chart.series.some(item => item.type === TYPES.BAR) && chart.series.some(item => item.type === TYPES.LINE)
        const isComboAreaLine = chart.series.some(item => item.type === TYPES.AREA) && chart.series.some(item => item.type === TYPES.LINE)
        HC_CONFIG[TYPES.PIE] = filter(chart.series, s => s.type === TYPES.PIE)

        // filter pie chart in series
        switch (true) {
          // special case
          case isComboBarLine:
          case isComboAreaLine:
            mappingBuilder.comboBarLine.buildAndRender(domId, data, componentConfig)
            return
          // un-common case
          case chartType === TYPES.LINE:
          case chartType === TYPES.AREA:
          case chartType === TYPES.SCATTER:
          case chartType === TYPES.BUBBLE:
          case chartType === TYPES.BULLETGAUGE:
          case chartType === TYPES.SOLIDGAUGE:
            mappingBuilder[chartType].buildAndRender(domId, data, componentConfig)
            return
          // common case
          case chartType === TYPES.HEAT_MAP:
            mappingBuilder[TYPES.HEAT_MAP].buildAndRender(domId, data, componentConfig, {
              mainQuery: callbackObj.mainQuery
            })
            return
          case chartType === TYPES.PIE:
            mappingBuilder[TYPES.PIE].buildAndRender(domId, data, componentConfig, {
              drillDown: callbackObj.drillDownCallback
            })
            return
          case chartType === TYPES.BAR:
            mappingBuilder[TYPES.BAR].buildAndRender(domId, data, componentConfig, {
              mainQuery: callbackObj.mainQuery,
              drillDown: callbackObj.drillDownCallback
            })
            return
        }

        if (isObject(chart.options)) {
          this.mappingChartOptionsToConfig(chart.options, config)
        }

        // tooltip
        this.formatTooltip(chart, componentConfig, config, isNoXColumn)

        forEach(chart.series, (item, index) => {
          if (TYPES_SUPPORTED_HC.includes(item.type)) {
            this.mappingDataSeries(item, chart.options, data, componentConfig, chart, HC_CONFIG, config, series, isNoXColumn)
          }
        })
        let isPie = chart.series.every(item => item.type === TYPES.PIE)
        let isBar = chart.series.every(item => item.type === TYPES.BAR)
        if (isNoXColumn && (isPie || isBar)) {
          let newSeriesData = series[0]
          series.splice(0, 1)
          series.forEach(item => {
            newSeriesData.data = [...newSeriesData.data, ...item.data]
          })
          series = [newSeriesData]
        }

        // draw chart bullet gauge
        if (HC_CONFIG[TYPES.BULLETGAUGE]) {
          let colors = util.randomColor(componentConfig.colorScheme, HC_CONFIG[TYPES.BULLETGAUGE].length).reverse()
          return forEach(HC_CONFIG[TYPES.BULLETGAUGE], (item, index) => {
            item.series[0].color = colors[index]
            let data = {
              id: `${componentConfig.id}_${index}`,
              colorScheme: componentConfig.colorScheme,
              widget: componentConfig.widget
            }
            let w = 100
            let h = 100 / HC_CONFIG[TYPES.BULLETGAUGE].length
            // console.log(cloneDeep(item), data)
            return this.drawChart(domId, el, data, item.series, item.config, data, h, w)
          })
        }

        // draw chart solid gauge
        if (HC_CONFIG[TYPES.SOLIDGAUGE]) {
          return forEach(HC_CONFIG[TYPES.SOLIDGAUGE], (item, index) => {
            let data = {
              id: `${componentConfig.id}_${index}`,
              colorScheme: componentConfig.colorScheme,
              widget: componentConfig.widget
            }
            let h = 100
            let w = 100 / HC_CONFIG[TYPES.SOLIDGAUGE].length
            return this.drawChart(domId, el, data, item.series, item.config, data, h, w)
          })
        }
        // TODO: Convert other type (pie, bar, ...)
        this.drawChart(domId, el, componentConfig, series, config, data)
      })
    }
  }

  isChartSupported(componentConfig) {
    if (componentConfig.charts) {
      return componentConfig.charts.every(chart => chart.series.every(item => TYPES_SUPPORTED_HC.includes(item.type)))
    }
    return false
  }

  mappingChartOptionsToConfig(options, config) {
    forEach(options, (item, name) => {
      switch (name) {
        case 'title':
        case 'subtitle':
          config[name] = item || ''
          break
        default:
          break
      }
    })
  }

  mappingDataSeries(targetSeries, targetOptions, metaData, componentConfig, chart, HC_CONFIG, config, series, isNoXColumn) {
    let seriesConfig = {
      name: targetSeries.name,
      id: targetSeries.id
    }
    const bins = componentConfig.bins && componentConfig.bins.length ? componentConfig.bins.map(bin => bin.alias) : []
    const { pie = {}, stacking, isHorizontal, borderWidth = 0 } = targetOptions
    const columns = componentConfig.columns || []
    const columnData = columns.find(col => col.name === targetSeries.data.x)
    let isXAxisTemporal = false
    let isXAxisText = false
    let nameAxis = { x: 'x', y: 'y', z: 'z' }
    if (columnData && columnData.type) isXAxisTemporal = DataTypeUtil.isTemporal(columnData.type)
    if (columnData && columnData.type) isXAxisText = DataTypeUtil.isText(columnData.type)
    let binnedXAxis = bins.findIndex(bin => bin === createBinColumnAlias(targetSeries.data.x))
    // mapping series
    switch (targetSeries.type) {
      case TYPES.PIE:
        const { type = 'pie' } = pie
        const { size, innerSize } = this.getHCConfigSize(type)
        // drillDown mapping
        config = addCallbackEventToDropOptions.bind(this)(config, metaData)

        if (!isNoXColumn || (isNoXColumn && chart.options.pie.type === 'doughnut')) {
          // calculate size and innerSize
          HC_CONFIG.widthPie = size / HC_CONFIG[TYPES.PIE].length
          HC_CONFIG.innerSizePie = !isNil(HC_CONFIG.innerSizePie) ? HC_CONFIG.sizePie : innerSize
          HC_CONFIG.sizePie = !isNil(HC_CONFIG.sizePie) ? HC_CONFIG.sizePie + HC_CONFIG.widthPie : innerSize + HC_CONFIG.widthPie
          // set size and innerSize to pie chart
          seriesConfig.size = `${HC_CONFIG.sizePie}%`
          seriesConfig.innerSize = `${HC_CONFIG.innerSizePie}%`
        }
        if (isXAxisTemporal && binnedXAxis === -1) {
          config.plotOptions.series = {
            dataLabels: {
              enabled: false
            }
          }
          // default legend option
          config.legend = this.getLegendOptions(chart)
          config.legend.labelFormatter = function() {
            return `${moment(this.name).format('MM/DD/YYYY')} (${this.percentage.toFixed(2)})`
          }
        } else {
          seriesConfig.dataLabels = {
            enabled: false
          }
          // default legend option
          config.legend = this.getLegendOptions(chart)
          config.legend.labelFormat = '{name} ({percentage:.1f} %)'
        }
        // default show legend
        seriesConfig.showInLegend = true
        seriesConfig.borderWidth = borderWidth
        // mapping axis
        this.mappingAxis(targetSeries, metaData, chart, config, seriesConfig, componentConfig)
        // add data
        seriesConfig.data = util
          .buildDataChartByXYZPoint(metaData, util.mappingColumnNameToAliasNameWithGrouping(targetSeries, componentConfig), bins)
          .map(item => {
            if (item.name === null || item.name === undefined) {
              item.name = 'Null'
            }
            if (item.name === '') {
              item.name = 'Empty'
            }
            return item
          })

        if (isNoXColumn) {
          seriesConfig.data = seriesConfig.data.map(d => {
            d.name = targetSeries.name
            return d
          })
        }
        // add type
        seriesConfig.type = HC_TYPES.PIE
        break
      case TYPES.LINE:
        let step = get(targetSeries, 'options.step', '')
        if (step) {
          seriesConfig.step = step
        } else {
          // add type
          seriesConfig.type = HC_TYPES.SPLINE
        }
        // mapping axis
        this.mappingAxis(targetSeries, metaData, chart, config, seriesConfig, componentConfig)
        // add data
        if (binnedXAxis !== -1 || isXAxisText) nameAxis.x = 'name'
        seriesConfig.data = util.buildDataChartByXYZPoint(metaData, util.mappingColumnNameToAliasNameWithGrouping(targetSeries, componentConfig), bins, nameAxis)
        // legend option
        config.legend = this.getLegendOptions(chart)
        break
      case TYPES.BAR:
        seriesConfig.stacking = stacking || ''

        // drillDown mapping
        config = addCallbackEventToDropOptions.bind(this)(config, metaData)
        // mapping axis
        this.mappingAxis(targetSeries, metaData, chart, config, seriesConfig, componentConfig, isNoXColumn)
        // add data
        if (binnedXAxis !== -1 || isXAxisText || isNoXColumn) nameAxis.x = 'name'
        seriesConfig.data = util.buildDataChartByXYZPoint(metaData, util.mappingColumnNameToAliasNameWithGrouping(targetSeries, componentConfig), bins, nameAxis)
        if (isNoXColumn) {
          seriesConfig.name = chart.options.legend.titleWithoutXColumn
          seriesConfig.data = seriesConfig.data.map(d => {
            d.name = targetSeries.name
            return d
          })
        }
        // add type
        seriesConfig.type = isHorizontal ? HC_TYPES.BAR : HC_TYPES.COLUMN
        // legend option
        config.legend = this.getLegendOptions(chart, isNoXColumn)

        break
      case TYPES.AREA:
        seriesConfig.stacking = stacking || 'normal'
        // mapping axis
        this.mappingAxis(targetSeries, metaData, chart, config, seriesConfig, componentConfig)
        // add data
        if (binnedXAxis !== -1 || isXAxisText) nameAxis.x = 'name'
        seriesConfig.data = util.buildDataChartByXYZPoint(metaData, util.mappingColumnNameToAliasNameWithGrouping(targetSeries, componentConfig), bins, nameAxis)
        // add type
        seriesConfig.type = HC_TYPES.AREASPLINE
        // legend option
        config.legend = this.getLegendOptions(chart)
        break
      case TYPES.SCATTER:
        // mapping axis
        this.mappingAxis(targetSeries, metaData, chart, config, seriesConfig, componentConfig)
        config.chart = { zoomType: 'xy' }
        // add data
        seriesConfig.data = util.buildDataChartByXYZPointForHC(metaData, util.mappingColumnNameToAliasNameWithGrouping(targetSeries, componentConfig), cloneDeep(config), bins)
        // add type
        seriesConfig.type = HC_TYPES.SCATTER
        // legend option
        config.legend = this.getLegendOptions(chart)
        break
      case TYPES.BUBBLE:
        config.chart = {
          plotBorderWidth: 1,
          zoomType: 'xy'
        }
        this.mappingAxisBubble(targetSeries, metaData, chart, config, seriesConfig, componentConfig)
        seriesConfig.data = util.buildDataChartByXYZPointForHC(metaData, util.mappingColumnNameToAliasNameWithGrouping(targetSeries, componentConfig), cloneDeep(config), bins)
        seriesConfig.type = HC_TYPES.BUBBLE
        // legend option
        config.legend = this.getLegendOptions(chart)
        break
      case TYPES.BULLETGAUGE:
        config.legend = { enabled: false }
        config.chart = { inverted: isHorizontal }
        config.title = { text: null }
        config.plotOptions = { series: { pointPadding: 0.25, borderWidth: 0, targetOptions: { width: '200%' } } }
        seriesConfig.pointPadding = 0.25
        seriesConfig.borderWidth = 0
        this.mappingAxisBulletGauge(targetSeries, chart, config)
        let dataRowBullet = util.buildDataChartByXYZPoint(metaData, util.mappingColumnNameToAliasNameWithGrouping(targetSeries, componentConfig), bins)
        seriesConfig.data = [{
          y: dataRowBullet[0].y,
          target: toNumber(get(targetSeries, 'options.target', dataRowBullet[0].y))
        }]
        seriesConfig.type = HC_TYPES.BULLETGAUGE
        if (!isObject(HC_CONFIG[TYPES.BULLETGAUGE])) {
          HC_CONFIG[TYPES.BULLETGAUGE] = []
        }
        HC_CONFIG[TYPES.BULLETGAUGE].push({
          series: [cloneDeep(seriesConfig)],
          config: cloneDeep(config)
        })
        break
      case TYPES.SOLIDGAUGE:
        config.pane = {
          center: ['50%', '85%'],
          size: '95%',
          startAngle: -90,
          endAngle: 90,
          background: { innerRadius: '60%', outerRadius: '100%', shape: 'arc' }
        }
        config.plotOptions = { solidgauge: { dataLabels: { y: 5, borderWidth: 0, useHTML: true } } }
        config.title = { text: null }
        config.tooltip = { enabled: false }
        let dataRowSolidGauge = util.buildDataChartByXYZPoint(metaData, util.mappingColumnNameToAliasNameWithGrouping(targetSeries, componentConfig), bins)
        seriesConfig.data = [toNumber(toNumber(dataRowSolidGauge[0].y).toFixed(2))]
        this.mappingAxisSolidGauge(targetSeries, chart, config, seriesConfig, get(componentConfig, 'widget.style', {}))
        seriesConfig.type = HC_TYPES.SOLIDGAUGE
        if (!isObject(HC_CONFIG[TYPES.SOLIDGAUGE])) {
          HC_CONFIG[TYPES.SOLIDGAUGE] = []
        }
        HC_CONFIG[TYPES.SOLIDGAUGE].push({
          series: [cloneDeep(seriesConfig)],
          config: cloneDeep(config)
        })
        break
    }
    // add config to series
    series.push(seriesConfig)
    config.title = { text: '' }
    config.subTitle = { text: '' }
  }

  getLegendOptions(chart, isNoXColumn) {
    let legend = {
      navigation: {
        activeColor: this.themeStyle.navigationActive,
        inactiveColor: this.themeStyle.navigationInactive,
        style: {
          color: this.themeStyle.accentColor
        }
      },
      itemStyle: {
        color: this.themeStyle.accentColor,
        fontWeight: 'normal',
        fontSize: '11px'
      },
      itemHoverStyle: {
        color: this.themeStyle.hoverItemColor
      },
      enabled: isNoXColumn ? false : get(chart, 'options.legend.enabled', 'true')
    }
    const position = get(chart, 'options.legend.position', 'right')
    const widthPercent = get(chart, 'options.legend.widthPercent', 40)
    const isHorizontal = get(chart, 'options.legend.isHorizontal', false)
    switch (position) {
      case 'left':
        legend.align = 'left'
        legend.verticalAlign = 'middle'
        legend.layout = isHorizontal ? 'horizontal' : 'vertical'
        legend.width = `${widthPercent}%`
        break
      case 'right':
        legend.align = 'right'
        legend.verticalAlign = 'middle'
        legend.layout = isHorizontal ? 'horizontal' : 'vertical'
        legend.width = `${widthPercent}%`
        break
      case 'top':
        legend.align = 'center'
        legend.verticalAlign = 'top'
        legend.layout = isHorizontal ? 'horizontal' : 'vertical'
        legend.maxWidth = `${widthPercent}%`
        break
      case 'bottom':
        legend.align = 'center'
        legend.verticalAlign = 'bottom'
        legend.layout = isHorizontal ? 'horizontal' : 'vertical'
        legend.maxWidth = `${widthPercent}%`
        break
    }
    return legend
  }

  stackingSupported(type = '') {
    const data = [
      'Position'
    ]
    return includes(data, type)
  }

  formatTooltip(chart, componentConfig, config, isNoXColumn) {
    let bins = componentConfig.bins
    const columns = componentConfig.columns || []
    config.tooltip = {
      useHTML: true,
      shared: true,
      headerFormat: '',
      formatter: function() {
        let arrayPoints = this.points ? this.points : [this]
        let tooltip = ``
        $.each(arrayPoints, function(i, e) {
          let targetSeries = chart.series.find(c => c.id === e.series.userOptions.id)
          let { data: { x, y, z }, type } = targetSeries
          let xColumn = componentConfig.columns.find(c => c.name === x)
          let yColumn = componentConfig.columns.find(c => c.name === y)
          let zColumn = componentConfig.columns.find(c => c.name === z)
          let columnXFormat = get(xColumn, `format`, null)
          let columnYFormat = get(yColumn, `format`, null)
          let columnZFormat = get(zColumn, `format`, null)
          let xValue = e.point.name || e.point.x
          let yValue = e.point.y
          let zValue = e.point.z
          // check temporal column and is not binned
          const isBinnedXCol = bins.findIndex(bin => bin.alias === createBinColumnAlias(x))
          const columnData = columns.find(col => col.name === x)
          let isTemporal = false
          if (columnData && columnData.type) isTemporal = DataTypeUtil.isTemporal(columnData.type)
          if (isTemporal && isBinnedXCol === -1) xValue = moment(xValue).format('MM/DD/YYYY')
          // format
          let formatXValue
          let formatYValue
          let formatZValue
          if (columnXFormat || columnYFormat || columnZFormat) {
            if (targetSeries) {
              if (columnXFormat && !isTemporal) {
                let xData = xValue
                if (isBinnedXCol !== -1) {
                  xData = { xValue, bin: true }
                }
                if (xData.match(/^-{0,1}\d+$/)) {
                  formatXValue = dsFormatManager.formatBin(xData, columnXFormat, false)
                } else {
                  formatXValue = dsFormatManager.create(columnXFormat, false)(xData)
                }
              }
              if (columnYFormat) {
                let yData = yValue
                // if (type === TYPES.SCATTER) {
                //   if (bins.length && bins.findIndex(bin => bin.alias === createBinColumnAlias(y, `${id}_bin`)) !== -1) {
                //     yData = { yValue, bin: true }
                //   }
                // } else if (type === TYPES.BUBBLE) {
                //   if (bins.length && bins.findIndex(bin => bin.alias === createBinColumnAlias(y)) !== -1) {
                //     yData = { yValue, bin: true }
                //   }
                // }
                formatYValue = dsFormatManager.formatBin(yData, columnYFormat, false)
              }
              if (columnZFormat) {
                formatZValue = dsFormatManager.create(columnZFormat, false)(zValue)
              }
            }
          }
          switch (type) {
            case TYPES.PIE:
              if (isNoXColumn) {
                tooltip += `<span style='color:${e.color}'>\u25CF</span> <b>${e.series.name}</b>: ${formatYValue || yValue || null}<br/>(${Math.round(this.point.percentage * 100) / 100}%)`
              } else {
                tooltip += `<span style='color:${e.color}'>\u25CF</span> <b>${e.series.name}</b> -
              ${formatXValue || xValue || null}:
              ${formatYValue || yValue || null}<br/>(${Math.round(this.point.percentage * 100) / 100}%)`
              }
              break
            case TYPES.BAR:
            case TYPES.LINE:
            case TYPES.AREA:
              if (i === 0) tooltip += `${formatXValue || xValue || null}<br/>`
              tooltip += `<span style='color:${e.color}'>\u25CF</span> <b>${e.series.name}</b>:
              ${formatYValue || yValue || null}<br/>`
              break
            default:
              tooltip += `<span style='color:${e.color}'>\u25CF</span> <b>${e.series.name}</b>: { ${without([
                xColumn ? `${xColumn.displayName || xColumn.name}: ${formatXValue || xValue || null}` : null,
                yColumn ? `${yColumn.displayName || yColumn.name}: ${formatYValue || yValue || null}` : null,
                zColumn ? `${zColumn.displayName || zColumn.name}: ${formatZValue || zValue || null}` : null,
                e.point.target ? `target: ${e.point.target}` : null
              ], null).join(', ')} }<br/>`
              break
          }
        })
        return tooltip
      }
    }
  }

  mappingAxisBubble(targetSeries, metaData, chart, config, series, componentConfig) {
    const bins = componentConfig.bins && componentConfig.bins.length ? componentConfig.bins.map(bin => bin.alias) : []
    if (chart.axis && chart.axis.x) {
      const xIndex = targetSeries.axis.x ? findIndex(chart.axis.x, ['id', targetSeries.axis.x]) : 0
      const xAxis = chart.axis.x[xIndex] || {}
      const bins = componentConfig.bins && componentConfig.bins.length ? componentConfig.bins.map(bin => bin.alias) : []
      const xColumnAlias = createBinColumnAlias(targetSeries.data.x)
      if (bins.length && bins.findIndex(bin => bin === xColumnAlias) !== -1) {
        let xCategories = util.buildDataChartByXYZPoint(metaData, {
          xCategories: bins.length && bins.findIndex(bin => bin === xColumnAlias) !== -1 ? xColumnAlias : targetSeries.data.x
        }, bins)
        config.xAxis = {
          categories: xCategories,
          gridLineWidth: 1,
          title: {
            text: get(xAxis, 'scaleLabel.display', false) ? get(xAxis, 'scaleLabel.labelString', '') : ''
          },
          plotLines: xAxis.plotLines || []
        }
      } else {
        // check column type
        const columns = componentConfig.columns || []
        const columnData = columns.find(col => col.name === targetSeries.data.x)
        let isTemporal = false
        if (columnData && columnData.type) isTemporal = DataTypeUtil.isTemporal(columnData.type)
        config.xAxis = {
          title: {
            text: get(xAxis, 'scaleLabel.display', false) ? get(xAxis, 'scaleLabel.labelString', '') : ''
          },
          plotLines: xAxis.plotLines || [],
          gridLineWidth: 1
        }
        if (isTemporal) {
          config.xAxis.type = 'datetime'
          config.xAxis.labels = {}
          xAxis.type = 'datetime'
        } else {
          const xAxisFormat = get(xAxis, `format`, null)
          config.xAxis.labels = {
            useHTML: true,
            formatter: function() {
              return `${xAxisFormat ? dsFormatManager.format(this.value, xAxisFormat, false) : this.value}`
            }
          }
        }
      }
    }

    if (chart.axis && chart.axis.y) {
      const yIndex = targetSeries.axis.y ? findIndex(chart.axis.y, ['id', targetSeries.axis.y]) : 0
      const yAxis = chart.axis.y[yIndex] || {}
      // only 1 axis y
      // series.yAxis = yIndex
      let yAxisFormat = get(yAxis, `format`, null)
      if (yAxisFormat) {
        yAxis.dsFormatManager = dsFormatManager.create(yAxisFormat, false)
      }

      if (!config.yAxis) {
        config.yAxis = []
      }

      const yColumnAlias = createBinColumnAlias(targetSeries.data.y)
      if (bins && bins.findIndex(bin => bin === yColumnAlias) !== -1) {
        let yCategories = util.buildDataChartByXYZPoint(metaData, {
          yCategories: yColumnAlias
        }, bins)
        let positionsObj = {}
        config.yAxis[yIndex] = {
          tickPositioner: function() {
            let positions = []
            let tick = Math.floor(this.dataMin)
            let distance = yCategories.length - 1
            let increment = 0
            if (distance !== 0) {
              increment = Math.ceil((this.dataMax - this.dataMin) / distance)
            }
            if (!increment) {
              if (yCategories && yCategories.length) {
                positions[0] = this.dataMin
                positionsObj[0] = yCategories[0]
              }
            } else {
              if (this.dataMax !== null && this.dataMin !== null) {
                let catIndex = 0
                for (tick; tick <= (this.dataMax + increment); tick += increment) {
                  positions.push(tick)
                  positionsObj[tick] = yCategories[catIndex]
                  catIndex++
                }
              }
            }
            return positions
          },
          labels: { // custom label for yAxis
            formatter: function() {
              return (positionsObj[this.value] ? positionsObj[this.value] : this.value)
            }
          },
          opposite: yAxis.opposite === true || false
        }
      } else {
        config.yAxis[yIndex] = {
          title: {
            text: get(yAxis, 'scaleLabel.display', false) ? get(yAxis, 'scaleLabel.labelString', '') : ''
          },
          maxPadding: 0.2,
          plotLines: yAxis.plotLines || [],
          labels: {
            y: 16,
            useHTML: true,
            formatter: function() {
              return `${yAxis.dsFormatManager ? yAxis.dsFormatManager(this.value) : this.value}`
            }
          }
        }
      }
      config.yAxis = config.yAxis.map(axis => {
        axis.labels.style = { color: this.themeStyle.accentColor }
        return axis
      })
      if (get(config, 'xAxis.labels', null) || get(config, 'xAxis.type', '') === 'datetime') {
        config.xAxis.labels.style = { color: this.themeStyle.accentColor }
      }
    }
  }

  mappingAxisSolidGauge(targetSeries, chart, config, series, widgetStyle) {
    const style = widgetStyle.foreground_color || null
    series.dataLabels = {
      format: `<div style='text-align:center'>
                <span style='font-size:${get(targetSeries, 'options.size', '25')}px; color: ${style || this.themeStyle.accentColor}'>{y}</span><br/>
                <span style='font-size:12px;opacity:0.4; color: ${style || this.themeStyle.accentColor}'>${get(targetSeries, 'options.subtitle', '')}</span>
               </div>`
    }
    if (chart.axis && chart.axis.y) {
      const yIndex = targetSeries.axis.y ? findIndex(chart.axis.y, ['id', targetSeries.axis.y]) : 0
      const yAxis = chart.axis.y[yIndex] || {}
      let max = toNumber(toNumber(yAxis.max).toFixed(2)) || 0
      let stops = yAxis.stops && yAxis.stops.map(e => {
        let a = (toNumber(toNumber(e[0]).toFixed(2)) < max) ? (toNumber(toNumber(e[0]).toFixed(2)) / max).toFixed(2) : 1
        return [a, e[1]]
      })
      let yAxisFormat = get(yAxis, `format`, null)
      if (yAxisFormat) {
        yAxis.dsFormatManager = dsFormatManager.create(yAxisFormat, false)
      }
      config.yAxis = [{
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
        max: max || 0,
        labels: {
          y: 16,
          useHTML: true,
          formatter: function() {
            return `${yAxis.dsFormatManager ? yAxis.dsFormatManager(this.value) : this.value}`
          }
        }
      }]
    }
    config.yAxis = config.yAxis.map(axis => {
      axis.labels.style = { color: this.themeStyle.accentColor }
      return axis
    })
  }

  mappingAxisBulletGauge(targetSeries, chart, config) {
    config.xAxis = {
      labels: {
        style: {
          color: this.themeStyle.accentColor
        }
      },
      categories: [`<span class='hc-cat-title'>${get(targetSeries, 'options.title', '')}</span><br/>
                    ${get(targetSeries, 'options.subtitle', '')}`]
    }

    if (chart.axis && chart.axis.y) {
      const yIndex = targetSeries.axis.y ? findIndex(chart.axis.y, ['id', targetSeries.axis.y]) : 0
      const yAxis = chart.axis.y[yIndex] || {}
      let yAxisFormat = get(yAxis, `format`, null)
      if (yAxisFormat) {
        yAxis.dsFormatManager = dsFormatManager.create(yAxisFormat, false)
      }
      config.yAxis = [{
        gridLineWidth: 0,
        title: {
          text: get(yAxis, 'scaleLabel.display', false) ? get(yAxis, 'scaleLabel.labelString', '') : ''
        },
        plotBands: yAxis.plotBands || [],
        labels: {
          useHTML: true,
          formatter: function() {
            return `${yAxis.dsFormatManager ? yAxis.dsFormatManager(this.value) : this.value}`
          }
        }
      }]
      config.yAxis = config.yAxis.map(axis => {
        axis.labels.style = { color: this.themeStyle.accentColor }
        return axis
      })
    }
  }

  mappingAxis(targetSeries, metaData, chart, config, series, componentConfig, isNoXColumn) {
    if (chart.axis && chart.axis.x) {
      const xAxis = chart.axis.x[0] || {}
      let bins = componentConfig.bins && componentConfig.bins.length ? componentConfig.bins.map(bin => bin.alias) : []
      const xColumnAlias = createBinColumnAlias(targetSeries.data.x)
      let isBinnedXAxis = bins.findIndex(bin => bin === xColumnAlias)
      if (isBinnedXAxis !== -1) {
        let xCategories = util.buildDataChartByXYZPoint(metaData, {
          xCategories: bins.length && bins.findIndex(bin => bin === xColumnAlias) !== -1 ? xColumnAlias : targetSeries.data.x
        }, bins)
        config.xAxis = {
          categories: xCategories,
          labels: {},
          title: {
            text: get(xAxis, 'scaleLabel.display', false) ? get(xAxis, 'scaleLabel.labelString', '') : ''
          }
        }
      } else {
        // check column type
        const columns = componentConfig.columns || []
        const columnData = columns.find(col => col.name === targetSeries.data.x)
        let isTemporal = false
        let isText = false
        if (columnData && columnData.type) isTemporal = DataTypeUtil.isTemporal(columnData.type)
        if (columnData && columnData.type) isText = DataTypeUtil.isText(columnData.type)
        config.xAxis = {
          title: {
            text: get(xAxis, 'scaleLabel.display', false) ? get(xAxis, 'scaleLabel.labelString', '') : ''
          }
        }
        if (isTemporal) {
          config.xAxis.type = 'datetime'
          config.xAxis.labels = {}
        } else {
          if (isText || isNoXColumn) config.xAxis.type = 'category'
          const xAxisFormat = get(xAxis, `format`, null)
          config.xAxis.labels = {
            useHTML: true,
            formatter: function() {
              return `${xAxisFormat ? dsFormatManager.format(this.value, xAxisFormat, false) : this.value}`
            }
          }
        }
      }
    }
    if (chart.axis && chart.axis.y) {
      const yIndex = targetSeries.axis.y ? findIndex(chart.axis.y, ['id', targetSeries.axis.y]) : 0
      const yAxis = chart.axis.y[yIndex] || {}
      // check type by series
      let hasBar = false
      let hasLine = false
      chart.series.forEach((ser, index) => {
        if (ser.type === CHART_JS_TYPE.BAR) hasBar = true
        if (ser.type === CHART_JS_TYPE.LINE) hasLine = true
      })
      if (hasBar && hasLine) {
        if (!(isEmpty(chart.axis.x) && isEmpty(chart.axis.y))) {
          series.yAxis = yIndex
        }
      }
      if (!config.yAxis) {
        config.yAxis = []
      }
      const bins = componentConfig.bins && componentConfig.bins.length ? componentConfig.bins.map(bin => bin.alias) : []
      const yColumnAlias = createBinColumnAlias(targetSeries.data.y, `${targetSeries.id}_bin`)
      if (bins && bins.findIndex(bin => bin === yColumnAlias) !== -1) {
        let yCategories = util.buildDataChartByXYZPoint(metaData, {
          series: get(componentConfig, 'charts[0].series', [])
        }, bins)
        let positionsObj = {}
        config.yAxis[yIndex] = {
          tickPositioner: function() {
            let positions = []
            let tick = Math.floor(this.dataMin)
            let distance = yCategories.length - 1
            let increment = 0
            if (distance !== 0) {
              increment = Math.ceil((this.dataMax - this.dataMin) / distance)
            }
            if (!increment) {
              if (yCategories && yCategories.length) {
                positions[0] = this.dataMin
                positionsObj[0] = yCategories[0]
              }
            } else {
              if (this.dataMax !== null && this.dataMin !== null) {
                let catIndex = 0
                for (tick; tick <= (this.dataMax + increment); tick += increment) {
                  positions.push(tick)
                  positionsObj[tick] = yCategories[catIndex]
                  catIndex++
                }
              }
            }
            return positions
          },
          labels: { // custom label for yAxis
            formatter: function() {
              return (positionsObj[this.value] ? positionsObj[this.value] : this.value)
            }
          },
          opposite: yAxis.opposite === true || false
        }
      } else {
        let yAxisFormat = get(yAxis, `format`, null)
        if (yAxisFormat) {
          yAxis.dsFormatManager = dsFormatManager.create(yAxisFormat, false)
        }
        config.yAxis[yIndex] = {
          showLastLabel: true,
          opposite: yAxis.position === 'right' || false,
          startOnTick: true,
          title: {
            text: get(yAxis, 'scaleLabel.display', false) ? get(yAxis, 'scaleLabel.labelString', '') : ''
          },
          labels: {
            useHTML: true,
            formatter: function() {
              return `${yAxis.dsFormatManager ? yAxis.dsFormatManager(this.value) : this.value}`
            }
          }
        }
        let tickInterval = get(yAxis, 'ticks.stepSize', null)
        let tickAmount = get(yAxis, 'ticks.maxTicksLimit', null)
        if (tickInterval) config.yAxis[yIndex].tickInterval = toNumber(tickInterval)
        if (tickAmount) config.yAxis[yIndex].tickAmount = toNumber(tickAmount)
        config.yAxis = config.yAxis.map(axis => {
          axis.labels.style = { color: this.themeStyle.accentColor }
          return axis
        })
      }
    }
    if (get(config, 'xAxis.labels', null) || get(config, 'xAxis.type', '') === 'datetime') {
      config.xAxis.labels.style = { color: this.themeStyle.accentColor }
    }
  }

  getHCConfigSize(type) {
    const HC_PIE_CONFIG_SIZE = {
      pie: { size: 100, innerSize: 0 },
      doughnut: { size: 50, innerSize: 50 }
    }
    return HC_PIE_CONFIG_SIZE[type] || HC_PIE_CONFIG_SIZE['pie']
  }

  drawChart(domId, el, componentConfig, series, config, { rows, cols }, h = 100, w = 100) {
    const id = makeDOMId(CHART_LIBRARY.HIGH_CHART, domId)
    let self = this
    $(document).ready(function() {
      if (w < 100) $(el).find('.chartSets').css('display', 'flex')
      $(el).find('.chartSets')
        .append(`<div id='${id}' style='height: ${h}%; width: ${w}%'></div>`)
        .ready(function() {
          // update theme options
          let customTheme = {}
          const style = get(componentConfig, 'widget.style.foreground_color', null)
          const yAxisNum = get(config.yAxis, 'length', 1)
          if (style) {
            customTheme = self.updateColor({ color: style }, componentConfig.id, yAxisNum)
            // update yaxis
            config.yAxis = [...config.yAxis].map((axis, index) => {
              return defaultsDeep(axis, customTheme.yAxis[index])
            })
          }
          // color hight chart
          config.colors = util.getColorSchemes(componentConfig.colorScheme)
          // Build the chart
          const chartOptions = {
            ...config,
            ...{
              chart: {
                ...config.chart,
                backgroundColor: self.themeStyle.mainColor,
                events: {
                  load: function() {
                    let chart = this
                    let legend = chart.legend
                    let legendMaxWidth = Highcharts.relativeLength(legend.options.maxWidth, 1) * chart.chartWidth
                    if (legend.options.maxWidth) {
                      if (legend.legendWidth > legendMaxWidth) {
                        legend.update({
                          width: legend.options.maxWidth
                        })
                      }
                    }
                    // add right event for drill down
                    if (self.callbackObj.drillDownCallback) {
                      this.series.forEach(item => {
                        item.points.forEach(p => {
                          if (p.graphic) {
                            p.graphic.on('contextmenu', function(e) {
                              e.preventDefault()
                              const seriesIndex = item.index
                              const { data } = self.config.charts[0].series[seriesIndex]
                              const hasBin = !isEmpty(self.config.bins)
                              const column = { name: data.x }
                              const columnIndex = findIndex(cols, (col) => (col.column || col.name) === (hasBin ? createBinColumnAlias(data.x) : data.x))

                              const values = rows.find(row => (isObject(row[columnIndex]) ? row[columnIndex].label : row[columnIndex]) === (isObject(p.options.root_Data.x) ? p.options.root_Data.x.label : p.options.root_Data.x))
                              self.callbackObj.drillDownCallback({
                                column,
                                value: values[columnIndex],
                                aggregations: self.config.grouping.aggregations
                              })
                            })
                          }
                        })
                      })
                    }
                  }
                }
              }
            },
            series
          }
          console.log('config bullet', chartOptions)
          window[id] = Highcharts.chart(id, defaultsDeep(chartOptions, customTheme))
        })
    })
  }

  updateSizeChart(domId, componentConfig) {
    const { charts } = componentConfig
    const type = charts[0].series[0].type
    const isComboBarLine = charts[0].series.some(item => item.type === TYPES.BAR) && charts[0].series.some(item => item.type === TYPES.LINE)
    const isComboAreaLine = charts[0].series.some(item => item.type === TYPES.AREA) && charts[0].series.some(item => item.type === TYPES.LINE)
    //
    switch (true) {
      case isComboAreaLine:
      case isComboBarLine:
        mappingBuilder['comboBarLine'].resize(domId)
        mappingBuilder['comboAreaLine'].resize(domId)
        break
      case [TYPES.HEAT_MAP, TYPES.PIE, TYPES.BAR, TYPES.LINE, TYPES.AREA, TYPES.BULLETGAUGE, TYPES.SOLIDGAUGE].includes(type):
        mappingBuilder[type].resize(domId)
        break
    }
    // for other case
    // const id = makeDOMId(CHART_LIBRARY.HIGH_CHART, domId)
    // const el = document.querySelector(`#${id}`)
    // if (domId && window[id] && el) {
    //   try {
    //     window[id].setSize(el.clientWidth, el.clientHeight)
    //   } catch {
    //     console.log('There is no setSize function')
    //   }
    // }
  }

  updateColor(color, id, yAxisNum = 1) {
    // set theme
    const newTheme = {
      title: {
        style: {
          color: color.color
        }
      },
      subtitle: {
        style: {
          color: color.color
        }
      },
      legend: {
        itemStyle: {
          color: color.color
        },
        itemHoverStyle: {
          color: color.color
        }
      },
      xAxis: {
        tickColor: color.color,
        labels: {
          style: {
            color: color.color
          }
        },
        title: {
          style: {
            color: color.color
          }
        }
      },
      yAxis: [],
      tooltip: {
        style: {
          color: color.color
        }
      },
      plotOptions: {
        gauge: {
          dataLabels: {
            style: color.color
          }
        },
        series: {
          dataLabels: {
            style: {
              color: color.color
            }
          }
        },
        solidgauge: {
          dataLabels: {
            style: {
              color: color.color
            }
          }
        }
      }
    }
    // yAxis
    for (let i = 0; i < yAxisNum; i++) {
      newTheme.yAxis.push({
        labels: {
          style: {
            color: color.color
          }
        },
        title: {
          style: {
            color: color.color
          }
        },
        tickColor: color.color
      })
    }
    // Apply the theme
    const chartId = `hc-${id}`
    if (window[chartId]) {
      setTimeout(function() {
        window[chartId].update(newTheme)
      }, 0)
    }
    return newTheme
  }
}
