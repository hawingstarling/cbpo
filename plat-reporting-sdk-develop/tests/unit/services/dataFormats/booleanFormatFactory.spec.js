import booleanFormatFactory from '@/services/dataFormats/booleanFormatFactory.js'

describe('booleanFormatFactory', () => {
  it('Check funtional formalt booleanFormatFactory', () => {
    // excute
    booleanFormatFactory({})(true)
    booleanFormatFactory({})(false)
  })
})
