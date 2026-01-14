import { checkDsColumn } from '@/utils/precondUtil.js'

describe('precondUtil.js', () => {
  it('check checkDsColumn', () => {
    // excute
    checkDsColumn({name: 'Seller', type: 'int'})
    // verify
    expect(typeof checkDsColumn).toBe('function')
  })
})
