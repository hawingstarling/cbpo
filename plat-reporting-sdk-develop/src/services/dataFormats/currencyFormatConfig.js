import numericFormatConfig from './numericFormatConfig'

export default {
  currency: {
    symbol: '$',
    symbolPrefix: true,
    inCents: true
  },
  numeric: Object.assign({}, numericFormatConfig)
}
