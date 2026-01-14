import { AbstractBuilder } from '@/components/widgets/elements/chart/builder/AbstractBuilder'
import dataFormatManager from '@/services/dataFormatManager'
import { COUNT_AGG, getDataAggregationFromType } from '@/services/ds/data/DataTypes'
import { SUPPORT_OPERATORS } from '@/services/ds/filter/FilterDefinitions'
import { createBinColumnAlias } from '@/utils/binUtils'
import { getStyle, mappingColumnNameToAliasNameWithGrouping } from '@/utils/chartUtil'
import HighMap from 'highcharts/modules/heatmap'
import Drilldown from 'highcharts/modules/drilldown'
import Map from 'highcharts/modules/map'
import get from 'lodash/get'
import minBy from 'lodash/minBy'
import maxBy from 'lodash/maxBy'
import cloneDeep from 'lodash/cloneDeep'
import defaultsDeep from 'lodash/defaultsDeep'
import isEmpty from 'lodash/isEmpty'
import range from 'lodash/range'
import axios from 'axios'
import { makeDOMId } from '@/components/widgets/elements/chart/types/ChartTypes'
import { CHART_LIBRARY } from '@/components/visualizationBuilder/VisualizationBuilderTypes'
import $ from 'jquery'

const __getCountriesJsFile = async (geo, geoDetail) => {
  try {
    const response = await axios.get(
      `https://code.highcharts.com/mapdata/countries/${geo}/${geoDetail}-all.js`
    )
    return response.data
  } catch (e) {
    throw new Error('Cannot fetch geo data')
  }
}

const __mapGeoLocation = (geo, geoDetail) => {
  try {
    return window.Highcharts.geojson(
      window.Highcharts.maps[`countries/${geo}/${geoDetail}-all`]
    )
  } catch (e) {
    return null
  }
}

const __fetchAndExcuse = async (geo, geoDetail) => {
  try {
    let mapData = __mapGeoLocation(geo, geoDetail)
    if (!mapData) {
      const jsFile = await __getCountriesJsFile(geo, geoDetail)
      // eslint-disable-next-line no-eval
      eval(jsFile)
      mapData = __mapGeoLocation(geo, geoDetail)
    }
    return mapData
  } catch (e) {
    console.error('Fail to fetch geo location', e)
    return []
  }
}

export class HeatMapBuilder extends AbstractBuilder {
  constructor(instance) {
    super(instance)
    // using Highcharts module
    Map(this.highcharts)
    HighMap(this.highcharts)
    Drilldown(this.highcharts)
    // map Highcharts module into window to excuse js file which download from highcharts data
    window.Highcharts = this.highcharts
  }

  // return basic config of heat map
  getBaseConfig() {
    return {
      title: {
        text: null
      },
      plotOptions: {
        mapline: {
          showInLegend: false,
          enableMouseTracking: false
        }
      }
    }
  }

  // show message when rendering
  showMessageRender(id) {
    const prefixId = makeDOMId(CHART_LIBRARY.HIGH_CHART, id)
    console.log(prefixId)
    const document = $(`#${prefixId} .chartSets`)[0]
    document.innerHTML = `<p style="text-align: center; padding: 25px; margin-bottom: 0">Rendering chart data</p>`
  }

  // build main config and data from config of element
  async buildAndRender(domId, dataSource, chartConfig, options) {
    this.showMessageRender(domId)

    const config = this.getBaseConfig()

    // build data from data of DS
    this.__cacheDataSource(domId, dataSource)

    const data = await this.__mappingDataFromDataSource(dataSource, chartConfig)

    const axis = this.__buildAxis(data.chartData, chartConfig)

    const tooltip = this.__buildTooltip(domId, dataSource, chartConfig)

    const title = this.__buildTitle(dataSource, chartConfig)

    const legend = this.__buildLegend(chartConfig)

    const mapNavigation = this.__buildMapper(chartConfig)

    const drilldownData = this.__buildDrilldown(domId, dataSource, chartConfig, options, { tooltip, axis })

    const langOptions = this.__buildLangOptions(chartConfig)

    this.__buildSeries(
      config,
      data,
      { title },
      get(chartConfig, 'charts[0].options', {})
    )

    this.__buildConfig(config, {
      axis,
      legend,
      tooltip,
      mapNavigation,
      drilldownData,
      langOptions
    })

    this.render(domId, config)
  }

  async __mappingDataFromDataSource(dataSource, chartConfig) {
    const { rows, cols } = dataSource
    const seriesItem = chartConfig.charts[0].series[0]
    const {
      // reference link: https://code.highcharts.com/mapdata/
      country: { geo, geoDetail = `${geo}-all` }
    } = seriesItem.data

    const { y } = mappingColumnNameToAliasNameWithGrouping(seriesItem, chartConfig)

    const indexY = cols.findIndex((col) => {
      return [y, createBinColumnAlias(y)].includes(col.alias || col.name)
    })

    const isDrilldownEnabled = get(chartConfig, 'drillDown.enabled')

    if (indexY === -1) throw new Error('Cannot find column')

    try {
      // find data from js file
      let mapData = await __fetchAndExcuse(geo, geoDetail)

      // convert data into map data
      const chartData = mapData.map((geo) => {
        const geoRow = rows.find((row) => row.includes(geo.name) || row.includes(geo.properties['hc-key']))
        const data = {
          code: geo.properties['hc-key'],
          name: geo.name,
          value: geoRow ? geoRow[indexY] : 0
        }
        if (isDrilldownEnabled) {
          data.drilldown = geo.properties['hc-key']
        }
        return data
      })

      return { chartData, mapData }
    } catch (e) {
      console.error(e)
      return { chartData: [], mapData: [] }
    }
  }

  __buildAxis(chartData, chartConfig) {
    const color = getStyle()

    // axis data
    const { x: xId, y: yId } = get(chartConfig, 'charts[0].series[0].axis', {})
    const { x: xAxes = [], y: yAxes = [] } = get(
      chartConfig,
      'charts[0].axis',
      {}
    )

    let isHorizontal = get(chartConfig, 'charts[0].options.legend.isHorizontal', true)
    // eslint-disable-next-line no-unused-vars
    const xAxis = xAxes.find((axis) => axis.id === xId)
    const yAxis = yAxes.find((axis) => axis.id === yId)

    const { value: minValue } = minBy(chartData, 'value') || { value: 0 }
    const { value: maxValue } = maxBy(chartData, 'value') || { value: 0 }

    const min = minValue < 0 ? minValue : 0
    const max = maxValue === minValue ? minValue + 1 : maxValue

    // checking min, max data
    const minColor = get(yAxis, 'ticks.minColor', '#F1EEF6')
    const maxColor = get(yAxis, 'ticks.maxColor', '#500007')
    const axisGirdColor = get(yAxis, 'axisGridColor', '#000000')
    const axisLabelColor = get(yAxis, 'axisLabelColor', color.accentColor)
    const yFormatter = yAxis.format ? dataFormatManager.create(yAxis.format, true) : null

    return {
      min,
      max,
      minColor,
      maxColor,
      gridLineColor: axisGirdColor,
      labels: {
        align: isHorizontal === true ? 'right' : 'left',
        style: {
          color: axisLabelColor
        },
        formatter: function() {
          return yFormatter ? yFormatter(this.value) : this.value
        }
      }
    }
  }

  __buildMapper(chartConfig) {
    return {
      enabled: get(chartConfig, 'charts[0].options.mapNavigation.enabled', true),
      enableMouseWheelZoom: get(chartConfig, 'charts[0].options.mapNavigation.enableMouseWheelZoom', false)
    }
  }

  __buildLegend(chartConfig) {
    const {
      enabled = true,
      isHorizontal = true,
      position = 'right'
    } = get(chartConfig, 'charts[0].options.legend', {})

    return {
      enabled,
      layout: isHorizontal ? 'horizontal' : 'vertical',
      align: position
    }
  }

  __buildTooltip(domId, dataSource, chartConfig) {
    const instance = this
    const { data: { x, y, tooltip }, id } = get(chartConfig, 'charts[0].series[0]')

    const columnX = get(chartConfig, 'columns', []).find(column => column.name === x)
    const columnY = get(chartConfig, 'columns', []).find(column => column.name === y)
    const columnsTooltip = get(chartConfig, 'columns', []).filter(column => get(tooltip, 'columns', []).includes(column.name))

    if (!columnY || !columnX) return {}

    const yFormatter = columnY.format ? dataFormatManager.create(columnY.format, true) : null
    const xFormatter = columnX.format ? dataFormatManager.create(columnX.format, true) : null
    const tooltipFormatters = columnsTooltip.map(column => {
      return column.format ? dataFormatManager.create(column.format, false) : null
    })

    return {
      shared: true,
      useHTML: true,
      headerFormat: '',
      formatter: function() {
        let template = get(tooltip, 'template')
        const ds = instance.__getCacheDataSource(domId)
        const seriesName = this.series.name
        const code = this.point.code || this.point.properties['hc-key']
        const name = xFormatter ? xFormatter(this.point.name) : this.point.name
        const value = yFormatter ? yFormatter(this.point.value) : this.point.value

        // build tooltip data
        const indexTooltips = columnsTooltip.map(col => ds.cols.findIndex((dsCol) => dsCol.name.includes(col.name) && dsCol.name.includes(id)))
        const rowIndex = ds.rows.findIndex(row => row.includes(code))
        const rowValues = ds.rows[rowIndex] || range(ds.cols.length).map(() => 0) // default value if code is not existed
        const tooltipValues = rowValues
          .filter((v, i) => indexTooltips.includes(i))
          .map((v, i) => {
            const format = tooltipFormatters[i]
            return format ? format(v) : v
          })

        // empty tooltip template
        if (!template) return `${name} : ${value}`

        const xName = columnX.name
        const yName = columnY.name

        // for template tooltip
        template = template
          .replace('$series_name', seriesName)
          .replace(`$${xName}`, name)
          .replace(`$${yName}`, value)

        tooltipValues.forEach((v, i) => {
          template = template.replace(`$${columnsTooltip[i].name}`, v)
        })

        return template
      }
    }
  }

  __buildTitle({ cols }, chartConfig) {
    const { data, name } = get(chartConfig, 'charts[0].series[0]')

    if (name) return name

    const { x, y } = data
    const currentXColumn = get(chartConfig, 'columns', []).find((col) =>
      [createBinColumnAlias(x), x].includes(col.name)
    )
    const currentAggregation = get(
      chartConfig,
      'grouping.aggregations',
      []
    ).find(aggr => [createBinColumnAlias(y), y].includes(aggr.column))

    if (!currentXColumn) {
      throw new Error('You must provide column in chart config')
    }

    return currentAggregation
      ? `${currentXColumn.displayName || x} (${getDataAggregationFromType(currentAggregation.aggregation).label})`
      : `${currentXColumn.displayName || x}`
  }

  __buildLangOptions(chartConfig) {
    const labelDrillUpButton = get(chartConfig, 'charts[0].options.labelDrillUpButton', null)

    // set label for drill up button
    return {
      drillUpText: '◁ ' + (labelDrillUpButton || 'Back to {series.name}')
    }
  }

  __buildSeries(config, { chartData, mapData }, { title }, { gridBorderColor, dataLabelColor }) {
    const color = getStyle()

    config.series = [
      {
        mapData: mapData,
        data: chartData.map(data => { data.borderColor = (gridBorderColor || '#000000'); return data }),
        joinBy: ['hc-key', 'code'],
        name: title,
        borderWidth: 0.5,
        dataLabels: {
          enabled: true,
          format: '{point.properties.postal-code}',
          color: dataLabelColor || color.accentColor
        }
      }
    ]
  }

  __buildConfig(config, { axis, legend, mapNavigation, tooltip, drilldownData, langOptions }) {
    const color = getStyle()

    defaultsDeep(config, {
      colorAxis: axis,
      legend,
      tooltip,
      mapNavigation,
      chart: {
        backgroundColor: color.mainColor
      }
    })

    if (drilldownData) {
      defaultsDeep(config, {
        chart: {
          events: {
            // about 2 options drilldown and drillup
            ...drilldownData.events
          }
        },
        drilldown: drilldownData.drillDown
      })
    }

    this.highcharts.setOptions({
      lang: langOptions
    })
  }

  __buildDrilldown(domId, dataSource, chartConfig, { mainQuery }, config) {
    if (!get(chartConfig, 'drillDown.enabled') || !get(chartConfig, 'drillDown.path.settings.length')) return null
    const instance = this

    const color = getStyle()
    const dataLabelColor = get(chartConfig, 'charts[0].options.dataLabelColor', color.accentColor)

    const drillDown = {
      activeDataLabelStyle: {
        color: dataLabelColor || color.accentColor,
        textDecoration: 'none',
        textOutline: '1px #ffffff'
      },
      drillUpButton: {
        relativeTo: 'spacingBox',
        position: {
          x: 0,
          y: 60
        }
      }
    }

    const events = {
      drilldown: async function(e) {
        if (!e.seriesOptions) {
          // Show the spinner
          this.showLoading('<i class="fa fa-circle-o-notch fa-spin"></i>')

          // build query
          const query = instance.__buildDrilldownQuery(e.point, chartConfig, mainQuery)
          // build new config
          const newChartConfig = instance.__buildDrilldownConfig(e.point, chartConfig, query)

          try {
            const dataSource = await window.CBPO.dsManager().getDataSource(chartConfig.dataSource).query(query)
            const { chartData, mapData } = await instance.__mappingDataFromDataSource(dataSource, newChartConfig)
            const axis = instance.__buildAxis(chartData, newChartConfig)

            // cache data source for tooltip builder
            instance.__cacheDataSource(domId, dataSource)

            if (!mapData.length) throw new Error('Invalid drilldow data')

            // map chart data into map data to keep tooltip
            mapData.forEach((data, i) => { data.value = chartData[i].value })

            // add new series
            this.addSeriesAsDrilldown(e.point, {
              name: e.point.name,
              data: mapData,
              axis,
              dataLabels: {
                enabled: true,
                format: '{point.name}',
                color: dataLabelColor || color.accentColor
              }
            })
            // update axis
            this.colorAxis[0].update(axis)
          } catch (e) {
            console.error('Fail to fetch data drill down', e)
          } finally {
            this.hideLoading()
          }
          // Load the drilldown map
        }
      },
      drillup: function() {
        instance.__cacheDataSource(domId, dataSource)
        this.colorAxis[0].update(cloneDeep(config.axis))
      }
    }

    return { events, drillDown }
  }

  __buildDrilldownQuery(point, chartConfig, query) {
    const clone = cloneDeep(query)
    const { x, y } = chartConfig.charts[0].series[0].data
    const [ path ] = chartConfig.drillDown.path.settings
    const yAggregation = query.group.aggregations.find(aggr => aggr.column === y)
    const otherAggregations = query.group.aggregations.filter(aggr => aggr.column !== y)

    // build filter
    const filter = {
      type: 'AND',
      conditions: [
        {
          column: x,
          operator: SUPPORT_OPERATORS.$eq.value,
          value: point.code
        }
      ]
    }

    const group = {
      columns: [ { name: path.column } ],
      aggregations: [
        {
          column: y,
          aggregation: yAggregation ? yAggregation.aggregation : COUNT_AGG.aggregation,
          alias: `${y}_${yAggregation ? yAggregation.aggregation : COUNT_AGG.aggregation}_${chartConfig.charts[0].series[0].id}`
        },
        ...otherAggregations
      ]
    }

    // add new filter
    if (isEmpty(clone.filter)) {
      clone.filter = filter
    } else {
      clone.filter.conditions.push(filter)
    }

    // replace group
    clone.group = group

    // replace order
    clone.orders.map(column => {
      if (column.column === x) {
        column.column = path.column
      }
    })

    return clone
  }

  __buildDrilldownConfig(point, chartConfig, query) {
    const clone = cloneDeep(chartConfig)
    // grouping
    clone.grouping = { ...query.group }
    // filter
    clone.filter = { ...query.filter }
    // change geo
    clone.charts[0].series[0].data.country.geoDetail = point.code

    return clone
  }

  __cacheDataSource(id, dataSource) {
    window[`series_${id}`] = dataSource
  }

  __getCacheDataSource(id) {
    return window[`series_${id}`]
  }
}

export const GEO_LOCATION_SUPPORTS = [
  { label: 'US', value: 'us' },
  { label: 'Canada', value: 'ca' }
]

export const GEO_DETAIL_LOCATION_SUPPORTS = {
  us: [
    { label: 'All', value: 'us-all' },
    { label: 'States', value: 'us' }
  ],
  ca: [
    { label: 'All', value: 'ca' }
  ]
}
