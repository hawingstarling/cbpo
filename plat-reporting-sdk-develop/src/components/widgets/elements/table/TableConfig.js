import _ from 'lodash'
import { DEFAULT_PAGINATION_CONFIG } from './pagination/PaginationConfig'
import { DEFAULT_OPTIONS_CONFIG } from './grouping/ColumnSettingsConfig'
import { DEFAULT_WIDGET_TITLE_CONFIG } from '@/components/widgets/title/WidgetTitleConfig'
import defaultCommonConfig from '@/services/dataFormats/commonFormatConfig'
import uuidv4 from 'uuid'
import { defaultTimezone } from '@/utils/timezoneUtil'

export const COMPACT_MODE = {
  NORMAL: 'normal',
  HIGH: 'high'
}

export const COMPACT_MODE_HEIGHT = {
  NORMAL: 32,
  HIGH: 20
}

export const BULK_ACTION_MODE = {
  CHECKBOX: 'checkbox',
  INLINE: 'inline',
  BOTH: 'both'
}

export const defaultTableConfig = {
  styles: {
    beautyScrollbar: false
  },
  header: {
    resizeMinWidth: null,
    multiline: false,
    draggable: false,
    sticky: false
  },
  drillDown: {
    enabled: false,
    config: {}
  },
  columns: [],
  sorting: [],
  widget: _.cloneDeep(DEFAULT_WIDGET_TITLE_CONFIG),
  sizeSettings: {
    defaultMinSize: 250,
    warningText: 'The area is too small for this visualization.'
  },
  globalControlOptions: _.defaultsDeep({}, DEFAULT_OPTIONS_CONFIG),
  grouping: {
    columns: [],
    aggregations: []
  },
  bins: [],
  pagination: _.defaultsDeep({}, DEFAULT_PAGINATION_CONFIG),
  formats: {
    binFormats: {
      // bin format configuration
    },
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
  compactMode: {
    enabled: false,
    mode: COMPACT_MODE.NORMAL // [ normal | high ] // (default is 'normal')
  },
  rowActions: {
    enabled: false,
    inline: 1, // number of inline item, else -> dropdown
    display: 'always', // always | onhover
    position: 'left', // left of row or right of row, for now just handle left, default: left
    colWidth: 150,
    controls: [],
    eventHandler: function(eventName, data) {
    }
  },
  bulkActions: {
    enabled: false,
    enableInlineAction: true,
    mode: BULK_ACTION_MODE.CHECKBOX,
    filterMode: false,
    total: 0,
    labels: {
      actionColumn: 'Actions',
      selectAll: 'Select all $total items',
      allSelected: 'All $total items selected'
    },
    controls: []
  },
  detailView: {
    enabled: false,
    mode: 'inline',
    action: {
      breakpoint: 768,
      props: { size: 'sm', variant: 'primary' },
      icons: {
        closed: 'fa-arrow-circle-o-down',
        opened: 'fa-arrow-circle-o-right'
      },
      label: 'View'
    },
    breakpoints: {
      1024: 3,
      768: 2,
      320: 1
    }
  },
  globalSummary: {
    enabled: false,
    summaries: []
  },
  tableSummary: {
    enabled: false, // default false
    position: 'footer', // header | footer | both
    labelActionColumn: 'Summary', // label of action column
    summaries: []
  },
  exportConfig: {
    query: {},
    polling: true, // false mean export is triggered and response is returned immediately in a single request
    pollingInterval: 2000 // interval between successive polling requests (in ms)
    // Note: Use polling=true for large exports that may take time to process
    // Use polling=false for small exports where immediate response is expected
  }
}

export const defaultColumnConfig = {
  header: {
    style: {
    },
    format: null
  },
  cell: {
    width: 100,
    style: {
    },
    computeClass: (value) => {},
    format: null,
    // aggregation formats (like sum, count, etc)
    aggrFormats: null,
    binFormats: null
  },
  sortable: {
    enabled: true
  },
  visible: true,
  detailColIndex: 0,
  isUniqueKey: false
}

export const defaultSummaryConfig = {
  label: '',
  format: null,
  expr: '',
  prefix: '',
  suffix: '',
  noDataMessage: 'No data',
  style: {}
}

export const defaultColumnSummaryConfig = {
  label: '',
  style: {},
  column: '',
  format: null,
  expr: '',
  noDataMessage: 'No data'
}

export const defaultFormatConfig = {
  common: _.cloneDeep(defaultCommonConfig),
  type: '',
  config: {}
}

export const makeTableDefaultConfig = (tableConfig) => {
  _.defaultsDeep(tableConfig, defaultTableConfig)
  // default column config
  tableConfig.columns.forEach((col) => {
    _.defaultsDeep(col, defaultColumnConfig)
  })
  // update id
  tableConfig.globalSummary.summaries.forEach((sum) => {
    if (!sum.id) sum.id = uuidv4()
    _.defaultsDeep(sum, defaultSummaryConfig)
  })
  // default summaries
  tableConfig.tableSummary.summaries.forEach((sum) => {
    if (!sum.id) sum.id = uuidv4()
    _.defaultsDeep(sum, defaultColumnSummaryConfig)
  })
  // default utc
  defaultTimezone(tableConfig)

  return tableConfig
}
