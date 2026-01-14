import numericFormatConfig from './numericFormatConfig'
import * as d3 from 'd3'
import _ from 'lodash'
export default (formatConfig) => {
  if (!_.isObject(formatConfig)) {
    console.error('formatConfig is required as an Object')
  }

  _.defaults(formatConfig, numericFormatConfig)

  let formatStr = ''
  if (formatConfig.comma) {
    formatStr = formatStr.concat(',')
  }
  if (formatConfig.precision >= 0) {
    formatStr = formatStr.concat('.', formatConfig.precision)
  }
  if (formatConfig.siPrefix) {
    formatStr = formatStr.concat('s')
  } else if (formatConfig.precision >= 0) {
    formatStr = formatStr.concat('f')
  } else {
    formatStr = formatStr.concat('g')
  }
  let isNumeric = (n) => {
    return !isNaN(parseFloat(n)) && isFinite(n)
  }
  return value => {
    if (isNumeric(value)) {
      return formatConfig.abs ? d3.format(formatStr)(Math.abs(value)) : d3.format(formatStr)(value)
    }
    console.warn(value + ' is not a number.')
    return value
  }
}
