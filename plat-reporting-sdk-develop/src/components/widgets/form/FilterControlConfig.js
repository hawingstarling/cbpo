import { SUPPORT_OPERATORS, OPTION_DEFAULT_SELECT_RANGE } from '@/services/ds/filter/FilterDefinitions'
import defaultsDeep from 'lodash/defaultsDeep'
import cloneDeep from 'lodash/cloneDeep'
import get from 'lodash/get'

export const CONTROL_TYPE = {
  AUTO: 'cbpo-filter-control-auto',
  INPUT: 'cbpo-filter-control-input',
  SELECT: 'cbpo-filter-control-select',
  RANGE: 'cbpo-filter-control-range',
  DATE_RANGE: 'cbpo-filter-control-range-select'
}
export const defaultSelectControlConfig = {
  common: {
    column: {
      name: null,
      type: null
    },
    operator: '==',
    options: {
      // for date_in operator only
      format: {
        start: 'YYYY-MM-DDT00:00:00Z',
        end: 'YYYY-MM-DDT23:59:59Z'
      }
    },
    value: undefined
  },
  label: {
    text: ''
  },
  dataSource: null,
  selection: {
    empty: {
      label: 'Please select',
      enabled: true,
      isEmptySelected: true
    },
    format: null,
    sort: 'asc',
    // option ({label, value})
    options: [],
    ignoreValues: []
  },
  infiniteScroll: {
    enable: false,
    limit: 30
  }
}

export const defaultInputControlConfig = {
  common: {
    column: {
      name: null,
      type: null
    },
    operator: '==',
    value: undefined
  },
  label: {
    text: ''
  },
  input: {
    format: null
  }
}

export const defaultTextAreaControlConfig = {
  common: {
    column: {
      name: null,
      type: null
    },
    operator: '==',
    value: undefined
  },
  label: {
    text: ''
  }
}

export const defaultInRangeControlConfig = {
  common: {
    column: {
      name: null,
      type: null
    },
    operator: SUPPORT_OPERATORS.in_range.value,
    value: [undefined, undefined]
  },
  label: {
    text: ''
  },
  range: {
    type: 'date',
    formatLabel: 'MM/DD/YYYY',
    formatValue: 'YYYY-MM-DD'
  }
}

export const defaultInRangeSelectControlConfig = {
  common: {
    column: {
      name: null,
      type: null
    },
    operator: SUPPORT_OPERATORS.in_range.value,
    value: [undefined, undefined]
  },
  label: {
    text: ''
  },
  range: {
    type: 'date',
    formatLabel: 'MM/DD/YYYY',
    formatValue: 'YYYY-MM-DD',
    visible: true
  },
  selection: {
    empty: {
      label: 'Select Date Range',
      enabled: true,
      isEmptySelected: true,
      isDefaultOption: true
    },
    sort: 'asc',
    options: OPTION_DEFAULT_SELECT_RANGE.map(option => {
      if (option.isDefault === undefined) option.isDefault = false
      return option
    })
  }
}

export const makeDefaultSelectControlConfig = selectConfig => {
  let config = defaultsDeep(selectConfig, defaultSelectControlConfig)
  return cloneDeep(config)
}

export const makeDefaultInputControlConfig = selectConfig => {
  let config = defaultsDeep(selectConfig, defaultInputControlConfig)
  return cloneDeep(config)
}

export const makeDefaultTextAreaControlConfig = selectConfig => {
  let config = defaultsDeep(selectConfig, defaultTextAreaControlConfig)
  return cloneDeep(config)
}

export const makeDefaultInRangeControlConfig = selectConfig => {
  let config = defaultsDeep(selectConfig, defaultInRangeControlConfig)
  config.common.operator = selectConfig.common.operator
  return cloneDeep(config)
}

export const makeDefaultInRangeSelectControlConfig = selectConfig => {
  let rangeOptions = cloneDeep(get(selectConfig, 'selection.options', []))
  let config = defaultsDeep(selectConfig, defaultInRangeSelectControlConfig)
  if (rangeOptions.length > 0) {
    config.selection.options = rangeOptions
  }
  config.common.operator = SUPPORT_OPERATORS.in_range.value
  return cloneDeep(config)
}

export const buildSpecialValuesKey = array => {
  return array.join('_****_$_****_')
}
