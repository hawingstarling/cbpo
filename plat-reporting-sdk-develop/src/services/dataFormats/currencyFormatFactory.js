import _ from 'lodash'
import currencyFormatConfig from './currencyFormatConfig'
import numericFormatFactory from './numericFormatFactory'
export default (formatConfig) => {
  _.defaults(formatConfig, currencyFormatConfig)
  let formatFn = numericFormatFactory(formatConfig.numeric)
  return (value) => {
    if (formatConfig.currency.inCents) {
      value = value * 0.01
    }
    if (!formatConfig.currency.symbol) {
      return formatFn(value)
    }
    if (!formatConfig.currency.symbolPrefix) {
      return formatFn(value) + formatConfig.currency.symbol
    }
    if (value < 0) {
      return '-' + formatConfig.currency.symbol + formatFn(value).replace('-', '')
    }
    return formatConfig.currency.symbol + formatFn(value)
  }
}
