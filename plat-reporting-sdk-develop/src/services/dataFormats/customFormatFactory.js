import defaultsDeep from 'lodash/defaultsDeep'
import isFunction from 'lodash/isFunction'
import customFormatConfig from '@/services/dataFormats/customFormatConfig'
import dsManager from '@/services/dataFormatManager'

export default (formatConfig) => {
  const config = defaultsDeep(formatConfig, customFormatConfig)
  return (cellValue, rowValue, isHtml = true) => {
    if (!isFunction(config.condition)) {
      console.error('condition in format type custom must be a function')
      return cellValue
    }
    const formatObj = config.condition(cellValue, rowValue)
    return formatObj ? dsManager.create(formatObj, isHtml)(cellValue) : cellValue
  }
}
