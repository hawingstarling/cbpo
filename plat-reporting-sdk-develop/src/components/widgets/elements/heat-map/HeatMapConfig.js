import { CHART_LIBRARY } from '@/components/visualizationBuilder/VisualizationBuilderTypes'
import { DEFAULT_PAGINATION_CONFIG } from '@/components/widgets/elements/table/pagination/PaginationConfig'
import { DEFAULT_WIDGET_TITLE_CONFIG } from '@/components/widgets/title/WidgetTitleConfig'
import cloneDeep from 'lodash/cloneDeep'
import defaultsDeep from 'lodash/defaultsDeep'
import { defaultTimezone } from '@/utils/timezoneUtil'

export const defaultConfig = {
  widget: defaultsDeep({ title: { enabled: false } }, cloneDeep(DEFAULT_WIDGET_TITLE_CONFIG)),
  columns: [],
  drillDown: {
    enabled: false,
    path: {
      settings: []
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
  pagination: defaultsDeep({limit: 99999}, DEFAULT_PAGINATION_CONFIG),
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

export const makeDefaultHeatMapConfig = (config) => {
  defaultsDeep(config, defaultConfig)
  config.library = CHART_LIBRARY.HIGH_CHART
  defaultTimezone(config)
  return config
}
