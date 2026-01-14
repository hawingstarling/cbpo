import * as util from '@/utils/chartUtil.js'

describe('chartUtil.js', () => {
  xit('check checkDsColumn', () => {
    // excute
    let result = util.randomColor(2)
    // verify
    expect(result).toEqual(['#1f77b4', '#aec7e8'])
  })
  xit('check checkDsColumn2', () => {
    // excute
    let result = util.randomColor(0)
    // verify
    expect(result).toEqual([])
  })
  xit('check checkDsColumn3', () => {
    // excute
    let result = util.randomColor('a')
    // verify
    expect(result).toEqual([])
  })
  xit('check buildDataChart', () => {
    // excute
    let result = util.buildDataChart({
      cols: [{name: 'column1'}, {name: 'column2'}],
      rows: [
        [1, 2],
        [3, 4],
        [5, 6]
      ]
    }, {
      x: 'column1',
      y: 'column2'
    })
    // verify
    expect(result).toEqual({
      data: [2, 4, 6],
      labels: [1, 3, 5]
    })
  })
  xit('Check format value with si prefix case 1', () => {
    expect(util.formatNumberWithSiPrefix(100)).toEqual(100)
  })
  xit('Check format value with si prefix case 2', () => {
    expect(util.formatNumberWithSiPrefix('abc')).toEqual('abc')
  })
  xit('Check format value with si prefix case 3', () => {
    expect(util.formatNumberWithSiPrefix(1000)).toEqual('1k')
  })
})
