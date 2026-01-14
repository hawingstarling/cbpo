import progressFormatFactory from '@/services/dataFormats/progressFormatFactory.js'

describe('progressFormatFactory', () => {
  it('Check functional format progressFormatFactory', () => {
    // excute
    progressFormatFactory({
      base: 1
    })(0.5)
    progressFormatFactory({
      isHtml: true
    })('50%')
  })
})
