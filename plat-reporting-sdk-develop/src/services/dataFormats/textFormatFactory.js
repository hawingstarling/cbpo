import { isObject, camelCase, startCase, defaultsDeep } from 'lodash'
import { textFormatConfig, TYPES_TRANSFORM } from './textFormatConfig'

export default (formatConfig) => {
  // check type before apply config
  if (!isObject(formatConfig)) {
    console.error('formatConfig is required as an Object')
  }

  // default config
  defaultsDeep(formatConfig, textFormatConfig)

  return value => {
    switch (formatConfig.transform) {
      case 'uppercase': return value.toUpperCase()
      case 'lowercase': return value.toLowerCase()
      case 'camelcase': return camelCase(value)
      case 'startcase': return startCase(value)
      default: {
        if (formatConfig.transform !== null) console.error('Transform type is invalid. These values is allowed: ' + TYPES_TRANSFORM.join(','))
        return value
      }
    }
  }
}
