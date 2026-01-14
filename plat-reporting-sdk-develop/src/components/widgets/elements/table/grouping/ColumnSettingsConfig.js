import _ from 'lodash'
export const OPTIONS = {
  AGGREGATION: 'aggregation',
  GLOBAL_GROUPING: 'globalGrouping',
  GLOBAL_GROUPING_VALUE: 'globalGroupingValue',
  GROUPING: 'grouping',
  EDIT_COLUMN: 'editColumn',
  EDIT_COLUMN_LABEL: 'editColumnLabel',
  EDIT_COLUMN_FORMAT: 'editColumnFormat',
  EDIT_BIN: 'editBin'
}

export const DEFAULT_STATE_BIN = {
  null: {
    binningType: null
  },
  auto_numeric: {
    binningType: 'auto',
    nice: true,
    expected: 5
  },
  uniform_numeric: {
    binningType: 'uniform',
    nice: true,
    width: 5
  },
  auto_temporal: {
    binningType: 'auto',
    expected: 5
  },
  uniform_temporal: {
    binningType: 'uniform',
    width: 1,
    unit: 'M'
  }
}

export const LIST_UNIT = [
  { value: 'Y', text: 'Year' },
  { value: 'Q', text: 'Quarter' },
  { value: 'M', text: 'Month' },
  { value: 'W', text: 'Week' },
  { value: 'd', text: 'Day' },
  { value: 'm', text: 'Minute' }
]

export const BINNING_TYPES = [
  { value: null, text: 'No Binning' },
  { value: 'auto', text: 'Auto' },
  { value: 'uniform', text: 'Uniform' }
]

export const DEFAULT_OPTIONS_CONFIG = {
  aggregation: {
    enabled: false
  },
  globalGrouping: {
    enabled: false,
    config: {
      value: false
    },
    position: 'top'
  },
  grouping: {
    enabled: false
  },
  editColumn: {
    enabled: false
  },
  editColumnLabel: {
    enabled: false
  },
  editColumnFormat: {
    enabled: false
  },
  editBin: {
    enabled: false
  }
}

export const defaultColumnSettingsConfig = {
  ...DEFAULT_OPTIONS_CONFIG
}

export const makeColumnSettingsDefaultConfig = (columnSettingsConfig) => {
  _.defaultsDeep(columnSettingsConfig, defaultColumnSettingsConfig)
}
