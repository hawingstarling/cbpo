import _ from 'lodash'
import defaultOverrideConfig from '@/services/dataFormats/overrideFormatConfig'

export default (formatConfig) => {
  if (!_.isObject(formatConfig)) {
    console.error('formatConfig is required as an Object')
  }

  _.defaults(formatConfig, defaultOverrideConfig)
  return () => formatConfig.format.text
}
