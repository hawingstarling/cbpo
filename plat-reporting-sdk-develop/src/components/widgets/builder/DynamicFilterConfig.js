import _ from 'lodash'
import { SUPPORT_LOGIC } from '@/utils/filterUtils'
import { generateIdIfNotExist } from '@/utils/configUtil.js'

const defaultTreeNode = {
  id: null,
  level: 0,
  column: '',
  value: '',
  operator: ''
}

const defaultFormColumnInputConfig = {
  name: '',
  operator: '$eq',
  value: ''
}

const defaultFormColumnSelectConfig = {
  name: '',
  options: []
}

export const defaultTreeGroup = {
  id: null,
  level: 0,
  type: SUPPORT_LOGIC.AND,
  conditions: []
}

export const defaultFilterConfig = {
  trigger: {
    label: 'Setting Filter'
  },
  modal: {
    title: 'Query Builder'
  },
  format: {
    temporal: {}
  },
  threshold: {
    maxLevel: 5
  },
  ignore: {
    global: {
      visible: false,
      value: false
    },
    base: {
      visible: false,
      value: false
    }
  },
  query: _.cloneDeep(defaultTreeGroup),
  form: {
    columns: [
      // Integration Part
      // { name: `name`, type: 'select', options: [ { text: 'Text', value: 'Value' } ] }
    ]
  }
}

export const getDefaultNode = (level = 0) => {
  let node = _.cloneDeep(defaultTreeNode)
  node.level = level + 1
  generateIdIfNotExist(node)
  return node
}

export const getDefaultGroup = (level = 0) => {
  let group = _.cloneDeep(defaultTreeGroup)
  group.level = level + 1
  generateIdIfNotExist(group)
  return group
}

export const makeDefaultValueOptions = (defaultNodes = []) => {
  return defaultNodes
    .filter(column => ['input', 'select'].includes(column.type))
    .filter(column => {
      if (column.type === 'input') return !!column.operator
      return column
    })
    .map(column => {
      switch (column.type) {
        case 'input':
          _.defaultsDeep(column, defaultFormColumnInputConfig)
          break
        case 'select':
          _.defaultsDeep(column, defaultFormColumnSelectConfig)
          break
      }
      return column
    })
}

export const makeFilterControlDefaultConfig = filterConfig => {
  _.defaultsDeep(filterConfig, defaultFilterConfig)
  filterConfig.form.columns = makeDefaultValueOptions(filterConfig.form.columns)
  filterConfig.format.temporal = {
    date: {
      type: 'date',
      formatValue: 'YYYY-MM-DD',
      formatLabel: 'MM/DD/YYYY'
    },
    datetime: {
      type: 'datetime',
      formatValue: 'YYYY-MM-DDTHH:mm:ss',
      formatLabel: 'MM/DD/YYYY hh:mm:ss A'
    }
  }
}
