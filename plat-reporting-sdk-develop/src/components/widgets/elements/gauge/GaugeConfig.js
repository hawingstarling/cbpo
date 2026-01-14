/**
 * This file contains chart component configuration utilities.
 * NOT chart library configuration in the ChartLibConfig.
 */
import precond from 'precond'
import { CHART_LIBRARY } from '@/components/visualizationBuilder/VisualizationBuilderTypes'
import _ from 'lodash'

const colorSchemes = {
  D3_10: 'D3_10',
  D3_20: 'D3_20',
  Google: 'Google'
}

const DEFAULT_PAGINATION_CONFIG = {
  limit: 5000,
  current: 1,
  type: 'buttons'
}

const defaultGaugeConfig = {
  library: CHART_LIBRARY.HIGH_CHART,
  columns: [],
  sizeSettings: {
    defaultMinSize: 250,
    warningText: 'The area is too small for this visualization.'
  },
  charts: [],
  sorting: [],
  grouping: {
    columns: [],
    aggregations: []
  },
  pagination: Object.assign({}, DEFAULT_PAGINATION_CONFIG),
  color_scheme: colorSchemes.Google,
  formats: {
    aggrs: {
      // aggregations format configuration
    }
  },
  messages: {
    no_data_at_all: 'No data',
    no_data_found: 'No data found'
  },
  exportConfig: {
    polling: true, // false mean export is triggered and response is returned immediately in a single request
    pollingInterval: 2000 // interval between successive polling requests (in ms)
    // Note: Use polling=true for large exports that may take time to process
    // Use polling=false for small exports where immediate response is expected
  }
}

const calculateGauge = (data) => {
  let g2 = _.toNumber(_.toNumber((1.4) * data).toFixed(2))
  let g1 = _.toNumber(_.toNumber(g2 * 0.65).toFixed(2))
  let g0 = _.toNumber(_.toNumber(g2 * 0.35).toFixed(2))
  return [g0, g1, g2]
}

export const makeDefaultBulletGaugeConfig = (element, value, seriesItem) => {
  let data = calculateGauge(value)
  let seriesIndex = _.findIndex(element.config.charts[0].series, e => e.id === seriesItem.id)
  let yIndex = _.findIndex(element.config.charts[0].axis.y, e => e.id === seriesItem.axis.y)
  let aggregationIndex = _.findIndex(element.config.grouping.aggregations, e => e.alias.includes(seriesItem.id))
  let {column, aggregation} = element.config.grouping.aggregations[aggregationIndex]
  // default plotBands
  element.config.charts[0].options.isHorizontal = true
  element.config.charts[0].series[seriesIndex].options.title = `${column} (${aggregation})`
  element.config.charts[0].axis.y[yIndex].plotBands = [{
    from: 0,
    to: data[0],
    color: '#666'
  }, {
    from: data[0],
    to: data[1],
    color: '#999'
  }, {
    from: data[1],
    to: data[2],
    color: '#bbb'
  }]
}

export const makeDefaultSolidGaugeConfig = (element, value, seriesItem) => {
  let data = calculateGauge(value)
  let seriesIndex = _.findIndex(element.config.charts[0].series, e => e.id === seriesItem.id)
  let yIndex = _.findIndex(element.config.charts[0].axis.y, e => e.id === seriesItem.axis.y)
  let aggregationIndex = _.findIndex(element.config.grouping.aggregations, e => e.alias.includes(seriesItem.id))
  let {column, aggregation} = element.config.grouping.aggregations[aggregationIndex]
  element.config.charts[0].series[seriesIndex].options.subtitle = `${column} (${aggregation})`
  element.config.charts[0].series[seriesIndex].options.size = 25
  element.config.charts[0].axis.y[yIndex].max = data[2]
  element.config.charts[0].axis.y[yIndex].stops = [
    [data[0], '#55BF3B'],
    [data[1], '#DDDF0D'],
    [data[2], '#DF5353']
  ]
}

export const makeDefaultGaugeConfig = (gaugeConfig) => {
  precond.checkIsObject(gaugeConfig, 'Config needs to be an object')
  _.defaultsDeep(gaugeConfig, defaultGaugeConfig)
}
