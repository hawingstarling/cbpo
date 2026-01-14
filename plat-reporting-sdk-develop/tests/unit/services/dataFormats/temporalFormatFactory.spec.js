import temporalFormatFactory from '@/services/dataFormats/temporalFormatFactory.js'

describe('temporalFormatFactory', () => {
  it('Check funtional formalt temporalFormatFactory', () => {
    // excute
    temporalFormatFactory()
    temporalFormatFactory({format: 'L'})('10/10/2010')
    temporalFormatFactory({format: ''})('10/10/2010')
  })
})
