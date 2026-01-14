import linkFormatFactory from '@/services/dataFormats/linkFormatFactory.js'

describe('linkFormatFactory', () => {
  it('Check funtional formalt linkFormatFactory', () => {
    // excute
    linkFormatFactory({})('gitlab.com')
    linkFormatFactory({})('https://gitlab.com')
  })
})
