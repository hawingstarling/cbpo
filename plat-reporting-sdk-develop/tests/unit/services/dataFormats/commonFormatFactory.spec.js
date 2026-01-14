import commonFormatFactory from '@/services/dataFormats/commonFormatFactory.js'

describe('commonFormatFactory', () => {
  it('Check funtional format commonFormatFactory', () => {
    // excute
    commonFormatFactory({html: '<span>EMPTY</span>'})(undefined)
    commonFormatFactory({})('')
    commonFormatFactory({prefix: 'e', suffix: 'e'}, function (e) {
      return e
    })('e')
  })
})
