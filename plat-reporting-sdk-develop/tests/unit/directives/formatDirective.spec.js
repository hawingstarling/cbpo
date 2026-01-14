import formatDirective from '@/directives/formatDirective.js'

describe('formatDirective', () => {
  it('Check object formalt formatDirective', () => {
    // excute
    formatDirective.bind({}, {})
    formatDirective.update(null, {value: 1, oldValue: 2})
    formatDirective.update(null, {value: 1, oldValue: 1})
    formatDirective.bind({innerHTML: ''}, {value: {
      data: 1,
      dataType: 1,
      aggr: false,
      aggrFormats: 1,
      format: 1
    }})
  })
  it('Check funtional bind', () => {
    // excute
    // formatDirective.bind({innerHTML: ''}, {value: {
    //   data: 1,
    //   dataType: 1,
    //   aggr: true,
    //   aggrFormats: 1,
    //   format: 1
    // }})
  })
})
