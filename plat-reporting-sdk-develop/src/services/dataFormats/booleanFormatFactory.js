import booleanFormatConfig from './booleanFormatConfig'
import _ from 'lodash'

// TODO isHtml option for this method
export default (formatConfig, isHtml) => {
  _.defaultsDeep(formatConfig, booleanFormatConfig)
  return (value) => {
    if (value) {
      value = isHtml ? formatConfig.positive.html : formatConfig.positive.text
    } else {
      value = isHtml ? formatConfig.negative.html : formatConfig.negative.text
    }
    return value
  }
}
