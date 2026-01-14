import currencyFormatFactory from '@/services/dataFormats/currencyFormatFactory.js'

describe('currencyFormatFactory', () => {
  it('Check funtional formalt currencyFormatFactory', () => {
    // excute
    currencyFormatFactory({
      currency: {
        inCents: 'dollar',
        symbolPrefix: '$',
        symbol: '%'
      }
    })(1)
    currencyFormatFactory({
      currency: {
        inCents: 'dollar',
        symbol: '%'
      }
    })(1)
    currencyFormatFactory({
      currency: ''
    })(1)
  })
})
