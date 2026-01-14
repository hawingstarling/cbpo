import namedFormatFactory from '@/services/dataFormats/namedFormatFactory.js'

describe('namedFormatFactory', () => {
  it('Check funtional formalt namedFormatFactory', () => {
    // excute
    namedFormatFactory('amazon')
    window.amazon = () => 'amazon'
    namedFormatFactory('amazon')
  })
})
