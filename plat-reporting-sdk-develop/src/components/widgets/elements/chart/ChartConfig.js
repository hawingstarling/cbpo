/**
 * This file contains chart component configuration utilities.
 * NOT chart library configuration in the ChartLibConfig.
 */
import precond from 'precond'
import defaultsDeep from 'lodash/defaultsDeep'
import cloneDeep from 'lodash/cloneDeep'
import get from 'lodash/get'
import { DEFAULT_WIDGET_TITLE_CONFIG } from '@/components/widgets/title/WidgetTitleConfig'
import { defaultTimezone } from '@/utils/timezoneUtil'

export const TYPES = {
  PIE: 'pie',
  BAR: 'bar',
  LINE: 'line',
  SCATTER: 'scatter',
  AREA: 'area',
  MIXIN: 'mixins',
  PARETO: 'pareto',
  BUBBLE: 'bubble',
  BULLETGAUGE: 'bulletgauge',
  SOLIDGAUGE: 'solidgauge',
  HEAT_MAP: 'heat-map'
}

export const CHART_JS_TYPE = {
  PIE: 'pie',
  BAR: 'bar',
  LINE: 'line',
  SCATTER: 'scatter',
  AREA: 'area',
  DOUGHNUT: 'doughnut',
  HORIZONTAL_BAR: 'horizontalBar',
  BUBBLE: 'bubble'
}

export const HC_TYPES = {
  SPLINE: 'spline',
  PIE: 'pie',
  COLUMN: 'column',
  BAR: 'bar',
  AREASPLINE: 'areaspline',
  SCATTER: 'scatter',
  BUBBLE: 'bubble',
  BULLETGAUGE: 'bullet',
  SOLIDGAUGE: 'solidgauge'
}

export const colorSchemes = {
  D3_10: 'D3_10',
  D3_20: 'D3_20',
  D3_30: 'D3_30',
  SC_1: 'SC_1',
  Google: 'Google'
}

const DEFAULT_PAGINATION_CONFIG = {
  limit: 1000,
  current: 1,
  type: 'buttons'
}

const defaultChartConfig = {
  widget: defaultsDeep({ title: { enabled: false } }, cloneDeep(DEFAULT_WIDGET_TITLE_CONFIG)),
  library: 'highcharts', // 'highcharts', // default chartjs for now, it should be CBPO in the future
  columns: [],
  drillDown: {
    enabled: false,
    config: {
    }
  },
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
  bins: [],
  pagination: defaultsDeep({}, DEFAULT_PAGINATION_CONFIG),
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
  timezone: {
    enabled: false,
    utc: null, // String value from moment().tz.names() list | abbr. maybe not accurate in some cases
    /* https://github.com/dmfilipenko/timezones.json */
    visible: true // show timezone select box
  },
  exportConfig: {
    polling: true, // false mean export is triggered and response is returned immediately in a single request
    pollingInterval: 2000 // interval between successive polling requests (in ms)
    // Note: Use polling=true for large exports that may take time to process
    // Use polling=false for small exports where immediate response is expected
  }
}

export const makeDefaultChartConfig = (chartConfig) => {
  precond.checkIsObject(chartConfig, 'Config needs to be an object')
  defaultsDeep(chartConfig, defaultChartConfig)
  if (chartConfig.charts[0]) {
    let isPie = get(chartConfig.charts[0], 'series', []).every(item => item.type === TYPES.PIE)
    let isScatter = get(chartConfig.charts[0], 'series', []).every(item => item.type === TYPES.SCATTER)
    if (isScatter) {
      chartConfig.bins = []
    }
    chartConfig.charts[0] = defaultsDeep(chartConfig.charts[0], {
      options: {
        series: {
          limit: 1000
        },
        legend: {
          widthPercent: 30,
          position: isPie ? 'right' : 'bottom',
          enabled: true
        }
      }
    })
  }
  defaultTimezone(chartConfig)
  return chartConfig
}
