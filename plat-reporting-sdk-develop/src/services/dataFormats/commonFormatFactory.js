import commonFormatConfig from './commonFormatConfig'
import _ from 'lodash'
export default (formatConfig, formatFunction, isHtml) => {
  _.defaultsDeep(formatConfig, commonFormatConfig)
  return (value, rowValue, provideIsHtml = isHtml) => {
    let commonObj = provideIsHtml ? formatConfig.html : formatConfig.plain
    // checking case null
    let result = checkingValue(value, commonObj)
    if (result.isEmpty) return result.value
    // else, try format valid value
    value = formatFunction(value, rowValue, provideIsHtml)
    // this will use for override if they default is null or empty, can reuse this common
    result = checkingValue(value, commonObj)
    if (result.isEmpty) return result.value
    // if result is not empty, return value with prefix, suffix
    if (formatConfig.prefix) {
      value = '' + formatConfig.prefix + value
    }
    if (formatConfig.suffix) {
      value = '' + value + formatConfig.suffix
    }
    return value
  }
}

const checkingValue = (value, commonObj) => {
  let isEmpty = true
  if (_.isNull(value) || _.isUndefined(value)) {
    return {
      value: commonObj.nil,
      isEmpty
    }
  }
  // empty
  if (_.isEmpty('' + value)) {
    return {
      value: commonObj.empty,
      isEmpty
    }
  }
  if (_.isNaN(value)) {
    return {
      value: commonObj.na,
      isEmpty
    }
  }
  isEmpty = false
  return { isEmpty, value }
}
