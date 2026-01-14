import { LocalFilterExpressionBuilder } from '@/services/ds/filter/FilterExpessionBuilders.js'

describe('FilterExpessionBuilders', () => {
  it('Check functional quoteColumn', () => {
    // setup
    var localFilterClass = new LocalFilterExpressionBuilder()
    // excute
    // localFilterClass.quoteColumn({column: '1'})
  })
  it('Check functional quoteValue', () => {
    // setup
    var localFilterClass = new LocalFilterExpressionBuilder()
    // excute
    // localFilterClass.quoteValue(1, 1)
  })
  it('Check class AbstractFilterExpressionBuilder', () => {
    // excute
    LocalFilterExpressionBuilder.quoteValue = function () {
      return ''
    }
  })
})
