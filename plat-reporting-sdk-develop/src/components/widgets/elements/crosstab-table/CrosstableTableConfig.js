import cloneDeep from 'lodash/cloneDeep'
import defaultsDeep from 'lodash/defaultsDeep'
import { DEFAULT_PAGINATION_CONFIG } from '../table/pagination/PaginationConfig'
import { DEFAULT_WIDGET_TITLE_CONFIG } from '@/components/widgets/title/WidgetTitleConfig'
import _ from 'lodash'
import { DEFAULT_OPTIONS_CONFIG } from '@/components/widgets/elements/table/grouping/ColumnSettingsConfig'
import { defaultTimezone } from '@/utils/timezoneUtil'

export const DEFAULT_CROSSTAB_TABLE_CONFIG = {
  dataSource: '',
  sizeSettings: {
    defaultMinSize: 250,
    warningText: 'The area is too small for this visualization.'
  },
  widget: cloneDeep(DEFAULT_WIDGET_TITLE_CONFIG),
  messages: {
    no_data_at_all: 'No data',
    no_data_found: 'No data found'
  },
  globalControlOptions: _.defaultsDeep({}, DEFAULT_OPTIONS_CONFIG),
  bins: [],
  formats: {
    aggrs: {}
  },
  sorting: [],
  xColumns: [],
  tColumns: [],
  yColumns: [],
  pagination: defaultsDeep({limit: 10}, cloneDeep(DEFAULT_PAGINATION_CONFIG)),
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

export const DEFAULT_CROSSTAB_COLUMN_CONFIG = {
  name: '',
  displayName: '',
  format: null,
  sort: {
    enabled: true,
    direction: null
  }
}

export const makeCrosstabTableDefaultConfig = (config) => {
  let callbackDefaultColumn = (column) => {
    defaultsDeep(column, DEFAULT_CROSSTAB_COLUMN_CONFIG)
    return column
  }
  defaultsDeep(config, DEFAULT_CROSSTAB_TABLE_CONFIG)
  config.xColumns = config.xColumns.map(callbackDefaultColumn)
  config.tColumns = config.tColumns.map(callbackDefaultColumn)
  config.yColumns = config.yColumns.map(callbackDefaultColumn)
  defaultTimezone(config)
}
