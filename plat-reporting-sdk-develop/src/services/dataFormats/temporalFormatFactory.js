import temporalFormatConfig from './temporalFormatConfig'
import moment from 'moment-timezone'
import _ from 'lodash'

export default (formatConfig) => {
  if (!_.isObject(formatConfig)) {
    console.error('formatConfig is required as an Object')
  }
  _.defaults(formatConfig, temporalFormatConfig)
  return value => {
    if (typeof value === 'number') return value
    // convert date object
    const dateValue = new Date(value)
    if (!(Object.prototype.toString.call(dateValue) === '[object Date]' && !isNaN(dateValue.getTime()))) return value
    let temp = ''
    if (formatConfig.format) {
      temp = !_.isEmpty(formatConfig.timezone)
        ? moment(dateValue).tz(formatConfig.timezone).format(formatConfig.format)
        : moment(dateValue).format(formatConfig.format)
    } else {
      console.error('formatConfig is required as an Object')
    }
    // TODO (tbd) more process for temporal format
    return temp || value
  }
}
