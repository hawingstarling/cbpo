import _ from 'lodash'
import moment from 'moment'
import { COLUMN_NAME_MAPPING } from '@/shared/constants/column.constant'

export const filterColumnName = function (str) {
  return str ? COLUMN_NAME_MAPPING[str] || str.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ') : ''
}

export const orderColumn = (listColumn) => {
  let listBeforeMap = _.cloneDeep(listColumn)
  let mappedList = []
  let arrayKey = Object.keys(COLUMN_NAME_MAPPING)
  _.forEach(arrayKey, key => {
    let column = _.find(listBeforeMap, item => {
      return item.name === key
    })
    if (column) {
      mappedList.push(column)
    } else {
      console.error(`Invalid column ${key}, it's often when the column is in configuration but not returned from data source`)
    }
  })
  return mappedList
}

export const numeral = (number) => {
  return number ? number.toString().replace(/(\d)(?=(\d\d\d)+(?!\d))/g, '$1,') : 0
}

export const formatCurrency = (value) => {
  if (String(value).includes('%')) return value
  if (isInvalidNumber(value)) return '-'
  const num = parseFloat(String(value).replace(/[$,]/g, ''))
  const isNegative = num < 0
  const formattedValue = Math.abs(num).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
  return `${isNegative ? '-' : ''}$${formattedValue}`
}
export const formatPercent = (value) => {
  if (String(value).includes('%')) return value
  return isInvalidNumber(value) ? '-' : `${parseFloat(value).toFixed(2)}%`
}

export const formatNumber = (value) => {
  if (String(value).includes('%')) return value
  return (isInvalidNumber(value)) ? '-' : new Intl.NumberFormat('en-US').format(Number(value))
}

export const isInvalidNumber = (value) => {
  return value === null || (typeof value === 'string' && value.trim() === '') || isNaN(Number(value))
}

export const formatDate = (value, format = 'DD-MM-YYYY') => {
  if (!value) return value
  const m = moment(value)
  if (!m.isValid()) return value
  return m.format(format)
}
